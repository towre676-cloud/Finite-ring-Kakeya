"""Orbits of AGL_n(F_2) on subsets of F_2^n (the heavy support B), with the
v0.2 necessary conditions for a no-full-fibre Kakeya configuration of total
size <= ub:

  h = |B| >= 1 + ceil(sqrt(N-1))                        (v0.2 Corollary 12)
  2 (N - 1 - d) <= L <= N - h,  d = |(B+B) \\ {0}|        (v0.2 Corollary 11, q >= 2)
  3h + 2 * 2 (N - 1 - d) <= ub                          (each heavy >= 3, each light = 2)
"""
import json, sys
from math import isqrt


def gens(n):
    N = 1 << n
    def lin(M):  # M: list of column images of basis vectors
        def f(x):
            y = 0
            for i in range(n):
                if x >> i & 1:
                    y ^= M[i]
            return y
        return [f(x) for x in range(N)]
    G = []
    # translation by e_1
    G.append([x ^ 1 for x in range(N)])
    # cyclic shift of coordinates
    G.append(lin([1 << ((i + 1) % n) for i in range(n)]))
    # transvection e_2 -> e_2 + e_1
    M = [1 << i for i in range(n)]; M[1] ^= 1
    G.append(lin(M))
    # transposition of e_1, e_2
    M = [1 << i for i in range(n)]; M[0], M[1] = M[1], M[0]
    G.append(lin(M))
    return G


def orbits(n):
    N = 1 << n
    G = gens(n)
    seen = bytearray(1 << N)
    reps = []
    for mask in range(1 << N):
        if seen[mask]:
            continue
        orb = [mask]; seen[mask] = 1; i = 0
        while i < len(orb):
            m = orb[i]; i += 1
            for g in G:
                im = 0
                x = m
                while x:
                    lo = x & -x
                    im |= 1 << g[lo.bit_length() - 1]
                    x ^= lo
                if not seen[im]:
                    seen[im] = 1; orb.append(im)
        reps.append((mask, len(orb)))
    return reps


def admissible(n, ub):
    N = 1 << n
    hmin = 1 + isqrt(N - 2) + 1 if (isqrt(N - 1) ** 2 != N - 1) else 1 + isqrt(N - 1)
    out = []
    for mask, size in orbits(n):
        B = [x for x in range(N) if mask >> x & 1]
        h = len(B)
        if h < hmin:
            continue
        D = {a ^ b for a in B for b in B} - {0}
        e = N - 1 - len(D)
        if 2 * e > N - h:
            continue
        if 3 * h + 4 * e > ub:
            continue
        out.append({"B": B, "h": h, "d": len(D), "orbit_size": size})
    return out


if __name__ == "__main__":
    n, ub = int(sys.argv[1]), int(sys.argv[2])
    o = orbits(n)
    assert sum(sz for _, sz in o) == 1 << (1 << n)
    adm = admissible(n, ub)
    print(json.dumps({"n": n, "orbits_total": len(o), "admissible": len(adm),
                      "by_h": {h: sum(1 for x in adm if x["h"] == h) for h in sorted({x["h"] for x in adm})}}))
    json.dump(adm, open(f"results/heavy_orbits_n{n}_ub{ub}.json", "w"))
