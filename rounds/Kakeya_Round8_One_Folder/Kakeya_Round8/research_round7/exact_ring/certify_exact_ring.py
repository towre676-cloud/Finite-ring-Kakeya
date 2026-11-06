#!/usr/bin/env python3
"""Proof-check exact-ring UNSAT; directly check every concrete SAT witness."""
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
import encode_exact_ring as E
import verify_exact_ring as G

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOLVER = Path("/tmp/kakeya_lean_round4/lean-4.24.0-linux/bin/cadical")
UNSAT = "PASS_EXACT_RING_UNSAT_CAKEML"
SAT = "PASS_ACTUAL_RING_KAKEYA_SAT_WITNESS"


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


A = module("exact_ring_proof_audit", ROOT / "research_round5/proof_audit/audit_certificates.py")
C = module("exact_ring_storage", ROOT / "research_round6/certificate_storage.py")


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".publishing")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    os.replace(temporary, path)


def sources():
    return {str(p.relative_to(ROOT)): A.sha(p) for p in [
        HERE / "encode_exact_ring.py", HERE / "verify_exact_ring.py", Path(__file__)]}


def case_universe(include_s13=True):
    result = []
    for ring in E.RINGS:
        for support in [[0, 1, 2], [0, 1, 2, 3]]:
            result.append({"case_id": f"n2_{ring}_s{len(support)}_budget9",
                           "dimension": 2, "ring": ring, "support": support,
                           "maximum": 4, "hub_min": 2, "total": 9,
                           "normalize": True, "purpose": "complete_dimension2_lower_bound"})
        result.append({"case_id": f"n2_{ring}_s4_budget10", "dimension": 2,
                       "ring": ring, "support": [0, 1, 2, 3],
                       "maximum": 4, "hub_min": 2, "total": 10,
                       "normalize": True, "purpose": "dimension2_concrete_upper_bound"})
    if include_s13:
        for ring in E.RINGS:
            result.append({"case_id": f"n5_{ring}_s13_T1022358_m2_18_budget93",
                           "dimension": 5, "ring": ring,
                           "support": [0, 1, 2, 4, 7, 8, 11, 12, 15, 16, 17, 18, 19],
                           "maximum": 18, "hub_min": 2, "total": 93,
                           "normalize": True, "purpose": "new_support13_exact_ring_diagnostic"})
    return result


def formula(case):
    return E.encode_support(case["support"], case["maximum"], case["hub_min"],
                            case["total"], case["dimension"], case["ring"], case["normalize"])


def publish(source, destination, digest):
    A.require(not destination.exists(), "Refusing to overwrite a published artifact")
    temporary = destination.with_suffix(destination.suffix + ".publishing")
    shutil.copyfile(source, temporary)
    A.require(A.sha(temporary) == digest, "Published bytes changed")
    os.replace(temporary, destination)


def extract_and_check_model(output, f):
    values = {}
    for line in output.splitlines():
        if line.startswith("v "):
            for word in line[2:].split():
                literal = int(word)
                if not literal:
                    continue
                variable, value = abs(literal), literal > 0
                A.require(variable not in values or values[variable] == value, "Contradictory SAT model")
                values[variable] = value
    A.require(all(variable in values for variable in f.members.values()), "Incomplete membership model")
    fibres = {a: frozenset(x for x in range(1 << f.dimension) if values[f.members[a, x]]) for a in f.support}
    canonical = E.actual_assignment(f, fibres)
    A.require(not E.first_failed_clauses(f, canonical), "SAT membership fails exact CNF")
    direct = G.verify_actual_kakeya(fibres, f.dimension, f.ring)
    A.require(direct["is_kakeya"] and direct["point_count"] <= f.total, "SAT witness fails direct ring geometry")
    weights = {a: len(Aa) for a, Aa in fibres.items()}
    A.require(f.hub_min <= weights[0] <= f.maximum and all(2 <= w <= weights[0] for w in weights.values()),
              "SAT witness violates support/maximum domain")
    return {"fibres": {str(a): sorted(Aa) for a, Aa in fibres.items()},
            "weights": {str(a): w for a, w in weights.items()},
            "ring": f.ring, "dimension": f.dimension, "direct_check": direct,
            "canonical_cnf_assignment_satisfied": True, "anchors": f.anchors}


