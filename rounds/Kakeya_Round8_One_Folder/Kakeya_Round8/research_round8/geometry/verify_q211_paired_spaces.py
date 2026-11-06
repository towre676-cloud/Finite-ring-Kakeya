#!/usr/bin/env python3
"""Exhaustive local geometry and constructive CNF controls for Q211 caps."""
from collections import Counter
from itertools import combinations, product
import hashlib
import json
from pathlib import Path
import time

from q211_paired_spaces import append_q211_pair_space_cuts, complete_assignment

HERE = Path(__file__).resolve().parent


def span(generators):
    values = {0}
    for generator in generators:
        values |= {x ^ generator for x in values}
    return frozenset(values)


def direction_space(points):
    origin = min(points)
    return span(x ^ origin for x in points)


def counts(points):
    result = [0] * 32
    for a, b in combinations(points, 2):
        result[a ^ b] += 1
    return result


def project(x, d):
    return min(x, x ^ d)


def pair_set(points, d):
    return {project(x, d) for x in points if x ^ d in points}


def all_subspaces():
    spaces = {frozenset({0})}
    for vector in range(1, 32):
        spaces |= {frozenset(set(H) | {x ^ vector for x in H})
                   for H in list(spaces) if vector not in H}
    assert len(spaces) == 374
    return sorted(spaces, key=lambda H: (len(H), sorted(H)))


class Formula:
    def __init__(self):
        self.n, self.cl = 0, []

    def new(self):
        self.n += 1
        return self.n

    def add(self, clause):
        self.cl.append(list(clause))


