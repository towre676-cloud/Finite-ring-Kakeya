"""kappa.py -- exact kappa_2(A) by SAT descent (CaDiCaL, incremental totaliser), in the new ring codes.

    python3 kappa.py W2^2 T2^2 W3^2 T3^2 W2^3 T2^3

Symmetry break: the (1,0)- and (0,1)-lines are translated onto the axes (valid in the plane).
This reproduces the certified ledger values; the DRUP-checked certificates remain those of the
earlier packages (cert_n3/, sat/counting/).  Output: results/kappa2.json with the tilt defect Delta_2.
"""
import sys, json, time, os
from pysat.card import ITotalizer
from pysat.solvers import Solver
from tilt import ring, kakeya_system


def kappa2(code, start=None):
    R = ring(code)
    dirs, pts, fam = kakeya_system(R, 2)
    idx = {x: i + 1 for i, x in enumerate(pts)}
    top = len(pts)
    cls = []
    xaxis = frozenset((s, 0) for s in R.els); yaxis = frozenset((0, s) for s in R.els)
    for Ls in fam:
        lits = []
        for L in Ls:
            top += 1; y = top; lits.append(y)
            for q in L: cls.append([-y, idx[q]])
        cls.append(lits)
    for L in (xaxis, yaxis):
        for q in L: cls.append([idx[q]])
    tot = ITotalizer(lits=list(range(1, len(pts) + 1)), ubound=len(pts), top_id=top)
    S = Solver(name='cadical195', bootstrap_with=cls + tot.cnf.clauses)
    t0 = time.time()
    assert S.solve()
    best = sum(1 for v in S.get_model()[:len(pts)] if v > 0)
    witness = None
    while True:
        K = best - 1
        if not S.solve(assumptions=[-tot.rhs[K]]): break
        m = S.get_model()
        best = sum(1 for v in m[:len(pts)] if v > 0)
        witness = sorted(pts[i] for i in range(len(pts)) if m[i] > 0)
    return R, best, round(time.time() - t0, 2)


if __name__ == '__main__':
    codes = sys.argv[1:] or ['W2^2', 'T2^2', 'W2^3', 'T2^3', 'W3^2', 'T3^2']
    res = {}
    for c in codes:
        R, k, t = kappa2(c)
        res[c] = {'ring': R.latex, 'kappa_2': k, 'seconds': t}
        print(c, k, t, flush=True)
    delta = {}
    for c in codes:
        if c[0] == 'W' and 'T' + c[1:] in res:
            delta[c[1:]] = res[c]['kappa_2'] - res['T' + c[1:]]['kappa_2']
    os.makedirs('results', exist_ok=True)
    json.dump({'kappa_2': res, 'Delta_2': delta}, open('results/kappa2.json', 'w'), indent=1)
    print('Delta_2', delta)
