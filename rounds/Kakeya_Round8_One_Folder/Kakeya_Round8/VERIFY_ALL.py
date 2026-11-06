"""Replay the round-2 finite certificates from a freshly unpacked archive.

Run with ordinary Python 3 (not -O). A C++17 g++ compiler is required for the
two independently authored census enumerators. No third-party Python package
or optimizer is used by this verification path.
"""
from pathlib import Path
import hashlib
import json
import os
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
if sys.flags.optimize:
    raise SystemExit("Assertions are required: run Python without -O/PYTHONOPTIMIZE.")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


manifest_path = ROOT / "MANIFEST.json"
manifest = json.loads(manifest_path.read_text())
for item in manifest["files"]:
    path = ROOT / item["path"]
    if not path.is_file() or path.stat().st_size != item["bytes"] or sha(path) != item["sha256"]:
        raise SystemExit("Payload hash mismatch: " + item["path"])
print(f"Initial payload hashes PASS: {len(manifest['files'])} files", flush=True)

STEPS = [
    ("independent_pair_and_block_censuses", "research_round2/root/verify_censuses.py"),
    ("m19_full_spectrum_duals", "research_round2/root/verify_spectrum_stage.py"),
    ("m19_outside_support_budget", "research_round2/root/verify_outside_support_stage.py"),
    ("m19_paired_block_duals", "research_round2/root/verify_block_stage.py"),
    ("m19_hub_inclusive_duals", "research_round2/root/verify_hub_stage.py"),
    ("m19_independent_degrees_and_duals", "research_round2/root/verify_degree_stage.py"),
    ("small_residue_geometry_controls", "research_round2/root/check_small_support_geometry.py"),
    ("middle_exact_spectrum_duals", "research_round2/middle/verify_global_spectrum_cuts.py"),
    ("middle_complete_support_reduction", "research_round2/middle/verify_middle_high_support_completion.py"),
    ("maximum11_complete_support_reduction", "research_round2/structural/m11_support/verify_cap11_support_through18.py"),
    ("halfspace_energy_controls_through18", "research_round2/middle/halfspace_energy_controls.py"),
    ("halfspace_energy_controls_through20", "research_round2/middle/stability_halfspace20_controls.py"),
    ("ten_heavy_deletion_controls", "research_round2/m11_extension/verify_ten_heavy_incidence.py"),
    ("refresh_m19_accounting", "research_round2/geometric/build_m19_round2_manifest.py"),
    ("refresh_consolidated_frontier", "research_round2/root/build_round2_frontier.py"),
]

logs = ROOT / "verification_logs"
logs.mkdir(exist_ok=True)
receipt = {
    "status": "RUNNING",
    "scope": "Round-2 finite censuses, exact integer certificates, complete partition reductions, and accounting. Analytic proofs are supplied for mathematical review; this is not formal proof-assistant verification. Inherited claims remain anchored to the prior checkpoint.",
    "initial_manifest_sha256": sha(manifest_path),
    "initial_payload_files_verified": len(manifest["files"]),
    "python_version": platform.python_version(),
    "steps": [],
}
receipt_path = ROOT / "VERIFICATION_RECEIPT.json"
started = time.monotonic()
env = dict(os.environ)
env.pop("PYTHONOPTIMIZE", None)
env["PYTHONDONTWRITEBYTECODE"] = "1"
for index, (name, relative_path) in enumerate(STEPS, 1):
    logfile = logs / (name + ".txt")
    step_started = time.monotonic()
    print(f"[{index}/{len(STEPS)}] {name}", flush=True)
    with logfile.open("w") as log:
        result = subprocess.run([sys.executable, str(ROOT / relative_path)], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
    record = {"name": name, "script": relative_path, "status": "PASS" if result.returncode == 0 else "FAIL", "returncode": result.returncode, "seconds": round(time.monotonic() - step_started, 3), "log": str(logfile.relative_to(ROOT)), "log_sha256": sha(logfile)}
    receipt["steps"].append(record)
    receipt["seconds"] = round(time.monotonic() - started, 3)
    if result.returncode:
        receipt["status"] = "FAIL"
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
        print(logfile.read_text()[-12000:], file=sys.stderr)
        raise SystemExit("Verification failed: " + name)
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"  PASS ({record['seconds']} seconds)", flush=True)

frontier = json.loads((ROOT / "Kakeya_Research_Frontier_Round2.json").read_text())
receipt["final_frontier"] = {
    "unrestricted_dimension5_theorem": frontier["unrestricted_dimension5_theorem"],
    "maximum11_remaining_affine_support_classes": frontier["dimension5_strata"]["maximum11"]["remaining_affine_support_classes"],
    "maximum12_through18_support_upper_bound": frontier["dimension5_strata"]["maximum12_through18"]["new_necessary_pair_active_support_upper_bound"],
    "maximum19_new_profile_exclusions": frontier["dimension5_strata"]["maximum19"]["new_disjoint_whole_profile_exclusions"],
    "maximum19_remaining_selected_profiles": frontier["dimension5_strata"]["maximum19"]["remaining_selected_profiles"],
}
receipt["status"] = "PASS_ALL_ROUND2_REPLAY_STEPS"
receipt["seconds"] = round(time.monotonic() - started, 3)
receipt["regenerated_frontier_sha256"] = sha(ROOT / "Kakeya_Research_Frontier_Round2.json")
receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({"status": receipt["status"], "seconds": receipt["seconds"], "frontier": receipt["final_frontier"]}, indent=2), flush=True)
