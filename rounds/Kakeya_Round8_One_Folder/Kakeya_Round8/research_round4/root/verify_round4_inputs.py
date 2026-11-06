"""Recompute the finite input spectrum and the nine-residue support bound.

The pair-spectrum enumerator is the separately written Round2 checker, not
the census producer. The tiny nine-point enumeration here is new and needs
no input catalogue. Neither computation substitutes for the analytic proofs.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import csv
import json
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def main():
    if sys.flags.optimize:
        raise SystemExit('Assertions are required; run without -O.')
    start = time.monotonic()
    census_path = ROOT / 'research_round2/geometric/PAIR_SPECTRUM_CENSUS.json'
    source = ROOT / 'research_round2/root/verify_pair_spectra.cpp'
    census = json.loads(census_path.read_text())
    with tempfile.TemporaryDirectory(prefix='kakeya_round4_pair_input_') as tmp:
        tmp = Path(tmp)
        exe, output = tmp / 'pair_checker', tmp / 'spectra.csv'
        subprocess.run(['g++', '-O3', '-std=c++17', str(source), '-o', str(exe)], check=True)
        run = subprocess.run([str(exe), str(output)], check=True, capture_output=True, text=True)
        actual = {w: set() for w in range(1, 20)}
        with output.open() as stream:
            for row in csv.reader(stream):
                actual[int(row[0])].add(tuple(map(int, row[1:])))
    counts = {}
    for w in range(1, 20):
        expected = {tuple(row['hist']) for row in census['weights'][str(w)]}
        assert actual[w] == expected, w
        for row in census['weights'][str(w)]:
            points = {x for x in range(32) if row['mask'] >> x & 1}
            assert len(points) == w
            pairs = [sum((x ^ d) in points for x in points) // 2 for d in range(1, 32)]
            assert tuple(pairs.count(p) for p in range(10)) == tuple(row['hist'])
        counts[w] = len(expected)
    nine = []
    for rank in (4, 5):
        basis = (0,) + tuple(1 << i for i in range(rank))
        rest = tuple(x for x in range(1 << rank) if x not in basis)
        histogram, witness = Counter(), None
        for extra in combinations(rest, 9 - len(basis)):
            points = basis + extra
            directions = {a ^ b for a, b in combinations(points, 2)}
            histogram[len(directions)] += 1
            if witness is None or len(directions) > witness['count']:
                witness = {'count': len(directions), 'points': points}
        assert max(histogram) <= 28
        nine.append({'rank': rank, 'normalized_sets': sum(histogram.values()),
                     'histogram': dict(sorted(histogram.items())), 'maximum_witness': witness})
    assert sum(row['normalized_sets'] for row in nine) == 2930
    assert max(row['maximum_witness']['count'] for row in nine) == 28
    receipt = {
        'status': 'PASS',
        'pair_spectrum_census_sha256': sha256(census_path.read_bytes()).hexdigest(),
        'pair_spectrum_checker_sha256': sha256(source.read_bytes()).hexdigest(),
        'pair_spectrum_counts': counts,
        'nine_residue_enumeration': nine,
        'normalization_justification': 'Any nine-point subset of F2^5 has affine rank4 or5. Translate one point to zero and map an affine basis selected from the set to the coordinate basis. All remaining point choices are enumerated; repeated affine classes do not affect completeness.',
        'scope': 'Finite input replay and a separately implemented corroboration of the inherited analytic nine-point bound. No new unrestricted Kakeya conclusion.',
        'seconds': round(time.monotonic() - start, 3),
    }
    (HERE / 'ROUND4_INPUT_REPLAY.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'status': receipt['status'], 'nine_point_sets': 2930,
                      'nine_point_maximum': 28, 'spectrum_weights_checked': 19,
                      'seconds': receipt['seconds']}, indent=2))


if __name__ == '__main__':
    main()
