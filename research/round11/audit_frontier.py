#!/usr/bin/env python3
"""Recompose the frozen frontier without modifying its sources or proof ledgers."""

import argparse
from collections import Counter
import hashlib
import importlib.util
from itertools import combinations
import json
from pathlib import Path

R8 = Path("rounds/Kakeya_Round8_One_Folder/Kakeya_Round8")
R9 = Path("rounds/Kakeya_Round9_Recovered_2026-11-04/Kakeya_Round9")
PROFILE = R8 / "research_round8/incidence/after_three_direction_survivors.txt"
MAP = R9 / "research_round7/geometry/SUPPORT13_MARKING_MAP.json"
CATALOGUE = R8 / "research_round6/imported_claude_round4/data/orbits_all.txt"
FRONTIER = R8 / "Kakeya_Research_Frontier_Round8.json"
M11 = R8 / ("research_sources/extracted/Kakeya_Reconciled_Proofs_2026-10-27/"
            "late_parallel_2214/extracted/m11_directional/inputs/CAP11_STRUCTURAL_REDUCTION.json")
PINS = {
    PROFILE: "1eaf4e100d9b9a4a65556c5251249fd1e7062d51e8771b7af83761ffabbd4423",
    MAP: "82947e90078689b065fc56fc9f19ad682541c110e7808fa24ba464c72e4e3600",
    CATALOGUE: "2532528fed96455f714acf83cb53ba66c4b0b97dc48d541a02718dae1910f1dc",
    FRONTIER: "7dfb95105c012c34bed77aabbe29f797642f0eb2181df8a16a90b7a482cfb888",
    M11: "e243b21e7496c1c271192b81987a68e3133da0ede8782d3d5ec2b5c50f9da52b",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def points(mask):
    return tuple(v for v in range(32) if mask >> v & 1)


def catalogue(path):
    result = {s: [] for s in range(13, 18)}
    for line in path.read_text().splitlines():
        outer, mask, _, covers = map(int, line.split())
        if outer + 1 in result:
            require(mask & 1 == 0 and mask.bit_count() == outer, "Bad marked catalogue row")
            differences = {a ^ b for a, b in combinations(points(mask | 1), 2)}
            require(covers == (len(differences) == 31), "Invalid difference-cover flag")
            if covers:
                result[outer + 1].append(mask)
    require(all(len(masks) == len(set(masks)) for masks in result.values()),
            "Duplicate marked catalogue mask")
    require([len(result[s]) for s in result] == [55, 88, 113, 131, 145],
            "Marked catalogue cardinalities changed")
    return result


def recover_transports(repo, groups):
    source = repo / R9 / "research_round9/recover.py"
    spec = importlib.util.spec_from_file_location("frozen_round9_recover", source)
    recovery = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(recovery)
    return recovery.transport_check(groups)


def compose_round10(repo, classes, inherited):
    """Bind historical receipts and Round 10 checker logs to the same queue."""
    base = repo / R9
    r10 = read(base / "research_round10/RESULTS.json")
    r9_cases = [read(p) for p in sorted((base / "research_round9/cases").glob("*/CASE.json"))]
    historical = {row["case"]["case_id"]: row for row in r9_cases}
    require(len(historical) == len(r9_cases) == 54, "Incomplete Round 9 queue")
    require(sum(r["exclusion_credited"] for r in r9_cases) == 29, "Wrong Round 9 credit")
    additions = {r["case_id"]: r for r in r10["cases"]}
    require(len(additions) == len(r10["cases"]), "Duplicate Round 10 case")
    require(set(additions) == {k for k, r in historical.items() if not r["exclusion_credited"]},
            "Round 10 queue differs from Round 9 gaps")
    runs = {}
    for path in sorted((base / "research_round10/cases").glob("*/RECEIPT.json")):
        row = read(path)
        if not row["exclusion_credited"]:
            continue
        case = row["case"]["case_id"]
        require(case in additions and row["case"] == historical[case]["case"],
                "Wrong Round 10 scope")
        require(row["baseline_expected_sha256"] == historical[case]["cnf_sha256"],
                "Wrong Round 10 baseline")
        audit = row["audit"]
        require(row["status"] == "CERTIFIED_EXCLUSION"
                and audit["status"] == "PASS_CNF_UNSAT_VIA_CAKEML_LRAT"
                and audit["input_sha256"] == {
                    "cnf": row["cnf_sha256"], "drat": row["storage"]["proof.drat"]["raw_sha256"]},
                "Unbound Round 10 proof receipt")
        for stage in ("drat_trim", "cake_lpr"):
            for stream in ("stdout", "stderr"):
                log = path.parent / f"audit_{stage}.{stream}.txt"
                require(sha(log) == audit[stage][stream + "_sha256"], "Checker log hash mismatch")
        require((path.parent / "audit_cake_lpr.stdout.txt").read_bytes() == b"s VERIFIED UNSAT\n",
                "Checker acceptance missing")
        key = (row["variant"], row["cnf_sha256"])
        runs.setdefault(case, set()).add(key)
    require(len(runs) == 25 and sum(map(len, runs.values())) == 26, "Round 10 credit changed")
    by_max = {12: set(inherited), 13: set(inherited)}
    for key, row in historical.items():
        case = row["case"]
        mask = case["nonzero_support_mask"]
        maximum = case["maximum_interval"][0]
        require(case["maximum_interval"] == [maximum, maximum] and maximum in by_max
                and case["total_upper_bound"] == 93 and case["distinguished_hub"] == 0
                and tuple(case["support"]) == points(mask | 1)
                and classes[mask] == case["unmarked_affine_class"]
                and mask not in by_max[maximum], "Overlapping or invalid Round 9 scope")
        if key in additions:
            report = additions[key]
            require(report["exclusion_credited"] and report["original_cnf_sha256"] == row["cnf_sha256"]
                    and runs.get(key) == {(v["variant"], v["cnf_sha256"])
                                          for v in report["accepted_variants"]}, "Unbound credit")
        else:
            require(row["status"] == "CERTIFIED_EXCLUSION", "Bad historical proof status")
        by_max[maximum].add(mask)
    require(all(covered == set(classes) for covered in by_max.values()), "Missing marked role")
    return {"round9_historical_cases": 29, "round10_cases": 25, "round10_checked_receipts": 26,
            "fresh_proof_stream_replays": 0, "complete_roles": {m: len(v) for m, v in by_max.items()}}


def audit(repo):
    if not __debug__:
        raise ValueError("Run without -O for the inherited transport checker")
    for path, expected in PINS.items():
        require(sha(repo / path) == expected, f"Changed pinned input {path}")
    frontier = read(repo / FRONTIER)
    partial = frontier["support13_partial_coverage"]
    marked = catalogue(repo / CATALOGUE)
    groups = read(repo / MAP)["groups"]
    classes = {mask: g["unmarked_affine_orbit_id"] for g in groups for mask in g["marked_nonzero_masks"]}
    require(len(groups) == 13 and set(classes) == set(marked[13]), "Inconsistent S13 catalogue")
    transports = recover_transports(repo, groups)
    require(transports == 169, "Incomplete hub transport check")
    inherited = set(partial["complete_masks"])
    require(len(inherited) == 28 and inherited <= classes.keys(), "Invalid inherited marked roles")
    round10 = compose_round10(repo, classes, inherited)
    partial_maxima = {int(k): set(v) for k, v in partial["partial_maxima_by_mask"].items()}
    open_marked = {}
    for maximum in range(14, 19):
        excluded = inherited | {k for k, v in partial_maxima.items() if maximum in v}
        require(len(excluded) == partial["certified_marked_cases_by_exact_maximum"][str(maximum)],
                "Inconsistent per-maximum coverage")
        open_marked[maximum] = [{"mask": k, "class": classes[k]} for k in sorted(classes.keys() - excluded)]

    profiles = set()
    cells = Counter()
    for line in (repo / PROFILE).read_text().splitlines():
        s, m, _energy, *w = map(int, line.split())
        require(s == len(w) and s in marked and 12 <= m <= 18 and max(w) == m
                and min(w) >= 2 and sum(w) <= 93, "Invalid weight profile")
        profile = tuple(sorted(w))
        require(profile not in profiles, "Duplicate profile")
        profiles.add(profile)
        cells[s, m] += 1
    require(len(profiles) == 182526 and len(cells) == 34, "Wrong inherited profile frontier")
    closed_cells = {(13, m) for m, n in round10["complete_roles"].items() if n == len(classes)}
    require(closed_cells == {(13, 12), (13, 13)} and closed_cells <= cells.keys(),
            "Wrong Round 10 profile intersection")
    overlap = {m: cells[s, m] for s, m in sorted(closed_cells)}
    require(overlap == {12: 9789, 13: 11962}, "Round 10 overlap counts changed")
    composed = {f"{s}/{m}": n for (s, m), n in sorted(cells.items()) if (s, m) not in closed_cells}

    m11 = frontier["dimension5_strata"]["maximum11"]
    previous = read(repo / R8 / "research_round3/m11/s16/M11_CURRENT_FRONTIER_AFTER_S16.json")
    closed = set(m11["round7_whole_affine_support_class_exclusions"] +
                 m11["round8_whole_affine_support_class_exclusions"])
    require(set(previous["remaining_orbits"]) - closed == set(m11["remaining_orbits"]),
            "Inconsistent maximum-11 exclusions")
    records = {r["orbit"]: r for r in read(repo / M11)["records"]}
    m11_rows = {s: [] for s in (14, 15, 16)}
    for orbit in m11["remaining_orbits"]:
        row = records[orbit]
        support = row["support_size"]
        require(tuple(sorted(row["support"])) == points(row["mask"])
                and row["mask"].bit_count() == support, "Wrong M11 representative")
        m11_rows[support].append({"class": orbit, "mask": row["mask"]})
    require([len(v) for v in m11_rows.values()] == [9, 16, 17], "Wrong maximum-11 counts")

    return {
        "scope": "both rings, dimension 5, total at most 93, pair-active support",
        "checked_source_hashes": {str(p): expected for p, expected in PINS.items()},
        "hub_transports_checked": transports, "round10": round10,
        "maximum11_open_affine_classes": m11_rows,
        "support13_open_marked_roles": open_marked,
        "support14_to17_difference_cover_catalogue_before_profile_join": {
            s: marked[s] for s in range(14, 18)},
        "inherited_profile_ledger_count": len(profiles),
        "inherited_profile_counts": {f"{s}/{m}": n for (s, m), n in sorted(cells.items())},
        "profile_overlap_with_closed_round10_cells": overlap,
        "profile_counts_after_round10_cell_overlay": composed,
        "profiles_after_round10_cell_overlay": sum(composed.values()),
        "open_profile_cells_after_overlay": len(composed),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path, help="Repository root with restored evidence")
    print(json.dumps(audit(parser.parse_args().repo.resolve()), indent=2))


if __name__ == "__main__":
    main()
