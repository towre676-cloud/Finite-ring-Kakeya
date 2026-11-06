"""Pair-budget relaxation (PB) of the fibre covering identity.

Integer variables s_a in [0, 2^n], p_a(v) in [0, floor(s_a/2)] with the exact
pair budget  sum_{v != 0} p_a(v) = C(s_a, 2) (p_a(v) is the TRUE pair count),
the defect triangle inequality d(v+w) <= d(v) + d(w) for d = s - 2p,
and for every v != 0 the counting form of the covering identity
    sum_{unordered {a, a+v}} p_a(v) * p_{a+v}(v) >= 2^{n-1}.
Every Kakeya set induces a feasible point (p_a(v) = |P_v(A_a)|), so
min PB <= k(R, n) for both rings.  The relaxation forgets the carry class
c_R and all positional information, hence is ring-independent."""
import sys, json, time
from ortools.sat.python import cp_model


TRIANGLE = True


def solve(n, time_limit=600, workers=2, ub=None, exclude=(), smax=None):
    N = 1 << n
    H = N >> 1
    m = cp_model.CpModel()
    s = [m.NewIntVar(0, N, f"s{a}") for a in range(N)]
    half = [m.NewIntVar(0, H, f"h{a}") for a in range(N)]
    pairs = [m.NewIntVar(0, N * (N - 1) // 2, f"c{a}") for a in range(N)]
    for a in range(N):
        m.AddDivisionEquality(half[a], s[a], 2)
        sm1 = m.NewIntVar(-1, N, "")
        m.Add(sm1 == s[a] - 1)
        prod = m.NewIntVar(-N, N * N, "")
        m.AddMultiplicationEquality(prod, [s[a], sm1])
        m.Add(2 * pairs[a] == prod)
    p = {}
    for a in range(N):
        for v in range(1, N):
            p[a, v] = m.NewIntVar(0, H, "")
            m.Add(p[a, v] <= half[a])
        m.Add(sum(p[a, v] for v in range(1, N)) == pairs[a])
        if TRIANGLE:
            # defect d(v) = s - 2p(v) = |A \ (A+v)| is subadditive:
            # |A ^ (A+v+w)| <= |A ^ (A+v)| + |(A+v) ^ (A+v+w)|
            for v in range(1, N):
                for w in range(v + 1, N):
                    m.Add(s[a] - 2 * p[a, v ^ w] <= 2 * s[a] - 2 * p[a, v] - 2 * p[a, w])
    for v in range(1, N):
        terms = []
        for a in range(N):
            if a < (a ^ v):
                t = m.NewIntVar(0, H * H, "")
                m.AddMultiplicationEquality(t, [p[a, v], p[a ^ v, v]])
                terms.append(t)
        m.Add(sum(terms) >= H)
    # symmetry (S1): AGL_n(F_2) permutes fibres and directions compatibly
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
    # d(v) = |A \ (A+v)| <= |V \ A|
    for a in range(N):
        for v in range(1, N):
            m.Add(s[a] - 2 * p[a, v] <= N - s[a])
    if smax is not None:
        for a in range(N):
            m.Add(s[a] <= smax)
    # exclude sorted profiles: count of fibres of each size must differ somewhere
    if exclude:
        cnt = {}
        for k in range(N + 1):
            bs = []
            for a in range(N):
                b = m.NewBoolVar("")
                m.Add(s[a] == k).OnlyEnforceIf(b)
                m.Add(s[a] != k).OnlyEnforceIf(b.Not())
                bs.append(b)
            cnt[k] = sum(bs)
        for prof in exclude:
            diffs = []
            for k in range(N + 1):
                c = prof.count(k)
                db = m.NewBoolVar("")
                m.Add(cnt[k] != c).OnlyEnforceIf(db)
                diffs.append(db)
            m.AddBoolOr(diffs)
    obj = sum(s)
    if ub is not None:
        m.Add(obj <= ub)
    m.Minimize(obj)
    sv = cp_model.CpSolver()
    sv.parameters.max_time_in_seconds = time_limit
    sv.parameters.num_workers = workers
    t0 = time.time()
    st = sv.Solve(m)
    out = {"n": n, "status": sv.StatusName(st), "seconds": round(time.time() - t0, 2),
           "bound": sv.BestObjectiveBound(), "conjecture": 3 * N - 2}
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        out["value"] = sv.ObjectiveValue()
        out["profile"] = sorted((sv.Value(x) for x in s), reverse=True)
    return out


if __name__ == "__main__":
    n = int(sys.argv[1]); tl = float(sys.argv[2]) if len(sys.argv) > 2 else 600
    r = solve(n, tl)
    print(json.dumps(r))
    json.dump(r, open(f"results/relaxation_n{n}.json", "w"))
