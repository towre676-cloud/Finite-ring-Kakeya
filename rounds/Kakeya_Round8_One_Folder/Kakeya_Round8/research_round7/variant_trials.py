#!/usr/bin/env python3
"""Bounded, proof-checked comparisons of explicitly named necessary relaxations.

No incomplete solver output establishes an exclusion.  Completed exact
CNFs and ordinary DRAT proofs are compressed, hashed and freshly replayed.
Earlier rounds and the complete S13 catalogue are read-only inputs.
"""
from pathlib import Path
import argparse
import gc
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
R6 = ROOT / "research_round6"
QUEUE = R6 / "next_frontier/SUPPORT13_CASE_QUEUE.json"
BASE_PATH = R6 / "encoder_audit/encode_maximal_cosets.py"
SOLVER = Path("/tmp/kakeya_lean_round4/lean-4.24.0-linux/bin/cadical")
ACCEPTED = "PASS_EXACT_VARIANT_CNF_DRAT_CAKEML"


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


A = module("r7_variants_audit", ROOT / "research_round5/proof_audit/audit_certificates.py")
C = module("r7_variants_storage", R6 / "certificate_storage.py")
BASE = module("r7_variants_base", BASE_PATH)


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".publishing")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    os.replace(temporary, path)


def source_paths(mode):
    paths = [Path(__file__), BASE_PATH,
             R6 / "joint_maxima/encode_joint_maxima.py",
             R6 / "imported_claude_round4/data/spec32.csv",
             R6 / "imported_claude_round4/data/Mtable.txt", QUEUE,
             R6 / "imported_claude_round4/data/orbits_all.txt"]
    if mode in ("span", "span4", "combined"):
        paths.append(HERE / "span_capacity/encode_span_capacity.py")
    if mode in ("dense", "combined"):
        paths.append(HERE / "dense_encoder/encode_dense_types.py")
    if mode in ("plane", "combined"):
        paths.append(HERE / "geometry/plane_cuts.py")
    return paths


def semantic_hashes(mode):
    return {str(p.relative_to(ROOT)): A.sha(p) for p in source_paths(mode)}


def make_formula(case, lower, upper, mode, SPEC, M, SUBS):
    S = case["support"]
    f = BASE.encode(S[1:], upper, SPEC, M, SUBS, outtotal=93,
                    hub_min=lower, strengthen=False)
    metadata = {"base_variables": f.n, "base_clauses": len(f.cl)}
    if mode in ("dense", "combined"):
        D = module("r7_variants_dense", HERE / "dense_encoder/encode_dense_types.py")
        directions = {v: [v ^ b for b in S if b != v] for v in S}
        D.append_dense_constraints(f, S, directions, SPEC, SUBS, f.z, f.y, f.h_selectors)
        metadata["dense"] = {"variables": f.dense_extra_variables, "clauses": f.dense_extra_clauses}
    if mode in ("plane", "combined"):
        P = module("r7_variants_plane", HERE / "geometry/plane_cuts.py")
        metadata["plane"] = P.add_plane_cuts(f, S, SPEC)
    if mode in ("span", "span4", "combined"):
        X = module("r7_variants_span", HERE / "span_capacity/encode_span_capacity.py")
        X.append_span_capacity(f, S, M, SUBS, dimensions=(4,) if mode == "span4" else (2, 3, 4))
        metadata["span"] = f.span_metadata
    return f, metadata


def write_verified(source, target, digest):
    A.require(not target.exists(), "Refusing to overwrite a published file")
    temporary = target.with_suffix(target.suffix + ".publishing")
    shutil.copyfile(source, temporary)
    A.require(A.sha(temporary) == digest, "Copy changed accepted bytes")
    os.replace(temporary, target)


