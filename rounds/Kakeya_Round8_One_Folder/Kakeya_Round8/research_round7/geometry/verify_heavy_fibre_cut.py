#!/usr/bin/env python3
"""Small complete controls for the support13 heavy-fibre lemma and cut."""
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import time

from heavy_fibre_cut import add_heavy_fibre_cut

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pair_counts(points):
    counts = [0] * 32
    for a, b in itertools.combinations(points, 2):
        counts[a ^ b] += 1
    return counts


def main():
    start = time.monotonic()
    light_count = 0
    for weight in (2, 3):
        for points in itertools.combinations(range(32), weight):
            counts = pair_counts(points)
            assert max(counts) == 1
            assert sum(counts) == weight * (weight - 1) // 2
            light_count += 1

    # All nine-pair fibres in one fixed direction d=1. Every nonzero d
    # is equivalent under a binary invertible linear map.
    periodic18 = 0
    for chosen in itertools.combinations(range(16), 9):
        points = tuple(x for index in chosen for x in (2 * index, 2 * index + 1))
        counts = pair_counts(points)
        assert counts[1] == 9 and sum(value == 9 for value in counts) == 1
        periodic18 += 1

    # Every set invariant under the representative two-space {0,1,2,3}.
    two_period_sets = 0
    for mask in range(256):
        points = {x for index in range(8) if (mask >> index) & 1
                  for x in range(4 * index, 4 * index + 4)}
        assert {x ^ 1 for x in points} == points
        assert {x ^ 2 for x in points} == points
        assert len(points) % 4 == 0 and len(points) != 18
        two_period_sets += 1

    inequalities = []
    for h in range(8):
        required = 16 * (31 - h * (h - 1) // 2)
        available = 24 * (13 - h) + h
        assert required > available
        assert required - available == 184 + 31 * h - 8 * h * h
        inequalities.append({'heavy_fibres': h, 'required_capacity': required,
                             'available_capacity_bound': available,
                             'strict_gap': required - available})

    path = ROOT / 'research_round6/joint_maxima/encode_joint_maxima.py'
    spec = importlib.util.spec_from_file_location('heavy_cut_baseline', path)
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)

    class RecordedCNF(base.CNF):
        def __init__(self):
            super().__init__()
            self.merges = []

        def unary_sum(self, literals):
            result = super().unary_sum(literals)
            if len(literals) > 1:
                self.merges.append((list(literals), result))
            return result

    formula = RecordedCNF()
    formula.z = {(v, i): formula.new() for v in range(13) for i in range(2)}
    original_variables = formula.n
    metadata = add_heavy_fibre_cut(formula, range(13), [(3,), (4,)])
    heavy = list(range(original_variables + 1, original_variables + 14))
    boolean_cases = 0
    for mask in range(1 << 13):
        assignment = {}
        for vertex in range(13):
            value = bool((mask >> vertex) & 1)
            assignment[formula.z[vertex, 0]] = not value
            assignment[formula.z[vertex, 1]] = value
            assignment[heavy[vertex]] = value
        for inputs, outputs in formula.merges:
            count = sum(assignment[value] for value in inputs)
            for threshold, variable in enumerate(outputs, 1):
                assignment[variable] = count >= threshold
        satisfied = all(any(assignment[abs(lit)] == (lit > 0) for lit in clause)
                        for clause in formula.cl)
        assert satisfied == (mask.bit_count() >= 8)
        boolean_cases += 1

    result = {'status': 'PASS_SUPPORT13_HEAVY_FIBRE_LEMMA_AND_BOOLEAN_CUT',
              'light_fibres_checked': light_count,
              'weight18_with_one_specified_period_checked': periodic18,
              'two_period_invariant_sets_checked': two_period_sets,
              'numerical_contradictions': inequalities,
              'complete_boolean_cardinality_cases': boolean_cases,
              'sample_cut_metadata': metadata,
              'new_unsat_exclusions_claimed': 0,
              'source_hashes': {str(p.relative_to(ROOT)): sha(p) for p in (
                  HERE / 'SUPPORT13_HEAVY_FIBRES.md', HERE / 'heavy_fibre_cut.py',
                  Path(__file__), path)},
              'seconds': round(time.monotonic() - start, 6)}
    output = HERE / 'SUPPORT13_HEAVY_FIBRE_REPLAY.json'
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
