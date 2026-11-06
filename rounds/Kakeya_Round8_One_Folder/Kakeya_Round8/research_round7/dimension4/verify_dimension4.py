#!/usr/bin/env python3
"""Portable replay of a partial or complete dimension-four proof collection."""
from pathlib import Path
from contextlib import ExitStack
import argparse
import gc
import hashlib
import json
import re
import shutil
import tempfile
import time
import certify_dimension4 as D

HERE, ROOT, P, E, G = D.HERE, D.ROOT, D.P, D.E, D.G
A, C = P.A, P.C
MANIFEST = HERE / "DIMENSION4_CERTIFICATE_MANIFEST.json"


def catalogue_replay():
    stored = D.load_catalogue()
    generated, transports = D.D4.build()
    for key, value in generated.items():
        A.require(stored[key] == value, "Dimension4 catalogue differs: " + key)
    transported_bytes = (json.dumps(transports, separators=(",", ":")) + "\n").encode()
    A.require(hashlib.sha256(transported_bytes).hexdigest() == stored["transport_file_sha256"],
              "Explicit complete transports do not regenerate")
    upper = D.upper_bound()
    A.require(upper == json.loads((HERE / "DIMENSION4_46_POINT_STAR.json").read_text()),
              "Forty-six-point upper-bound witness changed")
    return stored, {"all_32768_transports_reproduced": True,
                    "complete_GL4_group_order": stored["group_order"],
                    "covering_marked_classes": stored["covering_marked_orbit_count"],
                    "burnside_agrees_for_every_support_size": True,
                    "explicit_46_point_star_both_rings_rechecked": True}


def validate_parameters(case, catalogue):
    entries = {row["full_mask"]: row for row in catalogue["covering_cases"]}
    row = entries.get(case.get("catalogue_full_mask"))
    A.require(row is not None and case["support"] == row["support"], "Case not in complete covering catalogue")
    A.require(case["dimension"] == 4 and case["ring"] in E.RINGS and case["total"] == 45,
              "Incorrect dimension/ring/budget")
    A.require(2 <= case["hub_min"] <= case["maximum"] <= 16 and case["normalize"] is True,
              "Unsupported maximum interval or normalization")
    A.require(re.fullmatch(r"[A-Za-z0-9_]+", case["case_id"]) is not None, "Unsafe case ID")


def scope(rows, catalogue, checked=False):
    all_keys = [(entry["full_mask"], ring) for entry in catalogue["covering_cases"] for ring in E.RINGS]
    covered = {key: set() for key in all_keys}
    actual_sat = []
    for row in rows:
        case = row["parameters"]
        status = row["status"]
        if status == ("PASS_EXACT_DIMENSION4_UNSAT_CAKEML" if checked else P.UNSAT):
            covered[case["catalogue_full_mask"], case["ring"]].update(range(case["hub_min"], case["maximum"] + 1))
        if status == ("PASS_ACTUAL_DIMENSION4_KAKEYA_WITNESS" if checked else P.SAT):
            actual_sat.append(row["case_id"])
    complete = [key for key in all_keys if covered[key] == set(range(2, 17))]
    complete_both = [entry["full_mask"] for entry in catalogue["covering_cases"]
                     if all((entry["full_mask"], ring) in complete for ring in E.RINGS)]
    return {"catalogue_marked_classes": 28, "catalogue_ring_cases": 56,
            "complete_ring_cases": len(complete), "complete_marked_classes_both_rings": len(complete_both),
            "complete_ring_keys": [{"support_full_mask": mask, "ring": ring} for mask, ring in complete],
            "complete_both_ring_support_masks": complete_both,
            "remaining_ring_cases": 56 - len(complete),
            "partial_maxima": [{"support_full_mask": mask, "ring": ring, "maxima": sorted(values)}
                               for (mask, ring), values in covered.items() if values and len(values) < 15],
            "actual_counterexample_case_ids": actual_sat,
            "global_dimension4_minimum46_established": len(complete) == 56 and not actual_sat}


