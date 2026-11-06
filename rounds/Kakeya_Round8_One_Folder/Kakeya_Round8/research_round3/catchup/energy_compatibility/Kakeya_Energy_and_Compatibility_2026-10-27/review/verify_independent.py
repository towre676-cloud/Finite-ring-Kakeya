"""Independent tuple-arithmetic checks and tiny RUP replay. Standard library only.

This file does not import the producer's arithmetic, Fourier code, SAT
encoder, or proof checker. These are implementation controls; the written
all-dimension proofs do not depend on finite numerical experimentation.
"""
from itertools import product
from pathlib import Path
import hashlib
import json
import math
import random

ROOT = Path(__file__).resolve().parents[1]


def add(a, b, ring):
    return tuple((x + y) % 4 if ring == 'z4' else x ^ y
                 for x, y in zip(a, b))


def subtract(a, b, ring):
    return tuple((x - y) % 4 if ring == 'z4' else x ^ y
                 for x, y in zip(a, b))


def multiply(s, a, ring):
    if ring == 'z4':
        return tuple(s*x % 4 for x in a)
    return tuple(((s & 1)*(x & 1)) |
                 ((((s & 1)*(x >> 1)) ^ ((s >> 1)*(x & 1))) << 1)
                 for x in a)


def point(x, y, n):
    return tuple(((x >> i) & 1) + 2*((y >> i) & 1) for i in range(n))


def images(f, ring):
    return [{add(a, multiply(t, v, ring), ring) for v, a in f.items()}
            for t in range(4)]


def three_image_controls():
    rng = random.Random(20261027)
    counts = {'z4': 0, 'dual': 0}
    strict = {'z4': 0, 'dual': 0}
    examples = []
    for n in range(1, 7):
        N = 1 << n
        for r in range(n + 1):
            h = 1 << r
            m = N // h
            for _ in range(4):
                T = [0] + [(j << r) | rng.randrange(h) for j in range(1, m)]
                A = set()
                for x in range(h):
                    for j in range(m):
                        u = 0 if x == j == 0 else rng.randrange(h)
                        A.add(point(x, (j << r) | u, n))
                B = set()
                for y in T:
                    z = 0 if y == 0 else rng.randrange(m) << r
                    B.update(point(y, z | u, n) for u in range(h))
                assert len(A) == len(B) == N
                for ring in counts:
                    f = {subtract(b, a, ring): a for a in A for b in B}
                    assert len(f) == N*N
                    sets = images(f, ring)
                    sizes = [len(s) for s in sets]
                    assert sizes[0] == sizes[1] == sizes[3] == N
                    union_size = len(set().union(*sets))
                    assert union_size >= 4*N-h-m-1 >= 3*N-2
                    if sizes[2] > N:
                        assert n >= 2 and union_size >= 7*N//2-3
                        assert sizes[2] >= N+2
                        strict[ring] += 1
                    counts[ring] += 1
                    if n == 5:
                        examples.append({'ring': ring, 'n': n, 'h': h,
                                         'image_sizes': sizes, 'union': union_size})
    # All maps on a single coordinate: no structural assumption is imposed.
    all_maps = {}
    for ring in counts:
        checked = 0
        for outputs in product(range(4), repeat=4):
            f = {(v,): (outputs[v],) for v in range(4)}
            sets = images(f, ring)
            assert len(set().union(*sets)) >= 4
            checked += 1
        all_maps[ring] = checked
    return {'transversal_family_checks': counts, 'strict_fourth_image_checks': strict,
            'all_one_dimensional_maps': all_maps, 'dimension5_samples': examples}


def sharp_three_image_controls():
    """Check both explicit all-dimension constructions with tuple arithmetic."""
    rows = []
    for n in range(2, 8):
        N = 1 << n
        for family in ('fourth_N_plus_2', 'fourth_3N_over_2'):
            if family == 'fourth_N_plus_2':
                h = N // 2
                t, x0 = h, 1
                A = {point(x, y, n) for x in range(h)
                     for y in (0, t ^ x0 if x == x0 else t)}
                B = {point(x, y, n) for x in (0, t) for y in range(h)}
                expected_fourth = N+2
            else:
                T = range(0, N, 2)
                A = {point(0, y, n) for y in T}
                A.update(point(1, y ^ ((y >> 1) & 1), n) for y in T)
                B = {point(x, y, n) for x in T for y in (0, 1)}
                expected_fourth = 3*N//2
            assert len(A) == len(B) == N
            for ring in ('dual', 'z4'):
                f = {subtract(b, a, ring): a for a in A for b in B}
                assert len(f) == N*N
                sets = images(f, ring)
                sizes = [len(s) for s in sets]
                union_size = len(set().union(*sets))
                assert sizes == [N, N, expected_fourth, N]
                assert union_size == 7*N//2-3
                rows.append({'ring': ring, 'n': n, 'construction': family,
                             'image_sizes': sizes, 'union': union_size})
    return rows


