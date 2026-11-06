#!/usr/bin/env python3
"""Complete five-marked-support, two-ring dimension-three certificate run."""
from pathlib import Path
import argparse
from collections import Counter, defaultdict
import hashlib
import itertools
import json
import time
import certify_exact_ring as P
import encode_exact_ring as E
import verify_exact_ring as G

HERE = Path(__file__).resolve().parent


def span(vectors):
    out = {0}
    for v in vectors:
        out |= {x ^ v for x in list(out)}
    return out


def image(x, columns):
    y = 0
    for i, c in enumerate(columns):
        if x >> i & 1:
            y ^= c
    return y


def support_mask(support):
    return sum(1 << x for x in support)


def catalogue():
    maps = [columns for columns in itertools.product(range(1, 8), repeat=3)
            if len(span(columns)) == 8]
    assert len(maps) == len(set(maps)) == 168
    for columns in maps:
        assert {image(x, columns) for x in range(8)} == set(range(8))
    supports = [tuple([0] + list(T)) for size in range(5, 9)
                for T in itertools.combinations(range(1, 8), size - 1)]
    assert len(supports) == 64
    groups = defaultdict(list)
    transports = []
    for S in supports:
        assert {a ^ b for a in S for b in S} == set(range(8))
        choices = [(support_mask({image(a, cols) for a in S}), cols) for cols in maps]
        target, columns = min(choices)
        target_support = [x for x in range(8) if target >> x & 1]
        assert sorted(image(a, columns) for a in S) == target_support
        groups[target].append(support_mask(S))
        transports.append({"source_support": list(S), "source_full_mask": support_mask(S),
                           "target_full_mask": target, "linear_columns": list(columns)})
    expected = {31: 28, 61: 7, 63: 21, 127: 7, 255: 1}
    assert {mask: len(rows) for mask, rows in groups.items()} == expected
    entries = []
    for mask in sorted(groups, key=lambda m: (m.bit_count(), m)):
        S = [x for x in range(8) if mask >> x & 1]
        entries.append({"full_mask": mask, "support": S, "support_size": len(S),
                        "marked_orbit_size": len(groups[mask]),
                        "stabilizer_order": 168 // len(groups[mask]),
                        "all_source_masks": sorted(groups[mask])})
    return {"status": "PASS_COMPLETE_DIMENSION3_MARKED_SUPPORT_CATALOGUE",
            "dimension": 3, "group_order": 168, "group_columns": [list(c) for c in maps],
            "all_covering_supports_containing_zero": 64, "marked_class_count": 5,
            "by_support_size": {str(k): sum(e["support_size"] == k for e in entries) for k in range(5, 9)},
            "cases": entries, "all_transports": transports,
            "small_support_exclusion": "At most4supportvertices have atmost6edges, fewerthan7nonzeroresidue directions.",
            "large_support_coverage": "For|S|>=5inF2^3, S and S+d intersectfor everyd, bypigeonhole.",
            "hub_scope": "Zerois a largest fibre; tiesallowed. Alllinearorbits ofsupportscontainingzero areincluded."}


def cases(cat):
    result = []
    for entry in cat["cases"]:
        for ring in E.RINGS:
            result.append({"case_id": f"n3_{ring}_s{entry['support_size']}_S{entry['full_mask']}_budget21",
                           "dimension": 3, "ring": ring, "support": entry["support"],
                           "maximum": 8, "hub_min": 2, "total": 21, "normalize": True,
                           "purpose": "complete_dimension3_lower_bound"})
    assert len(result) == 10
    return result


def upper_bound():
    fibres = {0: frozenset(range(8))}
    fibres.update({a: frozenset({0, a}) for a in range(1, 8)})
    rows = []
    for ring in E.RINGS:
        direct = G.verify_actual_kakeya(fibres, 3, ring)
        assert direct["is_kakeya"] and direct["point_count"] == 22
        f = E.encode_support(range(8), 8, total=22, dimension=3, ring=ring)
        assert not E.first_failed_clauses(f, E.actual_assignment(f, fibres))
        rows.append({"ring": ring, "direct_check": direct,
                     "all_exact_cnf_clauses_satisfied": True, "variables": f.n, "clauses": len(f.cl)})
    return {"status": "PASS_EXPLICIT_22_POINT_KAKEYA_STAR_BOTH_RINGS",
            "dimension": 3, "fibres": {str(a): sorted(Aa) for a, Aa in fibres.items()},
            "ring_checks": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=60)
    parser.add_argument("--catalogue-only", action="store_true")
    parser.add_argument("--case-id", action="append")
    args = parser.parse_args()
    assert args.limit > 0
    started = time.monotonic()
    cat = catalogue()
    P.dump(HERE / "DIMENSION3_SUPPORT_CATALOGUE.json", cat)
    P.dump(HERE / "DIMENSION3_22_POINT_STAR.json", upper_bound())
    all_cases = cases(cat)
    P.dump(HERE / "DIMENSION3_CASE_UNIVERSE.json", all_cases)
    if args.catalogue_only:
        print(json.dumps({k: cat[k] for k in ["status", "group_order", "all_covering_supports_containing_zero", "marked_class_count", "by_support_size"]}))
        return
    selected = all_cases if args.case_id is None else [c for c in all_cases if c["case_id"] in args.case_id]
    if args.case_id is not None:
        assert set(args.case_id) == {c["case_id"] for c in selected}
    pins = P.A.verify_sources()
    binaries, build = P.A.build_checkers(HERE / "n3_bin", HERE / "n3_build_logs")
    source_hashes = {str(p.relative_to(P.ROOT)): P.A.sha(p) for p in [
        Path(__file__), HERE / "DIMENSION3_SUPPORT_CATALOGUE.json", HERE / "DIMENSION3_CASE_UNIVERSE.json"]}
    report = {"status": "RUNNING", "all_case_ids": [c["case_id"] for c in all_cases],
              "requested_case_ids": [c["case_id"] for c in selected],
              "catalogue_source_hashes": source_hashes, "exact_encoder_source_hashes": P.sources(),
              "checker_pins": pins, "checker_build": build, "cases": [],
              "exact_k3_equals22_established": False}
    output = HERE / "DIMENSION3_PRODUCTION.json"
    P.dump(output, report)
    for case in selected:
        result = P.run_one(case, binaries, args.limit)
        report["cases"].append(result)
        P.dump(output, report)
        print(json.dumps({key: result.get(key) for key in ["case_id", "status", "solve_seconds", "proof_bytes", "seconds"]}), flush=True)
    complete = len(selected) == 10 and all(r["status"] == P.UNSAT for r in report["cases"])
    report.update(status="PASS_ALL_TEN_DIMENSION3_UNSAT_CERTIFICATES" if complete else "INCOMPLETE_DIMENSION3_CERTIFICATION",
                  exact_k3_equals22_established=complete, seconds=round(time.monotonic() - started, 6))
    P.dump(output, report)
    print(json.dumps({k: report[k] for k in ["status", "exact_k3_equals22_established", "seconds"]}), flush=True)


if __name__ == "__main__":
    main()
