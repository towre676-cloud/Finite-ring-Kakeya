"""Portable Round6 replay: finite data, exact CNF binding, and checked proofs.

No SAT solver or network is required. The full default replays all76 main
refutations and both additional support13 refutations. --quick samples the
two main certificate collections and explicitly does not claim full replay.
Run from any working directory. Python3, gcc/g++, Linuxx86_64 are required.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quick', action='store_true')
    parser.add_argument('--jobs', type=int, choices=[1, 2], default=2)
    parser.add_argument('--wait-for-compact-production', action='store_true',
                        help='During checkpoint assembly, wait for the concurrent joint proof producer before its replay stage.')
    args = parser.parse_args()
    if sys.flags.optimize:
        raise SystemExit('Run without Python -O; inherited finite checks use assertions.')
    stages = [
        ('inherited_round5_finite_components', ['VERIFY_ROUND5.py']),
        ('imported_data_and_complete_catalogue', ['research_round6/catalogue_audit/verify_imported_data.py']),
        ('encoder_auxiliaries_and_fibre_lemmas', ['research_round6/encoder_audit/verify_encoder_lemmas.py']),
        ('optional_coset_encoder_soundness_controls', ['research_round6/encoder_audit/verify_maximal_coset_encoder.py']),
        ('unrestricted_support11_subspace_geometry', ['research_round6/structural_progress/verify_support11_subspaces.py']),
        ('additional_local_graph_restrictions', ['research_round6/structural_progress/verify_additional_local_cuts.py']),
        ('dense_fibre_complement_geometry', ['research_round6/next_frontier/verify_dense_complements.py']),
        ('maximum19_exact_formulas_and_compact_certificates',
         ['research_round6/compact_m19/verify_compact_m19.py', '--jobs', str(args.jobs)]
         + (['--quick'] if args.quick else [])),
        ('joint_maxima_exact_formulas_and_compact_certificates',
         ['research_round6/compact_certificates/verify_compact_certificates.py', '--jobs', str(args.jobs)]
         + (['--quick'] if args.quick else [])),
        ('support13_completed_certificates_and_timeout_accounting',
         ['research_round6/strengthened_trials/verify_strengthened_trials.py']),
        ('exact_frontier_subtraction', ['research_round6/merge_round6.py']),
    ]
    output = ROOT / 'research_round6/ROUND6_PORTABLE_REPLAY.json'
    logs = ROOT / 'research_round6/replay_logs'
    logs.mkdir(exist_ok=True)
    started = time.monotonic()
    receipt = {'status': 'RUNNING', 'quick': args.quick, 'stages': [],
               'full_main_certificate_replay': not args.quick,
               'main_formulas_to_replay': 4 if args.quick else 76,
               'additional_support13_formulas_to_replay': 2,
               'encoder_formally_verified': False, 'new_SAT_search_performed': False,
               'scope': 'Proof replay establishes exact CNF unsatisfiability. One-way semantics and analytic proofs are separate written arguments.'}
    output.write_text(json.dumps(receipt, indent=2) + '\n')
    for number, (name, command) in enumerate(stages, 1):
        if args.wait_for_compact_production and name == 'joint_maxima_exact_formulas_and_compact_certificates':
            manifest = ROOT / 'research_round6/compact_certificates/COMPACT_CERTIFICATE_MANIFEST.json'
            deadline = time.monotonic() + 1800
            announced = False
            while not manifest.is_file():
                if not announced:
                    print('Waiting for the complete joint compact manifest before proof replay.', flush=True)
                    announced = True
                if time.monotonic() >= deadline:
                    receipt.update(status='FAIL', error='Joint compact production did not publish its complete manifest in time.')
                    output.write_text(json.dumps(receipt, indent=2) + '\n')
                    raise SystemExit(receipt['error'])
                time.sleep(5)
        print(f'[{number}/{len(stages)}] {name}', flush=True)
        t = time.monotonic()
        stdout_path, stderr_path = logs / (name + '.stdout.txt'), logs / (name + '.stderr.txt')
        with stdout_path.open('wb') as stdout, stderr_path.open('wb') as stderr:
            result = subprocess.run([sys.executable] + command, cwd=ROOT,
                                    stdout=stdout, stderr=stderr)
        row = {'stage': name, 'returncode': result.returncode,
               'seconds': round(time.monotonic() - t, 6),
               'stdout_sha256': hashlib.sha256(stdout_path.read_bytes()).hexdigest(),
               'stderr_sha256': hashlib.sha256(stderr_path.read_bytes()).hexdigest()}
        receipt['stages'].append(row)
        receipt['seconds'] = round(time.monotonic() - started, 6)
        if result.returncode:
            receipt['status'] = 'FAIL'
            output.write_text(json.dumps(receipt, indent=2) + '\n')
            print(stdout_path.read_text(errors='replace'))
            print(stderr_path.read_text(errors='replace'), file=sys.stderr)
            raise SystemExit(result.returncode)
        output.write_text(json.dumps(receipt, indent=2) + '\n')
        print(f'  PASS ({row["seconds"]:.2f}s)', flush=True)
    receipt.update(status='PASS_QUICK_ROUND6_REPLAY_MAIN_CERTIFICATE_SAMPLES_ONLY'
                   if args.quick else 'PASS_ALL_ROUND6_FINITE_AND_CERTIFICATE_REPLAYS',
                   completed_stages=len(stages), seconds=round(time.monotonic() - started, 6))
    output.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({k: receipt[k] for k in ['status', 'completed_stages',
                                             'full_main_certificate_replay', 'seconds']}, indent=2))


if __name__ == '__main__':
    main()
