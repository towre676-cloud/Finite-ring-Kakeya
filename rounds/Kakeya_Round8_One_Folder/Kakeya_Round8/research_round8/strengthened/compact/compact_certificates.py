#!/usr/bin/env python3
"""Compact Round8 DRATs and replay them against unchanged original CNFs.

Original large DRAT payloads are required only for production. Portable
replay binds the original receipts and semantic scope, regenerates every
original CNF, and requires fresh CakeML acceptance of each compact proof.
"""
from contextlib import ExitStack
from pathlib import Path
import argparse
import gc
import importlib.util
import json
import re
import shutil
import sys
import tempfile
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SOURCE_DIR = HERE.parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(SOURCE_DIR))
spec = importlib.util.spec_from_file_location("round8_frozen_original_verifier", SOURCE_DIR / "verify_certificates.py")
V = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = V
spec.loader.exec_module(V)
P, A, C, X = V.P, V.A, V.C, V.X
dump = P.P.dump
SOURCE = SOURCE_DIR / "CERTIFICATE_MANIFEST.json"
MANIFEST = HERE / "COMPACT_CERTIFICATE_MANIFEST.json"
CORE_PASS = "PASS_ROUND8_COMPACT_DRAT_AGAINST_EXACT_ORIGINAL_CNF"


def source_inventory():
    """Bind original meaning/receipts/CNFs, explicitly without old proof bytes.

    This adapter does not call or weaken the frozen original verifier.
    It establishes no UNSAT claim. A newly accepted replacement proof is
    mandatory for every refutation credited by the compact replay.
    """
    P.load_freeze()
    digest = A.sha(SOURCE)
    source = json.loads(SOURCE.read_text())
    A.require(source["schema"] == "kakeya-round8-strengthened-certificate-inventory-v1" and
              source["frozen_sources_sha256"] == A.sha(P.FREEZE), "Original source inventory changed")
    catalogue = P.universe()
    ids = [item["case_id"] for item in source["cases"]]
    A.require(ids == source["case_ids"] and len(ids) == len(set(ids)), "Changed or duplicated source case IDs")
    for item in source["cases"]:
        row = item["original_case"]
        case_id, mask, mode = row["case_id"], row["nonzero_support_mask"], row["mode"]
        A.require(re.fullmatch(r"[A-Za-z0-9_]+", case_id) is not None and
                  case_id == item["case_id"] and case_id.startswith(f"s13_T{mask}_m11_{mode}_"),
                  "Unsafe or inconsistent original case ID")
        A.require(mask in catalogue and mode in P.MODES and
                  row["support"] == catalogue[mask]["support"] and row["distinguished_hub"] == 0 and
                  row["maximum_interval"] == [11, 11] and row["total_upper_bound"] == 93 and
                  row["ring_scope"] == "common_necessary_relaxation_both_rings", "Original mathematical scope differs")
        A.require(row["semantic_input_hashes"] == P.semantic_sources(mode) and
                  row["frozen_sources_sha256"] == A.sha(P.FREEZE), "Original semantic sources differ")
        folder = SOURCE_DIR / "cases" / case_id
        receipt = folder / "CASE_RECEIPT.json"
        A.require(A.sha(receipt) == item["receipt_sha256"] and json.loads(receipt.read_text()) == row,
                  "Original immutable receipt differs")
        A.require(row["process_supervision"]["whole_process_group_confirmed_absent"] is True and
                  row["unfinished_proof_retained"] is False, "Original publication status differs")
        storage = row["storage"]
        if row["status"] == P.ACCEPTED:
            A.require(row["exclusion_credited"] is True and set(storage) == {"input.cnf", "proof.drat"} and
                      row["audit"]["status"] == "PASS_CNF_UNSAT_VIA_CAKEML_LRAT" and
                      row["audit"]["input_sha256"] == {"cnf": row["cnf_sha256"], "drat": row["proof_sha256"]},
                      "Original accepted record lacks exact proof binding")
        else:
            A.require(row["status"] in ("TIMEOUT_OR_UNACCEPTED_UNCERTIFIED", "CHECKER_REJECTED_UNCERTIFIED",
                                         "SAT_RELAXATION_NO_ACTUAL_KAKEYA_WITNESS") and
                      row["exclusion_credited"] is False and set(storage) == {"input.cnf"},
                      "Unaccepted original outcome has acquired proof status")
        A.require(storage["input.cnf"]["raw_sha256"] == row["cnf_sha256"] and
                  A.sha(folder / "input.cnf.xz") == storage["input.cnf"]["xz_sha256"], "Stored original CNF changed")
        if "untrusted_search_provenance" in row:
            provenance = row["untrusted_search_provenance"]
            A.require(A.sha(folder / "rup_unit_preprocessing.txt") == provenance["metadata_sha256"] and
                      A.sha(folder / "rup_unit_prefix.txt") == provenance["prefix_sha256"], "Original search provenance changed")
            meta = json.loads((folder / "rup_unit_preprocessing.txt").read_text())
            A.require(meta["original_cnf_sha256"] == row["cnf_sha256"] and
                      meta["prefix_sha256"] == provenance["prefix_sha256"], "Original prefix belongs to another CNF")
    A.require(source["inventory_coverage"] == V.coverage([r["original_case"] for r in source["cases"]]),
              "Original scope arithmetic differs")
    A.require(A.sha(SOURCE) == digest, "Source inventory changed during read")
    return source, digest


