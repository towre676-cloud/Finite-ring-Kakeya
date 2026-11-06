#!/usr/bin/env python3
"""Standalone elementary prices plus complete ten-support classification.

Reads no fibre-spectrum or sumset-table file; calls no SAT solver and no
floating-point optimizer. It imports only the explicitly pinned finite
support classifier, with Python assertions required to remain enabled.
"""
from collections import Counter
from itertools import combinations, combinations_with_replacement
from math import comb
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
import time

from eleven_heavy_cut import add_eleven_heavy_cut

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MASKS = (377850134, 411136406, 671697334, 2185856310)
PHI = (0, 1, 4, 9, 16, 17)
BOUNDS = {
    "U": {6: 15, 7: 27, 8: 46, 9: 78, 10: 126, 11: 145},
    "W_rank3": {4: 3, 5: 12, 6: 17, 7: 27, 8: 48},
    "W_rank_ge4": {5: 3, 6: 12, 7: 17, 8: 34, 9: 48, 10: 51, 11: 51},
    "L": {2: 10, 3: 30},
}
GEOMETRY = ROOT / "research_round8/geometry/verify_ten_heavy_ranks.py"
GEOMETRY_SHA = "1bdd7cb3435a0c63cce03de0d33f8ef277108d3f5e41dd004fd81756d7bba289"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def elementary_capacity(p, q):
    bounds = [p*q, 16]
    if p == 3:
        bounds.append(q + 8)
    if q == 3:
        bounds.append(p + 8)
    return min(bounds)


def local_controls():
    price_rows = []
    for p in range(6):
        for q in range(6):
            cap = elementary_capacity(p, q)
            require(2*cap <= PHI[p] + PHI[q], "Pair-price bound failed")
            price_rows.append({"p": p, "q": q, "sumset_upper_bound": cap,
                               "price_sum": PHI[p] + PHI[q]})
    maxima = {r: -1 for r in range(5)}
    blocks = []
    for bits in range(16):
        A = {x for x in range(4) if bits >> x & 1}
        edges = sum(1 for a, b in combinations(A, 2) if a ^ b in (1, 2))
        maxima[len(A)] = max(maxima[len(A)], edges)
        require(not 0 < len(A) < 4 or len(A) - edges >= 1, "Partial-coset deficit failed")
        blocks.append({"four_cycle_subset_mask": bits, "points": len(A), "two_direction_edges": edges})
    require([maxima[r] for r in range(5)] == [0, 0, 1, 2, 4], "Four-cycle table changed")
    odd_controls = []
    # Eight quotient cosets suffice in F2^5. Sorted occupancy lists cover
    # every possibility relevant to this additive point/edge bound.
    for weight, expected in ((7, [3, 4]), (11, [3, 4, 4])):
        surviving = []
        for occupancies in combinations_with_replacement(range(5), 8):
            if sum(occupancies) == weight and sum(maxima[r] for r in occupancies) >= weight - 1:
                surviving.append([r for r in occupancies if r])
        require(surviving == [expected], "Odd maximal-pair coset partition changed")
        odd_controls.append({"weight": weight, "only_possible_nonempty_occupancies": expected})
    energy = {w: comb(w, 2) + 6*((1 << (w-6))-1) for w in range(6, 11)}
    require([energy[w] for w in range(6, 11)] == [15, 27, 46, 78, 135], "Relation-code energy arithmetic failed")
    require(all(135-(9-t)-8*t == 126-7*t <= 126 for t in range(10)), "Top-nine ten-set bound failed")
    require(PHI[5] + 8*PHI[4] == 145, "Eleven-set rank bound failed")
    return {"all_36_pair_prices": price_rows, "all_16_four_cycle_slices": blocks,
            "odd_maximal_pair_controls": odd_controls, "rank5_relation_code_energy_bounds": energy}


