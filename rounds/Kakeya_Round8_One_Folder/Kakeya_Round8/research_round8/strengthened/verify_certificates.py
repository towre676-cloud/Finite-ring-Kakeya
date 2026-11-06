#!/usr/bin/env python3
"""Portable exact-CNF replay of completed Round8 strengthened trial outcomes.

No SAT solver is invoked. Only mandatory accepted CakeML refutations earn
exclusion credit; a successfully regenerated timeout is still uncertified.
"""
from contextlib import ExitStack
from pathlib import Path
import argparse
import gc
import json
import re
import sys
import tempfile
import time

sys.dont_write_bytecode = True
import certify_strengthened as P

HERE, ROOT, A, C, X = P.HERE, P.ROOT, P.A, P.C, P.X
MANIFEST = HERE / "CERTIFICATE_MANIFEST.json"
PASS = "PASS_EXACT_ROUND8_REGENERATED_UNSAT_CAKEML"


def coverage(rows, checked=False):
    masks = sorted({r["nonzero_support_mask"] for r in rows
                    if r["status"] == (PASS if checked else P.ACCEPTED)})
    return {"declared_marked_roles": P.MASKS, "accepted_exact11_masks": masks,
            "accepted_distinct_marked_roles": len(masks),
            "all_four_declared_roles_have_new_exact11_refutations": set(masks) == set(P.MASKS),
            "whole_55_case_support13_claimed": False,
            "whole_weight_profiles_subtracted": 0,
            "ring_scope": "common_necessary_relaxation_both_rings"}


def validate_row(row, catalogue):
    mask, mode = row["nonzero_support_mask"], row["mode"]
    A.require(mask in catalogue and mode in P.MODES, "Unknown marked role or cut mode")
    A.require(re.fullmatch(r"[A-Za-z0-9_]+", row["case_id"]) is not None and
              row["case_id"].startswith(f"s13_T{mask}_m11_{mode}_"), "Unsafe or inconsistent case identifier")
    A.require(row["support"] == catalogue[mask]["support"] and row["distinguished_hub"] == 0 and
              row["maximum_interval"] == [11, 11] and row["total_upper_bound"] == 93 and
              row["ring_scope"] == "common_necessary_relaxation_both_rings", "Trial scope changed")
    A.require(row["semantic_input_hashes"] == P.semantic_sources(mode) and
              row["frozen_sources_sha256"] == A.sha(P.FREEZE), "Trial source binding changed")
    A.require(row["process_supervision"]["whole_process_group_confirmed_absent"] is True,
              "Trial was not published from stopped processes")
    folder = HERE / "cases" / row["case_id"]
    A.require(json.loads((folder / "CASE_RECEIPT.json").read_text()) == row, "Original receipt differs")
    A.require(row["unfinished_proof_retained"] is False, "Unexpected retained unfinished proof")
    if row["status"] == P.ACCEPTED:
        A.require(row["exclusion_credited"] is True and "proof.drat" in row["storage"] and
                  row["audit"]["status"] == "PASS_CNF_UNSAT_VIA_CAKEML_LRAT" and
                  row["audit"]["input_sha256"] == {"cnf": row["cnf_sha256"], "drat": row["proof_sha256"]},
                  "Accepted row lacks exact proof acceptance")
    else:
        A.require(row["status"] in ("TIMEOUT_OR_UNACCEPTED_UNCERTIFIED", "CHECKER_REJECTED_UNCERTIFIED",
                                     "SAT_RELAXATION_NO_ACTUAL_KAKEYA_WITNESS") and
                  row["exclusion_credited"] is False and "proof.drat" not in row["storage"],
                  "Unaccepted outcome acquired proof credit")
    for name, storage in row["storage"].items():
        A.require(name in ("input.cnf", "proof.drat"), "Unexpected storage name")
        A.require(A.sha(folder / (name + ".xz")) == storage["xz_sha256"], "Stored compressed bytes changed")
    if "untrusted_search_provenance" in row:
        info = row["untrusted_search_provenance"]
        A.require(A.sha(folder / "rup_unit_preprocessing.txt") == info["metadata_sha256"] and
                  A.sha(folder / "rup_unit_prefix.txt") == info["prefix_sha256"], "Search provenance changed")
        meta = json.loads((folder / "rup_unit_preprocessing.txt").read_text())
        A.require(meta["original_cnf_sha256"] == row["cnf_sha256"] and
                  meta["prefix_sha256"] == info["prefix_sha256"], "RUP prefix is bound to another formula")


def freeze_manifest():
    P.load_freeze()
    catalogue = P.universe()
    rows = []
    for path in sorted((HERE / "cases").glob("*/CASE_RECEIPT.json")):
        row = json.loads(path.read_text())
        validate_row(row, catalogue)
        rows.append({"case_id": row["case_id"], "receipt_sha256": A.sha(path), "original_case": row})
    result = {"schema": "kakeya-round8-strengthened-certificate-inventory-v1",
              "frozen_sources_sha256": A.sha(P.FREEZE), "cases": rows,
              "case_ids": [r["case_id"] for r in rows],
              "inventory_coverage": coverage([r["original_case"] for r in rows]),
              "encoder_formalized": False}
    P.P.dump(MANIFEST, result)
    return result


