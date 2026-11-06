"""Focused acceptance/rejection controls for the untrusted LRAT core producer."""
from pathlib import Path
import importlib.util
import json
import os
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location(
    "core_control_audit", ROOT / "research_round5/proof_audit/audit_certificates.py")
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)


def main():
    if not (HERE / "bin/lrat_core").is_file():
        (HERE / "bin").mkdir(exist_ok=True)
        subprocess.run(["g++", "-O3", "-std=c++17", str(HERE / "lrat_core.cpp"),
                        "-o", str(HERE / "bin/lrat_core")], check=True)
    if not (HERE / "bin/cake_lpr").is_file():
        A.verify_sources()
        A.build_checkers(HERE / "bin", HERE / "control_build_logs")
    log = HERE / "control_logs"
    log.mkdir(exist_ok=True)
    results = []
    with tempfile.TemporaryDirectory(prefix="kakeya_core_controls_", dir="/tmp") as temporary:
        work = Path(temporary)
        cnf = ROOT / "research_round5/proof_audit/controls/rat_example.cnf"
        proof = ROOT / "research_round5/proof_audit/control_audit/genuine_rat/converted.lrat"
        core = work / "rat_core.lrat"
        trimmed = subprocess.run([HERE / "bin/lrat_core", cnf, proof, core],
                                 capture_output=True, text=True, check=True)
        stats = json.loads(trimmed.stdout)
        if stats["retained_negative_hints"] != 3:
            raise ValueError("Expected three genuine RAT target references")
        accepted = A.run_checker(
            [HERE / "bin/cake_lpr", "--CML_HEAP_SIZE=64", "--CML_STACK_SIZE=64", cnf, core],
            log, "genuine_rat_core", 30, "s VERIFIED UNSAT", True)
        if not accepted["accepted"]:
            raise ValueError("Genuine RAT core rejected")
        results.append({"control": "genuine_rat_core", "expected": "ACCEPT",
                        "status": "PASS", "trim": stats, "cake_lpr": accepted})

        sat = work / "satisfiable.cnf"
        sat.write_text("p cnf 1 1\n1 0\n")
        bogus = work / "bogus.lrat"
        bogus.write_text("2 0 0\n")
        candidate = work / "bogus_core.lrat"
        subprocess.run([HERE / "bin/lrat_core", sat, bogus, candidate],
                       capture_output=True, text=True, check=True)
        rejected = A.run_checker(
            [HERE / "bin/cake_lpr", "--CML_HEAP_SIZE=64", "--CML_STACK_SIZE=64", sat, candidate],
            log, "bogus_core", 30, "s VERIFIED UNSAT", True)
        if rejected["accepted"]:
            raise ValueError("Bogus core accepted")
        results.append({"control": "satisfiable_formula_bogus_empty_clause",
                        "expected": "REJECT", "status": "PASS", "cake_lpr": rejected})

        original_cnf_hash = A.sha(sat)
        original_proof_hash = A.sha(bogus)
        aliases = [(sat, "CNF_direct"), (bogus, "proof_direct")]
        for source, name in ((sat, "CNF_hardlink"), (bogus, "proof_hardlink")):
            alias = work / name
            os.link(source, alias)
            aliases.append((alias, name))
        for alias, name in aliases:
            run = subprocess.run([HERE / "bin/lrat_core", sat, bogus, alias],
                                 capture_output=True, text=True)
            if run.returncode == 0 or A.sha(sat) != original_cnf_hash or A.sha(bogus) != original_proof_hash:
                raise ValueError("Original-input alias was not safely rejected")
            results.append({"control": name, "expected": "REJECT_WITH_INPUTS_UNCHANGED",
                            "status": "PASS", "stderr": run.stderr})
    receipt = {"status": "PASS_ALL_CORE_CONTROLS", "controls": results,
               "trimmer_correctness_formally_proved": False,
               "acceptance_authority": "Pinned CakeML checker, not the trimmer"}
    (HERE / "CORE_CONTROL_REPLAY.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "controls": len(results)}, indent=2))


if __name__ == "__main__":
    main()
