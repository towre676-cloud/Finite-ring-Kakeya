"""Focused controls; all proof-producing conversions remain untrusted."""
from pathlib import Path
import argparse
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location(
    "compact_control_replay", HERE / "verify_compact_certificates.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)
A = V.A


def preflight_controls(work):
    results = []
    original_here, original_argv = V.HERE, sys.argv
    try:
        V.HERE = work
        receipt = work / "QUICK_REPLAY_RECEIPT.json"
        for arguments, label in ((["--quick"], "missing_manifest"),
                                 (["--quick", "--timeout", "0"], "nonpositive_timeout"),
                                 (["--quick", "--heap-mb", "0"], "nonpositive_heap")):
            receipt.write_text(json.dumps({"status": "PASS_PREVIOUS_RUN"}) + "\n")
            sys.argv = ["verify_compact_certificates.py"] + arguments
            code = V.main()
            after = json.loads(receipt.read_text())
            if code == 0 or after["status"] != "FAIL" or after.get("new_acceptance_claimed") is not False:
                raise ValueError("Stale success survived failed preflight")
            results.append({"control": label, "expected": "FAIL_REPLACES_STALE_PASS", "status": "PASS"})
    finally:
        V.HERE, sys.argv = original_here, original_argv
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="kakeya_compact_controls_", dir="/tmp") as temporary:
        work = Path(temporary)
        results = preflight_controls(work)
        if not args.preflight_only:
            binary = work / "lrat_to_drat"
            subprocess.run(["g++", "-O3", "-std=c++17", str(HERE / "lrat_to_drat.cpp"),
                            "-o", str(binary)], check=True)
            A.verify_sources()
            bins, build = A.build_checkers(work / "bin", work / "build_logs")
            cnf = ROOT / "research_round5/proof_audit/controls/rat_example.cnf"
            lrat = ROOT / "research_round5/proof_audit/control_audit/genuine_rat/converted.lrat"
            proof = work / "genuine.drat"
            converted = subprocess.run([binary, cnf, lrat, proof], capture_output=True, text=True, check=True)
            stats = json.loads(converted.stdout)
            if stats["negative_hint_references"] != 3:
                raise ValueError("Expected three genuine RAT references")
            accepted = A.check_pair(cnf, proof, work / "genuine_audit", bins, 30, 64, 64, False)
            if accepted["status"] != "PASS_CNF_UNSAT_VIA_CAKEML_LRAT":
                raise ValueError("Converted genuine RAT proof rejected")
            results.append({"control": "genuine_rat_conversion", "expected": "ACCEPT",
                            "status": "PASS", "conversion": stats, "audit": accepted})
            sat = work / "satisfiable.cnf"
            sat.write_text("p cnf 1 1\n1 0\n")
            bogus_lrat = work / "bogus.lrat"
            bogus_lrat.write_text("2 0 0\n")
            bogus_drat = work / "bogus.drat"
            subprocess.run([binary, sat, bogus_lrat, bogus_drat], capture_output=True, text=True, check=True)
            rejected = A.check_pair(sat, bogus_drat, work / "bogus_audit", bins, 30, 64, 64, False)
            if rejected["status"] == "PASS_CNF_UNSAT_VIA_CAKEML_LRAT":
                raise ValueError("Invalid converted proof accepted")
            results.append({"control": "satisfiable_formula_bogus_proof", "expected": "REJECT",
                            "status": "PASS", "audit": rejected})
            original_hashes = (A.sha(sat), A.sha(bogus_lrat))
            targets = [(sat, "CNF_direct"), (bogus_lrat, "LRAT_direct")]
            for source, label in ((sat, "CNF_hardlink"), (bogus_lrat, "LRAT_hardlink")):
                target = work / label
                os.link(source, target)
                targets.append((target, label))
            for target, label in targets:
                run = subprocess.run([binary, sat, bogus_lrat, target], capture_output=True, text=True)
                if run.returncode == 0 or (A.sha(sat), A.sha(bogus_lrat)) != original_hashes:
                    raise ValueError("Original input alias was not safely rejected")
                results.append({"control": label, "expected": "REJECT_WITH_INPUTS_UNCHANGED", "status": "PASS"})
        record = {"status": "PASS_PREFLIGHT_CONTROLS_ONLY" if args.preflight_only else "PASS_ALL_COMPACT_CONTROLS",
                  "controls": results, "converter_correctness_formally_proved": False,
                  "acceptance_authority": "Fresh pinned DRAT-trim conversion followed by mandatory CakeML"}
    target = HERE / ("PREFLIGHT_CONTROL_REPLAY.json" if args.preflight_only else "COMPACT_CONTROL_REPLAY.json")
    target.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"status": record["status"], "controls": len(results)}))


if __name__ == "__main__":
    main()