def one(case, lower, upper, mode, limit, tag, binaries, SPEC, M, SUBS):
    mask = case["nonzero_support_mask"]
    cid = f"s13_T{mask}_m{lower}_{upper}_{mode}_{tag}"
    destination = HERE / "variant_cases" / cid
    A.require(not destination.exists(), "Choose a new tag; completed trials are immutable")
    started = time.monotonic()
    pins = semantic_hashes(mode)
    result = {"case_id": cid, "status": "STARTING", "mode": mode,
              "support": case["support"], "nonzero_support_mask": mask,
              "distinguished_hub": 0, "maximum_interval": [lower, upper],
              "total_upper_bound": 93, "ring_scope": "common_necessary_relaxation_both_rings",
              "semantic_input_hashes": pins, "solver_sha256": A.sha(SOLVER),
              "wall_limit_seconds": limit, "storage": {},
              "encoder_formalized": False}
    A.require(shutil.disk_usage("/tmp").free > 3 * 1024**3, "Temporary disk guard")
    with tempfile.TemporaryDirectory(prefix="kakeya_r7_variant_") as temporary:
        work = Path(temporary)
        cnf, proof = work / "input.cnf", work / "proof.drat"
        f, details = make_formula(case, lower, upper, mode, SPEC, M, SUBS)
        BASE.write_dimacs(f, cnf)
        result.update(variables=f.n, clauses=len(f.cl), extension=details,
                      cnf_sha256=A.sha(cnf), cnf_bytes=cnf.stat().st_size,
                      encode_seconds=round(time.monotonic() - started, 6))
        del f
        gc.collect()
        command = [str(SOLVER), "--no-binary", "--no-witness", "-t", str(limit), str(cnf), str(proof)]
        solve_started = time.monotonic()
        reason = None
        with (work / "solver.stdout.txt").open("wb") as out, (work / "solver.stderr.txt").open("wb") as err:
            process = subprocess.Popen(command, stdout=out, stderr=err)
            try:
                while process.poll() is None:
                    if time.monotonic() - solve_started > limit + 2:
                        reason = "WALL_TIMEOUT"
                    elif proof.exists() and proof.stat().st_size > 1024**3:
                        reason = "PROOF_SIZE_GUARD"
                    elif shutil.disk_usage("/tmp").free < 2 * 1024**3:
                        reason = "DISK_GUARD"
                    if reason:
                        process.kill()
                        break
                    time.sleep(0.2)
                code = process.wait()
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait()
        result.update(solver_returncode=code, stop_reason=reason,
                      solver_command=command, solve_seconds=round(time.monotonic() - solve_started, 6))
        if proof.exists():
            result.update(drat_sha256=A.sha(proof), drat_bytes=proof.stat().st_size)
        unsat = code == 20 and "s UNSATISFIABLE" in (work / "solver.stdout.txt").read_text()
        accepted = False
        if unsat:
            audit = A.check_pair(cnf, proof, work / "audit", binaries, 900, 1024, 256, False)
            result["audit"] = audit
            accepted = audit["status"] == "PASS_CNF_UNSAT_VIA_CAKEML_LRAT"
            A.require(audit["input_sha256"] == {"cnf": result["cnf_sha256"], "drat": result["drat_sha256"]},
                      "Unexpected exact checker inputs")
        result["status"] = ACCEPTED if accepted else (
            "TIMEOUT_UNCERTIFIED" if reason or code == 0 else "UNACCEPTED_UNCERTIFIED")
        A.require(semantic_hashes(mode) == pins, "Semantic source changed during trial")
        destination.mkdir(parents=True)
        for raw in [cnf] + ([proof] if accepted else []):
            expected = result["cnf_sha256"] if raw == cnf else result["drat_sha256"]
            meta = C.compress_verified(raw, expected, preset=1, remove_raw=True)
            stored = Path(str(raw) + ".xz")
            write_verified(stored, destination / stored.name, meta["xz_sha256"])
            A.require(C.logical_sha(destination / raw.name, prefer_compressed=True) == expected,
                      "Published decoded hash changed")
            result["storage"][raw.name] = meta
        if not accepted and proof.exists():
            result["discarded_unfinished_drat"] = {
                "sha256": result["drat_sha256"], "bytes": result["drat_bytes"],
                "reason": "Unaccepted trace; no mathematical exclusion."}
        for p in list(work.glob("*.txt")) + list((work / "audit").glob("*.txt")):
            write_verified(p, destination / p.name, A.sha(p))
        result.update(seconds=round(time.monotonic() - started, 6),
                      reconstructed_lrat_retained=False, unfinished_proof_retained=False)
        dump(destination / "CASE_RECEIPT.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mask", type=int, action="append", required=True)
    parser.add_argument("--mode", choices=["baseline", "span", "span4", "dense", "plane", "combined"],
                        action="append", required=True)
    parser.add_argument("--lower", type=int, default=2)
    parser.add_argument("--upper", type=int, default=18)
    parser.add_argument("--limit", type=int, default=60)
    parser.add_argument("--tag", required=True)
    args = parser.parse_args()
    A.require(2 <= args.lower <= args.upper <= 18 and args.limit > 0, "Invalid interval/limit")
    A.require(args.tag.replace("_", "").isalnum(), "Invalid tag")
    A.require(A.sha(BASE_PATH) == "7e3225d4b5d0ff50d4578fc7d1d4a924d122449ce4e87f00520bac0ee0016102",
              "Frozen base changed")
    queue = json.loads(QUEUE.read_text())
    cases = {c["nonzero_support_mask"]: c for c in queue["cases"]}
    A.require(set(args.mask) <= set(cases), "Unknown marked support")
    pins = A.verify_sources()
    binaries, build = A.build_checkers(HERE / "variant_bin", HERE / "variant_build_logs")
    dump(HERE / "VARIANT_BUILD_RECEIPT.json", {"pins": pins, "build": build})
    data = R6 / "imported_claude_round4/data"
    SPEC, M, SUBS = BASE.load_spectra(data / "spec32.csv"), BASE.load_M(data / "Mtable.txt"), BASE.all_subspaces()
    report = {"status": "RUNNING", "cases": [], "performance_caveat":
              "Single wall-limited runs in a shared environment; no general speed claim."}
    output = HERE / f"{args.tag}_VARIANT_TRIALS.json"
    dump(output, report)
    for mask in args.mask:
        for mode in args.mode:
            row = one(cases[mask], args.lower, args.upper, mode, args.limit,
                      args.tag, binaries, SPEC, M, SUBS)
            report["cases"].append(row)
            dump(output, report)
            print(json.dumps({k: row.get(k) for k in ["case_id", "status", "solve_seconds", "drat_bytes", "seconds"]}), flush=True)
    report["status"] = "COMPLETED_BOUNDED_VARIANT_TRIALS"
    dump(output, report)


if __name__ == "__main__":
    main()
