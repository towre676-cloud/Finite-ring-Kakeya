#!/usr/bin/env python3
"""Bind completed full proof replays to the delivered, immutable inputs.

This is a receipt/binding audit, not a fresh execution of the proof checker.
VERIFY_ROUND7.py runs fresh checkers by default. During checkpoint assembly,
this audit can reuse full replays already completed on the exact same bytes.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads((ROOT / path).read_text())


def module(name, path):
    path = ROOT / path
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def main():
    summaries = []
    exact = module("r7_bound_exact_replay", "research_round7/exact_ring/verify_certificates.py")
    manifest = exact.load_manifest()
    receipt_path = "research_round7/exact_ring/EXACT_RING_CERTIFICATE_REPLAY.json"
    receipt = read(receipt_path)
    require(receipt["status"] == "PASS_ALL_EXACT_RING_CERTIFICATES_AND_SMALL_DIMENSION_THEOREMS"
            and receipt["full_inventory_replayed"], "Exact-ring full replay absent")
    require(receipt["manifest_sha256"] == exact.A.sha(exact.MANIFEST)
            and receipt["source_hashes"] == exact.semantic_sources(), "Exact-ring source binding changed")
    require({r["case_id"] for r in receipt["cases"]} == set(manifest["case_ids"])
            and len(receipt["cases"]) == len(manifest["cases"]), "Incomplete exact-ring full receipt")
    replay_rows = {r["case_id"]: r for r in receipt["cases"]}
    for original in manifest["cases"]:
        row = replay_rows[original["case_id"]]
        require(row["parameters"] == original["parameters"] and row["production_status"] == original["status"],
                "Exact-ring replay scope differs from its source")
        if original["status"] == exact.P.UNSAT:
            require(row["status"] == "PASS_EXACT_REGENERATED_UNSAT_CAKEML"
                    and row["audit"]["status"] == "PASS_CNF_UNSAT_VIA_CAKEML_LRAT"
                    and row["audit"]["input_sha256"] == {"cnf": original["cnf_sha256"], "drat": original["proof_sha256"]}
                    and row["audit"]["cake_lpr"]["accepted"], "Exact-ring replay inspected different proof inputs")
        elif original["status"] == exact.P.SAT:
            witness_path = exact.HERE / "cases" / original["case_id"] / "ACTUAL_KAKEYA_WITNESS.json"
            require(sha(witness_path) == original["witness_sha256"], "Exact-ring witness changed")
            witness = json.loads(witness_path.read_text())
            fibres = {int(a): frozenset(points) for a, points in witness["fibres"].items()}
            actual = exact.G.verify_actual_kakeya(fibres, row["parameters"]["dimension"], row["parameters"]["ring"])
            require(row["status"] == "PASS_EXACT_CNF_AND_ACTUAL_RING_SAT_WITNESS"
                    and row["direct_geometry"] == actual and actual["is_kakeya"]
                    and actual["point_count"] <= original["parameters"]["total"], "Exact-ring actual witness failed")
        else:
            require(original["status"] == "TIMEOUT_UNCERTIFIED"
                    and row["status"] == "PASS_TIMEOUT_CNF_REGENERATION_NO_EXCLUSION"
                    and row["exclusion_credited"] is False and "proof.drat" not in original["storage"],
                    "Exact-ring timeout received certificate credit")
    require(receipt["theorems"] == exact.theorem_summary(receipt["cases"]), "Exact-ring theorem arithmetic changed")
    summaries.append({"collection": "exact_ring", "receipt": receipt_path,
                      "receipt_sha256": sha(ROOT / receipt_path), "cases": len(receipt["cases"]),
                      "full_replay_bound": True})

    support = module("r7_bound_compact_s13", "research_round7/compact_support13/verify_compact_support13.py")
    compact, source, catalogue = support.load_compact_inventory()
    receipt_path = "research_round7/compact_support13/COMPACT_SUPPORT13_REPLAY.json"
    receipt = read(receipt_path)
    require(receipt["status"] == "PASS_ALL_ORIGINAL_SUPPORT13_CASES_VIA_COMPACT_CAKEML_PROOFS"
            and receipt["full_original_inventory_replayed"], "Support13 full replay absent")
    require(receipt["compact_manifest_sha256"] == support.A.sha(support.MANIFEST)
            and receipt["source_manifest_sha256"] == compact["source_manifest_sha256"], "Support13 manifest binding changed")
    rows = {r["case_id"]: r for r in receipt["cases"]}
    require(len(rows) == len(receipt["cases"]) == len(compact["cases"])
            and set(rows) == set(compact["case_ids"]), "Incomplete support13 full receipt")
    for case in compact["cases"]:
        row, original = rows[case["case_id"]], case["original_case"]
        digest = case["core_sha256"] if case["representation"] == "COMPACT_DRAT" else original["proof_sha256"]
        require(row["status"] == "PASS_EXACT_ORIGINAL_CNF_AND_PORTABLE_CAKEML_PROOF"
                and row["cnf_sha256"] == original["cnf_sha256"] and row["checked_proof_sha256"] == digest,
                "Support13 replay inspected different bytes")
        require(row["nonzero_support_mask"] == original["nonzero_support_mask"]
                and row["maximum_interval"] == original["maximum_interval"], "Support13 replay scope changed")
    require(receipt["certified_inventory_coverage"] == support.V.coverage(source["cases"], catalogue),
            "Support13 coverage changed")
    summaries.append({"collection": "support13", "receipt": receipt_path,
                      "receipt_sha256": sha(ROOT / receipt_path), "cases": len(rows), "full_replay_bound": True})

    dimension4 = module("r7_bound_compact_n4", "research_round7/dimension4_compact/compact_dimension4.py")
    compact, source, catalogue = dimension4.load()
    receipt_path = "research_round7/dimension4_compact/COMPACT_DIMENSION4_REPLAY.json"
    receipt = read(receipt_path)
    require(receipt["status"] == "PASS_ALL_ORIGINAL_DIMENSION4_CASES_VIA_COMPACT_PROOFS"
            and receipt["full_inventory_replayed"], "Dimension4 full replay absent")
    require(receipt["compact_manifest_sha256"] == dimension4.A.sha(dimension4.MANIFEST)
            and receipt["source_hashes"] == dimension4.source_hashes(), "Dimension4 source binding changed")
    rows = {r["case_id"]: r for r in receipt["cases"]}
    require(len(rows) == len(receipt["cases"]) == len(compact["cases"])
            and set(rows) == set(compact["case_ids"]), "Incomplete dimension4 full receipt")
    for case in compact["cases"]:
        row, original = rows[case["case_id"]], case["original_case"]
        require(row["parameters"] == original["parameters"], "Dimension4 replay scope changed")
        require(row["regeneration"]["cnf_sha256"] == original["cnf_sha256"], "Dimension4 regenerated different CNF")
        if case["representation"] == "COMPACT_DRAT":
            require(row["status"] == "PASS_EXACT_DIMENSION4_UNSAT_CAKEML"
                    and row["audit"]["input_sha256"] == {"cnf": original["cnf_sha256"], "drat": case["core_sha256"]},
                    "Dimension4 replay inspected different proof")
        else:
            require(row["status"] == "PASS_TIMEOUT_REGENERATION_NO_EXCLUSION" and row["exclusion_credited"] is False,
                    "Uncertified dimension4 case received an exclusion")
    require(receipt["checked_scope"] == dimension4.V.scope(receipt["cases"], catalogue, checked=True),
            "Dimension4 scope arithmetic changed")
    summaries.append({"collection": "dimension4", "receipt": receipt_path,
                      "receipt_sha256": sha(ROOT / receipt_path), "cases": len(rows), "full_replay_bound": True})

    lean = []
    for name in ("SHEAR", "CHARGING"):
        path = HERE / "lean" / (name + "_LEAN_REPLAY.json")
        record = json.loads(path.read_text())
        require(record["status"].startswith("PASS_PINNED_LEAN_"), "Lean compilation receipt not accepted")
        for relative, digest in record["source_hashes"].items():
            require(sha(ROOT / relative) == digest, "Lean source changed")
        require(sha(HERE / "lean" / (name + "_LEAN_COMPILE_LOG.txt")) == record["compile_log_sha256"],
                "Lean compilation log changed")
        require(all(set(axioms) <= {"propext", "Quot.sound", "Classical.choice"}
                    for axioms in record["axiom_audits"].values()), "Unexpected Lean axiom")
        lean.append({"module": name, "receipt_sha256": sha(path), "statements": record["theorem_and_equivalence_count"]})
    result = {"status": "PASS_CURRENT_BYTES_BOUND_TO_COMPLETED_FULL_REPLAYS",
              "fresh_proof_checker_execution_in_this_script": False, "collections": summaries,
              "lean_compilation_receipts_bound": lean,
              "scope": "Receipt and source/payload binding only. The cited full replay receipts record actual checker executions. Run VERIFY_ROUND7.py without --reuse-checked-certificates for fresh proof checking."}
    (HERE / "COMPLETED_REPLAY_BINDINGS.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    destination = HERE / "COMPLETED_REPLAY_BINDINGS.json"
    destination.write_text(json.dumps({"status": "RUNNING"}) + "\n")
    try:
        main()
    except BaseException as error:
        destination.write_text(json.dumps({"status": "FAIL", "error": repr(error)}, indent=2) + "\n")
        raise
