#!/usr/bin/env python3
"""Produce and replay independently checked compact dimension-four DRATs.

Original proofs remain untouched and are not required for compact replay.
Each core is checked against its exact original CNF. Timeouts retain no
proof and receive no exclusion credit. The final manifest preserves the
complete source inventory and its mathematical scope.
"""
from pathlib import Path
from contextlib import ExitStack
import argparse
import gc
import json
import shutil
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE_DIR = HERE.parent / "dimension4"
sys.path.insert(0, str(SOURCE_DIR))
import verify_dimension4 as V

A, C, P, E, G = V.A, V.C, V.P, V.E, V.G
SOURCE = SOURCE_DIR / "DIMENSION4_CERTIFICATE_MANIFEST.json"
MANIFEST = HERE / "COMPACT_DIMENSION4_MANIFEST.json"
CORE_PASS = "PASS_COMPACT_DIMENSION4_DRAT_AGAINST_ORIGINAL_CNF"


def source_inventory():
    digest = A.sha(SOURCE)
    catalogue = V.D.load_catalogue()
    manifest = V.load(catalogue, check_artifact_bytes=False)
    A.require(A.sha(SOURCE) == digest, "Source inventory changed during read")
    return manifest, catalogue, digest


def source_hashes():
    return {**V.D.sources(), str((SOURCE_DIR / "verify_dimension4.py").relative_to(ROOT)):
            A.sha(SOURCE_DIR / "verify_dimension4.py"),
            str(Path(__file__).relative_to(ROOT)): A.sha(Path(__file__))}


def copy_verified(source, target, digest):
    A.require(not target.exists(), "Refusing to overwrite published bytes")
    shutil.copyfile(source, target)
    A.require(A.sha(target) == digest, "Published bytes differ")


def validate_core(row):
    folder = HERE / "cases" / row["case_id"]
    receipt = json.loads((folder / "CORE_RECEIPT.json").read_text())
    A.require(receipt["status"] == CORE_PASS and receipt["original_case"] == row,
              "Core is not bound to this exact original case")
    A.require(receipt["audit"]["status"] == "PASS_CNF_UNSAT_VIA_CAKEML_LRAT" and
              receipt["audit"]["input_sha256"] == {"cnf": row["cnf_sha256"], "drat": receipt["core_sha256"]},
              "Core lacked acceptance against exact original CNF")
    A.require(A.sha(folder / "core.drat.xz") == receipt["storage"]["xz_sha256"], "Stored core changed")
    A.require(C.logical_sha(folder / "core.drat", prefer_compressed=True) == receipt["core_sha256"], "Decoded core changed")
    return receipt


def regenerate(row, path):
    f = P.formula(row["parameters"])
    E.write_dimacs(f, path)
    metadata = {"variables": f.n, "clauses": len(f.cl), "cnf_sha256": A.sha(path)}
    del f
    gc.collect()
    A.require(metadata["cnf_sha256"] == row["cnf_sha256"], "Original formula regeneration differs")
    return metadata


