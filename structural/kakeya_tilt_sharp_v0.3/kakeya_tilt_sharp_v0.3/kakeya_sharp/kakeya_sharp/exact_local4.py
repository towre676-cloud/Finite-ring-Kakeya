"""Model X: the strongest ring-independent relaxation used for n = 4.

For every residue a the fibre's pair vector (s_a, p_a(1..N-1)) is constrained
to the exact table of realizable local types (all subsets of F_2^n, computed
here from scratch; it must reproduce the 3,967 types of the v0.2 catalogue).
On top of that:

  (cover)  for each v != 0:  sum over edges {a, a+v} of c_{a,v} >= N/2, where
           c <= min(N/2, p_a(v) p_{a+v}(v)) and c <= p_a p_b / 2 whenever the
           shared-period group J (Theorem 14 of v0.2) is nontrivial;
  (S1)     affine size ordering (sound);
  options  smax (max fibre size), hmin (number of fibres of size >= 3),
           full0 (fibre 0 full).

J is nontrivial iff some h not in <v> lies in H_A and in H_B + <v>, where
H_A = {0} u {h : 2 p_A(h) = s_A} is the stabiliser read from the pair vector.
Every Kakeya set in either ring induces a feasible point, so infeasibility of
X with ub = m proves k(R, n) > m in both rings within the stated case."""
import sys, json, time
from ortools.sat.python import cp_model