def read_cnf(path):
    variables = declared = None
    clauses = []
    current = []
    for line in path.read_text().splitlines():
        if not line.strip() or line.startswith('c'):
            continue
        if line.startswith('p'):
            _, fmt, nv, nc = line.split()
            assert fmt == 'cnf' and variables is None
            variables, declared = int(nv), int(nc)
            continue
        assert variables is not None
        for token in line.split():
            literal = int(token)
            if literal == 0:
                clauses.append(tuple(current))
                current = []
            else:
                assert abs(literal) <= variables
                current.append(literal)
    assert not current and len(clauses) == declared
    return variables, clauses


def rup(clauses, candidate):
    known = set()
    for literal in candidate:
        if literal in known:
            return True
        known.add(-literal)
    while True:
        changed = False
        for clause in clauses:
            if any(lit in known for lit in clause):
                continue
            remaining = [lit for lit in clause if -lit not in known]
            if not remaining:
                return True
            if len(remaining) == 1:
                known.add(remaining[0])
                changed = True
        if not changed:
            return False


def replay(path):
    nv, clauses = read_cnf(path / 'input.cnf')
    receipt = json.loads((path / 'result.json').read_text())
    assert hashlib.sha256((path/'input.cnf').read_bytes()).hexdigest() == receipt['cnf_sha256']
    assert hashlib.sha256((path/'proof.drat').read_bytes()).hexdigest() == receipt['proof_sha256']
    lemmas = 0
    empty = False
    proof = (path / 'proof.drat').read_text().splitlines()
    for line in proof:
        if not line.strip() or line.startswith('c') or line.startswith('d'):
            continue
        row = [int(t) for t in line.split()]
        assert row[-1] == 0 and all(0 < abs(x) <= nv for x in row[:-1])
        candidate = tuple(row[:-1])
        assert rup(clauses, candidate), (path, lemmas, candidate)
        clauses.append(candidate)
        lemmas += 1
        if not candidate:
            empty = True
            break
    assert empty
    # An empty proof cannot certify either nontrivial UNSAT instance.
    assert not any(len(c) == 0 for c in read_cnf(path/'input.cnf')[1])
    return {'case': path.name, 'variables': nv, 'lemmas': lemmas,
            'empty_clause_reached': empty, 'input_and_proof_hashes_match': True}


def norm_controls():
    rows = []
    for n in range(1, 13):
        N = 1 << n
        if n >= 4:
            assert (3*N-3)**2 > 4*N*(2*N-2)
        for p in (2, 3, 5, 10, 100):
            alpha = ((2*N-2)/N)**(1/(p-1))
            a = (alpha+1)/2 / ((N*alpha**p+2*N-2)/(N*N))**(1/p)
            ceiling = N*N/(a**p)
            assert ceiling <= 2*math.sqrt(N*(2*N-2)) + 1e-7
            if n == 5:
                rows.append({'p': p, 'norm_lower_bound': a,
                             'cardinality_bound_ceiling': ceiling})
    return {'n5_by_p': rows, 'n5_all_finite_p_ceiling': 2*math.sqrt(32*62),
            'integer_squared_obstruction_checked_n': list(range(4, 13))}


def main():
    result = {'status': 'PASS',
              'scope': 'Independent implementation controls, not unrestricted n5 closure',
              'three_image_controls': three_image_controls(),
              'sharp_three_image_constructions': sharp_three_image_controls(),
              'small_proof_replays': [replay(ROOT/'compute'/name) for name in
                                    ('n2_three_fibres_dual', 'n5_four12_block_dual')],
              'all_Lp_barrier': norm_controls()}
    dest = Path(__file__).with_name('INDEPENDENT_REVIEW.json')
    dest.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'status': result['status'], 'receipt': str(dest),
                      'three_image_checks': result['three_image_controls']['transversal_family_checks'],
                      'sharp_construction_checks': len(result['sharp_three_image_constructions']),
                      'proof_replays': result['small_proof_replays'],
                      'n5_all_finite_p_ceiling': result['all_Lp_barrier']['n5_all_finite_p_ceiling']}, indent=2))


if __name__ == '__main__':
    main()
