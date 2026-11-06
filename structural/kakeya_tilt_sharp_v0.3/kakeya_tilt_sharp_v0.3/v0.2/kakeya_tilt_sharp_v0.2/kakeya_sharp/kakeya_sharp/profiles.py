"""Equality-profile analysis inside the defect-triangle relaxation (T):
enumerate every fibre-size multiset admitting a T-feasible point of total
size <= m, by repeatedly solving and excluding the found sorted profile."""
import sys, json
from ortools.sat.python import cp_model
from . import relaxation as RX


def profiles(n, m, cap=None, time_limit=120):
    found = []
    while True:
        # rebuild model with exclusions on the sorted profile via max-fibre and count constraints
        r = RX.solve(n, time_limit, ub=m, exclude=found, smax=cap)
        if r["status"] not in ("OPTIMAL", "FEASIBLE"):
            return found, r["status"]
        found.append(r["profile"])


if __name__ == "__main__":
    n, m = int(sys.argv[1]), int(sys.argv[2])
    cap = int(sys.argv[3]) if len(sys.argv) > 3 else None
    f, st = profiles(n, m, cap)
    print(json.dumps({"n": n, "m": m, "smax_cap": cap, "profiles": f, "terminal_status": st}))