def source_hashes():
    return {**P.all_frozen_sources(), str(Path(__file__).relative_to(ROOT)): A.sha(Path(__file__))}


def regenerate(row, path):
    data = P.P.IMPORTED / "data"
    spectra, table, subspaces = X.load_spectra(data / "spec32.csv"), X.load_M(data / "Mtable.txt"), X.all_subspaces()
    formula, metadata = P.make_formula(P.universe()[row["nonzero_support_mask"]], row["mode"], spectra, table, subspaces)
    X.write_dimacs(formula, path)
    A.require(A.sha(path) == row["cnf_sha256"] and formula.n == row["variables"] and
              len(formula.cl) == row["clauses"] and json.loads(json.dumps(metadata)) == row["extension"],
              "Exact original formula regeneration differs")
    result = {"cnf_sha256": row["cnf_sha256"], "variables": formula.n, "clauses": len(formula.cl)}
    del formula
    gc.collect()
    return result


def validate_core(row):
    folder = HERE / "cases" / row["case_id"]
    core = json.loads((folder / "CORE_RECEIPT.json").read_text())
    A.require(core["status"] == CORE_PASS and core["original_case"] == row,
              "Compact core does not bind this original case")
    A.require(core["audit"]["status"] == "PASS_CNF_UNSAT_VIA_CAKEML_LRAT" and
              core["audit"]["input_sha256"] == {"cnf": row["cnf_sha256"], "drat": core["core_sha256"]},
              "Core was not accepted against the original CNF")
    A.require(A.sha(folder / "core.drat.xz") == core["storage"]["xz_sha256"] and
              C.logical_sha(folder / "core.drat", prefer_compressed=True) == core["core_sha256"],
              "Stored compact core changed")
    return core


def produce_one(row, source_digest, binaries):
    A.require(row["status"] == P.ACCEPTED, "Only accepted original refutations can be compacted")
    destination = HERE / "cases" / row["case_id"]
    if destination.exists():
        return validate_core(row)
    started = time.monotonic()
    original = SOURCE_DIR / "cases" / row["case_id"]
    for name, storage in row["storage"].items():
        A.require(A.sha(original / (name + ".xz")) == storage["xz_sha256"], "Original production artifact changed")
    with tempfile.TemporaryDirectory(prefix="kakeya_r8_core_") as temporary:
        work = Path(temporary)
        regeneration = regenerate(row, work / "regenerated.cnf")
        with ExitStack() as stack:
            cnf = stack.enter_context(C.materialized(original / "input.cnf", row["cnf_sha256"], work, prefer_compressed=True))
            proof = stack.enter_context(C.materialized(original / "proof.drat", row["proof_sha256"], work, prefer_compressed=True))
            core = work / "core.drat"
            trim = A.run_checker([binaries["drat-trim"], cnf, proof, "-l", core], work, "trim", 900, "s VERIFIED", False)
            A.require(trim["accepted"] and core.is_file(), "Core trimming failed")
            digest, byte_count = A.sha(core), core.stat().st_size
            audit = A.check_pair(cnf, core, work / "audit", binaries, 900, 1024, 256, False)
            A.require(audit["status"] == "PASS_CNF_UNSAT_VIA_CAKEML_LRAT" and
                      audit["input_sha256"] == {"cnf": row["cnf_sha256"], "drat": digest},
                      "Replacement core failed mandatory original-CNF CakeML check")
            A.require(A.sha(cnf) == row["cnf_sha256"] and A.sha(proof) == row["proof_sha256"], "Original decoded input changed")
        storage = C.compress_verified(core, digest, preset=3, remove_raw=True)
        storage.update(logical_path="core.drat", compressed_path="core.drat.xz")
        destination.mkdir(parents=True)
        P.P.publish_copy(Path(str(core) + ".xz"), destination / "core.drat.xz", storage["xz_sha256"])
        for path in list(work.glob("*.txt")) + list((work / "audit").glob("*.txt")):
            P.P.publish_copy(path, destination / path.name, A.sha(path))
        for name, info in row["storage"].items():
            A.require(A.sha(original / (name + ".xz")) == info["xz_sha256"], "Persisted original changed")
        result = {"status": CORE_PASS, "original_case": row, "case_id": row["case_id"],
                  "source_inventory_sha256_at_production": source_digest,
                  "core_sha256": digest, "core_raw_bytes": byte_count, "storage": storage,
                  "original_proof_xz_bytes": row["storage"]["proof.drat"]["xz_bytes"],
                  "formula_regeneration": regeneration, "trim": trim, "audit": audit,
                  "original_cnf_used_without_added_axioms": True,
                  "original_large_drat_required_for_replay": False,
                  "producer_sha256": A.sha(Path(__file__)), "seconds": round(time.monotonic() - started, 6)}
        dump(destination / "CORE_RECEIPT.json", result)
    return validate_core(row)