def run_one(case, binaries, limit):
    target = HERE / "cases" / case["case_id"]
    if target.exists():
        prior = json.loads((target / "CASE_RECEIPT.json").read_text())
        A.require(prior["parameters"] == case and prior["source_hashes"] == sources(), "Existing case has different semantics")
        for name, info in prior["storage"].items():
            A.require(A.sha(target / (name + ".xz")) == info["xz_sha256"], "Existing stored bytes changed")
            A.require(C.logical_sha(target / name, prefer_compressed=True) == info["raw_sha256"], "Existing decoded bytes changed")
        return prior
    started = time.monotonic()
    pins = sources()
    result = {"case_id": case["case_id"], "parameters": case, "status": "STARTING",
              "source_hashes": pins, "solver_sha256": A.sha(SOLVER), "wall_limit_seconds": limit,
              "census_dependency": False, "capacity_table_dependency": False,
              "encoder_formalized": False, "storage": {}}
    A.require(shutil.disk_usage("/tmp").free > 3 * 1024**3, "Temporary disk guard")
    with tempfile.TemporaryDirectory(prefix="kakeya_exact_ring_") as temporary:
        work = Path(temporary)
        cnf, proof = work / "input.cnf", work / "proof.drat"
        f = formula(case)
        E.write_dimacs(f, cnf)
        result.update(variables=f.n, clauses=len(f.cl), anchors=f.anchors,
                      cnf_sha256=A.sha(cnf), cnf_bytes=cnf.stat().st_size,
                      encode_seconds=round(time.monotonic() - started, 6))
        # Keep f to extract an independently checked concrete model if SAT.
        command = [str(SOLVER), "--no-binary", "-t", str(limit), str(cnf), str(proof)]
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
        result.update(solver_returncode=code, stop_reason=reason, solver_command=command,
                      solve_seconds=round(time.monotonic() - solve_started, 6))
        output = (work / "solver.stdout.txt").read_text()
        if proof.exists():
            result.update(proof_sha256=A.sha(proof), proof_bytes=proof.stat().st_size)
        accepted = False
        if code == 20 and "s UNSATISFIABLE" in output:
            audit = A.check_pair(cnf, proof, work / "audit", binaries, 900, 1024, 256, False)
            result["audit"] = audit
            A.require(audit["input_sha256"] == {"cnf": result["cnf_sha256"], "drat": result["proof_sha256"]},
                      "Checker inspected different bytes")
            accepted = audit["status"] == "PASS_CNF_UNSAT_VIA_CAKEML_LRAT"
            result["status"] = UNSAT if accepted else "UNACCEPTED_UNSAT_RESULT"
        elif code == 10 and "s SATISFIABLE" in output:
            witness = extract_and_check_model(output, f)
            dump(work / "ACTUAL_KAKEYA_WITNESS.json", witness)
            result.update(status=SAT, witness_sha256=A.sha(work / "ACTUAL_KAKEYA_WITNESS.json"),
                          direct_sat_check=witness["direct_check"])
        else:
            result["status"] = "TIMEOUT_UNCERTIFIED" if reason or code == 0 else "UNACCEPTED_SOLVER_RESULT"
        del f
        gc.collect()
        A.require(sources() == pins, "Exact encoder or validation source changed mid-run")
        target.mkdir(parents=True)
        for raw in [cnf] + ([proof] if accepted else []):
            expected = result["cnf_sha256"] if raw == cnf else result["proof_sha256"]
            info = C.compress_verified(raw, expected, preset=1, remove_raw=True)
            compressed = Path(str(raw) + ".xz")
            publish(compressed, target / compressed.name, info["xz_sha256"])
            A.require(C.logical_sha(target / raw.name, prefer_compressed=True) == expected, "Published logical bytes differ")
            result["storage"][raw.name] = info
        if not accepted and proof.exists():
            result["discarded_unaccepted_proof"] = {"sha256": result["proof_sha256"],
                "bytes": result["proof_bytes"], "reason": "Not an accepted UNSAT refutation; no exclusion credit."}
        for path in list(work.glob("*.txt")) + list(work.glob("*.json")) + list((work / "audit").glob("*.txt")):
            publish(path, target / path.name, A.sha(path))
        result.update(seconds=round(time.monotonic() - started, 6), unfinished_proof_retained=False)
        dump(target / "CASE_RECEIPT.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dimension2-only", action="store_true")
    parser.add_argument("--dimension5-only", action="store_true")
    parser.add_argument("--limit", type=int, default=60)
    args = parser.parse_args()
    A.require(args.limit > 0 and not (args.dimension2_only and args.dimension5_only), "Invalid selection")
    cases = case_universe(not args.dimension2_only)
    if args.dimension5_only:
        cases = [c for c in cases if c["dimension"] == 5]
    dump(HERE / "EXACT_RING_CASE_UNIVERSE.json", case_universe())
    pins = A.verify_sources()
    binaries, build = A.build_checkers(HERE / "bin", HERE / "build_logs")
    dump(HERE / "CHECKER_BUILD_RECEIPT.json", {"pins": pins, "build": build})
    report = {"status": "RUNNING", "cases": [], "source_hashes": sources()}
    output = HERE / ("DIMENSION2_PRODUCTION.json" if args.dimension2_only else
                     "DIMENSION5_PRODUCTION.json" if args.dimension5_only else "ALL_PRODUCTION.json")
    dump(output, report)
    for case in cases:
        result = run_one(case, binaries, min(args.limit, 30) if case["dimension"] == 2 else args.limit)
        report["cases"].append(result)
        dump(output, report)
        print(json.dumps({key: result.get(key) for key in ["case_id", "status", "solve_seconds", "proof_bytes", "seconds"]}), flush=True)
    report["status"] = "COMPLETED_EXACT_RING_DIAGNOSTICS"
    dump(output, report)


if __name__ == "__main__":
    main()