def local_types(n):
    N = 1 << n
    seen = {}
    for mask in range(1 << N):
        A = [u for u in range(N) if mask >> u & 1]
        S = set(A)
        p = tuple(sum(1 for u in A if (u ^ v) in S) // 2 for v in range(1, N))
        key = (len(A),) + p
        if key not in seen:
            seen[key] = mask
    return seen


def build(n, ub, smax=None, hmin=None, full0=False, period=True, sym=True, types=None, heavy=None, feas=False, sq=True, tri=True, order=False):
    N = 1 << n
    H = N >> 1
    if types is None:
        types = local_types(n)
    rows = [k for k in types if (smax is None or k[0] <= smax)]
    m = cp_model.CpModel()
    s, p, stab = {}, {}, {}
    for a in range(N):
        s[a] = m.NewIntVar(0, N, f"s{a}")
        for v in range(1, N):
            p[a, v] = m.NewIntVar(0, H, f"p{a}_{v}")
        if heavy is None:
            ra = rows
        elif a in heavy:
            ra = [k for k in rows if k[0] >= 3]
        else:
            ra = [k for k in rows if k[0] in (0, 2)]   # singletons are dominated by empty
        m.AddAllowedAssignments([s[a]] + [p[a, v] for v in range(1, N)], ra)
        for v in range(1, N):
            b = m.NewBoolVar(f"st{a}_{v}")   # v is a period of A_a (and A_a nonempty)
            m.Add(2 * p[a, v] == s[a]).OnlyEnforceIf(b)
            m.Add(2 * p[a, v] != s[a]).OnlyEnforceIf(b.Not())
            ne = m.NewBoolVar("")
            m.Add(s[a] >= 1).OnlyEnforceIf(ne)
            m.Add(s[a] == 0).OnlyEnforceIf(ne.Not())
            sb = m.NewBoolVar("")
            m.AddBoolAnd([b, ne]).OnlyEnforceIf(sb)
            m.AddBoolOr([b.Not(), ne.Not()]).OnlyEnforceIf(sb.Not())
            stab[a, v] = sb
    Y = {}
    if order:
        # order encoding y[a,v,k] = [p_a(v) >= k], k = 1..H
        for a in range(N):
            for v in range(1, N):
                ys = [m.NewBoolVar(f"y{a}_{v}_{k}") for k in range(1, H + 1)]
                for k in range(len(ys) - 1):
                    m.AddImplication(ys[k + 1], ys[k])
                m.Add(p[a, v] == sum(ys))
                Y[a, v] = ys
            # incidences: number of directions with a v-pair is at most the pair budget (redundant, linear)
        for v in range(1, N):
            # energy cut in linear form: sum_a p_a(v)^2 = sum_a sum_k (2k-1) y >= N
            m.Add(sum((2 * k + 1) * Y[a, v][k] for a in range(N) for k in range(H)) >= N)
    for v in range(1, N):
        terms = []
        for a in range(N):
            b = a ^ v
            if a > b:
                continue
            if order:
                # p_a p_b = sum_{i,j} [p_a >= i][p_b >= j]; c <= that sum (and c <= H separately)
                zs = []
                for i in range(1, H + 1):
                    for j in range(1, H + 1):
                        z = m.NewBoolVar("")
                        m.AddImplication(z, Y[a, v][i - 1]); m.AddImplication(z, Y[b, v][j - 1])
                        m.AddBoolOr([Y[a, v][i - 1].Not(), Y[b, v][j - 1].Not(), z])
                        zs.append(z)
                cap_lin = m.NewIntVar(0, H * H, "")
                m.Add(cap_lin == sum(zs))
            prod = m.NewIntVar(0, H * H, "")
            m.AddMultiplicationEquality(prod, [p[a, v], p[b, v]])
            c = m.NewIntVar(0, H, f"c{a}_{v}")
            m.Add(c <= prod)
            if order:
                m.Add(c <= cap_lin)
            if period:
                lits = []
                for h in range(1, N):
                    if h == v:
                        continue
                    # h in H_A, and (h in H_B or h+v in H_B)
                    for hb in (h, h ^ v):
                        if hb == 0:
                            continue
                        l = m.NewBoolVar("")
                        m.AddBoolAnd([stab[a, h], stab[b, hb]]).OnlyEnforceIf(l)
                        m.AddBoolOr([stab[a, h].Not(), stab[b, hb].Not()]).OnlyEnforceIf(l.Not())
                        lits.append(l)
                j2 = m.NewBoolVar("")
                m.AddBoolOr(lits).OnlyEnforceIf(j2)
                m.AddBoolAnd([x.Not() for x in lits]).OnlyEnforceIf(j2.Not())
                m.Add(2 * c <= prod).OnlyEnforceIf(j2)
            terms.append(c)
        m.Add(sum(terms) >= H)
    if sym and heavy is None:
        for a in range(N):
            m.Add(s[0] >= s[a])
            if a:
                m.Add(s[1] >= s[a])
        for k in range(2, n + 1):
            sp = {0}
            for i in range(k - 1):
                sp |= {x ^ (1 << i) for x in sp}
            for a in range(N):
                if a not in sp:
                    m.Add(s[1 << (k - 1)] >= s[a])
    if full0:
        m.Add(s[0] == N)
    if hmin is not None:
        hv = []
        for a in range(N):
            b = m.NewBoolVar("")
            m.Add(s[a] >= 3).OnlyEnforceIf(b)
            m.Add(s[a] <= 2).OnlyEnforceIf(b.Not())
            hv.append(b)
        m.Add(sum(hv) >= hmin)
    m.Add(sum(s.values()) <= ub)
    # redundant pair-budget identity per fibre (helps the LP relaxation)
    for a in range(N):
        pb = m.NewIntVar(0, N * (N - 1) // 2, "")
        m.AddElement(s[a], [k * (k - 1) // 2 for k in range(N + 1)], pb)
        m.Add(sum(p[a, v] for v in range(1, N)) == pb)
    if tri:
        # redundant linear copies of Theorem 7.1 (defect subadditivity) and d <= N - s,
        # implied by the exact type table but visible to the LP relaxation
        for a in range(N):
            for v in range(1, N):
                m.Add(s[a] - 2 * p[a, v] <= N - s[a])
                for w in range(v + 1, N):
                    m.Add(s[a] - 2 * p[a, v ^ w] <= 2 * s[a] - 2 * p[a, v] - 2 * p[a, w])
    if sq:
        # Cauchy-Schwarz cut: sum_{a} p_a(v) p_{a+v}(v) <= sum_a p_a(v)^2, and the left side
        # (ordered) is >= 2H by the covering condition, so sum_a p_a(v)^2 >= 2H = N.
        sqv = {}
        for a in range(N):
            for v in range(1, N):
                sqv[a, v] = m.NewIntVar(0, H * H, "")
                m.AddElement(p[a, v], [k * k for k in range(H + 1)], sqv[a, v])
        for v in range(1, N):
            m.Add(sum(sqv[a, v] for a in range(N)) >= N)
        m.Add(sum(sqv.values()) >= N * (N - 1))
    if not feas:
        m.Minimize(sum(s.values()))
    return m, s, p, len(types)


def solve(n, ub, time_limit=600, workers=2, **kw):
    t0 = time.time()
    m, s, p, ntypes = build(n, ub, **kw)
    sv = cp_model.CpSolver()
    sv.parameters.max_time_in_seconds = time_limit
    sv.parameters.num_workers = workers
    st = sv.Solve(m)
    out = {"n": n, "ub": ub, "options": {k: v for k, v in kw.items() if k != "types"},
           "local_types": ntypes, "status": sv.StatusName(st), "seconds": round(time.time() - t0, 2),
           "bound": sv.BestObjectiveBound()}
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        out["value"] = sv.ObjectiveValue()
        out["sizes"] = [sv.Value(s[a]) for a in range(1 << n)]
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int); ap.add_argument("ub", type=int)
    ap.add_argument("--seconds", type=float, default=600); ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--smax", type=int); ap.add_argument("--hmin", type=int)
    ap.add_argument("--full0", action="store_true"); ap.add_argument("--noperiod", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    r = solve(a.n, a.ub, a.seconds, a.workers, smax=a.smax, hmin=a.hmin, full0=a.full0, period=not a.noperiod)
    print(json.dumps(r), flush=True)
    if a.out:
        json.dump(r, open(a.out, "w"))
