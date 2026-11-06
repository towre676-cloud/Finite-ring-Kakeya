"""Independent ring-arithmetic checks for the fixed-shape offset CNF."""
import itertools
import json
from pathlib import Path
import random
import time

from translation_completion import CompletionCNF, affine_basis, coverage_counts


def direct_all_lines(n, ring):
    """Build directly from coordinates in the four-element ring.

    This deliberately uses no binary-vector carry or quotient routines from
    the encoder. Elements 0,1,2,3 denote a+2b or a+epsilon*b.
    """
    elems = list(itertools.product(range(4), repeat=n))
    index = {p: i for i, p in enumerate(elems)}

    def add(a, b):
        return (a + b) % 4 if ring == 'z4' else a ^ b

    def mul(a, b):
        if ring == 'z4':
            return a * b % 4
        return ((a & 1) & (b & 1)) | (((((a & 1) * (b >> 1)) ^ ((a >> 1) * (b & 1))) & 1) << 1)

    by_direction = []
    for direction in elems:
        if not any(v & 1 for v in direction):
            continue
        lines = set()
        for base in elems:
            line = tuple(sorted(index[tuple(add(a, mul(t, b)) for a, b in zip(base, direction))]
                                for t in range(4)))
            lines.add(sum(1 << p for p in line))
        by_direction.append(lines)
    masks = {}
    for residue in range(1 << n):
        for high in range(1 << n):
            coords = tuple(((residue >> j) & 1) | (((high >> j) & 1) << 1) for j in range(n))
            masks[residue, high] = 1 << index[coords]
    return by_direction, masks


def direct_good(shapes, offsets, lines, masks):
    K = sum(masks[x, a ^ offsets.get(x, 0)] for x, A in shapes.items() for a in A)
    return all(any(K & line == line for line in parallel) for parallel in lines)


def main():
    from pysat.solvers import Solver
    start = time.monotonic()
    directory = Path(__file__).resolve().parent
    total_families = total_offsets = 0
    status_counts = {ring: {'SAT': 0, 'UNSAT': 0} for ring in ('dual', 'z4')}
    # Complete quotient by translation for every subset of F2^2, including
    # the three distinct two-point direction types.
    shapes2 = [set(), {0}, {0,1}, {0,2}, {0,3}, {0,1,2}, {0,1,2,3}]
    ring_data = {ring: direct_all_lines(2, ring) for ring in status_counts}
    for spec in itertools.product(range(len(shapes2)), repeat=4):
        shapes = {x: shapes2[k] for x, k in enumerate(spec) if shapes2[k]}
        fixed = affine_basis(shapes)
        free = [x for x in shapes if x not in fixed]
        for ring, (lines, masks) in ring_data.items():
            possible = False
            for values in itertools.product(range(4), repeat=len(free)):
                offsets = dict(zip(free, values))
                actual = direct_good(shapes, offsets, lines, masks)
                translated = {x: {a ^ offsets.get(x, 0) for a in A} for x, A in shapes.items()}
                quotient = all(not row['missing'] for row in coverage_counts(2, translated, ring))
                assert actual == quotient, (spec, ring, offsets)
                possible |= actual
                total_offsets += 1
            model = CompletionCNF(2, shapes, ring)
            with Solver(name='g4', bootstrap_with=model.clauses) as solver:
                answer = solver.solve()
            assert answer == possible, (spec, ring, possible)
            status_counts[ring]['SAT' if answer else 'UNSAT'] += 1
            total_families += 1

    all_hole_cases = {}
    for ring, (lines, masks) in ring_data.items():
        passing, H_counts = [], [0]*4
        shapes = {x: {1,2,3} for x in range(4)}
        for values in itertools.product(range(4), repeat=4):
            offsets = dict(enumerate(values))
            if direct_good(shapes, offsets, lines, masks):
                passing.append(values)
                H = values[0] ^ values[1] ^ values[2] ^ values[3]
                H_counts[H] += 1
        all_hole_cases[ring] = {'assignments': 256, 'kakeya_assignments': len(passing),
                               'kakeya_by_total_hole_xor': H_counts,
                               'first_witness_holes': passing[0] if passing else None}
    assert all_hole_cases['dual']['kakeya_assignments'] == 0
    assert all_hole_cases['z4']['kakeya_by_total_hole_xor'] == [0,0,0,64]

    # n=3 direct arithmetic versus quotient coverage on fully arbitrary
    # translated shapes, to exercise nontrivial two-bit quotient maps.
    random3, rng = 0, random.Random(20261027)
    for ring in ('dual', 'z4'):
        lines, masks = direct_all_lines(3, ring)
        for _ in range(250):
            shapes = {x: {a for a in range(8) if rng.randrange(3)} for x in range(8)}
            offsets = {x: rng.randrange(8) for x in shapes}
            translated = {x: {a ^ offsets[x] for a in A} for x, A in shapes.items()}
            actual = direct_good(shapes, offsets, lines, masks)
            quotient = all(not row['missing'] for row in coverage_counts(3, translated, ring))
            assert actual == quotient
            # Pin all offsets with gauge disabled and compare satisfiability
            # with direct full-line inclusion.
            model = CompletionCNF(3, shapes, ring, fix_affine_gauge=False)
            pins = [model.var(('t',x,j)) * (1 if (offsets[x]>>j)&1 else -1)
                    for x in model.shapes for j in range(3)]
            with Solver(name='g4', bootstrap_with=model.clauses) as solver:
                answer = solver.solve(assumptions=pins)
            assert answer == actual
            random3 += 1

    result = {'exhaustive_n2_shape_families_both_rings': total_families,
              'n2_affine_gauge_offset_assignments_checked': total_offsets,
              'n2_status_counts': status_counts,
              'n2_all_three_point_fibres': all_hole_cases,
              'random_n3_pinned_offset_fixtures_both_rings': random3,
              'seconds': time.monotonic()-start,
              'scope': 'Encoder validation and exact n2 obstruction; no n5 exclusion asserted.'}
    (directory/'translation_completion_validation.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