def main():
    started = time.monotonic()
    flat = set(range(16))
    classified = 0
    q211, effective_directions, q205_directions, q205 = 0, 0, 0, 0
    for complement in combinations(range(16), 5):
        A = flat - set(complement)
        p = counts(A)
        energy = sum(value * value for value in p)
        classified += 1
        if energy == 211:
            q211 += 1
            K = frozenset({0} | {d for d in range(1, 32) if p[d] == 5})
            L = K | {d for d in range(1, 32) if p[d] == 4}
            assert len(K) == 4 and span(K) == K
            assert len(L) == 8 and span(L) == L
            assert {d for d in range(1, 32) if p[d] == 3} == flat - L
            for d in range(1, 32):
                if p[d] not in (3, 4):
                    continue
                P = pair_set(A, d)
                projected_K = frozenset(project(k, d) for k in K)
                assert len(P) == p[d] and len(projected_K) == 4
                assert direction_space(P) == projected_K
                effective_directions += 1
        elif energy == 205:
            q205 += 1
            circuit = {d for d in range(1, 32) if p[d] == 3}
            assert len(circuit) == 5
            for d in range(1, 32):
                if p[d] != 4:
                    continue
                P = pair_set(A, d)
                positive = {a ^ b for a, b in combinations(P, 2)}
                quotient = {project(x, d) for x in flat}
                missing = quotient - positive - {0}
                matching = [(a, b) for a, b in combinations(circuit, 2) if a ^ b == d]
                assert len(missing) == len(matching) == 1
                a, b = matching[0]
                assert {project(a, d), project(b, d)} == missing
                q205_directions += 1
        else:
            raise AssertionError('Unexpected eleven-point spectrum in a four-flat')
    assert (classified, q211, q205) == (4368, 1680, 2688)
    assert effective_directions == 20160 and q205_directions == 26880

    tetra = {0, 1, 2, 4}
    tetra_space = direction_space(tetra)
    missing = tetra_space - {0} - {a ^ b for a, b in combinations(tetra, 2)}
    assert missing == {7}
    plane_partners = 0
    plane_capacity_histogram = Counter()
    for P in combinations(range(16), 4):
        G = direction_space(P)
        if len(G) != 4:
            continue
        actual = len({a ^ b for a in P for b in tetra})
        intersection = G & tetra_space
        predicted = 8 if len(intersection) == 4 else 16 if intersection - {0} == missing else 12
        assert actual == predicted
        plane_capacity_histogram[actual] += 1
        plane_partners += 1
    assert plane_partners == 140
    triangles = list(combinations(range(8), 3))
    for P, Q in product(triangles, repeat=2):
        assert len({a ^ b for a in P for b in Q}) <= 7

    spaces = all_subspaces()
    K0, K1 = span((1, 2)), span((1, 16))
    H1 = span((1, 4, 8, 16))
    A0 = flat - (set(K0) | {4})
    A1 = set(H1) - (set(K1) | {4})
    cube = set(span((1, 4, 16)))
    H2 = span((1, 2, 4, 16))
    tetra_type = set(H2) - {0, 1, 2, 4, 16}
    families = [A0, A1, cube, tetra_type]
    signatures = []
    for A in families:
        p = counts(A)
        histogram = [p[1:].count(k) for k in range(17)]
        rank = len(direction_space(A)).bit_length() - 1
        signatures.append((len(A), tuple(histogram), rank, rank))
    spectra = sorted(set(signatures))
    actual_index = [spectra.index(value) for value in signatures]
    constructed = 0
    retained_sizes = []
    extra_examples = []
    for d in (1, 2, 3, 4, 8, 16, 20, 31):
        f = Formula()
        f.z = {(v, i): f.new() for v in (0, d) for i in range(len(spectra))}
        f.y = {(v, d, p): f.new() for v in (0, d) for p in range(6)}
        f.h_selectors = {v: {H: f.new() for H in spaces} for v in (0, d)}
        f.k_selectors = {v: {K: f.new() for K in spaces} for v in (0, d)}
        f.r8_edge_capacity = {(0, d): [f.new() for _ in range(16)]}
        original_n, original_c = f.n, len(f.cl)
        append_q211_pair_space_cuts(f, [0, d], spectra, spaces, enabled=False)
        assert (f.n, len(f.cl)) == (original_n, original_c)
        metadata = append_q211_pair_space_cuts(f, [0, d], spectra, spaces)
        retained_sizes.append(metadata)
        for ia, ib in product(range(len(families)), repeat=2):
            assignment = {}
            for v, index in ((0, ia), (d, ib)):
                A = families[index]
                p = counts(A)
                actual_H = direction_space(A)
                actual_K = frozenset({0} | {direction for direction in range(1, 32)
                                            if p[direction] == len(A) // 2})
                assert actual_K in spaces
                for i in range(len(spectra)):
                    assignment[f.z[v, i]] = i == actual_index[index]
                for k in range(6):
                    assignment[f.y[v, d, k]] = k == p[d]
                for H, literal in f.h_selectors[v].items():
                    assignment[literal] = H == actual_H
                for K, literal in f.k_selectors[v].items():
                    assignment[literal] = K == actual_K
            capacity = len({a ^ b for a in pair_set(families[ia], d)
                            for b in pair_set(families[ib], d)})
            for threshold, variable in enumerate(f.r8_edge_capacity[0, d], 1):
                assignment[variable] = capacity >= threshold
            complete_assignment(f, assignment)
            assert all(any(assignment[abs(lit)] == (lit > 0) for lit in clause) for clause in f.cl)
            constructed += 1
            if (d, ia, ib) in ((4, 0, 2), (8, 0, 1)):
                expected = 8 if d == 4 else 7
                assert capacity == expected
                assert len(span(direction_space(families[ia]) | direction_space(families[ib]))) == 32
                wrong = dict(assignment)
                wrong[f.r8_edge_capacity[0, d][expected]] = True
                assert any(not any(wrong[abs(lit)] == (lit > 0) for lit in clause) for clause in f.cl)
                extra_examples.append({'direction': d, 'left_family': ia, 'right_family': ib,
                                       'actual_capacity': capacity, 'inflated_capacity_rejected': expected + 1,
                                       'full_fibre_spans_together_fill_ambient5': True})
    assert constructed == 128 and len(extra_examples) == 2
    files = (Path(__file__), HERE / 'q211_paired_spaces.py', HERE / 'Q211_PAIRED_SPACES.md')
    result = {'status': 'PASS_Q211_EFFECTIVE_PAIR_GEOMETRY_AND_CONSTRUCTIVE_CNF_CONTROLS',
              'five_point_complements_checked': classified,
              'Q211_fibres': q211, 'Q211_nonmaximal_pair_directions_checked': effective_directions,
              'Q205_fibres': q205, 'Q205_tetrahedral_missing_direction_checks': q205_directions,
              'tetrahedron_plane_partners_checked': plane_partners,
              'tetrahedron_plane_capacity_histogram': dict(sorted(plane_capacity_histogram.items())),
              'three_by_three_common_three_space_checks': len(triangles) ** 2,
              'complete_actual_CNF_assignments': constructed,
              'disabled_identity_controls': 8,
              'strict_improvements_over_full_fibre_span_bound': extra_examples,
              'sample_two_vertex_CNF_metadata': retained_sizes[0],
              'new_SAT_exclusions_claimed': 0,
              'source_hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
              'seconds': round(time.monotonic() - started, 6)}
    (HERE / 'Q211_PAIRED_SPACES_REPLAY.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