def freeze():
    source, digest = source_inventory()
    rows = []
    for item in source["cases"]:
        original = item["original_case"]
        row = {"case_id": item["case_id"], "original_case": original,
               "original_receipt_sha256": item["receipt_sha256"]}
        if original["status"] == P.ACCEPTED:
            core = validate_core(original)
            row.update(representation="COMPACT_DRAT", core_sha256=core["core_sha256"],
                       core_xz_sha256=core["storage"]["xz_sha256"], core_xz_bytes=core["storage"]["xz_bytes"],
                       core_receipt_sha256=A.sha(HERE / "cases" / row["case_id"] / "CORE_RECEIPT.json"))
        else:
            row["representation"] = "UNCERTIFIED_CNF_ONLY"
        rows.append(row)
    snapshot = HERE / "SOURCE_CERTIFICATE_MANIFEST.json"
    if snapshot.exists():
        A.require(A.sha(snapshot) == digest, "Another source inventory is already frozen")
    else:
        shutil.copyfile(SOURCE, snapshot)
    result = {"schema": "kakeya-round8-compact-strengthened-v1", "source_manifest_sha256": digest,
              "source_hashes": source_hashes(), "cases": rows, "case_ids": source["case_ids"],
              "inventory_coverage": source["inventory_coverage"], "original_large_drat_required": False,
              "compact_proof_bytes": sum(r.get("core_xz_bytes", 0) for r in rows)}
    dump(MANIFEST, result)
    return result


def load():
    source, digest = source_inventory()
    compact = json.loads(MANIFEST.read_text())
    A.require(compact["schema"] == "kakeya-round8-compact-strengthened-v1" and
              compact["source_manifest_sha256"] == digest and compact["source_hashes"] == source_hashes(),
              "Compact source binding changed")
    A.require(A.sha(HERE / "SOURCE_CERTIFICATE_MANIFEST.json") == digest and
              compact["case_ids"] == source["case_ids"] == [r["case_id"] for r in compact["cases"]],
              "Compact inventory is incomplete or different")
    for row, original in zip(compact["cases"], source["cases"]):
        A.require(row["original_case"] == original["original_case"] and
                  row["original_receipt_sha256"] == original["receipt_sha256"], "Compact original-case binding differs")
        if row["original_case"]["status"] == P.ACCEPTED:
            A.require(row["representation"] == "COMPACT_DRAT", "Accepted case lost its required proof")
            receipt = HERE / "cases" / row["case_id"] / "CORE_RECEIPT.json"
            A.require(A.sha(receipt) == row["core_receipt_sha256"], "Core receipt changed")
            core = validate_core(row["original_case"])
            A.require(core["core_sha256"] == row["core_sha256"] and core["storage"]["xz_sha256"] == row["core_xz_sha256"],
                      "Compact proof digest differs")
        else:
            A.require(row["representation"] == "UNCERTIFIED_CNF_ONLY", "Uncertified case acquired a proof")
    A.require(compact["inventory_coverage"] == source["inventory_coverage"], "Compact coverage differs")
    return compact, source


