#!/usr/bin/env python3
"""Regenerate the two unfinished trial CNFs; grant no exclusion credit.

This is a finite replay, not a solver invocation.  It verifies the exact
formula/source bindings and that neither timeout carries a proof payload.
"""
from pathlib import Path
import gc
import json
import tempfile
import time

import certify_four_pair as T

HERE = Path(__file__).resolve().parent
P, X = T.P, T.X


def main():
    started = time.monotonic()
    output = HERE / "FOUR_PAIR_TRIALS_REPLAY.json"
    report = {"status": "RUNNING", "cases": [], "SAT_solver_invoked": False,
              "exclusions_credited": 0}
    P.dump(output, report)
    try:
        inventory_path = HERE / "FOUR_PAIR_TRIALS.json"
        inventory_digest = P.A.sha(inventory_path)
        inventory = json.loads(inventory_path.read_text())
        wanted = [377850134, 411136406]
        P.A.require(inventory["status"] == "COMPLETED_TWO_BOUNDED_FOUR_PAIR_TRIALS",
                    "Trials inventory is not complete")
        P.A.require(inventory["requested_masks"] == wanted and
                    inventory["maximum_interval"] == [11, 11] and
                    inventory["accepted_trials"] == 0, "Trial scope changed")
        rows = inventory["cases"]
        P.A.require([r["nonzero_support_mask"] for r in rows] == wanted,
                    "Missing, duplicated or changed trial")
        universe = {c["nonzero_support_mask"]: c for c in P.universe()}
        pins = T.semantic_hashes()
        P.A.require(P.A.sha(X.BASE) == P.ENCODER_HASH, "Frozen baseline changed")
        data = P.IMPORTED / "data"
        SPEC = X.load_spectra(data / "spec32.csv")
        M, SUBS = X.load_M(data / "Mtable.txt"), X.all_subspaces()
        for row in rows:
            mask = row["nonzero_support_mask"]
            case_id = f"s13_T{mask}_m11_11_four_pair_unique_t45"
            folder = HERE / "cases" / case_id
            P.A.require(row["case_id"] == case_id and
                        json.loads((folder / "CASE_RECEIPT.json").read_text()) == row,
                        "Original trial receipt differs")
            P.A.require(row["support"] == universe[mask]["support"] and
                        row["maximum_interval"] == [11, 11] and
                        row["total_upper_bound"] == 93 and
                        row["distinguished_hub"] == 0 and
                        row["ring_scope"] == "common_necessary_relaxation_both_rings",
                        "Trial mathematical scope differs")
            P.A.require(row["semantic_input_hashes"] == pins and
                        row["producer_sha256"] == P.A.sha(T.__file__) and
                        row["search_wrapper_sha256"] == P.A.sha(HERE.parent / "rup_unit_solver.py"),
                        "Trial sources changed")
            P.A.require(row["status"] == "TIMEOUT_OR_UNACCEPTED_UNCERTIFIED" and
                        row["original_baseline_CNF_claimed_refuted"] is False and
                        row["unfinished_proof_retained"] is False and
                        row["process_supervision"]["whole_process_group_confirmed_absent"] is True,
                        "Unfinished trial has acquired certificate status")
            P.A.require(set(row["storage"]) == {"input.cnf"} and
                        not list(folder.glob("*.drat*")) and "audit" not in row,
                        "Unexpected unaccepted proof payload or acceptance record")
            storage = row["storage"]["input.cnf"]
            P.A.require(P.A.sha(folder / "input.cnf.xz") == storage["xz_sha256"] and
                        P.C.logical_sha(folder / "input.cnf", prefer_compressed=True) ==
                        row["cnf_sha256"] == storage["raw_sha256"], "Stored trial CNF changed")
            with tempfile.TemporaryDirectory(prefix="kakeya_four_pair_replay_") as temporary:
                cnf = Path(temporary) / "regenerated.cnf"
                formula = T.make_formula(universe[mask], 11, 11, SPEC, M, SUBS)
                X.write_dimacs(formula, cnf)
                P.A.require(P.A.sha(cnf) == row["cnf_sha256"] and
                            cnf.stat().st_size == row["cnf_bytes"] and
                            formula.n == row["variables"] and len(formula.cl) == row["clauses"] and
                            json.loads(json.dumps(formula.four_pair_metadata)) == row["four_pair_extension"],
                            "Exact trial formula regeneration differs")
                del formula
                gc.collect()
            report["cases"].append({"case_id": case_id,
                                    "status": "PASS_EXACT_TIMEOUT_CNF_REGENERATION_NO_EXCLUSION",
                                    "cnf_sha256": row["cnf_sha256"],
                                    "new_clauses": row["four_pair_extension"]["new_clauses"],
                                    "exclusion_credited": False})
            P.dump(output, report)
        P.A.require(P.A.sha(inventory_path) == inventory_digest and
                    T.semantic_hashes() == pins, "Inputs changed during finite replay")
        report.update(status="PASS_BOTH_FOUR_PAIR_TIMEOUT_FORMULAS_NO_EXCLUSIONS",
                      inventory_sha256=inventory_digest, semantic_input_hashes=pins,
                      seconds=round(time.monotonic() - started, 6))
        P.dump(output, report)
        print(json.dumps({k: report[k] for k in ("status", "SAT_solver_invoked", "exclusions_credited", "seconds")}))
    except Exception as error:
        report.update(status="FAIL", error=repr(error), seconds=round(time.monotonic() - started, 6))
        P.dump(output, report)
        raise


if __name__ == "__main__":
    main()
