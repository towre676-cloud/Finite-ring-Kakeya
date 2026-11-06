#!/usr/bin/env python3
"""Bounded, proof-producing Round8 trials against exact strengthened CNFs."""
from pathlib import Path
import argparse
import gc
import importlib.util
import json
import shutil
import sys
import tempfile
import time

sys.dont_write_bytecode = True
import encode_strengthened as X

HERE, ROOT = X.HERE, X.ROOT


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


P = module("r8_safe_inherited_producer", ROOT / "research_round7/support13/certify_support13.py")
H = module("r8_heavy_difference_cover", ROOT / "research_round8/charging/heavy_cover_cut.py")
A, C = P.A, P.C
FREEZE = HERE / "FROZEN_SOURCES.json"
MASKS = [377850134, 411136406, 671697334, 2185856310]
MODES = {
    "baseline": (False, False, False),
    "heavy": (True, False, False),
    "tetrahedral": (False, True, False),
    "heavy_tetrahedral": (True, True, False),
    "heavy_cover": (True, False, True),
    "heavy_cover_tetrahedral": (True, True, True),
}
ACCEPTED = "PASS_EXACT_ROUND8_STRENGTHENED_CNF_DRAT_CAKEML"
WRAPPER = ROOT / "research_round7/support13/rup_unit_solver.py"


def semantic_sources(mode):
    A.require(mode in MODES, "Unknown explicit cut mode")
    paths = [X.BASE, X.EXPOSED_BASE, HERE / "encode_strengthened.py", HERE / "ONE_WAY_SOUNDNESS.txt",
             P.IMPORTED / "data/spec32.csv", P.IMPORTED / "data/Mtable.txt",
             P.IMPORTED / "data/orbits_all.txt", P.QUEUE]
    heavy, tetrahedral, cover = MODES[mode]
    if heavy:
        paths.extend([ROOT / "research_round7/geometry/SUPPORT13_HEAVY_FIBRES.md",
                      ROOT / "research_round7/geometry/SUPPORT13_EIGHT_HEAVY_COROLLARIES.md"])
    if tetrahedral:
        paths.append(ROOT / "research_round7/support13/four_pair_cut/FOUR_PAIR_CAPACITY_LEMMA.txt")
    if cover:
        paths.extend([Path(H.__file__), ROOT / "research_round8/charging/HEAVY_DIFFERENCE_COVER_THEOREM.md",
                      ROOT / "research_round7/dense_encoder/NINE_POINT_DIFFERENCE_ANALYTIC_PROOF.md"])
    return {str(p.relative_to(ROOT)): A.sha(p) for p in sorted(set(paths))}


def all_frozen_sources():
    sources = {}
    for mode in MODES:
        sources.update(semantic_sources(mode))
    for path in [Path(__file__), HERE / "verify_strengthened.py", HERE / "verify_certificates.py",
                 ROOT / "research_round8/charging/verify_heavy_cover.py", Path(P.__file__), WRAPPER]:
        sources[str(path.relative_to(ROOT))] = A.sha(path)
    return dict(sorted(sources.items()))


def freeze_sources():
    controls = json.loads((HERE / "STRENGTHENED_FINITE_REPLAY.json").read_text())
    A.require(controls["status"] == "PASS_ROUND8_STRENGTHENED_FINITE_CONTROLS",
              "Strengthened finite controls have not passed")
    for relative, digest in controls["source_hashes"].items():
        A.require(A.sha(ROOT / relative) == digest, "Finite controls predate a source change")
    cover_controls = json.loads((ROOT / "research_round8/charging/HEAVY_COVER_REPLAY.json").read_text())
    A.require(cover_controls["status"] == "PASS_HEAVY_DIFFERENCE_COVER_THEOREM_CONTROLS_AND_EXACT_PATTERN_INVENTORY",
              "Heavy-cover controls have not passed")
    for relative, digest in cover_controls["source_hashes"].items():
        A.require(A.sha(ROOT / relative) == digest, "Heavy-cover controls predate a source change")
    result = {"schema": "kakeya-round8-strengthened-frozen-sources-v1",
              "source_hashes": all_frozen_sources(),
              "semantic_sources_by_mode": {mode: semantic_sources(mode) for mode in MODES},
              "permitted_masks": MASKS, "maximum_interval": [11, 11], "total_upper_bound": 93,
              "ring_scope": "common_necessary_relaxation_both_rings",
              "encoder_formalized": False}
    if FREEZE.exists():
        A.require(json.loads(FREEZE.read_text()) == result, "Refusing to alter a frozen source set")
    else:
        P.dump(FREEZE, result)
    return result


