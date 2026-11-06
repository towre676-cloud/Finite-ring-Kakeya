#!/usr/bin/env python3
"""Bounded exact two-ring dimension-four search over a complete catalogue.

The unchanged exact-ring producer supplies search, publication, proof checking
and direct SAT-model checking. This driver changes only its destination and
source-provenance hooks; the encoder and search/check implementation are frozen.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXACT = HERE.parent / "exact_ring"
sys.path.insert(0, str(EXACT))
import certify_exact_ring as P
import encode_exact_ring as E
import verify_exact_ring as G
import catalogue_dimension4 as D4


def sources():
    paths = [EXACT / "encode_exact_ring.py", EXACT / "verify_exact_ring.py",
             EXACT / "certify_exact_ring.py", Path(__file__), HERE / "catalogue_dimension4.py",
             HERE / "DIMENSION4_SUPPORT_CATALOGUE.json", HERE / "DIMENSION4_ALL_MARKED_TRANSPORTS.json"]
    return {str(p.relative_to(ROOT)): P.A.sha(p) for p in paths}


# These are per-process configuration hooks, not edits to any earlier file.
P.HERE = HERE
P.sources = sources


def load_catalogue():
    cat = json.loads((HERE / "DIMENSION4_SUPPORT_CATALOGUE.json").read_text())
    P.A.require(cat["status"] == "PASS_COMPLETE_DIMENSION4_MARKED_SUPPORT_CATALOGUE" and
                cat["covering_marked_orbit_count"] == len(cat["covering_cases"]) == 28 and
                cat["group_order"] == 20160, "Wrong catalogue scope")
    P.A.require(P.A.sha(HERE / "catalogue_dimension4.py") == cat["source_sha256"], "Catalogue generator changed")
    P.A.require(P.A.sha(HERE / "DIMENSION4_ALL_MARKED_TRANSPORTS.json") == cat["transport_file_sha256"],
                "Explicit transports changed")
    for row in cat["covering_cases"]:
        P.A.require(row["full_mask"] == sum(1 << x for x in row["support"]) and D4.covers(row["support"]),
                    "Invalid covering representative")
    return cat


def universe(cat, lower=2, upper=16, tag="full"):
    cases = []
    for row in sorted(cat["covering_cases"], key=lambda x: (x["support_size"], x["full_mask"])):
        for ring in E.RINGS:
            cases.append({"case_id": f"n4_{ring}_s{row['support_size']}_S{row['full_mask']}_m{lower}_{upper}_{tag}",
                          "dimension": 4, "ring": ring, "support": row["support"],
                          "maximum": upper, "hub_min": lower, "total": 45, "normalize": True,
                          "purpose": "dimension4_complete_catalogue_bounded_search",
                          "catalogue_full_mask": row["full_mask"]})
    assert len(cases) == 56
    return cases


def upper_bound():
    fibres = {0: frozenset(range(16))}
    fibres.update({a: frozenset({0, a}) for a in range(1, 16)})
    rows = []
    for ring in E.RINGS:
        direct = G.verify_actual_kakeya(fibres, 4, ring)
        assert direct["is_kakeya"] and direct["point_count"] == 46
        f = E.encode_support(range(16), 16, total=46, dimension=4, ring=ring)
        assert not E.first_failed_clauses(f, E.actual_assignment(f, fibres))
        rows.append({"ring": ring, "direct_check": direct,
                     "all_exact_cnf_clauses_satisfied": True, "variables": f.n, "clauses": len(f.cl)})
    return {"status": "PASS_EXPLICIT_46_POINT_KAKEYA_STAR_BOTH_RINGS", "dimension": 4,
            "fibres": {str(a): sorted(Aa) for a, Aa in fibres.items()}, "ring_checks": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--tag", default="t20")
    parser.add_argument("--lower", type=int, default=2)
    parser.add_argument("--upper", type=int, default=16)
    parser.add_argument("--mask", type=int, action="append")
    parser.add_argument("--ring", choices=E.RINGS, action="append")
    parser.add_argument("--take", type=int)
    args = parser.parse_args()
    P.A.require(args.limit > 0 and 2 <= args.lower <= args.upper <= 16, "Invalid limit or maximum interval")
    P.A.require(args.tag.replace("_", "").isalnum(), "Unsafe tag")
    started = time.monotonic()
    cat = load_catalogue()
    P.dump(HERE / "DIMENSION4_FULL_CASE_UNIVERSE.json", universe(cat))
    P.dump(HERE / "DIMENSION4_46_POINT_STAR.json", upper_bound())
    all_cases = universe(cat, args.lower, args.upper, args.tag)
    selected = [c for c in all_cases if (args.mask is None or c["catalogue_full_mask"] in args.mask)
                and (args.ring is None or c["ring"] in args.ring)]
    if args.take is not None:
        selected = selected[:args.take]
    P.A.require(bool(selected), "No cases selected")
    pins = P.A.verify_sources()
    binaries, build = P.A.build_checkers(HERE / "bin", HERE / "build_logs")
    report = {"status": "RUNNING", "complete_catalogue_ring_cases": 56,
              "requested_cases": len(selected), "maximum_interval": [args.lower, args.upper],
              "source_hashes": sources(), "checker_source_pins": pins, "checker_build": build,
              "cases": [], "global_dimension4_minimum46_established": False}
    output = HERE / f"{args.tag}_m{args.lower}_{args.upper}_PRODUCTION.json"
    P.dump(output, report)
    for case in selected:
        row = P.run_one(case, binaries, args.limit)
        report["cases"].append(row)
        report["completed_cases"] = len(report["cases"])
        report["accepted_unsat_cases"] = sum(r["status"] == P.UNSAT for r in report["cases"])
        report["actual_sat_cases"] = sum(r["status"] == P.SAT for r in report["cases"])
        P.dump(output, report)
        print(json.dumps({k: row.get(k) for k in ["case_id", "status", "solve_seconds", "proof_bytes", "seconds"]}), flush=True)
    complete = len(selected) == 56 and args.lower == 2 and args.upper == 16 and all(r["status"] == P.UNSAT for r in report["cases"])
    report.update(status="PASS_ALL_56_DIMENSION4_UNSAT_CERTIFICATES" if complete else "COMPLETED_BOUNDED_DIMENSION4_SWEEP",
                  global_dimension4_minimum46_established=complete, seconds=round(time.monotonic() - started, 6))
    P.dump(output, report)
    print(json.dumps({k: report[k] for k in ["status", "accepted_unsat_cases", "actual_sat_cases",
                     "global_dimension4_minimum46_established", "seconds"]}), flush=True)


if __name__ == "__main__":
    main()