def integer_dual():
    rows = []
    for role, table in BOUNDS.items():
        for weight, resource in table.items():
            if role == "U":
                rhs = 45*weight + 85
            elif role == "L":
                rhs = 45*weight - 15
            else:
                rhs = 45*weight - 213 + (45 if role == "W_rank3" else 0)
            require(4*resource <= rhs, "Elementary resource row violates the stated dual")
            rows.append({"role": role, "weight": weight, "resource_upper_bound": resource,
                         "resource_times_four": 4*resource, "dual_upper_bound_times_four": rhs})
    available = 45*93 + 3*85 - 7*213 + 2*45 - 3*15
    required = 4*2*16*24
    require(available == 2994 < 3072 == required, "No strict ten-heavy contradiction")
    return {"row_inequalities": rows, "available_upper_bound_times_four": available,
            "required_resource_times_four": required, "strict_gap_times_four": required-available,
            "integer_resource_upper_bound": available//4, "required_resource": 768}


def budget_dp(hub_component=None):
    roles = ["W"]*7 + ["U"]*3 + ["L"]*3
    hub_index = roles.index(hub_component) if hub_component is not None else -1
    # Each state stores an integer optimum and an explicit extremizing path.
    dp = {(0, 0): (0, [])}
    for index, role in enumerate(roles):
        choices = []
        categories = ("W_rank3", "W_rank_ge4") if role == "W" else (role,)
        for category in categories:
            for weight, resource in BOUNDS[category].items():
                if index == hub_index and weight != 11:
                    continue
                choices.append((weight, int(category == "W_rank3"), resource, category))
        nxt = {}
        for (used, low_count), (value, path) in dp.items():
            for weight, low, resource, category in choices:
                key = used+weight, low_count+low
                if key[0] > 93 or key[1] > 2:
                    continue
                if key not in nxt or nxt[key][0] < value+resource:
                    nxt[key] = value+resource, path+[{
                        "vertex_role": role, "rank_class": category, "weight": weight,
                        "resource_upper_bound": resource, "distinguished_hub": index == hub_index}]
        dp = nxt
    key, (value, path) = max(dp.items(), key=lambda item: (item[1][0], item[0]))
    require(value < 768, "Elementary DP did not give a strict contradiction")
    require(value == sum(row["resource_upper_bound"] for row in path) and
            key[0] == sum(row["weight"] for row in path) and
            key[1] == sum(row["rank_class"] == "W_rank3" for row in path), "Extremizer arithmetic differs")
    return {"distinguished_weight11_hub_component": hub_component,
            "exact_maximum_of_elementary_relaxation": value, "total_weight": key[0],
            "rank3_W_vertices": key[1], "extremizing_relaxed_profile": path,
            "actual_Kakeya_configuration_claimed": False}


def complete_support_check():
    require(not sys.flags.optimize, "Run without Python -O; the imported finite classifier uses assertions")
    require(sha(GEOMETRY) == GEOMETRY_SHA, "Finite geometry classifier changed")
    spec = importlib.util.spec_from_file_location("r8_elementary_ten_support_geometry", GEOMETRY)
    G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)
    basis = {0, 1, 2, 4, 8, 16}
    extras = sorted(set(range(32)) - basis)
    checked, covers = 0, []
    for tail in combinations(extras, 4):
        points = basis | set(tail); checked += 1
        if len(G.differences(points)) == 31:
            covers.append(G.classify(points))
    require(checked == 14950 and len(covers) == 80, "Incomplete ten-set classification")
    delivered = json.loads((GEOMETRY.parent / "TEN_HEAVY_RANK_REPLAY.json").read_text())
    require(delivered["normalized_cover_decompositions"] == covers, "Delivered geometry decompositions differ")
    patterns = []
    for mask in MASKS:
        S = [0] + [v for v in range(1, 32) if mask >> v & 1]
        allowed = []
        for h in range(11, 14):
            for tail in combinations(S[1:], h-1):
                H = [0, *tail]
                if len(G.differences(H)) == 31:
                    allowed.append({"heavy_residues": H, "heavy_residue_mask": sum(1 << v for v in H),
                                    "light_residues": sorted(set(S)-set(H)), "heavy_count": h})
        patterns.append({"marked_nonzero_support_mask": mask, "support": S,
                         "hub_convention": "residue0 has weight11 and is heavy",
                         "remaining_heavy_patterns": len(allowed),
                         "remaining_by_heavy_count": dict(sorted(Counter(row["heavy_count"] for row in allowed).items())),
                         "allowed_heavy_patterns": allowed})
    require([row["remaining_heavy_patterns"] for row in patterns] == [33, 44, 37, 37], "Post-exclusion pattern counts differ")
    return {"normalized_sets_checked": checked, "normalized_difference_covers": len(covers),
            "all_decompositions_rechecked": True,
            "marked_support_patterns_after_eleven_heavy": patterns,
            "new_whole_support_exclusions_claimed": 0}