def load_freeze():
    result = json.loads(FREEZE.read_text())
    A.require(result["schema"] == "kakeya-round8-strengthened-frozen-sources-v1" and
              result["source_hashes"] == all_frozen_sources() and
              result["semantic_sources_by_mode"] == {mode: semantic_sources(mode) for mode in MODES},
              "Frozen source or semantics changed")
    A.require(result["permitted_masks"] == MASKS and result["maximum_interval"] == [11, 11] and
              result["total_upper_bound"] == 93, "Frozen trial scope changed")
    return result


def universe():
    all_cases = {row["nonzero_support_mask"]: row for row in P.universe()}
    return {mask: all_cases[mask] for mask in MASKS}


def make_formula(case, mode, spectra, table, subspaces):
    A.require(case["nonzero_support_mask"] in MASKS and mode in MODES, "Unsupported case or mode")
    heavy, tetrahedral, cover = MODES[mode]
    formula = X.encode(case["support"][1:], 11, spectra, table, subspaces,
                       total=93, hub_min=11, enabled=(mode != "baseline"),
                       heavy=heavy, tetrahedral=tetrahedral)
    metadata = {"strengthened": formula.r8_strengthened_metadata}
    if cover:
        metadata["heavy_difference_cover"] = H.add_heavy_cover_cut(formula, case["support"], spectra)
    return formula, metadata


def stored_case(folder):
    row = json.loads((folder / "CASE_RECEIPT.json").read_text())
    A.require(folder.name == row["case_id"], "Existing case identifier changed")
    for name, storage in row["storage"].items():
        A.require(name in ("input.cnf", "proof.drat"), "Unknown stored artifact")
        A.require(A.sha(folder / (name + ".xz")) == storage["xz_sha256"] and
                  C.logical_sha(folder / name, prefer_compressed=True) == storage["raw_sha256"],
                  "Existing stored bytes changed")
    A.require(row["semantic_input_hashes"] == semantic_sources(row["mode"]) and
              row["frozen_sources_sha256"] == A.sha(FREEZE), "Existing case source binding changed")
    return row


