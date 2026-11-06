"""Replay the Round4 finite certificates from a fresh extraction.

Requirements: Python 3 and a C++17-capable g++ on PATH. No network access,
solver, Lean installation, or additional Python package is needed. The
included Lean receipt records a separate pinned compilation, not a step in
this runner. Use --with-round3 to replay the complete inherited checkpoint
before any Round4 verifier can rewrite one of its intermediate receipts.

Run only against a fresh archive extraction: successful replay regenerates
receipts, so their recorded timings need not retain their initial hashes.
"""

from collections import Counter
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parent
MIDDLE = ROOT / 'research_round4/middle_inventory'
MONOGRAPH = ROOT / 'research_round4/Kakeya_Round4_Monograph.txt'
FRONTIER = ROOT / 'Kakeya_Research_Frontier_Round4.json'
MIDDLE_FRONTIER = MIDDLE / 'MIDDLE_FINAL_FRONTIER_AFTER_PRICING.json'
LEAN_RECEIPT = ROOT / 'research_round4/lean/LEAN_REPLAY_RECEIPT.json'
EXPECTED_COUNT = 275755
EXPECTED_EMPTY = [{'support': 17, 'maximum': 18}]

STEPS = [
    ('input_spectrum_and_nine_residue_replay',
     'research_round4/root/verify_round4_inputs.py'),
    ('inherited_exact_spectrum_certificates',
     'research_round2/middle/verify_global_spectrum_cuts.py'),
    ('twelve_point_energy_independent_enumeration',
     'research_round4/energy12/replay_energy12.py'),
    ('complete_middle_inventory_with_fresh_quota_enumeration',
     'research_round4/middle_inventory/verify_middle_inventory.py'),
    ('separate_joint_cube_inventory_review',
     'research_round4/optimization/review_middle_cube_inventory.py'),
    ('complete_priced_nine_stage',
     'research_round4/middle_inventory/verify_priced_nine.py'),
    ('separate_priced_nine_stage_review',
     'research_round4/optimization/review_priced_nine_stage.py'),
    ('regenerate_stable_middle_frontier',
     'research_round4/middle_inventory/build_middle_final_frontier.py'),
    ('exact_type_model_and_ring_carry_demonstrations',
     'research_round4/optimization/verify_optimization_demo.py'),
]


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def initial_manifest_check():
    path = ROOT / 'MANIFEST_ROUND4.json'
    manifest = read_json(path)
    names = set()
    for row in manifest['files']:
        name = row['path']
        relative = PurePosixPath(name)
        require(not relative.is_absolute() and '..' not in relative.parts,
                'Unsafe manifest path: ' + name)
        require(name not in names and name != path.name,
                'Duplicate or self-referential manifest path: ' + name)
        names.add(name)
        source = ROOT.joinpath(*relative.parts)
        require(source.is_file(), 'Missing payload file: ' + name)
        require(source.stat().st_size == row['bytes'] and sha(source) == row['sha256'],
                'Initial payload hash mismatch: ' + name)
    require(len(names) == manifest['payload_count'], 'Manifest payload count mismatch')
    require(sum(row['bytes'] for row in manifest['files']) == manifest['payload_bytes'],
            'Manifest payload byte count mismatch')
    print(f'Initial payload hashes PASS: {len(names)} files', flush=True)
    return manifest, sha(path)


