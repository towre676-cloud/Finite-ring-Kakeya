#!/usr/bin/env python3
"""Finite matching controls for the analytic actual-weight threshold.

No spectrum file, sumset table, support catalogue or SAT program is read.
The main theorem is proved in MATCHING_THRESHOLD_LEMMA.md. This program
checks a complete finite family of abstract matching capacities and small
literal matchings; it does not itself alter any profile frontier.
"""
from collections import Counter
from itertools import combinations_with_replacement, product
from pathlib import Path
import hashlib
import json
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prefixes(values):
    result = [0]
    for value in values:
        result.append(result[-1] + value)
    return result


def exhaustive_nine_heavy_controls():
    # Each matching is represented by its distinct heavy partner subset
    # and its number of light-light edges. Permuting light vertices or
    # pairing their names does not affect the upper bound being checked.
    masks = []
    for mask in range(1 << 9):
        t = mask.bit_count()
        if t <= 8:
            masks.append((mask, t, tuple(range((8-t)//2+1))))
    count = 0
    vectors = 0
    threshold_counts = Counter()
    equality_cases = 0
    minimum_positive_margin = None
    for ascending in combinations_with_replacement(range(2, 10), 9):
        q = tuple(reversed(ascending))
        Q = prefixes(q)
        rho = next(k for k in range(1, 10) if Q[k] >= 16)
        require(1 <= rho <= 8 and Q[rho-1] < 16 <= Q[rho], "Incorrect matching threshold bracket")
        r = (16+q[0]-1)//q[0]
        require(rho >= r, "Matching threshold weakened the maximum-only threshold")
        sums = [0]*(1 << 9)
        for mask in range(1, 1 << 9):
            bit = mask & -mask
            sums[mask] = sums[mask ^ bit] + q[bit.bit_length()-1]
        for mask, t, choices in masks:
            for u in choices:
                k = t+2*u
                capacity = sums[mask]+u
                margin = Q[k]-capacity
                require(margin >= 0, "Actual-partner matching bound failed")
                if k < rho:
                    require(capacity < 16, "Too few lights supply sixteen directions")
                if margin == 0:
                    equality_cases += 1
                elif minimum_positive_margin is None or margin < minimum_positive_margin:
                    minimum_positive_margin = margin
                count += 1
        vectors += 1
        threshold_counts[rho] += 1
    require(vectors == 11440, "Nine-ceiling-vector census differs")
    return {"sorted_nine_heavy_ceiling_vectors": vectors,
            "abstract_matching_capacity_cases": count,
            "threshold_distribution": dict(sorted(threshold_counts.items())),
            "matching_bound_equality_cases": equality_cases,
            "minimum_positive_capacity_margin": minimum_positive_margin,
            "ceiling_values": [2, 9], "maximum_active_light_vertices": 8,
            "per_vector_partner_and_light_light_patterns": len([(m,t,u) for m,t,choices in masks for u in choices])}


def literal_matchings(vertices, edges):
    vertices = tuple(vertices)
    if not vertices:
        yield ()
        return
    a = vertices[0]
    remainder = vertices[1:]
    yield from literal_matchings(remainder, edges)
    for b in remainder:
        if frozenset((a, b)) not in edges:
            continue
        left = tuple(v for v in remainder if v != b)
        for matching in literal_matchings(left, edges):
            yield ((a, b),) + matching


def literal_controls():
    heavy = tuple(range(3))
    light = tuple(range(3, 6))
    vertices = heavy + light
    edges = {frozenset((a, b)) for a in vertices for b in vertices
             if a < b and not (a in heavy and b in heavy)}
    matchings = tuple(literal_matchings(vertices, edges))
    canonical = {tuple(sorted(tuple(sorted(e)) for e in matching)) for matching in matchings}
    require(len(canonical) == len(matchings), "Literal matching generator duplicated a matching")
    checked = 0
    for q in product(range(2, 6), repeat=3):
        Q = prefixes(sorted(q, reverse=True))
        for matching in matchings:
            used = [v for edge in matching for v in edge]
            require(len(used) == len(set(used)), "Generated edges are not a matching")
            k = sum(v in light for v in used)
            capacity = 0
            for a, b in matching:
                if a in heavy:
                    capacity += q[a]
                elif b in heavy:
                    capacity += q[b]
                else:
                    capacity += 1
            require(capacity <= Q[k], "Literal matching violates top-k capacity")
            checked += 1
    return {"labelled_matchings_of_three_heavy_and_three_light_vertices": len(matchings),
            "labelled_heavy_ceiling_assignments": 4**3,
            "literal_weighted_matchings_checked": checked}


def premise_and_threshold_controls():
    q = (9, 6, 2, 2, 2, 2, 2, 2, 2)
    Q = prefixes(q)
    require((16+q[0]-1)//q[0] == 2 and Q[2] == 15 and Q[3] == 17,
            "Strict weighted-threshold example differs")
    invalid_capacity = 2*q[0]
    require(invalid_capacity > Q[2], "Reused heavy partner did not violate the bound")
    H = {0, 4, 8, 12, 16, 20, 24, 28}
    D = {a ^ b for a in H for b in H if a != b}
    missing = set(range(1, 32))-D
    light_three = {0, 1, 2}
    light_directions = {a ^ b for a in light_three for b in light_three if a != b}
    require(len(H) == 8 and light_directions <= missing and len(light_directions) == 3,
            "Eight-heavy plane-free-premise control differs")
    # Count profiles of light2/light3 fibres, not placements. Check the
    # stronger threshold never loses a maximum-only incidence exclusion.
    threshold_inequalities = 0
    for ascending in combinations_with_replacement(range(2, 10), 9):
        q = tuple(reversed(ascending))
        Q = prefixes(q)
        rho = next(k for k in range(1, 10) if Q[k] >= 16)
        r = (16+q[0]-1)//q[0]
        for L in range(9):
            for L3 in range(L+1):
                available = (L-L3)+2*L3
                require(not (3*r > available) or 3*rho > available,
                        "Matching threshold lost an earlier exclusion")
                if rho > L:
                    require(3*rho > available, "Too-few-lights case escaped the test")
                threshold_inequalities += 1
    return {"strict_improvement_example": {"heavy_ceilings": list((9, 6, 2, 2, 2, 2, 2, 2, 2)),
                                           "maximum_only_threshold": 2, "matching_threshold": 3},
            "invalid_heavy_partner_reuse_rejected_by_bound": True,
            "eight_heavy_example_requires_three_incidences_from_one_light_fibre": True,
            "integer_incidence_comparisons_checked": threshold_inequalities}


def main():
    started = time.monotonic()
    abstract = exhaustive_nine_heavy_controls()
    literal = literal_controls()
    premises = premise_and_threshold_controls()
    paths = [Path(__file__), HERE / "MATCHING_THRESHOLD_LEMMA.md",
             ROOT / "research_round8/incidence/MISSING_DIRECTION_INCIDENCE.md",
             ROOT / "research_round7/dense_encoder/NINE_POINT_DIFFERENCE_ANALYTIC_PROOF.md"]
    report = {"status": "PASS_ACTUAL_WEIGHT_MATCHING_THRESHOLD_CONTROLS",
              "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in paths},
              "abstract_matching_controls": abstract, "literal_matching_controls": literal,
              "premise_and_threshold_controls": premises,
              "mathematical_scope": "Nine heavy fibres, at most eight light2/3 fibres; analytic theorem applies to both rings and does not need a total-weight bound.",
              "finite_control_scope": "All sorted nine-heavy pair ceilings2..9, covering inherited maxima through18; all heavy partner subsets and feasible light-light counts using at most8 lights.",
              "proof_is_analytic_not_dependent_on_finite_controls": True,
              "profile_frontier_read_or_written": False,
              "spectrum_or_sumset_census_read": False,
              "SAT_or_proof_checker_called": False,
              "new_ledger_exclusions_claimed_by_this_replay": 0,
              "seconds": round(time.monotonic()-started, 6)}
    output = HERE / "MATCHING_THRESHOLD_REPLAY.json"
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "vectors": abstract["sorted_nine_heavy_ceiling_vectors"],
                      "matching_cases": abstract["abstract_matching_capacity_cases"],
                      "literal_cases": literal["literal_weighted_matchings_checked"],
                      "seconds": report["seconds"]}, indent=2))


if __name__ == "__main__":
    main()
