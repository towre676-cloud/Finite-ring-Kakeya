"""Exact arithmetic for R^n with R in {Z/4Z, F_2[eps]/(eps^2)}.

A vector of R^n is encoded by its residue/fibre decomposition x = a + pi*u with
a, u in V = F_2^n (binary representatives), packed as the integer a | (u << n).
All operations are exact integer bit manipulations; nothing is approximated.
"""
from itertools import product

RINGS = ("Z4", "D2")  # Z/4Z and dual numbers F_2[eps]/(eps^2)


def pack(a, u, n):
    return a | (u << n)


def unpack(x, n):
    m = (1 << n) - 1
    return x & m, x >> n


def add(R, x, y, n):
    a1, u1 = unpack(x, n)
    a2, u2 = unpack(y, n)
    if R == "D2":
        return pack(a1 ^ a2, u1 ^ u2, n)
    # Z/4: (a1+2u1)+(a2+2u2) = (a1^a2) + 2(u1^u2^(a1&a2))  -- binary carry
    return pack(a1 ^ a2, u1 ^ u2 ^ (a1 & a2), n)


def scal(R, t, x, n):
    """t in R encoded as (t0, t1) meaning t0 + pi*t1."""
    t0, t1 = t
    a, u = unpack(x, n)
    if t0 == 0:
        return pack(0, a if t1 else 0, n)
    # t = 1 + pi*t1 : (1+pi t1)(a + pi u) = a + pi(u + t1 a)  in both rings
    # (in Z/4, 3*(a+2u) = a + 2(a+u) mod 4 with a,u in {0,1}: 3a = a + 2a, 6u = 2u.)
    return pack(a, u ^ (a if t1 else 0), n)


SCALARS = [(0, 0), (1, 0), (0, 1), (1, 1)]  # 0, 1, pi, 1+pi
UNITS = [(1, 0), (1, 1)]


def all_points(n):
    return range(1 << (2 * n))


def directions(n):
    """Representatives of primitive directions modulo units: b = v + pi w,
    v != 0, w taken modulo <v> (since (1+pi)(v+pi w) = v + pi(w+v))."""
    reps = []
    for v in range(1, 1 << n):
        seen = set()
        for w in range(1 << n):
            key = min(w, w ^ v)
            if key in seen:
                continue
            seen.add(key)
            reps.append(pack(v, key, n))
    return reps


def line(R, x, b, n):
    return frozenset(add(R, x, scal(R, t, b, n), n) for t in SCALARS)


def lines_in_direction(R, b, n):
    """All distinct lines with direction b (cosets of R*b)."""
    out, covered = [], set()
    for x in all_points(n):
        if x in covered:
            continue
        L = line(R, x, b, n)
        covered |= L
        out.append(L)
    return out


def is_kakeya(R, K, n):
    K = set(K)
    for b in directions(n):
        if not any(L <= K for L in lines_in_direction(R, b, n)):
            return False
    return True


def K_star(n):
    """The conjectured extremal set: full zero fibre plus {v, v + pi v}."""
    S = {pack(0, u, n) for u in range(1 << n)}
    for v in range(1, 1 << n):
        S.add(pack(v, 0, n))
        S.add(pack(v, v, n))
    return S


def fibres(K, n):
    A = {a: set() for a in range(1 << n)}
    for x in K:
        a, u = unpack(x, n)
        A[a].add(u)
    return A


def carry_class(R, a, v):
    return 0 if R == "D2" else (a & v)


def covers_via_fibre_identity(R, K, n):
    """Check the fibre covering identity for every residue direction v != 0:
    union over unordered {a, a+v} of P_v(A_a) + P_v(A_{a+v}) + c_R(a,v)
    equals V/<v>.  Classes mod <v> are represented by min(w, w^v)."""
    A = fibres(K, n)
    cls = lambda w, v: min(w, w ^ v)
    for v in range(1, 1 << n):
        P = {a: {cls(u, v) for u in A[a] if (u ^ v) in A[a]} for a in A}
        got = set()
        for a in A:
            if a > (a ^ v):
                continue
            c = carry_class(R, a, v)
            for p in P[a]:
                for q in P[a ^ v]:
                    got.add(cls(p ^ q ^ c, v))
        if len(got) != (1 << (n - 1)):
            return False
    return True