def replay_one(row, binaries, temporary_root):
    started = time.monotonic()
    original = row["original_case"]
    folder = SOURCE_DIR / "cases" / row["case_id"]
    result = {"case_id": row["case_id"], "nonzero_support_mask": original["nonzero_support_mask"],
              "maximum_interval": [11, 11], "mode": original["mode"], "representation": row["representation"],
              "status": "RUNNING", "original_large_drat_read": False}
    logs = HERE / "replay_logs" / row["case_id"]
    logs.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix="case_", dir=temporary_root) as temporary:
            work = Path(temporary)
            result["regeneration"] = regenerate(original, work / "regenerated.cnf")
            with ExitStack() as stack:
                cnf = stack.enter_context(C.materialized(folder / "input.cnf", original["cnf_sha256"], work, prefer_compressed=True))
                if row["representation"] == "COMPACT_DRAT":
                    core_folder = HERE / "cases" / row["case_id"]
                    proof = stack.enter_context(C.materialized(core_folder / "core.drat", row["core_sha256"], work, prefer_compressed=True))
                    audit = A.check_pair(cnf, proof, work / "audit", binaries, 900, 1024, 256, False)
                    A.require(audit["status"] == "PASS_CNF_UNSAT_VIA_CAKEML_LRAT" and
                              audit["input_sha256"] == {"cnf": original["cnf_sha256"], "drat": row["core_sha256"]},
                              "Compact proof rejected against exact original CNF")
                    A.require(C.logical_sha(core_folder / "core.drat", prefer_compressed=True) == row["core_sha256"],
                              "Persisted compact proof changed")
                    result.update(status=V.PASS, audit=audit, exclusion_credited=True,
                                  checked_proof_sha256=row["core_sha256"])
                    for path in (work / "audit").glob("*.txt"):
                        (logs / path.name).write_bytes(path.read_bytes())
                else:
                    result.update(status="PASS_UNCERTIFIED_FORMULA_REGENERATION_NO_EXCLUSION", exclusion_credited=False)
                A.require(C.logical_sha(folder / "input.cnf", prefer_compressed=True) == original["cnf_sha256"] and
                          A.sha(cnf) == original["cnf_sha256"], "Original formula bytes changed")
    except BaseException as error:
        result.update(status="FAIL", error=repr(error), exclusion_credited=False)
    result["seconds"] = round(time.monotonic() - started, 6)
    dump(logs / "CORE_REPLAY.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--produce", action="store_true")
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--replay", action="store_true")
    args = parser.parse_args()
    output = HERE / "COMPACT_CERTIFICATE_REPLAY.json"
    started = time.monotonic()
    report = {"status": "RUNNING", "cases": [], "full_inventory_replayed": False,
              "SAT_solver_invoked": False, "original_large_drat_required": False}
    if args.replay:
        dump(output, report)
    try:
        if args.produce:
            source, digest = source_inventory()
            production = {"status": "RUNNING", "cases": []}
            production_output = HERE / "CORE_PRODUCTION.json"
            dump(production_output, production)
            with tempfile.TemporaryDirectory(prefix="kakeya_r8_core_tools_") as temporary:
                binaries, build = A.build_checkers(Path(temporary) / "bin", HERE / "build_logs")
                production.update(checker_source_pins=A.verify_sources(), checker_build=build)
                for item in source["cases"]:
                    row = item["original_case"]
                    if row["status"] != P.ACCEPTED:
                        continue
                    core = produce_one(row, digest, binaries)
                    outcome = {"case_id": row["case_id"], "status": core["status"],
                               "old_xz_bytes": core["original_proof_xz_bytes"],
                               "core_xz_bytes": core["storage"]["xz_bytes"], "seconds": core["seconds"]}
                    production["cases"].append(outcome)
                    dump(production_output, production)
                    print(json.dumps(outcome), flush=True)
            production["status"] = "PASS_ALL_REQUESTED_ROUND8_CORE_PRODUCTIONS"
            dump(production_output, production)
        if args.freeze:
            freeze()
        if args.replay:
            compact, source = load()
            manifest_digest = A.sha(MANIFEST)
            report.update(compact_manifest_sha256=manifest_digest,
                          source_manifest_sha256=compact["source_manifest_sha256"], source_hashes=source_hashes())
            with tempfile.TemporaryDirectory(prefix="kakeya_r8_compact_replay_") as temporary:
                work = Path(temporary)
                binaries, build = A.build_checkers(work / "bin", HERE / "replay_build_logs")
                report.update(checker_source_pins=A.verify_sources(), checker_build=build)
                for row in compact["cases"]:
                    result = replay_one(row, binaries, work)
                    report["cases"].append(result)
                    dump(output, report)
                    print(json.dumps({k: result[k] for k in ("case_id", "status", "seconds")}), flush=True)
                    A.require(result["status"].startswith("PASS_"), "Round8 compact replay failed")
            load()
            A.require(A.sha(MANIFEST) == manifest_digest, "Compact inventory changed during replay")
            report.update(status="PASS_ALL_ROUND8_OUTCOMES_VIA_COMPACT_EXACT_CNF_CAKEML_PROOFS",
                          full_inventory_replayed=True, checked_coverage=V.coverage(report["cases"], checked=True),
                          seconds=round(time.monotonic() - started, 6))
            dump(output, report)
            print(json.dumps({k: report[k] for k in ("status", "checked_coverage", "seconds")}), flush=True)
    except BaseException as error:
        if args.replay:
            report.update(status="FAIL", full_inventory_replayed=False, error=repr(error),
                          seconds=round(time.monotonic() - started, 6))
            dump(output, report)
        raise


if __name__ == "__main__":
    main()
