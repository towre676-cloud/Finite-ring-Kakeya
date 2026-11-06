#!/usr/bin/env python3
"""Replay all new Round8 certificates and finite mathematics, without SAT search.

Inherited Round7 payloads are hash-bound, not re-certified by this script.
--reuse-checked-certificates binds the already completed full new replay;
the default freshly checks all four compact proofs against regenerated CNFs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
HERE = ROOT / "research_round8"


def main():
    # Erase any preceding run's completion flags before parsing can fail.
    (HERE / "ROUND8_PORTABLE_REPLAY.json").write_text(json.dumps({
        "status": "RUNNING", "stages": [],
        "fresh_all_four_new_proofs_requested": False,
        "previous_complete_new_proof_replay_receipt_reuse_requested": False,
        "fresh_all_four_new_proofs_replayed": False,
        "previous_complete_new_proof_replay_receipts_reused": False,
        "inherited_proofs_freshly_replayed": False,
        "SAT_search_performed": False}, indent=2) + "\n")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inherited-archive", type=Path,
                        help="Optional sealed Round7 ZIP for a development workspace; extracted packages need no ZIP.")
    parser.add_argument("--reuse-checked-certificates", action="store_true")
    args = parser.parse_args()
    if sys.flags.optimize:
        raise SystemExit("Run without Python -O; finite checks intentionally use assertions.")
    inherited = ["research_round8/bind_round7.py"]
    if args.inherited_archive:
        inherited += ["--archive", str(args.inherited_archive.resolve())]
    stages = [
        ("immutable_inherited_checkpoint", inherited),
        ("new_strengthened_encoder_controls", ["research_round8/strengthened/verify_strengthened.py"]),
        ("ten_heavy_and_full_difference_cover", ["research_round8/charging/verify_heavy_cover.py"]),
        ("complete_ten_heavy_geometry_and_rank_consequences", ["research_round8/geometry/verify_ten_heavy_ranks.py"]),
        ("elementary_ten_heavy_exclusion", ["research_round8/charging/verify_ten_heavy_elementary.py"]),
        ("independent_actual_fibre_price_enumeration", ["research_round8/geometry/verify_local_rank_prices.py"]),
        ("independent_integer_dual_and_dynamic_program", ["research_round8/root_audit/verify_ten_heavy_dual.py"]),
        ("hyperplane_crossing_pair_controls", ["research_round8/hyperplane/verify_hyperplane_cut.py"]),
        ("Q211_effective_pair_spaces", ["research_round8/geometry/verify_q211_paired_spaces.py"]),
        ("new_missing_direction_incidence_controls", ["research_round8/incidence/verify_incidence_budget.py"]),
        ("sixteen_whole_profile_incidence_exclusions", ["research_round8/incidence/verify_incidence_profile_exclusions.py"]),
        ("extended_128_whole_profile_incidence_exclusions", ["research_round8/incidence/verify_extended_incidence_profiles.py"]),
        ("general_175_whole_profile_incidence_exclusions", ["research_round8/incidence/verify_general_incidence_profiles.py"]),
        ("distinct_heavy_partner_matching_controls", ["research_round8/geometry/verify_matching_threshold.py"]),
        ("matching_745_whole_profile_incidence_exclusions", ["research_round8/incidence/verify_matching_incidence_profiles.py"]),
        ("three_direction_950_cumulative_profile_exclusions", ["research_round8/incidence/verify_three_direction_profiles.py"]),
        ("complete_pending_middle_maximum_queue", ["research_round8/build_next_attack_queue.py"]),
    ]
    if not args.reuse_checked_certificates:
        stages.append(("fresh_all_four_compact_proofs", ["research_round8/strengthened/compact/compact_certificates.py", "--replay"]))
    stages.append(("complete_checked_coverage_and_frontier_accounting", ["research_round8/merge_round8.py"]))
    stages.append(("exact_monograph_source_and_pdf_binding", ["research_round8/verify_monograph_artifact.py"]))
    logs = HERE / "integrated_replay_logs"
    logs.mkdir(parents=True, exist_ok=True)
    output = HERE / "ROUND8_PORTABLE_REPLAY.json"
    started = time.monotonic()
    result = {"status": "RUNNING", "stages": [],
              "fresh_all_four_new_proofs_requested": not args.reuse_checked_certificates,
              "previous_complete_new_proof_replay_receipt_reuse_requested": args.reuse_checked_certificates,
              "fresh_all_four_new_proofs_replayed": False,
              "previous_complete_new_proof_replay_receipts_reused": False,
              "inherited_proofs_freshly_replayed": False, "SAT_search_performed": False}
    output.write_text(json.dumps(result, indent=2) + "\n")
    for number, (name, arguments) in enumerate(stages, 1):
        print(f"[{number}/{len(stages)}] {name}", flush=True)
        began = time.monotonic()
        stdout, stderr = logs / (name + ".stdout.txt"), logs / (name + ".stderr.txt")
        with stdout.open("wb") as out, stderr.open("wb") as err:
            process = subprocess.run([sys.executable] + arguments, cwd=ROOT, stdout=out, stderr=err)
        row = {"stage": name, "returncode": process.returncode,
               "seconds": round(time.monotonic()-began, 6),
               "stdout_sha256": hashlib.sha256(stdout.read_bytes()).hexdigest(),
               "stderr_sha256": hashlib.sha256(stderr.read_bytes()).hexdigest()}
        result["stages"].append(row)
        result["seconds"] = round(time.monotonic()-started, 6)
        if process.returncode:
            result["status"] = "FAIL"
            output.write_text(json.dumps(result, indent=2) + "\n")
            print(stdout.read_text(errors="replace"))
            print(stderr.read_text(errors="replace"), file=sys.stderr)
            raise SystemExit(process.returncode)
        if name == "fresh_all_four_compact_proofs":
            result["fresh_all_four_new_proofs_replayed"] = True
        if name == "complete_checked_coverage_and_frontier_accounting" and args.reuse_checked_certificates:
            result["previous_complete_new_proof_replay_receipts_reused"] = True
        output.write_text(json.dumps(result, indent=2) + "\n")
        print(f"  PASS ({row['seconds']:.2f}s)", flush=True)
    result.update(status="PASS_ROUND8_INTEGRATION_WITH_BOUND_FULL_PROOF_RECEIPTS" if args.reuse_checked_certificates
                  else "PASS_ROUND8_FRESH_ALL_NEW_CERTIFICATES_AND_FINITE_RESULTS",
                  completed_stages=len(stages), seconds=round(time.monotonic()-started, 6))
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "completed_stages", "seconds")}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except BaseException as error:
        if isinstance(error, SystemExit) and error.code in (None, 0):
            raise
        destination = HERE / "ROUND8_PORTABLE_REPLAY.json"
        try:
            old = json.loads(destination.read_text()) if destination.exists() else {}
            old.update(status="FAIL", error=repr(error))
            destination.write_text(json.dumps(old, indent=2) + "\n")
        except OSError:
            pass
        raise