def freeze(catalogue):
    rows = []
    for receipt_path in sorted((HERE / "cases").glob("*/CASE_RECEIPT.json")):
        record = json.loads(receipt_path.read_text())
        case = record["parameters"]
        validate_parameters(case, catalogue)
        A.require(record["source_hashes"] == D.sources(), "Production semantic source changed")
        row = {"case_id": case["case_id"], "parameters": case, "status": record["status"],
               "receipt_sha256": A.sha(receipt_path), "storage": record["storage"],
               "cnf_sha256": record["cnf_sha256"]}
        for name, info in row["storage"].items():
            A.require(A.sha(receipt_path.parent / (name + ".xz")) == info["xz_sha256"], "Stored artifact hash changed")
            A.require(C.logical_sha(receipt_path.parent / name, prefer_compressed=True) == info["raw_sha256"],
                      "Decoded artifact hash changed")
        if row["status"] == P.UNSAT:
            row["proof_sha256"] = record["proof_sha256"]
            A.require("proof.drat" in row["storage"], "Missing completed refutation")
        elif row["status"] == P.SAT:
            row["witness_sha256"] = record["witness_sha256"]
            A.require(A.sha(receipt_path.parent / "ACTUAL_KAKEYA_WITNESS.json") == row["witness_sha256"], "SAT witness changed")
        else:
            A.require(row["status"] == "TIMEOUT_UNCERTIFIED", "Unexpected production result")
            A.require("proof.drat" not in row["storage"], "Unaccepted proof must not receive certificate status")
        rows.append(row)
    result = {"schema": "kakeya-dimension4-exact-certificates-v1", "source_hashes": D.sources(),
              "cases": rows, "case_ids": [r["case_id"] for r in rows],
              "inventory_scope": scope(rows, catalogue), "encoder_formalized": False,
              "census_dependency": False, "capacity_table_dependency": False}
    P.dump(MANIFEST, result)
    return result


def load(catalogue, check_artifact_bytes=True):
    """Bind original scope; compact replay may replace old proof byte checks.

    False does not establish UNSAT. A replacement verifier must check its
    new proof against the byte-identically regenerated original formula.
    """
    manifest = json.loads(MANIFEST.read_text())
    A.require(manifest["schema"] == "kakeya-dimension4-exact-certificates-v1" and
              manifest["source_hashes"] == D.sources(), "Manifest semantics changed")
    ids = [row["case_id"] for row in manifest["cases"]]
    A.require(ids == manifest["case_ids"] and len(ids) == len(set(ids)), "Duplicate or altered case IDs")
    for row in manifest["cases"]:
        case = row["parameters"]
        validate_parameters(case, catalogue)
        A.require(case["case_id"] == row["case_id"], "Case ID differs from parameters")
        folder = HERE / "cases" / row["case_id"]
        A.require(A.sha(folder / "CASE_RECEIPT.json") == row["receipt_sha256"], "Production receipt changed")
        for name, info in row["storage"].items():
            A.require(name in ("input.cnf", "proof.drat"), "Unexpected artifact name")
            if check_artifact_bytes:
                A.require(A.sha(folder / (name + ".xz")) == info["xz_sha256"], "Compressed artifact changed")
    A.require(manifest["inventory_scope"] == scope(manifest["cases"], catalogue), "Inventory coverage arithmetic changed")
    return manifest


