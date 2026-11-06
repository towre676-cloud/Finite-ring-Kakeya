#!/usr/bin/env python3
"""Fresh portable replay of exact-ring formulas, proofs and actual witnesses."""
from pathlib import Path
from contextlib import ExitStack
import argparse
import gc
import json
import shutil
import tempfile
import time
import certify_exact_ring as P
import certify_dimension3 as N3
import encode_exact_ring as E
import verify_exact_ring as G

HERE, ROOT, A, C = P.HERE, P.ROOT, P.A, P.C
MANIFEST = HERE / "EXACT_RING_CERTIFICATE_MANIFEST.json"


def catalogue_checks():
    generated = N3.catalogue()
    stored = json.loads((HERE / "DIMENSION3_SUPPORT_CATALOGUE.json").read_text())
    A.require(generated == stored, "Dimension3 catalogue does not regenerate exactly")
    A.require(generated["marked_class_count"] == 5 and generated["group_order"] == 168,
              "Dimension3 catalogue has wrong scope")
    rows = []
    for case in generated["cases"]:
        for ring in E.RINGS:
            direct = G.direct_line_terms(case["support"], 3, ring)
            encoded = G.encoder_line_terms(case["support"], 3, ring)
            A.require(direct == encoded, "Dimension3 exact coverage terms differ from ring arithmetic")
            rows.append({"support_full_mask": case["full_mask"], "ring": ring,
                         "directions": len(direct), "literal_line_terms": sum(map(len, direct.values()))})
    upper = N3.upper_bound()
    A.require(upper == json.loads((HERE / "DIMENSION3_22_POINT_STAR.json").read_text()),
              "Dimension3 explicit upper-bound witness changed")
    return generated, {"complete_marked_catalogue_reproduced": True,
                       "all_ten_literal_ring_line_families_equal_encoder_terms": rows,
                       "explicit_22_point_star_both_rings_rechecked": True}


def universe():
    return P.case_universe() + N3.cases(N3.catalogue())


def semantic_sources():
    extra = {str(path.relative_to(ROOT)): A.sha(path) for path in [
        HERE / "certify_dimension3.py", HERE / "DIMENSION3_SUPPORT_CATALOGUE.json",
        HERE / "DIMENSION3_CASE_UNIVERSE.json", HERE / "DIMENSION3_22_POINT_STAR.json"]}
    return {**P.sources(), **extra}


def freeze_manifest():
    rows = []
    for case in universe():
        folder = HERE / "cases" / case["case_id"]
        receipt_path = folder / "CASE_RECEIPT.json"
        record = json.loads(receipt_path.read_text())
        A.require(record["parameters"] == case, "Production parameters differ from complete case universe")
        A.require(record["source_hashes"] == P.sources(), "Production source changed")
        row = {"case_id": case["case_id"], "parameters": case, "status": record["status"],
               "receipt": str(receipt_path.relative_to(ROOT)), "receipt_sha256": A.sha(receipt_path),
               "cnf_sha256": record["cnf_sha256"], "storage": record["storage"]}
        for name, info in row["storage"].items():
            A.require(A.sha(folder / (name + ".xz")) == info["xz_sha256"], "Stored certificate bytes changed")
            A.require(C.logical_sha(folder / name, prefer_compressed=True) == info["raw_sha256"],
                      "Decoded certificate bytes changed")
        if record["status"] == P.UNSAT:
            row["proof_sha256"] = record["proof_sha256"]
            A.require("proof.drat" in row["storage"], "Accepted proof is missing")
        elif record["status"] == P.SAT:
            row["witness_sha256"] = record["witness_sha256"]
            A.require(A.sha(folder / "ACTUAL_KAKEYA_WITNESS.json") == row["witness_sha256"], "SAT witness changed")
        else:
            A.require(record["status"] == "TIMEOUT_UNCERTIFIED", "Unexpected unaccepted production status")
            A.require("proof.drat" not in row["storage"], "Unaccepted proof must not be a delivered certificate")
        rows.append(row)
    manifest = {"schema": "kakeya-exact-ring-certificates-v1", "source_hashes": semantic_sources(),
                "status": "FROZEN_INVENTORY_REQUIRING_FRESH_REPLAY", "cases": rows,
                "case_ids": [r["case_id"] for r in rows], "census_dependency": False,
                "capacity_table_dependency": False, "encoder_formalized": False}
    P.dump(MANIFEST, manifest)
    return manifest


