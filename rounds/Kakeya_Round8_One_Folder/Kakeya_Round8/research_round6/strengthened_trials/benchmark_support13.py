#!/usr/bin/env python3
"""Four bounded paired diagnostics; live formulas/proofs/logs remain under /tmp."""
from pathlib import Path
import gc
import errno
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
IMPORTED = HERE.parent / "imported_claude_round4"
SOLVER = Path("/tmp/kakeya_lean_round4/lean-4.24.0-linux/bin/cadical")
CHECKER = HERE.parent / "joint_maxima/bin/cake_lpr"
LIMIT = 60


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    out = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(out)
    return out


A = module("s13_audit_helpers", ROOT / "research_round5/proof_audit/audit_certificates.py")
C = module("s13_certificate_storage", HERE.parent / "certificate_storage.py")
E = module("s13_strong_encoder", HERE.parent / "encoder_audit/encode_maximal_cosets.py")
B = module("s13_baseline_encoder", HERE.parent / "joint_maxima/encode_joint_maxima.py")


def dump(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")


def historical(mask):
    rows = [
        json.loads(line)
        for line in (IMPORTED / "results/explore_m11_18.jsonl").read_text().splitlines()
    ]
    return [r for r in rows if r["s"] == 13 and r["T"] == mask]


def selected_cases():
    masks = [37848950, 1022358]
    catalogue = {}
    for line in (IMPORTED / "data/orbits_all.txt").read_text().splitlines():
        k, mask, stab, covering = map(int, line.split())
        if mask in masks:
            catalogue[mask] = (k, stab, covering)
    cases = []
    for mask, label in zip(masks, ["easy", "intermediate"]):
        k, stab, covering = catalogue[mask]
        if k != 12 or covering != 1 or mask.bit_count() != 12:
            raise ValueError("Selected support is not a covering support13 orbit")
        T = [x for x in range(1, 32) if mask >> x & 1]
        S = [0] + T
        if {a ^ b for a in S for b in S} != set(range(32)):
            raise ValueError("Support does not cover")
        old = historical(mask)
        cases.append({
            "mask": mask, "support": S, "stabilizer_order": stab,
            "selection_label": label,
            "historical_fixed_maximum_trials": old,
            "selection_rule": "Easy and intermediate relative to imported fixed-maximum exploration; the planned hard third case was deferred to prioritize the main frontier.",
        })
    return cases


def publish_file(source, target):
    # Finished immutable source only.  Some mounted workspaces report equal
    # st_dev yet reject rename with EXDEV; copy and verify in that situation.
    try:
        os.replace(source, target)
    except OSError as error:
        if error.errno != errno.EXDEV:
            raise
        expected = A.sha(source)
        shutil.copyfile(source, target)
        if A.sha(target) != expected:
            raise ValueError("Completed-file publication changed bytes")
        source.unlink()


def run_one(case, strengthened, SPEC, M, SUBS, provenance):
    mode = "maximal_cosets" if strengthened else "baseline"
    case_id = f"s13_T{case['mask']}_m2_18_{mode}"
    destination = HERE / "cases" / case_id
    if destination.exists():
        raise FileExistsError("Refusing to overwrite a completed trial: " + str(destination))
    record = {
        "case_id": case_id, "status": "STARTING", "mode": mode,
        "source_mask": case["mask"], "support": case["support"],
        "distinguished_hub": 0, "maximum_interval": [2, 18],
        "total_budget": 93, "ring_scope": "common_relaxation_both_rings",
        "semantic_input_hashes": provenance, "solver_wall_timeout": LIMIT,
        "encoder_soundness_formalized": False,
        "selection_label": case["selection_label"],
    }
    started = time.monotonic()
    if shutil.disk_usage("/tmp").free < 1024**3:
        record.update(status="RESOURCE_GUARD_NOT_RUN", reason="Less than1GiB free disk")
        return record
    with tempfile.TemporaryDirectory(prefix="kakeya_s13_trial_", dir="/tmp") as td:
        work = Path(td)
        cnf, proof = work / "input.cnf", work / "proof.lrat"
        T = [x for x in case["support"] if x]
        if strengthened:
            f = E.encode(T, 18, SPEC, M, SUBS, outtotal=93, hub_min=2, strengthen=True)
        else:
            f = B.encode(T, 18, SPEC, M, SUBS, outtotal=93, hub_min=2)
        E.write_dimacs(f, cnf)
        record.update(
            variables=f.n, clauses=len(f.cl), cnf_sha256=A.sha(cnf),
            cnf_bytes=cnf.stat().st_size, encode_seconds=round(time.monotonic()-started, 6),
        )
        del f
        gc.collect()
        command = [str(SOLVER), "--lrat", "--no-binary", "--no-witness",
                   "-t", str(LIMIT), str(cnf), str(proof)]
        solve_started = time.monotonic()
        timed_out = False
        with (work/"solver.stdout.txt").open("wb") as stdout, (work/"solver.stderr.txt").open("wb") as stderr:
            try:
                result = subprocess.run(command, stdout=stdout, stderr=stderr, timeout=LIMIT)
                code = result.returncode
            except subprocess.TimeoutExpired:
                code = None
                timed_out = True
        record.update(
            solver_returncode=code, timed_out=timed_out,
            solver_command=command, solve_seconds=round(time.monotonic()-solve_started, 6),
        )
        if proof.exists():
            record.update(lrat_bytes=proof.stat().st_size, lrat_sha256=A.sha(proof))
        unsat = code == 20 and "s UNSATISFIABLE" in (work/"solver.stdout.txt").read_text()
        accepted = False
        if unsat:
            check = A.run_checker(
                [CHECKER, "--CML_HEAP_SIZE=1024", "--CML_STACK_SIZE=256", cnf, proof],
                work, "cake_lpr", 180, "s VERIFIED UNSAT", True,
            )
            unchanged = A.sha(cnf) == record["cnf_sha256"] and A.sha(proof) == record["lrat_sha256"]
            accepted = check["accepted"] and unchanged
            record.update(cake_lpr=check, inputs_unchanged=unchanged)
            record["status"] = "PASS_CNF_UNSAT_VIA_CAKEML_LRAT" if accepted else "CHECK_FAILED"
        else:
            record["status"] = "TIMEOUT_UNCERTIFIED" if timed_out else "UNACCEPTED_SOLVER_RESULT"
        # Only completed files are published, after solver and checker have stopped.
        destination.mkdir(parents=True)
        stored = {}
        for raw in [cnf] + ([proof] if accepted else []):
            expected = record["cnf_sha256"] if raw == cnf else record["lrat_sha256"]
            meta = C.compress_verified(raw, expected, preset=1, remove_raw=True)
            compressed = Path(str(raw)+".xz")
            target = destination/compressed.name
            publish_file(compressed, target)
            if C.logical_sha(destination/raw.name, prefer_compressed=True) != expected:
                raise ValueError("Published file changed")
            meta.update(logical_path=str((destination/raw.name).relative_to(HERE)),
                        compressed_path=str(target.relative_to(HERE)))
            stored[raw.name] = meta
        record["storage"] = stored
        record["unfinished_lrat_retained"] = False
        if not accepted and proof.exists():
            record["discarded_unaccepted_lrat"] = {
                "bytes": record.get("lrat_bytes", 0),
                "sha256": record.get("lrat_sha256"),
                "reason": "No accepted refutation; partial or unaccepted proof discarded.",
            }
            proof.unlink()
        for name in ["solver.stdout.txt","solver.stderr.txt","cake_lpr.stdout.txt","cake_lpr.stderr.txt"]:
            source = work/name
            if source.exists():
                publish_file(source,destination/name)
        record["seconds"] = round(time.monotonic()-started,6)
        dump(destination/"CASE_RECEIPT.json",record)
    return record


def main():
    HERE.mkdir(parents=True,exist_ok=True)
    if A.sha(HERE.parent/"encoder_audit/encode_maximal_cosets.py") != "7e3225d4b5d0ff50d4578fc7d1d4a924d122449ce4e87f00520bac0ee0016102":
        raise ValueError("Strengthened encoder changed since its audited tests")
    if A.sha(HERE.parent/"joint_maxima/encode_joint_maxima.py") != "776af5c5699f5e153990cdfb8b0897d690202c9895dd95134eec9b8df295feba":
        raise ValueError("Baseline encoder changed")
    checker_build = json.loads((HERE.parent/"joint_maxima/BUILD_RECEIPT.json").read_text())
    if A.sha(CHECKER) != checker_build["build"]["checkers"]["cake_lpr"]["binary_sha256"]:
        raise ValueError("Pinned checker binary mismatch")
    pins=A.verify_sources()
    provenance={str(p.relative_to(ROOT)):A.sha(p) for p in [
        HERE.parent/"encoder_audit/encode_maximal_cosets.py",
        HERE.parent/"joint_maxima/encode_joint_maxima.py",
        IMPORTED/"data/spec32.csv",IMPORTED/"data/Mtable.txt",
        IMPORTED/"data/orbits_all.txt",
    ]}
    cases=selected_cases()
    dump(HERE/"CASE_SELECTION.json",cases)
    dump(HERE/"TOOL_PROVENANCE.json",{
        "solver_sha256":A.sha(SOLVER),"checker_sha256":A.sha(CHECKER),
        "checker_build_receipt":"../joint_maxima/BUILD_RECEIPT.json",
        "checker_build_receipt_sha256":A.sha(HERE.parent/"joint_maxima/BUILD_RECEIPT.json"),
        "pins":pins,"semantic_input_hashes":provenance,
    })
    SPEC=E.load_spectra(IMPORTED/"data/spec32.csv")
    M=E.load_M(IMPORTED/"data/Mtable.txt")
    SUBS=E.all_subspaces()
    report={
        "status":"RUNNING","scope":"Two selected support13 marked cases; maximum interval2..18; paired60s diagnostics, not a complete support sweep.",
        "methodological_limit":"Single runs in a shared environment; solver times do not establish general speedups.",
        "requested_trials":4,"cases":[],
    }
    for index,case in enumerate(cases):
        # Alternate order to avoid always giving one formula the same sequence position.
        for strengthened in ([False,True] if index%2==0 else [True,False]):
            result=run_one(case,strengthened,SPEC,M,SUBS,provenance)
            report["cases"].append(result)
            dump(HERE/"BENCHMARK_RECEIPT.json",report)
            print(json.dumps({k:result.get(k) for k in ["case_id","status","solve_seconds","lrat_bytes","seconds"]}),flush=True)
    report["status"]="COMPLETED_BOUNDED_DIAGNOSTIC"
    report["accepted_trials"]=sum(r["status"]=="PASS_CNF_UNSAT_VIA_CAKEML_LRAT" for r in report["cases"])
    report["distinct_marked_support_exclusions"]=len({r["source_mask"] for r in report["cases"] if r["status"]=="PASS_CNF_UNSAT_VIA_CAKEML_LRAT"})
    dump(HERE/"BENCHMARK_RECEIPT.json",report)
    print(json.dumps({k:report[k] for k in ["status","accepted_trials","distinct_marked_support_exclusions"]}),flush=True)


if __name__=="__main__":
    main()