def replay_one(row, binaries, temporary_root):
    started = time.monotonic()
    case = row["parameters"]
    folder, logs = HERE / "cases" / row["case_id"], HERE / "replay_logs" / row["case_id"]
    logs.mkdir(parents=True, exist_ok=True)
    result = {"case_id": row["case_id"], "parameters": case, "production_status": row["status"], "status": "RUNNING"}
    try:
        with tempfile.TemporaryDirectory(prefix="case_", dir=temporary_root) as temporary:
            work = Path(temporary)
            f = P.formula(case)
            regenerated = work / "regenerated.cnf"
            E.write_dimacs(f, regenerated)
            A.require(A.sha(regenerated) == row["cnf_sha256"], "Exact formula regeneration mismatch")
            with ExitStack() as stack:
                cnf = stack.enter_context(C.materialized(folder / "input.cnf", row["cnf_sha256"], work, prefer_compressed=True))
                if row["status"] == P.UNSAT:
                    proof = stack.enter_context(C.materialized(folder / "proof.drat", row["proof_sha256"], work, prefer_compressed=True))
                    audit = A.check_pair(cnf, proof, work / "audit", binaries, 900, 1024, 256, False)
                    A.require(audit["status"] == "PASS_CNF_UNSAT_VIA_CAKEML_LRAT", "Pinned CakeML checker rejected")
                    A.require(audit["input_sha256"] == {"cnf": row["cnf_sha256"], "drat": row["proof_sha256"]}, "Checker inspected wrong inputs")
                    result.update(status="PASS_EXACT_DIMENSION4_UNSAT_CAKEML", audit=audit)
                    for p in (work / "audit").glob("*.txt"):
                        shutil.copyfile(p, logs / p.name)
                elif row["status"] == P.SAT:
                    witness_path = folder / "ACTUAL_KAKEYA_WITNESS.json"
                    A.require(A.sha(witness_path) == row["witness_sha256"], "Witness changed")
                    witness = json.loads(witness_path.read_text())
                    fibres = {int(a): frozenset(Aa) for a, Aa in witness["fibres"].items()}
                    assignment = E.actual_assignment(f, fibres)
                    A.require(not E.first_failed_clauses(f, assignment), "Concrete model violates exact CNF")
                    geometry = G.verify_actual_kakeya(fibres, 4, case["ring"])
                    A.require(geometry["is_kakeya"] and geometry["point_count"] <= 45, "Claimed actual counterexample fails direct geometry")
                    result.update(status="PASS_ACTUAL_DIMENSION4_KAKEYA_WITNESS", direct_geometry=geometry)
                else:
                    A.require(row["status"] == "TIMEOUT_UNCERTIFIED", "Unexpected status")
                    result.update(status="PASS_TIMEOUT_REGENERATION_NO_EXCLUSION", exclusion_credited=False)
                for name, info in row["storage"].items():
                    A.require(C.logical_sha(folder / name, prefer_compressed=True) == info["raw_sha256"], "Persisted decoded bytes changed")
                A.require(A.sha(cnf) == row["cnf_sha256"], "Materialized formula changed")
            del f
            gc.collect()
    except Exception as error:
        result.update(status="FAIL", error=repr(error))
    result["seconds"] = round(time.monotonic() - started, 6)
    P.dump(logs / "CASE_REPLAY.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--quick", action="store_true", help="Replay at most four cases; cannot establish whole-inventory coverage")
    args = parser.parse_args()
    started = time.monotonic()
    destination = HERE / ("DIMENSION4_QUICK_REPLAY.json" if args.quick else "DIMENSION4_FULL_REPLAY.json")
    receipt = {"status": "RUNNING", "quick": args.quick, "cases": [], "full_inventory_replayed": False}
    P.dump(destination, receipt)
    try:
        catalogue, checks = catalogue_replay()
        if args.freeze:
            freeze(catalogue)
        manifest = load(catalogue)
        selected = manifest["cases"][:4] if args.quick else manifest["cases"]
        receipt.update(manifest_sha256=A.sha(MANIFEST), source_hashes=D.sources(), catalogue_checks=checks,
                       claimed_inventory_scope=manifest["inventory_scope"], checker_source_pins=A.verify_sources())
        with tempfile.TemporaryDirectory(prefix="kakeya_dimension4_replay_") as temporary:
            work = Path(temporary)
            binaries, build = A.build_checkers(work / "bin", HERE / "replay_build_logs")
            receipt["checker_build"] = build
            for row in selected:
                result = replay_one(row, binaries, work)
                receipt["cases"].append(result)
                P.dump(destination, receipt)
                print(json.dumps({k: result[k] for k in ["case_id", "status", "seconds"]}), flush=True)
                A.require(result["status"].startswith("PASS_"), "Case replay failed")
        receipt.update(status="PASS_SAMPLED_DIMENSION4_CERTIFICATES" if args.quick else "PASS_ALL_DELIVERED_DIMENSION4_CERTIFICATES",
                       full_inventory_replayed=not args.quick, checked_scope=scope(receipt["cases"], catalogue, checked=True),
                       seconds=round(time.monotonic() - started, 6))
        P.dump(destination, receipt)
        print(json.dumps({k: receipt[k] for k in ["status", "checked_scope", "seconds"]}), flush=True)
    except Exception as error:
        receipt.update(status="FAIL", error=repr(error), seconds=round(time.monotonic() - started, 6))
        P.dump(destination, receipt)
        raise


if __name__ == "__main__":
    main()