def load_manifest():
    manifest = json.loads(MANIFEST.read_text())
    A.require(manifest["schema"] == "kakeya-exact-ring-certificates-v1", "Unexpected manifest schema")
    A.require(manifest["source_hashes"] == semantic_sources(), "Manifest semantic sources changed")
    expected = universe()
    A.require([r["parameters"] for r in manifest["cases"]] == expected, "Incomplete or altered case universe")
    A.require(manifest["case_ids"] == [c["case_id"] for c in expected], "Case IDs differ")
    A.require(len(set(manifest["case_ids"])) == len(expected), "Duplicate case")
    for row in manifest["cases"]:
        folder = HERE / "cases" / row["case_id"]
        receipt = folder / "CASE_RECEIPT.json"
        A.require(str(receipt.relative_to(ROOT)) == row["receipt"] and A.sha(receipt) == row["receipt_sha256"],
                  "Receipt path or content changed")
        for name, info in row["storage"].items():
            A.require(name in ("input.cnf", "proof.drat"), "Unexpected stored artifact")
            A.require(A.sha(folder / (name + ".xz")) == info["xz_sha256"], "Stored compressed hash changed")
    return manifest


def replay_one(row, binaries, temporary_root):
    started = time.monotonic()
    case = row["parameters"]
    folder = HERE / "cases" / row["case_id"]
    logs = HERE / "replay_logs" / row["case_id"]
    logs.mkdir(parents=True, exist_ok=True)
    result = {"case_id": row["case_id"], "parameters": case, "production_status": row["status"],
              "status": "RUNNING"}
    try:
        with tempfile.TemporaryDirectory(prefix="case_", dir=temporary_root) as temporary:
            work = Path(temporary)
            f = P.formula(case)
            regenerated = work / "regenerated.cnf"
            E.write_dimacs(f, regenerated)
            A.require(A.sha(regenerated) == row["cnf_sha256"], "Exact CNF regeneration differs")
            with ExitStack() as stack:
                cnf = stack.enter_context(C.materialized(folder / "input.cnf", row["cnf_sha256"], work, prefer_compressed=True))
                if row["status"] == P.UNSAT:
                    proof = stack.enter_context(C.materialized(folder / "proof.drat", row["proof_sha256"], work, prefer_compressed=True))
                    audit = A.check_pair(cnf, proof, work / "audit", binaries, 900, 1024, 256, False)
                    A.require(audit["status"] == "PASS_CNF_UNSAT_VIA_CAKEML_LRAT", "Mandatory CakeML replay rejected")
                    A.require(audit["input_sha256"] == {"cnf": row["cnf_sha256"], "drat": row["proof_sha256"]},
                              "Checker inspected different inputs")
                    result.update(status="PASS_EXACT_REGENERATED_UNSAT_CAKEML", audit=audit)
                    for source in (work / "audit").glob("*.txt"):
                        shutil.copyfile(source, logs / source.name)
                elif row["status"] == P.SAT:
                    witness_path = folder / "ACTUAL_KAKEYA_WITNESS.json"
                    A.require(A.sha(witness_path) == row["witness_sha256"], "Actual witness hash changed")
                    witness = json.loads(witness_path.read_text())
                    fibres = {int(a): frozenset(Aa) for a, Aa in witness["fibres"].items()}
                    assignment = E.actual_assignment(f, fibres)
                    A.require(not E.first_failed_clauses(f, assignment), "Actual SAT witness violates exact formula")
                    geometry = G.verify_actual_kakeya(fibres, case["dimension"], case["ring"])
                    A.require(geometry["is_kakeya"] and geometry["point_count"] <= case["total"],
                              "Actual SAT witness fails literal ring geometry")
                    result.update(status="PASS_EXACT_CNF_AND_ACTUAL_RING_SAT_WITNESS", direct_geometry=geometry)
                else:
                    A.require(row["status"] == "TIMEOUT_UNCERTIFIED", "Unexpected unaccepted status")
                    result.update(status="PASS_TIMEOUT_CNF_REGENERATION_NO_EXCLUSION", exclusion_credited=False)
                for name, info in row["storage"].items():
                    A.require(C.logical_sha(folder / name, prefer_compressed=True) == info["raw_sha256"],
                              "Persisted logical bytes changed during replay")
                A.require(A.sha(cnf) == row["cnf_sha256"], "Materialized formula changed")
            del f
            gc.collect()
    except Exception as error:
        result.update(status="FAIL", error=repr(error))
    result["seconds"] = round(time.monotonic() - started, 6)
    P.dump(logs / "CASE_REPLAY.json", result)
    return result


