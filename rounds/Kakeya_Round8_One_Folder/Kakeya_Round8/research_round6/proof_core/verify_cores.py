"""Portable replay of all declared compressed LRAT core certificates.

Requires Python3, a C compiler, Linux x86_64, and temporary disk space for the
largest one or two ASCII cores. Does not need original solver proofs, a SAT
solver, the untrusted trimmer, or network access.
"""
from pathlib import Path
import argparse
import concurrent.futures
import functools
import hashlib
import importlib.util
import json
import lzma
import re
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location(
    "core_replay_pinned_audit", ROOT / "research_round5/proof_audit/audit_certificates.py")
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)
storage_spec = importlib.util.spec_from_file_location(
    "core_certificate_storage", ROOT / "research_round6/certificate_storage.py")
STORAGE = importlib.util.module_from_spec(storage_spec)
storage_spec.loader.exec_module(STORAGE)


def dump(path, record):
    temporary = Path(str(path) + ".tmp")
    temporary.write_text(json.dumps(record, indent=2) + "\n")
    temporary.replace(path)


@functools.lru_cache(maxsize=2)
def encoder_inputs(kind):
    imported = ROOT / "research_round6/imported_claude_round4"
    path = (ROOT / "research_round6/joint_maxima/encode_joint_maxima.py"
            if kind == "joint" else imported / "src/encode_cnf2.py")
    spec = importlib.util.spec_from_file_location("core_exact_encoder_" + kind, path)
    encoder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(encoder)
    return (encoder, encoder.load_spectra(imported / "data/spec32.csv"),
            encoder.load_M(imported / "data/Mtable.txt"), encoder.all_subspaces())


def regenerate_exact_cnf(record, destination):
    encoder, spectra, capacities, subspaces = encoder_inputs(record["source_kind"])
    marked = record["marked_support"]
    A.require(marked["distinguished_hub"] == 0, "Exact encoder requires hub at residue zero")
    outer = [v for v in marked["support"] if v != 0]
    if record["source_kind"] == "joint":
        formula = encoder.encode(outer, 18, spectra, capacities, subspaces,
                                 outtotal=93, hub_min=2)
    else:
        formula = encoder.encode(outer, 19, spectra, capacities, subspaces)
    encoder.write_dimacs(formula, destination)
    del formula
    A.require(A.sha(destination) == record["cnf_sha256"],
              "Exact regenerated CNF does not match the declared support/maximum case")


def verify_case(task):
    record, executable, timeout, heap_mb = task
    started = time.monotonic()
    case_id = record["case_id"]
    folder = HERE / "cases" / case_id
    output = HERE / "replay_logs" / case_id
    output.mkdir(parents=True, exist_ok=True)
    result = {"case_id": case_id, "status": "NOT_ACCEPTED"}
    try:
        logical_cnf = (folder / record["cnf_from_case_folder"]).resolve()
        compressed = folder / record["core_file"]
        A.require(A.sha(compressed) == record["compressed_sha256"], "Compressed core hash mismatch")
        with tempfile.TemporaryDirectory(prefix="kakeya_core_replay_", dir="/tmp") as temporary, \
                STORAGE.materialized(logical_cnf, record["cnf_sha256"], directory=temporary,
                                     prefer_compressed=True) as cnf:
            regenerated = Path(temporary) / "regenerated.cnf"
            regenerate_exact_cnf(record, regenerated)
            regenerated.unlink()
            proof = Path(temporary) / "core.lrat"
            digest = hashlib.sha256()
            size = 0
            with lzma.open(compressed, "rb") as source, proof.open("wb") as destination:
                for block in iter(lambda: source.read(4 << 20), b""):
                    size += len(block)
                    A.require(size <= record["core_bytes"], "Decoded proof exceeds declared size")
                    digest.update(block)
                    destination.write(block)
            A.require(size == record["core_bytes"], "Decoded proof size mismatch")
            A.require(digest.hexdigest() == record["core_sha256"], "Decoded core hash mismatch")
            checked = A.run_checker(
                [executable, f"--CML_HEAP_SIZE={heap_mb}", "--CML_STACK_SIZE=256", cnf, proof],
                output, "cake_lpr", timeout, "s VERIFIED UNSAT", True)
            result["cake_lpr"] = checked
            A.require(checked["accepted"], "CakeML did not accept")
            A.require(A.sha(cnf) == record["cnf_sha256"], "CNF changed during replay")
            A.require(A.sha(proof) == record["core_sha256"], "Core changed during replay")
            A.require(A.sha(compressed) == record["compressed_sha256"],
                      "Stored compressed certificate changed during replay")
            A.require(STORAGE.logical_sha(logical_cnf, prefer_compressed=True) == record["cnf_sha256"],
                      "Stored CNF artifact changed during replay")
            result.update(status="PASS_CORE_LRAT_VIA_CAKEML",
                          cnf_sha256=record["cnf_sha256"], core_sha256=record["core_sha256"],
                          byte_identical_cnf_regeneration=True)
    except Exception as error:
        result["error"] = repr(error)
    result["seconds"] = round(time.monotonic() - started, 6)
    return result