def produce_one(row, source_digest, binaries):
    A.require(row["status"] == P.UNSAT, "Only accepted UNSAT proofs may be compacted")
    original = SOURCE_DIR / "cases" / row["case_id"]
    destination = HERE / "cases" / row["case_id"]
    if destination.exists():
        return validate_core(row)
    start = time.monotonic()
    for name, info in row["storage"].items():
        A.require(A.sha(original / (name + ".xz")) == info["xz_sha256"], "Original stored bytes changed")
    with tempfile.TemporaryDirectory(prefix="kakeya_n4_core_") as temporary:
        work = Path(temporary)
        metadata = regenerate(row, work / "regenerated.cnf")
        with ExitStack() as stack:
            cnf = stack.enter_context(C.materialized(original / "input.cnf", row["cnf_sha256"], work, prefer_compressed=True))
            proof = stack.enter_context(C.materialized(original / "proof.drat", row["proof_sha256"], work, prefer_compressed=True))
            core = work / "core.drat"
            trim = A.run_checker([binaries["drat-trim"], cnf, proof, "-l", core], work, "trim", 900, "s VERIFIED", False)
            A.require(trim["accepted"] and core.is_file(), "Proof trimming failed")
            digest, raw_bytes = A.sha(core), core.stat().st_size
            audit = A.check_pair(cnf, core, work / "audit", binaries, 900, 1024, 256, False)
            A.require(audit["status"] == "PASS_CNF_UNSAT_VIA_CAKEML_LRAT", "Replacement proof rejected")
            A.require(audit["input_sha256"] == {"cnf": row["cnf_sha256"], "drat": digest}, "Wrong exact checker inputs")
            A.require(A.sha(cnf) == row["cnf_sha256"] and A.sha(proof) == row["proof_sha256"], "Original decoded input changed")
        storage = C.compress_verified(core, digest, preset=6, remove_raw=True)
        destination.mkdir(parents=True)
        copy_verified(Path(str(core) + ".xz"), destination / "core.drat.xz", storage["xz_sha256"])
        for source in list(work.glob("*.txt")) + list((work / "audit").glob("*.txt")):
            copy_verified(source, destination / source.name, A.sha(source))
        for name, info in row["storage"].items():
            A.require(A.sha(original / (name + ".xz")) == info["xz_sha256"], "Persisted original changed")
        result = {"status": CORE_PASS, "case_id": row["case_id"], "original_case": row,
                  "source_inventory_sha256_at_production": source_digest,
                  "core_sha256": digest, "core_raw_bytes": raw_bytes, "storage": storage,
                  "original_proof_compressed_bytes": (original / "proof.drat.xz").stat().st_size,
                  "formula_regeneration": metadata, "trim": trim, "audit": audit,
                  "original_cnf_used_without_added_axioms": True,
                  "original_proof_payload_required_for_replay": False,
                  "producer_sha256": A.sha(Path(__file__)), "seconds": round(time.monotonic() - start, 6)}
        P.dump(destination / "CORE_RECEIPT.json", result)
    return validate_core(row)


def freeze():
    source, catalogue, digest = source_inventory()
    rows = []
    for original in source["cases"]:
        row = {"case_id": original["case_id"], "original_case": original}
        if original["status"] == P.UNSAT:
            core = validate_core(original)
            folder = HERE / "cases" / row["case_id"]
            row.update(representation="COMPACT_DRAT", core_sha256=core["core_sha256"],
                       core_xz_sha256=core["storage"]["xz_sha256"], core_xz_bytes=core["storage"]["xz_bytes"],
                       core_receipt_sha256=A.sha(folder / "CORE_RECEIPT.json"))
        elif original["status"] == P.SAT:
            row["representation"] = "ACTUAL_SAT_WITNESS"
        else:
            A.require(original["status"] == "TIMEOUT_UNCERTIFIED", "Unknown unaccepted status")
            row["representation"] = "TIMEOUT_CNF_ONLY"
        rows.append(row)
    A.require([r["case_id"] for r in rows] == source["case_ids"], "Incomplete compact inventory")
    snapshot = HERE / "SOURCE_DIMENSION4_MANIFEST.json"
    if snapshot.exists():
        A.require(A.sha(snapshot) == digest, "A different final source snapshot is already frozen")
    else:
        shutil.copyfile(SOURCE, snapshot)
    result = {"schema": "kakeya-compact-dimension4-v1", "source_manifest_sha256": digest,
              "source_hashes": source_hashes(), "cases": rows, "case_ids": source["case_ids"],
              "inventory_scope": source["inventory_scope"], "original_drat_payloads_required": False,
              "compact_proof_bytes": sum(r.get("core_xz_bytes", 0) for r in rows)}
    P.dump(MANIFEST, result)
    return result


def load():
    compact = json.loads(MANIFEST.read_text())
    source, catalogue, digest = source_inventory()
    A.require(compact["schema"] == "kakeya-compact-dimension4-v1" and compact["source_manifest_sha256"] == digest,
              "Source inventory changed")
    A.require(compact["source_hashes"] == source_hashes(), "Semantic or replay source changed")
    A.require(A.sha(HERE / "SOURCE_DIMENSION4_MANIFEST.json") == digest, "Source snapshot changed")
    A.require(compact["case_ids"] == source["case_ids"] == [r["case_id"] for r in compact["cases"]],
              "Missing, reordered or duplicated compact case")
    for row, original in zip(compact["cases"], source["cases"]):
        A.require(row["original_case"] == original, "Compact case differs from original")
        original_folder = SOURCE_DIR / "cases" / row["case_id"]
        A.require(A.sha(original_folder / "input.cnf.xz") == original["storage"]["input.cnf"]["xz_sha256"], "Original CNF changed")
        if original["status"] == P.UNSAT:
            A.require(row["representation"] == "COMPACT_DRAT", "Wrong proof representation")
            folder = HERE / "cases" / row["case_id"]
            A.require(A.sha(folder / "CORE_RECEIPT.json") == row["core_receipt_sha256"], "Core receipt changed")
            core = validate_core(original)
            A.require(core["core_sha256"] == row["core_sha256"] and core["storage"]["xz_sha256"] == row["core_xz_sha256"],
                      "Core proof binding changed")
        elif original["status"] == P.SAT:
            A.require(row["representation"] == "ACTUAL_SAT_WITNESS", "Wrong SAT representation")
        else:
            A.require(row["representation"] == "TIMEOUT_CNF_ONLY", "Timeout received proof status")
    A.require(compact["inventory_scope"] == source["inventory_scope"] == V.scope(source["cases"], catalogue), "Scope arithmetic changed")
    return compact, source, catalogue


