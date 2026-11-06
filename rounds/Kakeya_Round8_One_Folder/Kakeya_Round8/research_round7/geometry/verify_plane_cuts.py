#!/usr/bin/env python3
"""Replay the finite plane relation and the optional clause wrapper.

No SAT search or third-party Python package is needed. An independently
enumerated 16-point space checks the smaller version of the recurrence;
explicit 32-point witnesses check every state of the full recurrence.
"""
import hashlib
import importlib.util
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
import time

from plane_cuts import (PATTERNS, add_plane_cuts, attainable,
                        closed_form_feasible, weight_intervals)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pair_count(mask, direction, dimension=5):
    return sum((mask >> x & 1) and (mask >> (x ^ direction) & 1)
               for x in range(1 << dimension) if x < (x ^ direction))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    start = time.monotonic()
    # Verify all sixteen subsets of one coset, not just the listed patterns.
    local = {(mask.bit_count(), *(pair_count(mask, d, 2) for d in (1, 2, 3)))
             for mask in range(16)}
    assert local == {row for row, mask in PATTERNS}
    for row, mask in PATTERNS:
        assert row == (mask.bit_count(), *(pair_count(mask, d, 2) for d in (1, 2, 3)))

    # Exhaustive independent subset enumeration in binary four-space.
    observed4 = {(mask.bit_count(), *(pair_count(mask, d, 4) for d in (1, 2, 3)))
                 for mask in range(1 << 16)}
    assert observed4 == set(attainable(4))

    states = attainable(8)
    for row, mask in states.items():
        assert row == (mask.bit_count(), *(pair_count(mask, d) for d in (1, 2, 3)))
    tested = 0
    for w in range(33):
        for p, q, r in itertools.product(range(17), repeat=3):
            tested += 1
            assert closed_form_feasible(w, p, q, r) == ((w, p, q, r) in states)
    intervals = weight_intervals()
    assert len(states) == 2233 and len(intervals) == 629

    base_path = ROOT / 'research_round6/joint_maxima/encode_joint_maxima.py'
    spectrum_path = ROOT / 'research_round6/imported_claude_round4/data/spec32.csv'
    base = load(base_path, 'plane_verification_base')
    spectra = base.load_spectra(spectrum_path)
    chosen_indices = [i for i, sp in enumerate(spectra) if 2 <= sp[0] <= 18]
    formula = base.CNF()
    formula.z = {(0, i): formula.new() for i in chosen_indices}
    formula.y = {(0, d, k): formula.new() for d in (1, 2, 3) for k in range(10)}
    stats = add_plane_cuts(formula, [0], spectra)
    assert stats['local_planes'] == 1

    def clauses_hold(w, counts, index):
        assignment = {literal: False for literal in formula.z.values()}
        assignment[formula.z[0, index]] = True
        assignment.update({literal: (k == counts[d - 1])
                           for (v, d, k), literal in formula.y.items()})
        assignment.update({literal: (w >= threshold)
                           for (v, threshold), literal in formula.plane_weight_thresholds.items()})
        assert len(assignment) == formula.n
        return all(any(assignment[abs(lit)] == (lit > 0) for lit in clause)
                   for clause in formula.cl)

    actual_checks = 0
    for (w, p, q, r), mask in states.items():
        if not 2 <= w <= 18:
            continue
        hist = Counter(pair_count(mask, d) for d in range(1, 32))
        choices = [i for i in chosen_indices if spectra[i][0] == w and
                   spectra[i][1] == [hist[k] for k in range(17)]]
        assert choices
        assert clauses_hold(w, (p, q, r), choices[0])
        actual_checks += 1

    rejected_checks = 0
    accepted_histogram_checks = 0
    for w in range(2, 19):
        for counts in itertools.product(range(w // 2 + 1), repeat=3):
            multiplicities = Counter(counts)
            choices = [i for i in chosen_indices if spectra[i][0] == w and
                       all(spectra[i][1][k] >= n for k, n in multiplicities.items())]
            if not choices:
                continue
            expected = (w, *counts) in states
            assert clauses_hold(w, counts, choices[0]) == expected
            rejected_checks += not expected
            accepted_histogram_checks += expected

    by_weight = []
    for w in range(33):
        by_weight.append({'weight': w, 'feasible_ordered_pair_triples':
                          sum(row[0] == w for row in states)})
    relation_path = HERE / 'PLANE_PAIR_TABLE.json'
    relation = {'ambient_dimension': 5, 'plane_dimension': 2, 'cosets': 8,
                'tuple_count': len(states), 'tuple_order': ['weight', 'p_d', 'p_e', 'p_d_plus_e'],
                'tuples': sorted(states),
                'weight_intervals': [{'counts': list(counts), 'minimum_weight': bounds[0],
                                      'maximum_weight': bounds[1]}
                                     for counts, bounds in sorted(intervals.items())]}
    relation_path.write_text(json.dumps(relation, indent=2) + '\n')
    receipt = {'status': 'PASS_EXACT_PLANE_RELATION_AND_CLAUSE_WRAPPER',
               'ambient_dimension': 5,
               'full_state_count': len(states), 'distinct_pair_triples': len(intervals),
               'local_subsets_checked': 16, 'binary4_subsets_exhausted': 65536,
               'binary4_relation_size': len(observed4),
               'closed_form_quadruples_checked': tested,
               'explicit_binary5_witnesses_checked': len(states),
               'actual_fibre_clause_extensions_checked': actual_checks,
               'census_compatible_impossible_quadruples_rejected': rejected_checks,
               'census_compatible_possible_quadruples_accepted': accepted_histogram_checks,
               'sample_wrapper_stats': stats,
               'by_weight': by_weight,
               'source_hashes': {str(path.relative_to(ROOT)): sha(path) for path in
                                [HERE / 'plane_cuts.py', Path(__file__).resolve(),
                                 base_path, spectrum_path, relation_path]},
               'seconds': round(time.monotonic() - start, 6),
               'whole_support_exclusions_credited': 0,
               'formalization': 'Finite replay and written proof; not proof-assistant formalized.'}
    (HERE / 'PLANE_PAIR_REPLAY.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({k: v for k, v in receipt.items() if k not in ('by_weight', 'source_hashes')}, indent=2))


if __name__ == '__main__':
    main()