def authoritative_binding(rows, kind):
    if kind == "joint":
        path = ROOT / "research_round6/joint_maxima/JOINT_CERTIFICATE_MANIFEST.json"
        manifest = json.loads(path.read_text())
        A.require(manifest["schema"] == "kakeya-joint-maximum-certificate-v1", "Wrong joint manifest schema")
        A.require(manifest["status"] == "PASS_COMPLETE_38_CASE_INVENTORY_AND_ACCEPTED_FILE_HASHES",
                  "Original joint manifest is incomplete")
        A.require(manifest["maximum_interval"] == [2, 18] and manifest["total_upper_bound"] == 93,
                  "Original joint mathematical parameters differ")
        A.require(manifest["ring_scope"] == "common_necessary_relaxation_both_rings",
                  "Original joint ring scope differs")
        sources = {str(ROOT / relative): digest for relative, digest in manifest["semantic_input_hashes"].items()}
        key = lambda row: row["case_id"]
    else:
        path = ROOT / "research_round6/certification/M19_CERTIFICATE_MANIFEST.json"
        manifest = json.loads(path.read_text())
        A.require(manifest["schema"] == "kakeya-proof-audit-v1", "Wrong m19 manifest schema")
        sources = {str((path.parent / item["path"]).resolve()): item["sha256"]
                   for item in manifest["semantic_reference_files"]}
        key = lambda row: row["case_id"][len("m19_"):]
    encoder = (ROOT / "research_round6/joint_maxima/encode_joint_maxima.py"
               if kind == "joint" else ROOT / "research_round6/imported_claude_round4/src/encode_cnf2.py")
    required = {str(encoder), str(ROOT / "research_round6/imported_claude_round4/data/spec32.csv"),
                str(ROOT / "research_round6/imported_claude_round4/data/Mtable.txt")}
    A.require(required <= set(sources), "Missing mathematical encoder/data source pins")
    for source, digest in sources.items():
        A.require(A.sha(source) == digest, "Semantic input source has changed: " + source)
    declared = manifest["cases"]
    table = {row["case_id"]: row for row in declared}
    A.require(len(declared) == len(table) == 38, "Wrong original manifest case inventory")
    A.require(set(table) == set(manifest["expected_case_ids"]) == {key(row) for row in rows},
              "Core cases differ from original authoritative manifest")
    for row in rows:
        original = table[key(row)]
        A.require(row["cnf_sha256"] == original["cnf_sha256"], "Core CNF differs from authoritative manifest")
        A.require(row["expected_lrat_sha256"] == original["lrat_sha256"],
                  "Source LRAT provenance differs from authoritative manifest")
        A.require(row["marked_support"] == original["marked_support"], "Support metadata changed")
        cnf = (path.parent / original["cnf"]).resolve()
        relative_cnf = (HERE / "cases" / row["case_id"] / row["cnf_from_case_folder"]).resolve()
        A.require(cnf == relative_cnf, "CNF path differs from authoritative manifest")
        if kind == "joint":
            A.require(row["maximum_interval"] == original["maximum_interval"] == [2, 18]
                      and original["total_upper_bound"] == 93, "Case interval/budget mismatch")
        else:
            A.require(original["metadata"]["m"] == 19
                      and original["metadata"]["total_upper_bound"] == 93, "Case maximum/budget mismatch")
    return {"status": "PASS_AUTHORITATIVE_MANIFEST_AND_SEMANTIC_SOURCE_BINDING",
            "manifest": str(path.relative_to(ROOT)), "manifest_sha256": A.sha(path),
            "semantic_input_hashes": {str(Path(p).relative_to(ROOT)): digest for p, digest in sources.items()}}


