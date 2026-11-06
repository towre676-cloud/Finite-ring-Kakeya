"""Portable standard-library verifier for saved translation-completion cases.

No SAT library or executable is needed.  Independently replays the short RUP
proofs, reconstructs each CNF, checks SAT witnesses by coordinate ring
arithmetic, and recomputes the complete n=2 translation classification.
"""
import hashlib
import itertools
import json
from pathlib import Path

from translation_completion import CompletionCNF, affine_basis, tree_union_upper_bound
from validate_translation_completion import direct_all_lines, direct_good


def read_cnf(path):
    lines = path.read_text().splitlines()
    header = lines.pop(0).split()
    assert header[:2] == ['p', 'cnf'] and len(header) == 4
    variables, number = map(int, header[2:])
    clauses = []
    for line in lines:
        row = list(map(int, line.split()))
        assert row and row[-1] == 0 and 0 not in row[:-1]
        assert all(abs(v) <= variables for v in row[:-1])
        clauses.append(tuple(row[:-1]))
    assert len(clauses) == number
    return variables, clauses


def unit_conflict(clauses, assumptions):
    values = {}
    for literal in assumptions:
        variable, value = abs(literal), literal > 0
        if variable in values and values[variable] != value:
            return True
        values[variable] = value
    while True:
        changed = False
        for clause in clauses:
            if any(abs(lit) in values and values[abs(lit)] == (lit > 0) for lit in clause):
                continue
            free = [lit for lit in clause if abs(lit) not in values]
            if not free:
                return True
            if len(free) == 1:
                lit = free[0]
                values[abs(lit)] = lit > 0
                changed = True
        if not changed:
            return False


def verify_rup(cnf, proof):
    variables, clauses = read_cnf(cnf)
    count, empty = 0, False
    for line in proof.read_text().splitlines():
        if not line.strip():
            continue
        # Retaining a deleted verified consequence only strengthens the
        # checker database and is sound for checking subsequent RUP clauses.
        if line.startswith('d '):
            continue
        row = list(map(int, line.split()))
        assert row and row[-1] == 0 and 0 not in row[:-1]
        clause = tuple(row[:-1])
        assert all(abs(lit) <= variables for lit in clause)
        assert unit_conflict(clauses, [-lit for lit in clause]), (proof, count)
        clauses.append(clause)
        count += 1
        empty |= not clause
    assert empty
    return count


def verify_coordinate_witness(n, shapes, ring, directions):
    N = 1 << n
    points = {tuple(((x >> j)&1) + 2*((y >> j)&1) for j in range(n))
              for x, A in shapes.items() for y in A}
    vectors = 0
    for low in directions:
        for high in range(N):
            v = tuple(((low>>j)&1) + 2*((high>>j)&1) for j in range(n))
            multiples = []
            for t in range(4):
                if ring == 'z4':
                    multiples.append(tuple(t*u % 4 for u in v))
                else:
                    multiples.append(tuple(((t&1)*(u&1)) + 2*(((t&1)*(u>>1)) ^ ((t>>1)*(u&1)))
                                           for u in v))
            good = False
            for p in points:
                if ring == 'z4':
                    good = all(tuple((a+b)%4 for a,b in zip(p,m)) in points for m in multiples)
                else:
                    good = all(tuple(a^b for a,b in zip(p,m)) in points for m in multiples)
                if good:
                    break
            assert good, (n, ring, low, high)
            vectors += 1
    return vectors


def main():
    here = Path(__file__).resolve().parent
    cases = []
    for file in sorted(here.glob('n*/result.json')):
        data = json.loads(file.read_text())
        folder = file.parent
        cnf = folder/'input.cnf'
        assert hashlib.sha256(cnf.read_bytes()).hexdigest() == data['cnf_sha256']
        shapes = {int(x): set(A) for x,A in data['fixed_shapes'].items()}
        directions = data.get('required_residue_directions', list(range(1,1<<data['n'])))
        model = CompletionCNF(data['n'], shapes, data['ring'], residue_directions=directions)
        nv, clauses = read_cnf(cnf)
        assert nv == len(model.vars) and list(map(list, clauses)) == model.clauses
        record = {'case': folder.name, 'status': data['status'], 'variables': nv,
                  'clauses': len(clauses), 'required_residue_directions': directions,
                  'tree_overlap_failures': sum(r['upper_bound'] < model.Q for r in model.tree_prechecks)}
        if data['status'] == 'UNSAT':
            proof = folder/'proof.drat'
            assert hashlib.sha256(proof.read_bytes()).hexdigest() == data['proof_sha256']
            record['python_rup_clauses_checked_including_empty'] = verify_rup(cnf, proof)
        elif data['status'] == 'SAT':
            offsets = {int(x): t for x,t in data['offsets'].items()}
            actual = {x:{a^offsets[x] for a in A} for x,A in shapes.items()}
            assert {str(x):sorted(A) for x,A in actual.items()} == data['witness_fibres']
            record['coordinate_arithmetic_primitive_vectors_checked'] = verify_coordinate_witness(
                data['n'], actual, data['ring'], directions)
        else:
            raise AssertionError('Only completed proof/witness cases belong in this suite.')
        cases.append(record)

    # Independent exhaustive small-space result, without invoking the CNF.
    shapes2 = [set(),{0},{0,1},{0,2},{0,3},{0,1,2},{0,1,2,3}]
    n2_counts = {ring:{'SAT':0,'UNSAT':0} for ring in ('dual','z4')}
    for ring in n2_counts:
        lines,masks = direct_all_lines(2,ring)
        for spec in itertools.product(range(7),repeat=4):
            shapes = {x:shapes2[k] for x,k in enumerate(spec) if shapes2[k]}
            basis = affine_basis(shapes)
            free = [x for x in shapes if x not in basis]
            good = any(direct_good(shapes,dict(zip(free,t)),lines,masks)
                       for t in itertools.product(range(4),repeat=len(free)))
            n2_counts[ring]['SAT' if good else 'UNSAT'] += 1
    archived = json.loads((here/'translation_completion_validation.json').read_text())
    assert n2_counts == archived['n2_status_counts']

    # All three-set systems in F2^2 and every relative translation: a complete
    # check of the new tree-overlap inequality beyond its two-set base case.
    subsets = [{x for x in range(4) if mask>>x&1} for mask in range(16)]
    tree_checks = 0
    for A,B,C in itertools.product(subsets,repeat=3):
        bound = tree_union_upper_bound([A,B,C],4)['upper_bound']
        for s,t in itertools.product(range(4),repeat=2):
            assert len(A | {x^s for x in B} | {x^t for x in C}) <= bound
            tree_checks += 1
    result = {'status':'PASS','solver_dependency':False,'cases':cases,
              'exhaustive_n2_direct_classification':n2_counts,
              'exhaustive_F2_squared_three_set_tree_checks':tree_checks,
              'scope':'Fixed-shape translations and stated local direction blocks only; no full n5 closure.'}
    (here/'STANDARD_LIBRARY_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
