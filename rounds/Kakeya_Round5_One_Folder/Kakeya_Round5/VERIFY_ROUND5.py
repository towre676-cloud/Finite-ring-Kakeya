"""Portable exact Round5 replay. Python standard library and a C compiler suffice.

The optional Lean compilation requires the separately pinned Lean/Mathlib
installation. Discovery solvers, network access and prior SAT solvers are not
required for the default replay. Run from any working directory.
"""
from hashlib import sha256
from pathlib import Path
import argparse
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
STAGES = [
    ('complete_38_marked_cases', ['research_round5/encoding_bridge/verify_marked_cover.py']),
    ('nine_residue_geometry', ['research_round5/nine_geometry/verify_nine_geometry.py']),
    ('multiple_price_certificates', ['research_round5/middle_duals/verify_multi_prices.py', '--tag', 'full']),
    ('analytic_240_exclusions', ['research_round5/middle_duals/verify_small_light_analytic.py']),
    ('separate_geometry_table', ['research_round5/middle_duals/verify_nine_degree_types.py']),
    ('standalone_support10_classification', ['research_round5/support10_roles/verify_support10_structure.py']),
    ('historical_641_role_exclusions', ['research_round5/support10_roles/verify_support10_roles.py']),
    ('full_support10_weight_crosscheck', ['research_round5/support10_roles/FULL_S10_verify.py']),
    ('support10_common_neighbours', ['research_round5/support10_roles/verify_support10_mantel_obstruction.py']),
    ('support10_rigidity_applications', ['research_round5/support10_roles/verify_support10_rigidity.py']),
    ('verified_checker_pipeline', ['research_round5/proof_audit/verify_pipeline.py']),
    ('exact_merged_frontier', ['research_round5/merge_round5.py']),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mathlib', type=Path)
    parser.add_argument('--lean-bin', type=Path)
    args = parser.parse_args()
    if sys.flags.optimize:
        raise SystemExit('Do not disable assertions.')
    if bool(args.mathlib) != bool(args.lean_bin):
        raise SystemExit('Provide both --mathlib and --lean-bin, or neither.')
    stages = list(STAGES)
    if args.mathlib:
        stages.append(('pinned_Lean_semantic_bridge', [
            'research_round5/encoding_bridge/verify_carry_lean.py', '--mathlib', str(args.mathlib.resolve()),
            '--lean-bin', str(args.lean_bin.resolve())]))
    started = time.monotonic()
    records = []
    output = ROOT / 'research_round5/ROUND5_PORTABLE_REPLAY.json'
    for index, (name, command) in enumerate(stages, 1):
        print(f'[{index}/{len(stages)}] {name}', flush=True)
        t = time.monotonic()
        result = subprocess.run([sys.executable] + command, cwd=ROOT,
                                capture_output=True, text=True)
        record = {'stage': name, 'returncode': result.returncode,
                  'seconds': round(time.monotonic()-t, 6),
                  'stdout_sha256': sha256(result.stdout.encode()).hexdigest(),
                  'stderr_sha256': sha256(result.stderr.encode()).hexdigest()}
        records.append(record)
        if result.returncode:
            print(result.stdout)
            print(result.stderr, file=sys.stderr)
            output.write_text(json.dumps({'status':'FAIL', 'stages':records}, indent=2)+'\n')
            raise SystemExit(result.returncode)
    receipt = {'status':'PASS_ALL_ROUND5_FINITE_REPLAYS', 'stages':records,
               'completed_stages':len(records), 'Lean_recompiled_in_this_run':bool(args.mathlib),
               'seconds':round(time.monotonic()-started, 6),
               'new_Claude_proof_files_checked':0,
               'scope':'Exact finite replay plus mandatory CakeML acceptance of four archived examples. Analytic theorem arguments remain explicit hand proofs. New Claude A-E/CNF/DRAT artifacts were unavailable.'}
    output.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('status','completed_stages','Lean_recompiled_in_this_run','seconds','new_Claude_proof_files_checked')},indent=2))


if __name__ == '__main__':
    main()