def cut_controls():
    class Formula:
        def __init__(self):
            self.n = 13; self.cl = []
            self.r8_heavy_cover_count_outputs = list(range(1, 14))
            self.r8_heavy_cover_metadata = {
                "theorem": "SUPPORT13_MAXIMUM_LE11_REQUIRES_TEN_HEAVY_AND_FULL_HEAVY_DIFFERENCE_COVER",
                "support_size": 13, "maximum_domain_weight": 11}
        def add(self, clause):
            self.cl.append(list(clause))
    f = Formula(); metadata = add_eleven_heavy_cut(f, total_upper_bound=93)
    require(f.cl == [[11]] and f.n == 13, "The append-only counter cut changed")
    for count in range(14):
        values = [False] + [count >= j for j in range(1, 14)]
        require(all(any(values[x] for x in clause) for clause in f.cl) == (count >= 11), "Counter threshold changed")
    rejected = []
    for name, budget, broken in (("budget94", 94, False), ("missing_preceding_cover", 93, True)):
        f = Formula()
        if broken:
            f.r8_heavy_cover_metadata = {}
        try:
            add_eleven_heavy_cut(f, total_upper_bound=budget)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("Invalid cut precondition accepted: " + name)
    return {"threshold_values_checked": 14, "negative_controls_rejected": rejected, "metadata": metadata}


def main():
    started = time.monotonic()
    output = HERE / "TEN_HEAVY_ELEMENTARY_REPLAY.json"
    result = {"status": "RUNNING"}; output.write_text(json.dumps(result)+"\n")
    try:
        result.update(local_controls=local_controls(), integer_dual=integer_dual(),
                      exact_integer_dp=[budget_dp(role) for role in (None, "W", "U")],
                      support_classification=complete_support_check(), cut_controls=cut_controls())
        require([row["exact_maximum_of_elementary_relaxation"] for row in result["exact_integer_dp"]] == [744, 729, 744],
                "Independent elementary DP values changed")
        paths = [Path(__file__), HERE / "eleven_heavy_cut.py", HERE / "TEN_HEAVY_ELEMENTARY_PRICE_BOUNDS.md",
                 HERE / "HEAVY_DIFFERENCE_COVER_THEOREM.md", HERE / "heavy_cover_cut.py",
                 GEOMETRY, GEOMETRY.parent / "TEN_HEAVY_RANK_CONSEQUENCES.md"]
        result.update(status="PASS_ELEVEN_HEAVY_THEOREM_ELEMENTARY_PRICES_AND_COMPLETE_SUPPORT_CLASSIFICATION",
                      theorem="Support13, maximum fibre<=11 and total<=93 imply at least11 fibres of weight>=4, in both rings.",
                      fibre_spectrum_census_read=False, quotient_sumset_table_read=False,
                      SAT_solver_called=False, floating_point_optimizer_called=False,
                      source_hashes={str(path.relative_to(ROOT)): sha(path) for path in paths},
                      seconds=round(time.monotonic()-started, 6))
        output.write_text(json.dumps(result, indent=2)+"\n")
        print(json.dumps({"status": result["status"], "available_times_four": 2994, "required_times_four": 3072,
                          "elementary_DP": [744, 729, 744], "normalized_supports": 14950,
                          "seconds": result["seconds"]}, indent=2))
    except BaseException as error:
        result.update(status="FAIL", error=repr(error)); output.write_text(json.dumps(result, indent=2)+"\n")
        raise


if __name__ == "__main__":
    main()
