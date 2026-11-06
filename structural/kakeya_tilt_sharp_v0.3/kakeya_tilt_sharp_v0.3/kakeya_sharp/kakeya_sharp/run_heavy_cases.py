"""Run model X on every admissible heavy-support orbit (no full fibre)."""
import sys, json, time
from .exact_local4 import solve, local_types

if __name__ == "__main__":
    n, ub, tl = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
    only_unknown = sys.argv[4] if len(sys.argv) > 4 else None   # path of a previous log: rerun its UNKNOWN cases
    tag = sys.argv[5] if len(sys.argv) > 5 else ""
    feas = bool(only_unknown)
    smax = (1 << n) - 1
    cases = json.load(open(f"results/heavy_orbits_n{n}_ub{ub}.json"))
    if only_unknown and only_unknown != "all":
        todo = {tuple(json.loads(l)["B"]) for l in open(only_unknown) if json.loads(l)["status"] == "UNKNOWN"}
        cases = [c for c in cases if tuple(c["B"]) in todo]
        cases.sort(key=lambda c: -c["h"])
    T = local_types(n)
    res = []
    for c in cases:
        r = solve(n, ub, tl, 2, smax=smax, heavy=set(c["B"]), types=T, feas=feas)
        r["B"] = c["B"]; r["h"] = c["h"]; r["d"] = c["d"]
        r.pop("options", None)
        print(json.dumps(r), flush=True)
        res.append(r)
        json.dump(res, open(f"results/X_heavy_cases_n{n}_ub{ub}{tag}.json", "w"))
