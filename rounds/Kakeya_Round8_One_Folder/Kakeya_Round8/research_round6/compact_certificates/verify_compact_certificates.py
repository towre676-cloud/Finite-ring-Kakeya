"""Portable proof replay of all38 standard compact DRAT certificates.

No original dense LRAT or old source core is needed. Regenerate the exact CNF,
decode and hash the stored DRAT, run pinned DRAT-trim to produce fresh LRAT,
and require pinned CakeML acceptance against that same exact CNF.
"""
from pathlib import Path
import argparse
import concurrent.futures
import hashlib
import importlib.util
import json
import lzma
import re
import shutil
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location(
    "compact_replay_semantics", ROOT / "research_round6/proof_core/verify_cores.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)
A, STORAGE = V.A, V.STORAGE


def dump(path, value):
    temporary = Path(str(path) + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def load_manifest():
    path = HERE / "COMPACT_CERTIFICATE_MANIFEST.json"
    manifest = json.loads(path.read_text())
    A.require(manifest["schema"] == "kakeya-compact-drat-v1", "Wrong compact schema")
    A.require(manifest["status"] == "PASS_COMPLETE_38_COMPACT_DRAT_CERTIFICATES",
              "Compact manifest is incomplete")
    A.require(manifest["scope"] == "joint_maximum_2_18"
              and manifest["maximum_interval"] == [2, 18]
              and manifest["total_upper_bound"] == 93
              and manifest["ring_scope"] == "common_necessary_relaxation_both_rings",
              "Wrong mathematical scope")
    reference = manifest["original_joint_manifest"]
    original_path = (HERE / reference["path"]).resolve()
    A.require(original_path == ROOT / "research_round6/joint_maxima/JOINT_CERTIFICATE_MANIFEST.json",
              "Wrong authoritative source manifest path")
    A.require(A.sha(original_path) == reference["sha256"], "Authoritative manifest hash mismatch")
    original = json.loads(original_path.read_text())
    A.require(original["schema"] == "kakeya-joint-maximum-certificate-v1"
              and original["status"] == "PASS_COMPLETE_38_CASE_INVENTORY_AND_ACCEPTED_FILE_HASHES",
              "Original joint manifest is incomplete")
    A.require(original["maximum_interval"] == [2, 18]
              and original["total_upper_bound"] == 93
              and original["ring_scope"] == manifest["ring_scope"],
              "Original source scope differs")
    A.require(manifest["semantic_input_hashes"] == original["semantic_input_hashes"],
              "Semantic source pins differ")
    required = {
        "research_round6/joint_maxima/encode_joint_maxima.py",
        "research_round6/imported_claude_round4/data/spec32.csv",
        "research_round6/imported_claude_round4/data/Mtable.txt",
        "research_round6/catalogue_audit/CLAUDE_TO_ROUND5_38_CASE_MAP.json",
    }
    A.require(required <= set(manifest["semantic_input_hashes"]), "Missing semantic source pins")
    for relative, digest in manifest["semantic_input_hashes"].items():
        A.require(A.sha(ROOT / relative) == digest, "Changed semantic source: " + relative)
    original_cases = {row["case_id"]: row for row in original["cases"]}
    declared = manifest["cases"]
    cases = {row["case_id"]: row for row in declared}
    expected = manifest["expected_case_ids"]
    A.require(len(declared) == len(cases) == len(expected) == len(set(expected)) == 38,
              "Expected exactly38 distinct compact cases")
    A.require(set(cases) == set(expected) == set(original["expected_case_ids"]) == set(original_cases),
              "Compact cases do not exactly cover the original case universe")
    normalized = []
    for row in declared:
        case_id = row["case_id"]
        A.require(re.fullmatch(r"m2_18_[A-Za-z0-9_.-]+", case_id), "Unsafe or wrong case ID")
        old = original_cases[case_id]
        A.require(row["source_kind"] == "joint" and row["maximum_interval"] == [2, 18]
                  and row["total_upper_bound"] == 93, "Wrong case parameters")
        A.require(row["marked_support"] == old["marked_support"]
                  and row["cnf_sha256"] == old["cnf_sha256"]
                  and row["expected_lrat_sha256"] == old["lrat_sha256"],
                  "Case differs from authoritative CNF/support/source binding")
        A.require((HERE / row["cnf"]).resolve() == (original_path.parent / old["cnf"]).resolve(),
                  "CNF path differs from authoritative manifest")
        A.require(row["proof"] == f"cases/{case_id}/proof.drat.xz"
                  and row["receipt"] == f"cases/{case_id}/CASE_RECEIPT.json",
                  "Unexpected compact proof/receipt path")
        receipt_path = HERE / row["receipt"]
        A.require(A.sha(receipt_path) == row["receipt_sha256"], "Case receipt hash mismatch")
        receipt = json.loads(receipt_path.read_text())
        A.require(receipt["status"] == "PASS_COMPACT_DRAT_VIA_CAKEML",
                  "Case lacks required production acceptance")
        for key in ("case_id", "source_kind", "maximum_interval", "total_upper_bound",
                    "marked_support", "cnf_sha256", "expected_lrat_sha256",
                    "source_core_sha256", "source_core_bytes", "source_core_compressed_sha256",
                    "drat_sha256", "drat_bytes", "compressed_sha256", "compressed_bytes"):
            A.require(row[key] == receipt[key], "Case fields differ from acceptance receipt: " + key)
        A.require(receipt["joint_manifest_sha256"] == reference["sha256"],
                  "Receipt binds another source manifest")
        A.require(receipt["audit"]["status"] == "PASS_CNF_UNSAT_VIA_CAKEML_LRAT"
                  and receipt["audit"]["drat_trim"]["accepted"]
                  and receipt["audit"]["cake_lpr"]["accepted"]
                  and receipt["audit"]["input_sha256"] == {
                      "cnf": row["cnf_sha256"], "drat": row["drat_sha256"]},
                  "Malformed previous acceptance evidence")
        normalized.append({"case_id": case_id[len("m2_18_"):],
                           "marked_support": row["marked_support"]})
    contract = dict(manifest["coverage_contract"])
    geometry_manifest = {"expected_case_ids": [row["case_id"] for row in normalized],
                         "coverage_contract": contract}
    coverage = A.check_marked_contract(geometry_manifest, normalized, path)
    return manifest, declared, coverage


def replay_one(task):
    row, binaries, timeout, heap_mb = task
    started = time.monotonic()
    case_id = row["case_id"]
    output = HERE / "replay_logs" / case_id
    output.mkdir(parents=True, exist_ok=True)
    result = {"case_id": case_id, "status": "NOT_ACCEPTED"}
    try:
        logical_cnf = (HERE / row["cnf"]).resolve()
        stored = HERE / row["proof"]
        A.require(stored.stat().st_size == row["compressed_bytes"], "Compressed size mismatch")
        A.require(A.sha(stored) == row["compressed_sha256"], "Compressed DRAT hash mismatch")
        with tempfile.TemporaryDirectory(prefix="kakeya_compact_replay_", dir="/tmp") as temporary, \
                STORAGE.materialized(logical_cnf, row["cnf_sha256"], directory=temporary,
                                     prefer_compressed=True) as cnf:
            work = Path(temporary)
            regenerated = work / "regenerated.cnf"
            V.regenerate_exact_cnf(row, regenerated)
            regenerated.unlink()
            proof = work / "proof.drat"
            digest = hashlib.sha256()
            size = 0
            with lzma.open(stored, "rb") as source, proof.open("wb") as destination:
                for block in iter(lambda: source.read(4 << 20), b""):
                    size += len(block)
                    A.require(size <= row["drat_bytes"], "Decoded DRAT exceeds declared size")
                    digest.update(block)
                    destination.write(block)
            A.require(size == row["drat_bytes"] and digest.hexdigest() == row["drat_sha256"],
                      "Decoded DRAT is not the accepted exact proof")
            audit = A.check_pair(cnf, proof, work / "audit", binaries, timeout, heap_mb, 256, False)
            result["audit"] = audit
            A.require(audit["status"] == "PASS_CNF_UNSAT_VIA_CAKEML_LRAT",
                      "Required DRAT-trim and CakeML route did not accept")
            A.require(audit["input_sha256"] == {"cnf": row["cnf_sha256"], "drat": row["drat_sha256"]},
                      "Checker used unexpected inputs")
            A.require(A.sha(stored) == row["compressed_sha256"],
                      "Persisted DRAT archive changed during checking")
            A.require(STORAGE.logical_sha(logical_cnf, prefer_compressed=True) == row["cnf_sha256"],
                      "Persisted CNF changed during checking")
            for p in (work / "audit").glob("*.txt"):
                shutil.copyfile(p, output / p.name)
            result.update(status="PASS_COMPACT_DRAT_REPLAY_VIA_CAKEML",
                          cnf_sha256=row["cnf_sha256"], drat_sha256=row["drat_sha256"],
                          byte_identical_cnf_regeneration=True,
                          original_dense_lrat_required=False)
    except Exception as error:
        result["error"] = repr(error)
    result["seconds"] = round(time.monotonic() - started, 6)
    return result


def run(args, target, started):
    if args.jobs not in (1, 2):
        raise ValueError("Use one or two workers")
    if args.timeout <= 0 or args.heap_mb <= 0:
        raise ValueError("Timeout and heap limit must be positive")
    manifest, rows, coverage = load_manifest()
    if args.quick:
        rows = [min((r for r in rows if len(r["marked_support"]["support"]) == size),
                    key=lambda r: r["drat_bytes"]) for size in (11, 12)]
    rows.sort(key=lambda row: row["drat_bytes"], reverse=True)
    pins = A.verify_sources()
    binaries, build = A.build_checkers(HERE / "replay_bin", HERE / "replay_build_logs")
    results = []
    dump(target, {"status": "RUNNING", "quick": args.quick, "expected": len(rows),
                  "completed": 0, "cases": []})
    with concurrent.futures.ProcessPoolExecutor(args.jobs) as pool:
        futures = [pool.submit(replay_one, (row, binaries, args.timeout, args.heap_mb)) for row in rows]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps({k: result.get(k) for k in ("case_id", "status", "seconds")}), flush=True)
            dump(target, {"status": "RUNNING", "quick": args.quick, "expected": len(rows),
                          "completed": len(results), "cases": results})
    good = len(results) == len(rows) and all(
        r["status"] == "PASS_COMPACT_DRAT_REPLAY_VIA_CAKEML" for r in results)
    record = {"status": "PASS_ALL_REQUESTED_COMPACT_REPLAYS" if good else "INCOMPLETE_OR_FAILED",
              "quick": args.quick, "full_scope_replayed": not args.quick,
              "expected": len(rows), "completed": len(results), "cases": results,
              "coverage": coverage, "semantic_input_hashes": manifest["semantic_input_hashes"],
              "compact_manifest_sha256": A.sha(HERE / "COMPACT_CERTIFICATE_MANIFEST.json"),
              "original_joint_manifest": manifest["original_joint_manifest"],
              "pinned_sources": pins, "checker_build": build,
              "encoder_formally_verified": False, "converter_trusted_for_unsat": False,
              "original_dense_lrat_required": False,
              "seconds": round(time.monotonic() - started, 6)}
    dump(target, record)
    print(record["status"], flush=True)
    return 0 if good else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--heap-mb", type=int, default=1024)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    started = time.monotonic()
    target = HERE / ("QUICK_REPLAY_RECEIPT.json" if args.quick else "COMPACT_REPLAY_RECEIPT.json")
    # Invalidate any previous success before reading manifests, source pins,
    # or rebuilding checkers. A failed preflight cannot leave a stale PASS.
    dump(target, {"status": "RUNNING", "quick": args.quick,
                  "expected": None, "completed": 0, "cases": []})
    try:
        return run(args, target, started)
    except Exception as error:
        dump(target, {"status": "FAIL", "quick": args.quick,
                      "error": repr(error), "seconds": round(time.monotonic() - started, 6),
                      "full_scope_replayed": False, "new_acceptance_claimed": False})
        print("FAIL:", repr(error), flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
