"""tilt.py -- the two length-l chain rings with residue field F_p, in Teichmuller coordinates.

Notation (NOTATION.md):
    A_{p,l}       = W_l(F_p) = Z/p^l             (mixed characteristic)       code  W{p}^{l}
    A_{p,l}^flat  = F_p[t]/(t^l)                 (equal characteristic)       code  T{p}^{l}
    pi            uniformiser (p, resp. t);  rho : A^n -> F_p^n  reduction mod pi
    [a]           Teichmuller lift of a in F_p   (a^{p^{l-1}} lifted, resp. the constant a)
    gamma(a,b)    carry cocycle: [a]+[b] = [a+b] + pi*[gamma(a,b)] + O(pi^2);  gamma == 0 on the flat side
    kappa_n(A)    least |K| for K a Kakeya set in A^n
    Delta_n(p,l)  = kappa_n(A_{p,l}) - kappa_n(A_{p,l}^flat)   (tilt defect)

Every element of A is written x = [x_0] + pi [x_1] + ... + pi^{l-1}[x_{l-1}], digits x_i in F_p.
Elements are encoded as integers 0..p^l-1 internally; `digits` / `from_digits` convert.
"""
import itertools


class ChainRing:
    def __init__(self, p, l, flat):
        self.p, self.l, self.flat = p, l, flat
        self.q = p ** l
        self.code = f"{'T' if flat else 'W'}{p}^{l}"
        self.latex = (r"A_{%d,%d}^\flat" if flat else r"A_{%d,%d}") % (p, l)
        q = self.q
        if flat:
            # integer code = sum c_i p^i, c_i the coefficient of t^i
            dec = lambda x: [(x // p ** i) % p for i in range(l)]
            enc = lambda c: sum((ci % p) * p ** i for i, ci in enumerate(c))
            def add(x, y): return enc([a + b for a, b in zip(dec(x), dec(y))])
            def mul(x, y):
                a, b = dec(x), dec(y); c = [0] * l
                for i in range(l):
                    for j in range(l - i): c[i + j] += a[i] * b[j]
                return enc(c)
            self._teich = lambda a: a % p
        else:
            add = lambda x, y: (x + y) % q
            mul = lambda x, y: (x * y) % q
            self._teich = lambda a: pow(a % p, p ** (l - 1), q) if a % p else 0
        self.els = list(range(q))
        self.A = [[add(a, b) for b in self.els] for a in self.els]
        self.M = [[mul(a, b) for b in self.els] for a in self.els]
        self.units = [x for x in self.els if x % p]
        self.pi = p                      # code of the uniformiser in both encodings
        self.T = [self._teich(a) for a in range(p)]
        self.neg = [next(y for y in self.els if self.A[x][y] == 0) for x in self.els]
        # Teichmuller digit expansion, computed from the ring tables only
        self._dig = {}
        for ds in itertools.product(range(p), repeat=l):
            self._dig[self.from_digits(ds)] = ds
        assert len(self._dig) == q

    def teich(self, a):
        return self.T[a % self.p]

    def from_digits(self, ds):
        x, piw = 0, 1
        for d in ds:
            x = self.A[x][self.M[piw][self.T[d]]]
            piw = self.M[piw][self.pi]
        return x

    def digits(self, x):
        return self._dig[x]

    def gamma(self, a, b):
        """carry cocycle: second Teichmuller digit of [a]+[b]."""
        return self.digits(self.A[self.teich(a)][self.teich(b)])[1] if self.l > 1 else 0


def A(p, l):
    return ChainRing(p, l, flat=False)


def Aflat(p, l):
    return ChainRing(p, l, flat=True)


def ring(code):
    """'W2^2', 'T5^2', ... ; legacy codes Z4 D2 Z8 T8 Z9 D3 Z25 D5 accepted with a mapping."""
    legacy = {'Z4': 'W2^2', 'D2': 'T2^2', 'Z8': 'W2^3', 'T8': 'T2^3', 'Z9': 'W3^2', 'D3': 'T3^2',
              'Z16': 'W2^4', 'T16': 'T2^4', 'Z25': 'W5^2', 'D5': 'T5^2', 'Z27': 'W3^3',
              'T27': 'T3^3', 'Z49': 'W7^2', 'D7': 'T7^2'}
    code = legacy.get(code, code)
    kind, rest = code[0], code[1:]
    p, l = map(int, rest.split('^'))
    return ChainRing(p, l, flat=(kind == 'T'))


def directions(R, n):
    seen, dirs = set(), []
    U = set(R.units)
    for v in itertools.product(R.els, repeat=n):
        if v in seen or not any(x in U for x in v): continue
        cls = {tuple(R.M[u][x] for x in v) for u in R.units}
        seen |= cls; dirs.append(min(cls))
    return dirs


def line(R, x, v):
    return frozenset(tuple(R.A[x[i]][R.M[s][v[i]]] for i in range(len(x))) for s in R.els)


def kakeya_system(R, n):
    dirs = directions(R, n)
    pts = list(itertools.product(R.els, repeat=n))
    fam = []
    for v in dirs:
        seen, Ls = set(), []
        for x in pts:
            if x in seen: continue
            L = line(R, x, v); seen |= L; Ls.append(L)
        fam.append(Ls)
    return dirs, pts, fam


def is_kakeya(R, n, K, fam=None):
    if fam is None: fam = kakeya_system(R, n)[2]
    K = set(K)
    return all(any(L <= K for L in Ls) for Ls in fam)