def load_manifest():
    P.load_freeze()
    catalogue = P.universe()
    result = json.loads(MANIFEST.read_text())
    A.require(result["schema"] == "kakeya-round8-strengthened-certificate-inventory-v1" and
              result["frozen_sources_sha256"] == A.sha(P.FREEZE), "Manifest source freeze changed")
    ids = [r["case_id"] for r in result["cases"]]
    A.require(ids == result["case_ids"] and len(ids) == len(set(ids)), "Incomplete or duplicate inventory")
    for item in result["cases"]:
        row = item["original_case"]
        A.require(item["case_id"] == row["case_id"] and
                  A.sha(HERE / "cases" / row["case_id"] / "CASE_RECEIPT.json") == item["receipt_sha256"],
                  "Original case binding changed")
        validate_row(row, catalogue)
    A.require(result["inventory_coverage"] == coverage([r["original_case"] for r in result["cases"]]),
              "Inventory coverage changed")
    return result


def replay_one(row, binaries, temporary_root, spectra, table, subspaces):
    started = time.monotonic()
    result = {"case_id": row["case_id"], "nonzero_support_mask": row["nonzero_support_mask"],
              "maximum_interval": [11, 11], "mode": row["mode"], "status": "RUNNING"}
    folder = HERE / "cases" / row["case_id"]
    logs = HERE / "replay_logs" / row["case_id"]
    logs.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix="case_", dir=temporary_root) as temporary:
            work = Path(temporary)
            case = P.universe()[row["nonzero_support_mask"]]
            formula, metadata = P.make_formula(case, row["mode"], spectra, table, subspaces)
            X.write_dimacs(formula, work / "regenerated.cnf")
            A.require(A.sha(work / "regenerated.cnf") == row["cnf_sha256"] and
                      formula.n == row["variables"] and len(formula.cl) == row["clauses"] and
                      json.loads(json.dumps(metadata)) == row["extension"], "Exact strengthened CNF regeneration differs")
            del formula
            gc.collect()
            with ExitStack() as stack:
                cnf = stack.enter_context(C.materialized(folder / "input.cnf", row["cnf_sha256"], work, prefer_compressed=True))
                if row["status"] == P.ACCEPTED:
                    proof = stack.enter_context(C.materialized(folder / "proof.drat", row["proof_sha256"], work, prefer_compressed=True))
                    audit = A.check_pair(cnf, proof, work / "audit", binaries, 900, 1024, 256, False)
                    A.require(audit["status"] == "PASS_CNF_UNSAT_VIA_CAKEML_LRAT" and
                              audit["input_sha256"] == {"cnf": row["cnf_sha256"], "drat": row["proof_sha256"]},
                              "Mandatory exact-CNF CakeML replay rejected")
                    result.update(status=PASS, audit=audit, exclusion_credited=True)
                    for path in (work / "audit").glob("*.txt"):
                        (logs / path.name).write_bytes(path.read_bytes())
                else:
                    result.update(status="PASS_UNCERTIFIED_FORMULA_REGENERATION_NO_EXCLUSION", exclusion_credited=False)
                for name, storage in row["storage"].items():
                    A.require(C.logical_sha(folder / name, prefer_compressed=True) == storage["raw_sha256"],
                              "Persisted decoded artifact changed")
                A.require(A.sha(cnf) == row["cnf_sha256"], "Checker input CNF changed")
            result["cnf_sha256"] = row["cnf_sha256"]
    except BaseException as error:
        result.update(status="FAIL", error=repr(error), exclusion_credited=False)
    result["seconds"] = round(time.monotonic() - started, 6)
    P.P.dump(logs / "CASE_REPLAY.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    output = HERE / "CERTIFICATE_REPLAY.json"
    report = {"status": "RUNNING", "cases": [], "full_inventory_replayed": False, "SAT_solver_invoked": False}
    P.P.dump(output, report)
    started = time.monotonic()
    try:
        if args.freeze:
            freeze_manifest()
        manifest = load_manifest()
        manifest_digest = A.sha(MANIFEST)
        report.update(manifest_sha256=manifest_digest, frozen_sources_sha256=A.sha(P.FREEZE))
        data = P.P.IMPORTED / "data"
        spectra, table, subspaces = X.load_spectra(data / "spec32.csv"), X.load_M(data / "Mtable.txt"), X.all_subspaces()
        with tempfile.TemporaryDirectory(prefix="kakeya_r8_replay_") as temporary:
            work = Path(temporary)
            binaries, build = A.build_checkers(work / "bin", HERE / "replay_build_logs")
            report.update(checker_source_pins=A.verify_sources(), checker_build=build)
            for item in manifest["cases"]:
                result = replay_one(item["original_case"], binaries, work, spectra, table, subspaces)
                report["cases"].append(result)
                P.P.dump(output, report)
                print(json.dumps({k: result[k] for k in ("case_id", "status", "seconds")}), flush=True)
                A.require(result["status"].startswith("PASS_"), "Round8 certificate replay failed")
        load_manifest()
        A.require(A.sha(MANIFEST) == manifest_digest, "Inventory changed during replay")
        report.update(status="PASS_ALL_ROUND8_STRENGTHENED_OUTCOMES", full_inventory_replayed=True,
                      checked_coverage=coverage(report["cases"], checked=True),
                      seconds=round(time.monotonic() - started, 6))
        P.P.dump(output, report)
    except BaseException as error:
        report.update(status="FAIL", full_inventory_replayed=False, error=repr(error), seconds=round(time.monotonic() - started, 6))
        P.P.dump(output, report)
        raise


if __name__ == "__main__":
    main()