def replay_one(row, binaries, temporary_root):
    started = time.monotonic()
    original = row["original_case"]
    case = original["parameters"]
    source_folder = SOURCE_DIR / "cases" / row["case_id"]
    result = {"case_id": row["case_id"], "parameters": case, "representation": row["representation"],
              "original_drat_read": False, "status": "RUNNING"}
    logs = HERE / "replay_logs" / row["case_id"]
    logs.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix="case_", dir=temporary_root) as temporary:
            work = Path(temporary)
            result["regeneration"] = regenerate(original, work / "regenerated.cnf")
            with ExitStack() as stack:
                cnf = stack.enter_context(C.materialized(source_folder / "input.cnf", original["cnf_sha256"], work, prefer_compressed=True))
                if row["representation"] == "COMPACT_DRAT":
                    core_folder = HERE / "cases" / row["case_id"]
                    proof = stack.enter_context(C.materialized(core_folder / "core.drat", row["core_sha256"], work, prefer_compressed=True))
                    audit = A.check_pair(cnf, proof, work / "audit", binaries, 900, 1024, 256, False)
                    A.require(audit["status"] == "PASS_CNF_UNSAT_VIA_CAKEML_LRAT" and
                              audit["input_sha256"] == {"cnf": original["cnf_sha256"], "drat": row["core_sha256"]},
                              "Compact proof failed mandatory exact-CNF CakeML check")
                    A.require(C.logical_sha(core_folder / "core.drat", prefer_compressed=True) == row["core_sha256"], "Persisted core changed")
                    result.update(status="PASS_EXACT_DIMENSION4_UNSAT_CAKEML", audit=audit)
                    for path in (work / "audit").glob("*.txt"):
                        shutil.copyfile(path, logs / path.name)
                elif row["representation"] == "ACTUAL_SAT_WITNESS":
                    witness_path = source_folder / "ACTUAL_KAKEYA_WITNESS.json"
                    A.require(A.sha(witness_path) == original["witness_sha256"], "Actual witness changed")
                    witness = json.loads(witness_path.read_text())
                    fibres = {int(a): frozenset(Aa) for a, Aa in witness["fibres"].items()}
                    f = P.formula(case)
                    A.require(not E.first_failed_clauses(f, E.actual_assignment(f, fibres)), "Concrete witness fails exact CNF")
                    geometry = G.verify_actual_kakeya(fibres, 4, case["ring"])
                    A.require(geometry["is_kakeya"] and geometry["point_count"] <= 45, "Concrete witness fails ring geometry")
                    result.update(status="PASS_ACTUAL_DIMENSION4_KAKEYA_WITNESS", direct_geometry=geometry)
                    del f
                else:
                    result.update(status="PASS_TIMEOUT_REGENERATION_NO_EXCLUSION", exclusion_credited=False)
                A.require(C.logical_sha(source_folder / "input.cnf", prefer_compressed=True) == original["cnf_sha256"], "Persisted original CNF changed")
                A.require(A.sha(cnf) == original["cnf_sha256"], "Materialized CNF changed")
    except Exception as error:
        result.update(status="FAIL", error=repr(error))
    result["seconds"] = round(time.monotonic() - started, 6)
    P.dump(logs / "CORE_REPLAY.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--produce", action="store_true")
    parser.add_argument("--case", action="append")
    parser.add_argument("--take", type=int)
    parser.add_argument("--tag", default="worker")
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--replay", action="store_true")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    started = time.monotonic()
    output = HERE / ("COMPACT_DIMENSION4_QUICK_REPLAY.json" if args.quick else "COMPACT_DIMENSION4_REPLAY.json")
    replay_report = {"status": "RUNNING", "quick": args.quick, "cases": [],
                     "full_inventory_replayed": False, "original_drat_required": False}
    # Replace an old PASS before any source/manifest/catalogue preflight.
    # This also covers an invocation combining --freeze with --replay.
    if args.replay:
        P.dump(output, replay_report)
    try:
        A.require(args.tag.replace("_", "").isalnum(), "Unsafe worker tag")
        if args.produce:
            source, catalogue, source_digest = source_inventory()
            rows = [r for r in source["cases"] if r["status"] == P.UNSAT and (args.case is None or r["case_id"] in args.case)]
            if args.case is not None:
                A.require(set(args.case) == {r["case_id"] for r in rows}, "Requested core case unavailable")
            rows.sort(key=lambda r: r["storage"]["proof.drat"]["xz_bytes"], reverse=True)
            if args.take is not None:
                rows = rows[:args.take]
            report = {"status": "RUNNING", "source_manifest_sha256_at_start": source_digest, "cases": []}
            path = HERE / f"{args.tag}_PRODUCTION.json"
            P.dump(path, report)
            with tempfile.TemporaryDirectory(prefix="kakeya_n4_core_tools_") as temporary:
                binaries, build = A.build_checkers(Path(temporary) / "bin", HERE / f"build_logs_{args.tag}")
                report.update(checker_pins=A.verify_sources(), checker_build=build)
                for row in rows:
                    core = produce_one(row, source_digest, binaries)
                    item = {"case_id": row["case_id"], "status": core["status"],
                            "old_compressed_bytes": core["original_proof_compressed_bytes"],
                            "new_compressed_bytes": core["storage"]["xz_bytes"], "seconds": core["seconds"]}
                    report["cases"].append(item); P.dump(path, report); print(json.dumps(item), flush=True)
            report["status"] = "PASS_ALL_REQUESTED_DIMENSION4_CORE_PRODUCTIONS"
            P.dump(path, report)
        if args.freeze:
            compact = freeze()
            print(json.dumps({"frozen_cases": len(compact["cases"]), "compact_proof_bytes": compact["compact_proof_bytes"]}), flush=True)
        if args.replay:
            compact, source, catalogue = load()
            _, catalogue_checks = V.catalogue_replay()
            rows = compact["cases"][:4] if args.quick else compact["cases"]
            replay_report.update(compact_manifest_sha256=A.sha(MANIFEST), catalogue_checks=catalogue_checks,
                                 source_hashes=source_hashes())
            P.dump(output, replay_report)
            with tempfile.TemporaryDirectory(prefix="kakeya_n4_compact_replay_") as temporary:
                work = Path(temporary)
                binaries, build = A.build_checkers(work / "bin", HERE / "replay_build_logs")
                replay_report.update(checker_source_pins=A.verify_sources(), checker_build=build)
                for row in rows:
                    result = replay_one(row, binaries, work)
                    replay_report["cases"].append(result); P.dump(output, replay_report)
                    print(json.dumps({k: result[k] for k in ["case_id", "status", "seconds"]}), flush=True)
                    A.require(result["status"].startswith("PASS_"), "Compact dimension4 replay failed")
            current_source, _, current_digest = source_inventory()
            A.require(current_digest == compact["source_manifest_sha256"] and source_hashes() == compact["source_hashes"], "Semantic binding changed during replay")
            replay_report.update(status="PASS_SAMPLED_COMPACT_DIMENSION4_CASES" if args.quick else "PASS_ALL_ORIGINAL_DIMENSION4_CASES_VIA_COMPACT_PROOFS",
                                 full_inventory_replayed=not args.quick,
                                 checked_scope=V.scope(replay_report["cases"], catalogue, checked=True),
                                 seconds=round(time.monotonic() - started, 6))
            P.dump(output, replay_report)
            print(json.dumps({k: replay_report[k] for k in ["status", "checked_scope", "seconds"]}), flush=True)
    except BaseException as error:
        if args.replay:
            replay_report.update(status="FAIL", error=repr(error),
                                 full_inventory_replayed=False,
                                 seconds=round(time.monotonic() - started, 6))
            P.dump(output, replay_report)
        raise


if __name__ == "__main__":
    main()
