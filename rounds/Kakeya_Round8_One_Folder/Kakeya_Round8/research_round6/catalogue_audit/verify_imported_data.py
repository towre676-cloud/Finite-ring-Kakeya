"""Rebuild imported data without changing the uploaded checkpoint.

The source census is a finite enumeration, not a proof-assistant theorem.
This replay also checks the exact 38-case bijection against our earlier,
independently enumerated marked-support contract.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from math import comb
import hashlib
import json
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
IMPORTED = HERE.parent / 'imported_claude_round4'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def gaussian(n, k):
    num = den = 1
    for i in range(k):
        num *= 2 ** (n - i) - 1
        den *= 2 ** (i + 1) - 1
    return num // den


def regenerate(name, target):
    dest = HERE / 'data_replay'
    dest.mkdir(exist_ok=True)
    binary = dest / name
    source = IMPORTED / 'src' / (name + '.cpp')
    start = time.monotonic()
    build = subprocess.run(['g++', '-O2', '-std=c++17', str(source), '-o', str(binary)],
                           capture_output=True, text=True, timeout=120)
    (dest / (name + '.build.log')).write_text(build.stdout + build.stderr)
    if build.returncode:
        raise RuntimeError('Build failed: ' + name)
    with (dest / target).open('wb') as stdout, (dest / (name + '.stderr.log')).open('wb') as stderr:
        completed = subprocess.run([str(binary)], stdout=stdout, stderr=stderr, timeout=1800)
    if completed.returncode:
        raise RuntimeError('Enumeration failed: ' + name)
    expected = sha(IMPORTED / 'data' / target)
    actual = sha(dest / target)
    if expected != actual:
        raise ValueError('Data regeneration differs: ' + target)
    row = {'name': name, 'status': 'PASS_BYTE_IDENTICAL',
           'source_sha256': sha(source), 'data_sha256': actual,
           'seconds': round(time.monotonic() - start, 3)}
    print(json.dumps(row), flush=True)
    return row


def catalogue_checks():
    GL = 9999360
    totals = {}
    orbit_counts = {}
    covering = {}
    seen = set()
    marked_rows = []
    sys.path.insert(0, str(ROOT / 'research_round5' / 'encoding_bridge'))
    from map_marked_case import map_marked_support
    for line in (IMPORTED / 'data/orbits_all.txt').read_text().splitlines():
        k, mask, stab, cov = map(int, line.split())
        if (k, mask) in seen or mask.bit_count() != k or mask & 1 or GL % stab:
            raise ValueError('Invalid orbit row')
        seen.add((k, mask))
        support = [0] + [x for x in range(1, 32) if mask >> x & 1]
        actual_cover = len({x ^ y for x in support for y in support}) == 32
        if actual_cover != bool(cov):
            raise ValueError('Incorrect covering flag')
        totals[k] = totals.get(k, 0) + GL // stab
        orbit_counts[k] = orbit_counts.get(k, 0) + 1
        if cov:
            covering[k + 1] = covering.get(k + 1, 0) + 1
        if cov and k + 1 in (11, 12):
            marked_rows.append(dict(source_mask=mask, stabilizer_order=stab,
                                    **map_marked_support(support, 0)))
    mobius = []
    for k in range(5, 32):
        count = sum(gaussian(5, j) * (-1) ** (5 - j)
                    * 2 ** ((5 - j) * (4 - j) // 2) * comb(2 ** j - 1, k)
                    for j in range(6))
        if totals.get(k) != count:
            raise ValueError('Mobius count mismatch at k=' + str(k))
        mobius.append({'nonzero_points': k, 'orbit_count': orbit_counts[k],
                       'weighted_orbit_count': totals[k], 'mobius_count': count})
    contract = json.loads((ROOT / 'research_round5/encoding_bridge/M19_MARKED_CASE_CONTRACT.json').read_text())
    expected = {r['case_id'] for r in contract['cases']}
    actual = {r['case_id'] for r in marked_rows}
    if len(marked_rows) != 38 or len(actual) != 38 or actual != expected:
        raise ValueError('Incomplete or duplicated marked-support mapping')
    report = {'status': 'PASS_COMPLETE_BIJECTION',
              'scope': 'Support metadata, not CNF meaning or proof acceptance.',
              'cases': marked_rows}
    (HERE / 'CLAUDE_TO_ROUND5_38_CASE_MAP.json').write_text(json.dumps(report, indent=2) + '\n')
    return {'covering_marked_supports': covering, 'mobius_checks': mobius,
            'marked_case_bijection': 'PASS_13_PLUS_25',
            'mathematical_scope': 'Completeness also uses the reviewed orbit enumerator: each canonical label is an actual image and reported stabilizers are correct.'}


def main():
    result = {'status': 'INCOMPLETE'}
    receipt = HERE / 'IMPORTED_DATA_REPLAY.json'
    receipt.write_text(json.dumps(result) + '\n')
    try:
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = [pool.submit(regenerate, name, target) for name, target in
                       [('orbits_all', 'orbits_all.txt'), ('spectra32', 'spec32.csv'), ('msum', 'Mtable.txt')]]
            result['regeneration'] = [f.result() for f in futures]
        result['catalogue'] = catalogue_checks()
        result['status'] = 'PASS'
    except Exception as exc:
        result['status'] = 'FAIL'
        result['error'] = str(exc)
        receipt.write_text(json.dumps(result, indent=2) + '\n')
        raise
    receipt.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'marked_cases': 38}), flush=True)


if __name__ == '__main__':
    main()
