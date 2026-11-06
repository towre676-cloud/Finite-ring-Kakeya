#!/usr/bin/env python3
"""Regenerate exact selected CNFs and replay the two accepted S13 LRAT files."""
from pathlib import Path
import gc
import importlib.util
import json
import tempfile
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
IMPORTED=HERE.parent/"imported_claude_round4"


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    out=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(out)
    return out


A=module("s13_replay_audit",ROOT/"research_round5/proof_audit/audit_certificates.py")
C=module("s13_replay_storage",HERE.parent/"certificate_storage.py")
E=module("s13_replay_strong",HERE.parent/"encoder_audit/encode_maximal_cosets.py")
B=module("s13_replay_baseline",HERE.parent/"joint_maxima/encode_joint_maxima.py")


def main():
    started=time.monotonic()
    report=json.loads((HERE/"BENCHMARK_RECEIPT.json").read_text())
    if report["status"]!="COMPLETED_BOUNDED_DIAGNOSTIC":
        raise ValueError("Diagnostic collection is incomplete")
    expected={(mask,mode) for mask in [37848950,1022358] for mode in ["baseline","maximal_cosets"]}
    actual={(r["source_mask"],r["mode"]) for r in report["cases"]}
    if len(report["cases"])!=4 or actual!=expected:
        raise ValueError("Unexpected diagnostic inventory")
    SPEC=E.load_spectra(IMPORTED/"data/spec32.csv")
    M=E.load_M(IMPORTED/"data/Mtable.txt")
    SUBS=E.all_subspaces()
    replay={"status":"RUNNING","cases":[],"accepted_certificates":0,"uncertified_timeouts":0}
    A.verify_sources()
    with tempfile.TemporaryDirectory(prefix="kakeya_s13_replay_",dir="/tmp") as td:
        temporary=Path(td)
        binaries,build=A.build_checkers(temporary/"bin",temporary/"build_logs")
        replay["checker_build"]=build
        for row in report["cases"]:
            folder=HERE/"cases"/row["case_id"]
            saved=json.loads((folder/"CASE_RECEIPT.json").read_text())
            if saved!=row:
                raise ValueError("Per-case receipt differs from collection")
            for rel,digest in row["semantic_input_hashes"].items():
                if A.sha(ROOT/rel)!=digest:
                    raise ValueError("Changed semantic source: "+rel)
            if row["maximum_interval"]!=[2,18] or row["total_budget"]!=93:
                raise ValueError("Wrong domain")
            T=[x for x in range(1,32) if row["source_mask"]>>x&1]
            if row["support"]!=[0]+T or len(T)!=12:
                raise ValueError("Support metadata mismatch")
            if {a^b for a in row["support"] for b in row["support"]}!=set(range(32)):
                raise ValueError("Support is not covering")
            local=temporary/row["case_id"]
            local.mkdir()
            if row["mode"]=="maximal_cosets":
                f=E.encode(T,18,SPEC,M,SUBS,outtotal=93,hub_min=2,strengthen=True)
            else:
                f=B.encode(T,18,SPEC,M,SUBS,outtotal=93,hub_min=2)
            cnf=local/"input.cnf"
            E.write_dimacs(f,cnf)
            if f.n!=row["variables"] or len(f.cl)!=row["clauses"]:
                raise ValueError("Formula dimensions changed")
            del f
            gc.collect()
            if A.sha(cnf)!=row["cnf_sha256"]:
                raise ValueError("Formula regeneration is not byte identical")
            if C.logical_sha(folder/"input.cnf",prefer_compressed=True)!=row["cnf_sha256"]:
                raise ValueError("Stored formula changed")
            outcome={"case_id":row["case_id"],"formula_regeneration":"BYTE_IDENTICAL","cnf_sha256":row["cnf_sha256"]}
            if row["status"]=="PASS_CNF_UNSAT_VIA_CAKEML_LRAT":
                with C.materialized(folder/"proof.lrat",row["lrat_sha256"],directory=td,prefer_compressed=True) as lrat:
                    check=A.run_checker(
                        [binaries["cake_lpr"],"--CML_HEAP_SIZE=1024","--CML_STACK_SIZE=256",cnf,lrat],
                        local,"cake_lpr",180,"s VERIFIED UNSAT",True,
                    )
                    if not check["accepted"] or A.sha(cnf)!=row["cnf_sha256"] or A.sha(lrat)!=row["lrat_sha256"]:
                        raise ValueError("Accepted LRAT did not replay")
                outcome.update(status="PASS_CNF_UNSAT_VIA_CAKEML_LRAT",cake_lpr=check)
                replay["accepted_certificates"]+=1
            elif row["status"]=="TIMEOUT_UNCERTIFIED":
                if (folder/"proof.lrat").exists() or (folder/"proof.lrat.xz").exists():
                    raise ValueError("Unexpected purported timeout certificate")
                outcome["status"]="UNCERTIFIED_TIMEOUT_REMAINS_UNCERTIFIED"
                replay["uncertified_timeouts"]+=1
            else:
                raise ValueError("Unexpected diagnostic status")
            replay["cases"].append(outcome)
    if replay["accepted_certificates"]!=2 or replay["uncertified_timeouts"]!=2:
        raise ValueError("Unexpected replay totals")
    replay.update(
        status="PASS",
        distinct_marked_support_exclusions=1,
        scope="One selected support13 marked class at maximum2..18; both baseline and strengthened certificates accepted. The second selected class remains uncertified.",
        seconds=round(time.monotonic()-started,6),
        encoder_formally_verified=False,
    )
    (HERE/"S13_DIAGNOSTIC_REPLAY.json").write_text(json.dumps(replay,indent=2)+"\n")
    print(json.dumps({k:replay[k] for k in ["status","accepted_certificates","uncertified_timeouts","distinct_marked_support_exclusions","seconds"]},indent=2))


if __name__=="__main__":
    main()
