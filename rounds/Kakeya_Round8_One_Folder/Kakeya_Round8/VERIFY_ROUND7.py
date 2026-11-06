#!/usr/bin/env python3
"""Portable Round7 replay; no SAT solver or network is needed.

Default: all new certificates, finite lemmas and exact frontier accounting.
Inherited Round6 proof collections are sampled unless --inherited-full is set.
--quick samples the new S13/n4 collections and does not claim a full new replay.
--reuse-checked-certificates binds already completed full replays to current
bytes instead of executing those checkers again. It is explicit in the receipt.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
HERE = ROOT / "research_round7"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--jobs", type=int, choices=(1, 2), default=2)
    parser.add_argument("--inherited-full", action="store_true")
    parser.add_argument("--reuse-checked-certificates", action="store_true")
    parser.add_argument("--mathlib")
    parser.add_argument("--lean-bin")
    args = parser.parse_args()
    if sys.flags.optimize:
        raise SystemExit("Run without Python -O; inherited finite checks use assertions.")
    if bool(args.mathlib) != bool(args.lean_bin):
        raise SystemExit("Supply both --mathlib and --lean-bin for fresh Lean compilation.")
    if args.quick and args.reuse_checked_certificates:
        raise SystemExit("Choose a fresh quick sample or bound full receipts, not both.")
    stages = [
        ("inherited_round6", ["VERIFY_ROUND6.py", "--jobs", str(args.jobs)] + ([] if args.inherited_full else ["--quick"])),
        ("dimension3_elementary_proof_checks", ["research_round7/dimension3/verify_dimension3_hand_proof.py"]),
        ("literal_ring_encoder_and_shear_controls", ["research_round7/exact_ring/verify_exact_ring.py"]),
        ("dense_fibre_direction_types", ["research_round7/dense_encoder/verify_dense_encoder.py"]),
        ("shared_span_capacity", ["research_round7/span_capacity/verify_span_capacity.py"]),
        ("three_direction_plane_compatibility", ["research_round7/geometry/verify_plane_cuts.py"]),
        ("all_support13_largest_vertex_transports", ["research_round7/geometry/replay_support13_markings.py"]),
        ("eight_heavy_fibres", ["research_round7/geometry/verify_heavy_fibre_cut.py"]),
        ("eight_heavy_corollaries", ["research_round7/geometry/verify_eight_heavy_corollaries.py"]),
        ("difference8_bound", ["research_round7/dense_encoder/difference8_bound.py"]),
        ("difference9_bound", ["research_round7/dense_encoder/difference9_bound.py"]),
        ("four_pair_capacity", ["research_round7/support13/four_pair_cut/verify_four_pair_cut.py"]),
        ("four_pair_encoding", ["research_round7/support13/four_pair_cut/verify_four_pair_encoder.py"]),
        ("four_pair_timeout_accounting", ["research_round7/support13/four_pair_cut/verify_four_pair_trials.py"]),
        ("exact_shape_relaxation", ["research_round7/exact_shape/verify_exact_shape.py"]),
        ("exact_shape_trial_accounting", ["research_round7/exact_shape/verify_trials.py"]),
        ("proof_prefixed_rup_controls", ["research_round7/support13/verify_rup_unit_controls.py", "--replay"]),
        ("support13_coverage_negative_controls", ["research_round7/support13/verify_collection_controls.py"]),
        ("integer_profile_certificates", ["research_round7/charging/verify_profile_exclusions.py"]),
    ]
    if not args.reuse_checked_certificates:
        stages += [
            ("exact_ring_complete_certificates", ["research_round7/exact_ring/verify_certificates.py"]),
            ("support13_compact_certificates", ["research_round7/compact_support13/verify_compact_support13.py", "--jobs", str(args.jobs)] + (["--quick"] if args.quick else [])),
            ("dimension4_compact_certificates", ["research_round7/dimension4_compact/compact_dimension4.py", "--replay"] + (["--quick"] if args.quick else [])),
        ]
    if args.mathlib:
        for topic in ("shear", "charging"):
            stages.append(("lean_" + topic, [f"research_round7/lean/verify_{topic}_lean.py", "--mathlib", args.mathlib, "--lean-bin", args.lean_bin]))
    stages += [("bind_completed_full_replays", ["research_round7/bind_completed_replays.py"]),
               ("exact_frontier_accounting", ["research_round7/merge_round7.py"])]
    logs = HERE / "integrated_replay_logs"
    logs.mkdir(parents=True, exist_ok=True)
    output = HERE / ("ROUND7_QUICK_REPLAY.json" if args.quick else "ROUND7_PORTABLE_REPLAY.json")
    start = time.monotonic()
    receipt = {"status": "RUNNING", "quick": args.quick, "stages": [],
               "fresh_all_new_proof_replay": not args.quick and not args.reuse_checked_certificates,
               "completed_full_certificate_receipts_reused": args.reuse_checked_certificates,
               "fresh_all_inherited_proofs_replayed": args.inherited_full,
               "fresh_lean_compilation": bool(args.mathlib), "SAT_search_performed": False}
    output.write_text(json.dumps(receipt, indent=2) + "\n")
    for index, (name, command) in enumerate(stages, 1):
        print(f"[{index}/{len(stages)}] {name}", flush=True)
        began = time.monotonic()
        stdout, stderr = logs / (name + ".stdout.txt"), logs / (name + ".stderr.txt")
        with stdout.open("wb") as out, stderr.open("wb") as err:
            process = subprocess.run([sys.executable] + command, cwd=ROOT, stdout=out, stderr=err)
        row = {"stage": name, "returncode": process.returncode, "seconds": round(time.monotonic()-began, 6),
               "stdout_sha256": hashlib.sha256(stdout.read_bytes()).hexdigest(),
               "stderr_sha256": hashlib.sha256(stderr.read_bytes()).hexdigest()}
        receipt["stages"].append(row)
        receipt["seconds"] = round(time.monotonic()-start, 6)
        if process.returncode:
            receipt["status"] = "FAIL"
            output.write_text(json.dumps(receipt, indent=2) + "\n")
            print(stdout.read_text(errors="replace")); print(stderr.read_text(errors="replace"), file=sys.stderr)
            raise SystemExit(process.returncode)
        output.write_text(json.dumps(receipt, indent=2) + "\n")
        print(f"  PASS ({row['seconds']:.2f}s)", flush=True)
    receipt.update(status="PASS_ROUND7_QUICK_SAMPLE_AND_BOUND_FULL_RECEIPTS" if args.quick else
                   "PASS_ROUND7_INTEGRATION_WITH_BOUND_FULL_REPLAY_RECEIPTS" if args.reuse_checked_certificates else
                   "PASS_ROUND7_FRESH_ALL_NEW_CERTIFICATE_REPLAY", completed_stages=len(stages), seconds=round(time.monotonic()-start, 6))
    output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({k: receipt[k] for k in ("status", "completed_stages", "seconds")}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except BaseException as error:
        if isinstance(error, SystemExit) and error.code in (None, 0):
            raise
        destination = HERE / ("ROUND7_QUICK_REPLAY.json" if "--quick" in sys.argv else "ROUND7_PORTABLE_REPLAY.json")
        try:
            receipt = json.loads(destination.read_text()) if destination.exists() else {}
            receipt.update(status="FAIL", error=repr(error))
            destination.write_text(json.dumps(receipt, indent=2) + "\n")
        except OSError:
            pass
        raise