def check_final_frontier(frontier_initial, middle_initial):
    require(FRONTIER.read_bytes() == frontier_initial,
            'The root frontier changed during replay')
    require(MIDDLE_FRONTIER.read_bytes() == middle_initial,
            'Regenerated stable middle frontier differs from the packaged version')
    frontier = read_json(FRONTIER)
    middle = read_json(MIDDLE_FRONTIER)
    require(frontier['unrestricted_dimension5_theorem'] == 'OPEN',
            'The unrestricted dimension-five theorem must remain marked OPEN')
    require(middle['status'] == 'PASS', 'Final middle frontier is not PASS')
    require(middle['remaining_weight_profiles'] == EXPECTED_COUNT,
            'Unexpected final middle inventory count')
    require(middle['empty_cells'] == EXPECTED_EMPTY,
            'Unexpected closed support/maximum cells')
    require(middle['remaining_nonempty_cells'] == 55,
            'Unexpected number of nonempty middle cells')

    counts, seen = Counter(), set()
    final_path = MIDDLE / 'after_priced_nine_survivors.txt'
    with final_path.open(encoding='utf-8') as stream:
        for number, line in enumerate(stream, 1):
            fields = tuple(map(int, line.split()))
            require(len(fields) >= 4, f'Malformed final profile on line {number}')
            support, maximum, _bound, *weights = fields
            profile = tuple(weights)
            require(10 <= support <= 17 and 12 <= maximum <= 18,
                    f'Profile outside the inventoried range on line {number}')
            require(len(profile) == support and profile[0] == maximum
                    and sum(profile) == 93 and min(profile) >= 2
                    and profile == tuple(sorted(profile, reverse=True)),
                    f'Invalid normalized profile on line {number}')
            require(profile not in seen, f'Duplicate final profile on line {number}')
            seen.add(profile)
            counts[support, maximum] += 1
    require(len(seen) == EXPECTED_COUNT, 'Final survivor list has the wrong length')
    expected_keys = {(s, m) for s in range(10, 18) for m in range(12, 19)}
    rows = {(row['support'], row['maximum']): row for row in middle['records']}
    require(len(middle['records']) == len(rows) == 56 and set(rows) == expected_keys,
            'Final frontier does not contain each of the 56 middle cells exactly once')
    for key, row in rows.items():
        require(row['remaining_weight_profiles'] == counts[key],
                'Final list and middle frontier disagree at cell ' + str(key))
    empty = [{'support': s, 'maximum': m} for s, m in sorted(expected_keys)
             if counts[s, m] == 0]
    require(empty == EXPECTED_EMPTY, 'Final list closes an unexpected set of cells')
    require(frontier['dimension5_strata']['maximum12_through18']
            ['remaining_weight_profiles'] == EXPECTED_COUNT,
            'Root stratum count disagrees with the final list')
    root_middle = frontier['middle_weight_inventory']
    for key in ('remaining_weight_profiles', 'empty_cells', 'remaining_nonempty_cells'):
        require(root_middle[key] == middle[key],
                'Root and middle frontiers disagree: ' + key)
    root_rows = {(row['support'], row['maximum']): row for row in root_middle['records']}
    require(len(root_middle['records']) == len(root_rows) == 56
            and set(root_rows) == expected_keys,
            'Root frontier does not contain all 56 middle cells')
    for key, row in root_rows.items():
        require(row['remaining_weight_profiles'] == counts[key],
                'Root frontier disagrees with the final list at cell ' + str(key))
    for name, expected_sha in middle['stable_files'].items():
        require(sha(MIDDLE / name) == expected_sha,
                'Final middle frontier stable-file mismatch: ' + name)
    return {
        'unrestricted_dimension5_theorem': 'OPEN',
        'middle_total_normalized_weight_profiles': middle['all_weight_profiles'],
        'middle_remaining_weight_profiles': EXPECTED_COUNT,
        'middle_new_priced_nine_exclusions': middle['new_priced_nine_cuts'],
        'middle_empty_cells': empty,
        'middle_remaining_nonempty_cells': 55,
        'maximum18_pair_active_support_upper_bound': 16,
        'remaining_list_sha256': sha(final_path),
        'root_frontier_sha256': sha(FRONTIER),
        'regenerated_middle_frontier_sha256': sha(MIDDLE_FRONTIER),
        'counting_scope': 'Weight-profile relaxation survivors, not Kakeya constructions.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--with-round3', action='store_true',
                        help='Replay the complete inherited Round3 checkpoint first.')
    args = parser.parse_args()
    if sys.flags.optimize:
        raise SystemExit('Assertions are required; run without -O or PYTHONOPTIMIZE.')

    manifest, manifest_sha = initial_manifest_check()
    words = len(MONOGRAPH.read_text(encoding='utf-8').split())
    require(words == 1500, f'Monograph word count is {words}, expected exactly 1500')
    report_words = len((ROOT / 'Kakeya_Research_Round4_Report.txt')
                       .read_text(encoding='utf-8').split())
    frontier_initial, middle_initial = FRONTIER.read_bytes(), MIDDLE_FRONTIER.read_bytes()
    lean = read_json(LEAN_RECEIPT)
    require(lean['status'] == 'PASS_PINNED_LEAN_KERNEL_COMPILATION'
            and lean['theorem_count'] == 13 and lean['standard_axioms_only'] is True,
            'Included separate Lean compilation receipt is inconsistent')
    require(lean['source_sha256'] == sha(ROOT / 'research_round4/lean/CubeMaster.lean')
            and lean['log_sha256'] == sha(ROOT / 'research_round4/lean/LEAN_COMPILE_LOG.txt'),
            'Included Lean receipt does not match its source and compilation log')

    env = dict(os.environ)
    env.pop('PYTHONOPTIMIZE', None)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    steps = list(STEPS)
    if args.with_round3:
        steps.insert(0, ('complete_inherited_round3_replay', 'VERIFY_ROUND3.py'))

    # Creating new Round4 log files does not alter any inherited input. The
    # optional Round3 subprocess is the first operation that runs a verifier.
    logs = ROOT / 'verification_logs_round4'
    logs.mkdir(exist_ok=True)
    receipt_path = ROOT / 'VERIFICATION_RECEIPT_ROUND4.json'
    receipt = {
        'status': 'RUNNING',
        'scope': ('All credited Round4 finite input checks, twelve-point enumeration, '
                  'complete middle weight inventory, exact local certificates, and '
                  'bounded type-model demonstrations. Analytic proofs are included '
                  'separately; this is not a formal proof of the unrestricted theorem.'),
        'initial_manifest_sha256': manifest_sha,
        'initial_payload_files_verified': manifest['payload_count'],
        'python_version': platform.python_version(),
        'monograph_whitespace_words': words,
        'report_whitespace_words': report_words,
        'round3_replayed_in_this_run': args.with_round3,
        'inherited_round3_receipt': 'Kakeya_Round3_Portable_Replay_Receipt.json',
        'lean_replayed_in_this_run': False,
        'lean_status': 'NOT_RERUN_BY_PORTABLE_FINITE_RUNNER',
        'included_separate_lean_receipt': str(LEAN_RECEIPT.relative_to(ROOT)),
        'included_separate_lean_receipt_sha256': sha(LEAN_RECEIPT),
        'included_separate_lean_theorems': 13,
        'lean_scope_limit': lean['not_formalized'],
        'network_or_installation_requested': False,
        'steps': [],
    }
    started = time.monotonic()

    def save_receipt():
        receipt['seconds'] = round(time.monotonic() - started, 3)
        receipt_path.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')

    try:
        for index, (name, relative) in enumerate(steps, 1):
            print(f'[{index}/{len(steps)}] {name}', flush=True)
            log = logs / (name + '.txt')
            begin = time.monotonic()
            with log.open('w', encoding='utf-8') as stream:
                result = subprocess.run([sys.executable, str(ROOT / relative)],
                                        cwd=ROOT, env=env, stdout=stream,
                                        stderr=subprocess.STDOUT)
            row = {
                'name': name, 'script': relative,
                'status': 'PASS' if result.returncode == 0 else 'FAIL',
                'returncode': result.returncode,
                'seconds': round(time.monotonic() - begin, 3),
                'log': str(log.relative_to(ROOT)), 'log_sha256': sha(log),
            }
            receipt['steps'].append(row)
            save_receipt()
            if result.returncode:
                print(log.read_text(encoding='utf-8', errors='replace')[-12000:],
                      file=sys.stderr)
                raise RuntimeError('Verification failed: ' + name)
            print(f"  PASS ({row['seconds']} seconds)", flush=True)
        receipt['final_frontier'] = check_final_frontier(frontier_initial, middle_initial)
        receipt['status'] = 'PASS_ALL_ROUND4_FINITE_REPLAY_STEPS'
        save_receipt()
    except Exception as error:
        receipt['status'] = 'FAIL'
        receipt['error'] = str(error)
        save_receipt()
        raise
    print(json.dumps({'status': receipt['status'], 'seconds': receipt['seconds'],
                      'lean_status': receipt['lean_status'],
                      'frontier': receipt['final_frontier']}, indent=2), flush=True)


if __name__ == '__main__':
    main()