def theorem_summary(rows):
    by_id = {r["case_id"]: r for r in rows}
    n2_required = [c for c in P.case_universe(False) if c["total"] == 9]
    n2_upper = [c for c in P.case_universe(False) if c["total"] == 10]
    n3_required = N3.cases(N3.catalogue())
    n2 = all(by_id.get(c["case_id"], {}).get("status") == "PASS_EXACT_REGENERATED_UNSAT_CAKEML" for c in n2_required)
    n2 &= all(by_id.get(c["case_id"], {}).get("status") == "PASS_EXACT_CNF_AND_ACTUAL_RING_SAT_WITNESS"
              and by_id[c["case_id"]]["direct_geometry"]["point_count"] == 10 for c in n2_upper)
    n3 = all(by_id.get(c["case_id"], {}).get("status") == "PASS_EXACT_REGENERATED_UNSAT_CAKEML" for c in n3_required)
    return {"global_dimension2_minimum10_both_rings_certified": bool(n2),
            "global_dimension3_minimum22_both_rings_certified": bool(n3),
            "dimension3_complete_marked_support_classes": 5,
            "dimension3_required_ring_specific_refutations": 10,
            "dimension5_exclusions_credited": sum(r["parameters"]["dimension"] == 5 and
                r["status"] == "PASS_EXACT_REGENERATED_UNSAT_CAKEML" for r in rows),
            "semantic_dependency": "Manual exact-encoder and complete-support reduction proofs; CNF UNSAT checked by pinned CakeML.",
            "full_encoder_formalized": False, "census_dependency": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    started = time.monotonic()
    receipt = {"status": "RUNNING", "cases": []}
    destination = HERE / "EXACT_RING_CERTIFICATE_REPLAY.json"
    P.dump(destination, receipt)
    try:
        catalogue, checks = catalogue_checks()
        if args.freeze:
            freeze_manifest()
        manifest = load_manifest()
        receipt.update(manifest_sha256=A.sha(MANIFEST), source_hashes=semantic_sources(), catalogue_checks=checks,
                       checker_source_pins=A.verify_sources())
        with tempfile.TemporaryDirectory(prefix="kakeya_exact_ring_replay_") as temporary:
            work = Path(temporary)
            binaries, build = A.build_checkers(work / "bin", HERE / "replay_build_logs")
            receipt["checker_build"] = build
            for row in manifest["cases"]:
                result = replay_one(row, binaries, work)
                receipt["cases"].append(result)
                P.dump(destination, receipt)
                print(json.dumps({k: result[k] for k in ["case_id", "status", "seconds"]}), flush=True)
                A.require(result["status"].startswith("PASS_"), "Exact-ring case replay failed")
        conclusions = theorem_summary(receipt["cases"])
        A.require(conclusions["global_dimension2_minimum10_both_rings_certified"] and
                  conclusions["global_dimension3_minimum22_both_rings_certified"], "Complete small theorem missing a certificate")
        receipt.update(status="PASS_ALL_EXACT_RING_CERTIFICATES_AND_SMALL_DIMENSION_THEOREMS",
                       theorems=conclusions, full_inventory_replayed=True,
                       cases_replayed=len(receipt["cases"]), seconds=round(time.monotonic() - started, 6))
        P.dump(destination, receipt)
        print(json.dumps({k: receipt[k] for k in ["status", "theorems", "cases_replayed", "seconds"]}), flush=True)
    except Exception as error:
        receipt.update(status="FAIL", error=repr(error), seconds=round(time.monotonic() - started, 6))
        P.dump(destination, receipt)
        raise


if __name__ == "__main__":
    main()
