"""checks.py -- certificates for the notation reform (run: python3 checks.py).  Writes results/notation_checks.json.

N1  carry cocycle: gamma computed from the ring tables equals (a^p+b^p-(a+b)^p)/p mod p on A_{p,2}
    and 0 on A_{p,2}^flat; at p=2 it is a AND b (the old kappa(a,alpha)=a^alpha).
N2  fibre-trace law (l=2): for x=[a]+pi[b], v=[alpha]+pi[beta], alpha!=0, the digit set of the line over
    a+sigma*alpha is b+sigma*beta+gamma(a,sigma*alpha)+<alpha>, exhaustively, in both rings.
N3  the old c_a(sigma) of Proposition 3 is a coordinate artifact: with Teichmuller slopes the offset is
    g+sigma*delta exactly; with the integer representative a it is g+sigma*(delta+e(a)), e(a)=(a-[a])/p,
    a reparametrisation of the lift index delta.
N4  Propositions 2 and 3 rebuilt in Teichmuller coordinates, sizes and the Kakeya property verified by
    brute force in both rings.
"""
import itertools, json, os, time
from tilt import A, Aflat, line, kakeya_system, is_kakeya

out = {}
t0 = time.time()

# ---------- N1
n1 = {}
for p in (2, 3, 5, 7):
    for R in (A(p, 2), Aflat(p, 2)):
        ok = True
        for a in range(p):
            for b in range(p):
                want = 0 if R.flat else ((a ** p + b ** p - (a + b) ** p) // p) % p
                ok &= R.gamma(a, b) == want
                if p == 2: ok &= R.gamma(a, b) == (0 if R.flat else a & b)
        n1[R.code] = ok
out['N1_gamma_formula'] = n1
assert all(n1.values())


# ---------- N2
def vadd(R, x, y): return tuple(R.A[a][b] for a, b in zip(x, y))
def vdig(R, x, i): return tuple(R.digits(c)[i] for c in x)
def lift(R, ds0, ds1): return tuple(R.from_digits((u, w)) for u, w in zip(ds0, ds1))

n2 = {}
for p, n in ((2, 2), (2, 3), (3, 2), (3, 3), (5, 2)):
    for R in (A(p, 2), Aflat(p, 2)):
        F = list(itertools.product(range(p), repeat=n))
        D0 = [R.digits(c)[0] for c in R.els]; D1 = [R.digits(c)[1] for c in R.els]
        G = [[R.gamma(u, w) for w in range(p)] for u in range(p)]
        tot = bad = 0
        for a in F:
            for b in F:
                x = lift(R, a, b)
                for al in F:
                    if not any(al): continue
                    for be in F:
                        v = lift(R, al, be)
                        got = {}
                        for s in R.els:                       # one pass over the line, bucketed by base point
                            y = [R.A[x[i]][R.M[s][v[i]]] for i in range(n)]
                            got.setdefault(tuple(D0[c] for c in y), set()).add(tuple(D1[c] for c in y))
                        for sg in range(p):
                            base = tuple((ai + sg * ci) % p for ai, ci in zip(a, al))
                            off = [(b[i] + sg * be[i] + G[a[i]][sg * al[i] % p]) % p for i in range(n)]
                            pred = {tuple((off[i] + r * al[i]) % p for i in range(n)) for r in range(p)}
                            tot += 1; bad += got[base] != pred
        n2[f"{R.code} n={n}"] = {'incidences': tot, 'mismatches': bad}
        assert bad == 0
out['N2_trace_law'] = n2

# ---------- N3
n3 = {}
for p in (3, 5, 7):
    for R in (A(p, 2), Aflat(p, 2)):
        teich_ok, naive_shift = True, set()
        for a in range(p):
            e = R.digits(a)[1]                       # second digit of the integer representative a
            naive_shift.add(e)
            for d in range(p):
                for g in range(p):
                    x = (0, R.from_digits((0, g)))
                    vT = (R.from_digits((1, 0)), R.from_digits((a, d)))
                    vN = (R.from_digits((1, 0)), R.A[a][R.M[R.pi][R.teich(d)]])   # old: a + eps*delta
                    for sg in range(2, p):
                        for v, want in ((vT, (g + sg * d) % p), (vN, (g + sg * (d + e)) % p)):
                            fib = {R.digits(y[1])[1] for y in line(R, x, v)
                                   if R.digits(y[0])[0] == sg and R.digits(y[1])[0] == (sg * a) % p
                                   and R.digits(y[0])[1] == 0}
                            # restrict to the X-digit-1 = 0 slice: the trace's Y-digit at that point
                            teich_ok &= fib == {want}
        n3[R.code] = {'teichmuller_offset_is_g+sigma*delta': teich_ok,
                      'naive_digit_offsets_e(a)': sorted(naive_shift)}
        assert teich_ok
out['N3_prop3_carry_is_coordinate_artifact'] = n3


# ---------- N4
def prop2(R, n):
    """one full fibre: rho^{-1}(0) plus, for each alpha != 0 and each lift beta, the line through pi[beta']
    with trace <alpha> over alpha.  (p = 2.)"""
    p = R.p
    F = list(itertools.product(range(p), repeat=n))
    K = {lift(R, (0,) * n, b) for b in F}
    for al in F:
        if not any(al): continue
        for be in F:
            # trace over alpha is b + beta + gamma(0,alpha) + <alpha> = b + beta + <alpha>; take b = -beta
            b = tuple((-c) % p for c in be)
            K |= line(R, lift(R, (0,) * n, b), lift(R, al, be))
    return K


def M_of(p):
    best, arg = None, None
    for g in itertools.product(range(p), repeat=p):
        s = sum(len({(g[d] + sg * d) % p for d in range(p)}) for sg in range(2, p))
        if best is None or s < best: best, arg = s, g
    return best, arg


def prop3(R, g):
    p = R.p
    K = set()
    for X in (0, 1):                                     # full fibres over O and over ell* = {x = 1}
        for y in range(p) if X == 1 else (0,):
            for d0, d1 in itertools.product(range(p), repeat=2):
                K.add((R.from_digits((X, d0)), R.from_digits((y, d1))))
    for a in range(p):
        for d in range(p):
            K |= line(R, (0, R.from_digits((0, g[d]))), (R.from_digits((1, 0)), R.from_digits((a, d))))
    return K

n4 = {}
for n in (2, 3, 4, 5):
    for R in (A(2, 2), Aflat(2, 2)):
        K = prop2(R, n)
        ok = is_kakeya(R, n, K)
        n4[f"Prop2 {R.code} n={n}"] = {'size': len(K), 'law': 3 * 2 ** n - 2, 'kakeya': ok}
        assert ok and len(K) == 3 * 2 ** n - 2
for p in (3, 5, 7):
    Mp, g = M_of(p)
    for R in (A(p, 2), Aflat(p, 2)):
        K = prop3(R, g)
        ok = is_kakeya(R, 2, K)
        n4[f"Prop3 {R.code}"] = {'M(p)': Mp, 'g': list(g), 'size': len(K),
                                 'formula': (p + 1) * p * p + p * p * Mp, 'kakeya': ok}
        assert ok and len(K) == (p + 1) * p * p + p * p * Mp
out['N4_constructions'] = n4
out['wall_seconds'] = round(time.time() - t0, 1)

os.makedirs('results', exist_ok=True)
json.dump(out, open('results/notation_checks.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