def one(case, mode, limit, tag, binaries, spectra, table, subspaces, checker_timeout):
    mask = case["nonzero_support_mask"]
    case_id = f"s13_T{mask}_m11_{mode}_{tag}"
    destination = HERE / "cases" / case_id
    if destination.exists():
        row = stored_case(destination)
        A.require(row["solver_limit_seconds"] == limit, "Existing trial has another limit; choose a new tag")
        return row
    started = time.monotonic()
    pins = semantic_sources(mode)
    freeze_digest = A.sha(FREEZE)
    row = {"case_id": case_id, "status": "STARTING", "mode": mode,
           "nonzero_support_mask": mask, "support": case["support"], "distinguished_hub": 0,
           "maximum_interval": [11, 11], "total_upper_bound": 93,
           "ring_scope": "common_necessary_relaxation_both_rings",
           "semantic_input_hashes": pins, "frozen_sources_sha256": freeze_digest,
           "producer_sha256": A.sha(Path(__file__)), "search_wrapper_sha256": A.sha(WRAPPER),
           "solver_binary_sha256": A.sha(P.DEFAULT_SOLVER), "solver_limit_seconds": limit,
           "encoder_formalized": False, "storage": {}}
    A.require(shutil.disk_usage("/tmp").free >= 3*1024**3, "Less than3GiB temporary disk free")
    with tempfile.TemporaryDirectory(prefix=f"kakeya_r8_{mask}_") as temporary:
        work = Path(temporary)
        cnf, proof = work / "input.cnf", work / "proof.drat"
        formula, metadata = make_formula(case, mode, spectra, table, subspaces)
        X.write_dimacs(formula, cnf)
        row.update(variables=formula.n, clauses=len(formula.cl), extension=metadata,
                   cnf_sha256=A.sha(cnf), cnf_bytes=cnf.stat().st_size,
                   encode_seconds=round(time.monotonic() - started, 6))
        del formula
        gc.collect()
        command = [str(WRAPPER), "--no-binary", "--no-witness", "-t", str(limit), str(cnf), str(proof)]
        supervision = P.run_guarded_solver(command, work, limit,
                                           proof_byte_limit=768*1024**2, min_free_bytes=2*1024**3)
        row.update(supervision, solver_command=command,
                   live_drat_byte_limit=768*1024**2, minimum_free_disk_bytes=2*1024**3)
        A.require(A.sha(cnf) == row["cnf_sha256"], "Solver changed the original strengthened CNF")
        if proof.exists():
            row.update(proof_sha256=A.sha(proof), proof_bytes=proof.stat().st_size)
        accepted = False
        unsat = row["solver_returncode"] == 20 and "s UNSATISFIABLE" in (work / "solver.stdout.txt").read_text()
        if unsat:
            regenerated, regenerated_metadata = make_formula(case, mode, spectra, table, subspaces)
            X.write_dimacs(regenerated, work / "regenerated.cnf")
            A.require(A.sha(work / "regenerated.cnf") == row["cnf_sha256"] and
                      regenerated_metadata == metadata, "Fresh formula regeneration differs")
            del regenerated
            gc.collect()
            audit = A.check_pair(cnf, proof, work / "audit", binaries, checker_timeout, 1024, 256, False)
            row["audit"] = audit
            A.require(audit["input_sha256"] == {"cnf": row["cnf_sha256"], "drat": row["proof_sha256"]},
                      "Checker received different exact inputs")
            accepted = audit["status"] == "PASS_CNF_UNSAT_VIA_CAKEML_LRAT"
            row["status"] = ACCEPTED if accepted else "CHECKER_REJECTED_UNCERTIFIED"
        elif row["solver_returncode"] == 10:
            row["status"] = "SAT_RELAXATION_NO_ACTUAL_KAKEYA_WITNESS"
        else:
            row["status"] = "TIMEOUT_OR_UNACCEPTED_UNCERTIFIED"
        A.require(semantic_sources(mode) == pins and A.sha(FREEZE) == freeze_digest,
                  "Frozen semantics changed during trial")
        load_freeze()
        destination.mkdir(parents=True)
        for raw in [cnf] + ([proof] if accepted else []):
            digest = row["cnf_sha256"] if raw == cnf else row["proof_sha256"]
            storage = C.compress_verified(raw, digest, preset=1, remove_raw=True)
            compressed = Path(str(raw) + ".xz")
            P.publish_copy(compressed, destination / compressed.name, storage["xz_sha256"])
            A.require(C.logical_sha(destination / raw.name, prefer_compressed=True) == digest,
                      "Published decoded artifact differs")
            storage.update(logical_path=raw.name, compressed_path=compressed.name)
            row["storage"][raw.name] = storage
        if not accepted and proof.exists():
            row["discarded_unaccepted_proof"] = {"sha256": row["proof_sha256"], "bytes": row["proof_bytes"]}
        for path in list(work.glob("*.txt")) + list((work / "audit").glob("*.txt")):
            P.publish_copy(path, destination / path.name, A.sha(path))
        prefix, preprocessing = destination / "rup_unit_prefix.txt", destination / "rup_unit_preprocessing.txt"
        if preprocessing.exists():
            details = json.loads(preprocessing.read_text())
            A.require(details["original_cnf_sha256"] == row["cnf_sha256"] and
                      details["prefix_sha256"] == A.sha(prefix), "RUP-prefix provenance differs")
            row["untrusted_search_provenance"] = {"metadata_sha256": A.sha(preprocessing),
                                                   "prefix_sha256": A.sha(prefix),
                                                   "added_units": details["added_unit_count"]}
        row.update(seconds=round(time.monotonic() - started, 6),
                   unfinished_proof_retained=False, reconstructed_lrat_retained=False,
                   original_round6_baseline_claimed_refuted=(mode == "baseline" and accepted),
                   exclusion_credited=accepted)
        P.dump(destination / "CASE_RECEIPT.json", row)
    return stored_case(destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--mode", choices=MODES, default="heavy_cover_tetrahedral")
    parser.add_argument("--mask", action="append", type=int)
    parser.add_argument("--limit", type=int, default=120)
    parser.add_argument("--tag", default="first120")
    parser.add_argument("--worker", default="main")
    parser.add_argument("--check-timeout", type=int, default=900)
    args = parser.parse_args()
    A.require(args.tag.replace("_", "").isalnum() and args.worker.replace("_", "").isalnum(), "Unsafe namespace")
    A.require(args.limit > 0 and args.check_timeout > 0, "Invalid resource limit")
    if args.freeze:
        freeze_sources()
        print(json.dumps({"frozen_sources_sha256": A.sha(FREEZE)}), flush=True)
    if not args.run:
        return
    load_freeze()
    requested = MASKS if args.mask is None else args.mask
    A.require(len(requested) == len(set(requested)) and set(requested) <= set(MASKS), "Unsupported or duplicate mask")
    cases = universe()
    tool_root = HERE / "worker_tools" / args.worker
    binaries, build = A.build_checkers(tool_root / "bin", tool_root / "build_logs")
    P.dump(tool_root / "BUILD_RECEIPT.json", {"pins": A.verify_sources(), "build": build,
                                             "frozen_sources_sha256": A.sha(FREEZE)})
    data = P.IMPORTED / "data"
    spectra, table, subspaces = X.load_spectra(data / "spec32.csv"), X.load_M(data / "Mtable.txt"), X.all_subspaces()
    output = HERE / f"{args.tag}_{args.mode}_SWEEP.json"
    report = {"status": "RUNNING", "requested_masks": requested, "mode": args.mode,
              "maximum_interval": [11, 11], "cases": [], "full_support13_claimed": False}
    P.dump(output, report)
    started = time.monotonic()
    try:
        for mask in requested:
            if (HERE / "STOP_REQUESTED").exists():
                report["stop_requested"] = True
                break
            row = one(cases[mask], args.mode, args.limit, args.tag, binaries,
                      spectra, table, subspaces, args.check_timeout)
            report["cases"].append(row)
            report["seconds"] = round(time.monotonic() - started, 6)
            P.dump(output, report)
            print(json.dumps({k: row.get(k) for k in ("case_id", "status", "solve_seconds", "proof_bytes", "seconds")}), flush=True)
        report.update(status="COMPLETED_BOUNDED_ROUND8_SEARCH",
                      accepted_cases=sum(row["status"] == ACCEPTED for row in report["cases"]),
                      seconds=round(time.monotonic() - started, 6))
        P.dump(output, report)
    except BaseException as error:
        report.update(status="FAILED_UNCERTIFIED_RUN", error=repr(error), seconds=round(time.monotonic() - started, 6))
        P.dump(output, report)
        raise


if __name__ == "__main__":
    main()