def inventory(index):
    A.require(index["status"] == "PASS_ALL_REQUESTED_CORES", "Batch receipt is not complete")
    A.require(index["selection_complete_for_scope"], "Selected cases cannot certify a complete scope")
    scope = index["scope"]
    A.require(scope in ("joint", "m19", "both"), "Unknown scope")
    declared = index["cases"]
    rows = []
    for record in declared:
        case_id = record["case_id"]
        A.require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", case_id), "Unsafe case identifier")
        receipt = HERE / "cases" / case_id / "CORE_RECEIPT.json"
        saved = json.loads(receipt.read_text())
        A.require(saved == record, "Individual core receipt differs from batch manifest")
        A.require(saved["status"] == "PASS_CORE_LRAT_VIA_CAKEML", "Unaccepted core in batch")
        rows.append(saved)
    A.require(len(rows) == len({r["case_id"] for r in rows}), "Duplicate case identifier")
    contract = ROOT / "research_round5/encoding_bridge/M19_MARKED_CASE_CONTRACT.json"
    expected_geometry = [r["case_id"] for r in json.loads(contract.read_text())["cases"]]
    coverage = {}
    for kind in (["joint", "m19"] if scope == "both" else [scope]):
        selected = [r for r in rows if r["source_kind"] == kind]
        interval = [2, 18] if kind == "joint" else [19, 19]
        prefix = "m2_18_" if kind == "joint" else "m19_"
        A.require(len(selected) == 38, f"Expected38 {kind} cases")
        A.require(all(r["maximum_interval"] == interval for r in selected), "Wrong maximum interval")
        normalized = []
        for record in selected:
            A.require(record["case_id"].startswith(prefix), "Case prefix mismatch")
            normalized.append({"case_id": record["case_id"][len(prefix):],
                               "marked_support": record["marked_support"]})
        manifest = {"expected_case_ids": expected_geometry,
                    "coverage_contract": {"path": str(contract), "sha256": A.M19_CONTRACT_SHA256,
                                          "ring_scope": "common_relaxation_both_rings"}}
        coverage[kind] = A.check_marked_contract(manifest, normalized, HERE / "CORE_BATCH_RECEIPT.json")
        coverage[kind]["semantic_binding"] = authoritative_binding(selected, kind)
    A.require(len(rows) == (76 if scope == "both" else 38), "Unexpected case count")
    return rows, coverage


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--heap-mb", type=int, default=1024)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    if args.jobs not in (1, 2):
        raise ValueError("Use one or two workers")
    index = json.loads((HERE / "CORE_BATCH_RECEIPT.json").read_text())
    rows, coverage = inventory(index)
    if args.quick:
        rows = [min((r for r in rows if len(r["marked_support"]["support"]) == size),
                    key=lambda r: r["core_bytes"]) for size in (11, 12)]
    rows.sort(key=lambda r: r["core_bytes"], reverse=True)
    pins = A.verify_sources()
    binaries, build = A.build_checkers(HERE / "replay_bin", HERE / "replay_build_logs")
    started = time.monotonic()
    results = []
    target = HERE / ("QUICK_CORE_REPLAY.json" if args.quick else "CORE_REPLAY.json")
    with concurrent.futures.ProcessPoolExecutor(args.jobs) as pool:
        futures = [pool.submit(verify_case, (r, binaries["cake_lpr"],
                                            args.timeout, args.heap_mb)) for r in rows]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps({k: result.get(k) for k in ["case_id", "status", "seconds"]}), flush=True)
            dump(target, {"status": "RUNNING", "quick": args.quick, "completed": len(results),
                          "expected": len(rows), "cases": results})
    good = len(results) == len(rows) and all(
        r["status"] == "PASS_CORE_LRAT_VIA_CAKEML" for r in results)
    report = {"status": "PASS_ALL_REQUESTED_CORE_REPLAYS" if good else "INCOMPLETE_OR_FAILED",
              "quick": args.quick, "full_scope_replayed": not args.quick,
              "scope": index["scope"], "completed": len(results), "expected": len(rows),
              "cases": results, "coverage": coverage, "pinned_sources": pins,
              "checker_build": build, "encoder_soundness_proved_by_this_replay": False,
              "seconds": round(time.monotonic() - started, 6)}
    dump(target, report)
    print(report["status"], flush=True)
    return 0 if good else 1


if __name__ == "__main__":
    raise SystemExit(main())
