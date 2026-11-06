"""Replay of the Round 4 certified result (maximum fibre 19, supports 11 and 12).

Steps:
  1. compile the C++ tools (orbit enumerator, spectrum census, sumset table, two DRAT checkers);
  2. regenerate the support-orbit list, pair-spectrum census and sumset table and compare
     them byte-for-byte with data/;
  3. check orbit-stabilizer sums against a Mobius count of spanning sets;
  4. for each of the 38 covering support orbits of size 11 or 12 (m = 19): encode the CNF,
     solve with CaDiCaL (PySAT) with proof logging, and check the DRAT proof with
     src/dratback (backward) and, with --both, also src/dratcheck (forward).

Requirements: Python 3.10+, g++ (C++17), python-sat (pip install python-sat).
Usage:  python3 VERIFY_ROUND4.py [--quick] [--both] [--jobs N]
  --quick  checks only the first orbit of each size (minutes instead of ~1-2 hours).
Do not run with python -O.
"""
import sys, os, subprocess, json, hashlib, time, tempfile
from math import comb
from concurrent.futures import ProcessPoolExecutor

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC, DATA, OUT = ROOT + '/src', ROOT + '/data', ROOT + '/replay_out'
sys.path.insert(0, SRC)
if sys.flags.optimize:
    raise SystemExit('run without -O')

def sh(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode not in (0,) and not kw.get('check_ok'):
        pass
    return r

def build():
    os.makedirs(OUT, exist_ok=True)
    for name in ['orbits_all', 'spectra32', 'msum', 'dratcheck', 'dratback']:
        r = sh(['g++', '-O2', '-std=c++17', '-o', f'{OUT}/{name}', f'{SRC}/{name}.cpp'])
        assert r.returncode == 0, r.stderr
    print('build PASS', flush=True)

def regenerate():
    for exe, ref in [('orbits_all', 'orbits_all.txt'), ('spectra32', 'spec32.csv'), ('msum', 'Mtable.txt')]:
        r = sh([f'{OUT}/{exe}'])
        assert r.returncode == 0
        a = r.stdout.encode(); b = open(f'{DATA}/{ref}', 'rb').read()
        assert hashlib.sha256(a).digest() == hashlib.sha256(b).digest(), ref + ' differs'
        if exe == 'orbits_all':
            stats = r.stderr
        print(f'regenerate {ref} PASS', flush=True)
    # orbit-stabilizer vs Mobius count of spanning k-subsets of PG(4,2)
    def gb(n, k):
        num = den = 1
        for i in range(k): num *= 2 ** (n - i) - 1; den *= 2 ** (i + 1) - 1
        return num // den
    GL = 9999360
    tot = {}
    for line in open(f'{DATA}/orbits_all.txt'):
        k, T, st, cov = map(int, line.split())
        assert GL % st == 0
        tot[k] = tot.get(k, 0) + GL // st
    for k in range(5, 32):
        mob = sum(gb(5, j) * (-1) ** (5 - j) * 2 ** ((5 - j) * (4 - j) // 2) * comb(2 ** j - 1, k) for j in range(6))
        assert tot[k] == mob, k
    print('orbit-stabilizer completeness PASS (k=5..31)', flush=True)

def one(args):
    m, Tm, both = args
    import encode_cnf2 as E
    from pysat.solvers import Solver
    SPEC = E.load_spectra(f'{DATA}/spec32.csv'); M = E.load_M(f'{DATA}/Mtable.txt'); SUBS = E.all_subspaces()
    T = [x for x in range(1, 32) if Tm >> x & 1]
    t = time.time()
    f = E.encode(T, m, SPEC, M, SUBS)
    with tempfile.TemporaryDirectory(dir=OUT) as d:
        cnf, prf = d + '/f.cnf', d + '/p.drat'
        E.write_dimacs(f, cnf)
        h = hashlib.sha256(open(cnf, 'rb').read()).hexdigest()
        s = Solver(name='cadical195', with_proof=True, bootstrap_with=f.cl)
        sat = s.solve()
        if sat:
            return {'m': m, 'T': Tm, 'status': 'SAT_RELAXATION', 'cnf_sha256': h}
        with open(prf, 'w') as o: o.write('\n'.join(s.get_proof()) + '\n')
        s.delete()
        res = {'m': m, 'T': Tm, 'cnf_sha256': h, 'clauses': len(f.cl)}
        checks = ['dratback'] + (['dratcheck'] if both else [])
        ok = True
        for c in checks:
            r = sh([f'{OUT}/{c}', cnf, prf])
            res[c] = r.stdout.strip(); ok = ok and r.returncode == 0 and r.stdout.startswith('s VERIFIED')
        res['status'] = 'EXCLUDED_DRAT_VERIFIED' if ok else 'CHECK_FAILED'
        res['sec'] = round(time.time() - t, 1)
        return res

def certify(quick, both, jobs):
    orbs = []
    for line in open(f'{DATA}/orbits_all.txt'):
        k, T, st, cov = map(int, line.split())
        if cov and k + 1 in (11, 12): orbs.append((k + 1, T))
    assert sum(1 for s, _ in orbs if s == 11) == 13 and sum(1 for s, _ in orbs if s == 12) == 25
    if quick:
        orbs = [next(o for o in orbs if o[0] == 11), next(o for o in orbs if o[0] == 12)]
    results = []
    with ProcessPoolExecutor(jobs) as ex:
        for r in ex.map(one, [(19, T, both) for s, T in orbs]):
            print(r['m'], r['T'], r['status'], r.get('sec'), flush=True); results.append(r)
    good = all(r['status'] == 'EXCLUDED_DRAT_VERIFIED' for r in results)
    receipt = {'status': 'PASS' if good else 'FAIL', 'quick': quick, 'orbits_checked': len(results),
               'claim': 'm=19, pair-active support 11 or 12: no solution of conditions (A)-(E); every case refuted by a checked DRAT proof',
               'results': results}
    open(f'{ROOT}/VERIFICATION_RECEIPT_ROUND4.json', 'w').write(json.dumps(receipt, indent=1) + '\n')
    print('certification', receipt['status'], flush=True)
    return good

if __name__ == '__main__':
    quick = '--quick' in sys.argv; both = '--both' in sys.argv
    jobs = int(sys.argv[sys.argv.index('--jobs') + 1]) if '--jobs' in sys.argv else os.cpu_count()
    build(); regenerate()
    sys.exit(0 if certify(quick, both, jobs) else 1)
