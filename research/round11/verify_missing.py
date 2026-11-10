#!/usr/bin/env python3
"""Replay exact finite exclusions of non-covering heavy sets. No SAT solver."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations, product
import json
from pathlib import Path

from audit_frontier import R8, audit, points, require, sha

DIRECTIONS = frozenset(range(1, 32))
SPECTRUM = R8 / "research_round6/imported_claude_round4/data/spec32.csv"
SPECTRUM_SHA = "a61140936f55aa278de40d1b66e537138048322d152141ccc436d42c0f8fefab"


def capacity(p, q):
    """Upper bound for a quotient sumset with p,q <= 7."""
    small, large = sorted((p, q))
    if small == 3 and large > 4:
        return large + 8
    return min(16, p * q)


def matchings(support):
    edges = [[] for _ in range(32)]
    for a, b in combinations(sorted(support), 2):
        edges[a ^ b].append((a, b))
    return edges


def normalized_two_missing():
    """Any H with two missing differences spans the full affine space."""
    basis = (0, 1, 2, 4, 8, 16)
    checked = 0
    missing_two = 0
    for extra in combinations(sorted(DIRECTIONS - set(basis)), 4):
        heavy = basis + extra
        edges = matchings(heavy)
        missing = [d for d in sorted(DIRECTIONS) if not edges[d]]
        checked += 1
        if len(missing) != 2:
            continue
        missing_two += 1
        outside_plane = set(DIRECTIONS) - {*missing, missing[0] ^ missing[1]}
        touched = {a for d in outside_plane if len(edges[d]) == 1 for a in edges[d][0]}
        require(touched == set(heavy), f"Uncovered heavy vertex in {heavy}")
    require((checked, missing_two) == (14950, 5220), "Changed normalized geometry counts")
    return {"normalized_heavy_sets_checked": checked, "two_missing": missing_two}


def load_spectra(repo):
    path = repo / SPECTRUM
    require(sha(path) == SPECTRUM_SHA, "Changed spectrum census")
    spectra = defaultdict(set)
    for line in path.read_text().splitlines():
        w, *counts, _rank = map(int, line.split(","))
        require(len(counts) == 17 and min(counts) >= 0 and sum(counts) == 31
                and sum(p * n for p, n in enumerate(counts)) == w * (w - 1) // 2
                and not any(counts[w // 2 + 1:]), "Malformed spectrum")
        spectra[w].add(tuple(sum(counts[p:]) for p in range(8)))
    require(all(spectra[w] for w in range(4, 16)), "Missing required weight")
    return spectra


def light_options(support, a, missing):
    """Project a light fibre's exact weight and directions onto its support edges."""
    incident = {a ^ b for b in support if a != b}
    options = {(2, frozenset({missing}))}
    for e in sorted(DIRECTIONS - {missing}):
        options.add((3, frozenset({missing, e, e ^ missing} & incident)))
    return sorted(options, key=lambda row: (row[0], tuple(sorted(row[1]))))


def active_edges(edges, lights):
    return [
        [(a, b) for a, b in line if (a not in lights or d in lights[a])
         and (b not in lights or d in lights[b])]
        for d, line in enumerate(edges)
    ]


def weight_assignments(heavy, weights, room, index=0):
    """Enumerate every point in the bounded integer budget box."""
    if index == len(heavy):
        yield weights
        return
    a = heavy[index]
    lower = weights[a]
    for extra in range(min(room, weights[0] - lower) + 1):
        weights[a] = lower + extra
        yield from weight_assignments(heavy, weights, room - extra, index + 1)
    weights[a] = lower


def check_weights(active, heavy, weights, spectra, capacity_cache):
    """Return a direction deficit, or explicit spectrum deficits, or neither."""
    required = defaultdict(list)
    for d in range(1, 32):
        edges = active[d]
        ceilings = [(weights[a] // 2, weights[b] // 2) for a, b in edges]
        upper = [capacity_cache[p, q] for p, q in ceilings]
        total = sum(upper)
        if total < 16:
            return d, None
        for (a, b), (p, q), contribution in zip(edges, ceilings, upper):
            demand = 16 - (total - contribution)
            if demand <= 0:
                continue
            if a in heavy:
                required[a].append(next(k for k in range(1, p + 1)
                                        if capacity_cache[k, q] >= demand))
            if b in heavy:
                required[b].append(next(k for k in range(1, q + 1)
                                        if capacity_cache[p, k] >= demand))
    failures = []
    for a in sorted(required):
        demand = tuple(sum(k >= p for k in required[a]) for p in range(1, 8))
        if not any(all(hist[p] >= demand[p - 1] for p in range(1, 8))
                   for hist in spectra[weights[a]]):
            failures.append({"vertex": a, "weight": weights[a], "tails_ge_1_to_7": demand})
    return None, failures


def one_missing(repo, coverage):
    spectra = load_spectra(repo)
    roles = coverage["support13_open_marked_roles"]
    require(roles["14"] == roles["15"], "Expected identical open role lists")
    caps = {(p, q): capacity(p, q) for p, q in product(range(8), repeat=2)}
    counts = {m: Counter() for m in (14, 15)}
    tally = Counter()
    witnesses = []
    by_role = {}
    for role in roles["14"]:
        mask = role["mask"]
        support = set(points(mask | 1))
        edges = matchings(support)
        role_count = Counter()
        for light in combinations(sorted(support - {0}), 3):
            heavy = support - set(light)
            he = matchings(heavy)
            missing = [d for d in range(1, 32) if not he[d]]
            role_count[f"heavy_sets_missing_{len(missing)}"] += 1
            if len(missing) == 2 and all(a ^ d in heavy for a in light for d in missing):
                role_count["two_missing_all_partners_present"] += 1
            if len(missing) != 1:
                continue
            d = missing[0]
            partners = [a ^ d for a in light]
            if not all(a in heavy for a in partners):
                continue
            role_count["one_missing_all_partners_present"] += 1
            for choice in product(*(light_options(support, a, d) for a in light)):
                role_count["effective_light_choices"] += 1
                active = active_edges(edges, {a: dirs for a, (_, dirs) in zip(light, choice)})
                touched = {a for edge in active if len(edge) == 1
                           and set(edge[0]) <= heavy for a in edge[0]}
                light_weights = {a: w for a, (w, _) in zip(light, choice)}
                for m in (14, 15):
                    lower = {a: (8 if a in touched else 4) for a in heavy}
                    lower[0] = m
                    lower.update(light_weights)
                    mass = sum(lower.values())
                    if mass > 93:
                        counts[m]["light_plus_private_mass_deficit"] += 1
                        continue
                    pair_shortfall = max(0, 16 - sum(lower[a] // 2 for a in partners))
                    # All adjustable heavy lower bounds are even. The hub is fixed.
                    if mass + 2 * pair_shortfall > 93:
                        counts[m]["missing_direction_mass_deficit"] += 1
                        continue
                    counts[m]["effective_choices_requiring_weight_enumeration"] += 1
                    for weights in weight_assignments(sorted(heavy - {0}), lower, 93 - mass):
                        counts[m]["weight_assignments_checked"] += 1
                        direction, failures = check_weights(active, heavy, weights, spectra, caps)
                        if direction is not None:
                            counts[m]["direction_capacity_deficit"] += 1
                        else:
                            require(failures, f"One-missing relaxation survives: {mask}, {m}, {light}, {choice}, {weights}")
                            counts[m]["spectrum_deficit"] += 1
                            witnesses.append({
                                "mask": mask, "maximum": m, "missing": d, "light": light,
                                "light_options": [(w, sorted(ds)) for w, ds in choice],
                                "weights": dict(sorted(weights.items())), "spectrum_deficits": failures,
                            })
        by_role[mask] = dict(sorted(role_count.items()))
        tally.update(role_count)
    require(len(by_role) == 27 and tally["effective_light_choices"] == 114466, "Scope changed")
    return {"marked_roles_per_maximum": len(by_role), "tally": dict(sorted(tally.items())),
            "by_role": by_role, "by_maximum": counts, "spectrum_leaf_witnesses": witnesses}


def full_cover_cuts(coverage):
    """Round 10-style positive heavy clauses for the newly proved full-cover rule."""
    cases = []
    counts = Counter()
    for role in coverage["support13_open_marked_roles"]["14"]:
        support = set(points(role["mask"] | 1))
        light_choices = [frozenset(light) for k in range(4)
                         for light in combinations(sorted(support - {0}), k)]
        forbidden = []
        for light in light_choices:
            heavy = support - light
            missing = DIRECTIONS - {a ^ b for a, b in combinations(heavy, 2)}
            counts["checked_light_choices"] += 1
            if missing and not any(prior <= light for prior, _ in forbidden):
                forbidden.append((light, min(missing)))
        for light in light_choices:
            heavy = support - light
            covers = all(any(a ^ d in heavy for a in heavy) for d in DIRECTIONS)
            require(covers == (not any(prior <= light for prior, _ in forbidden)),
                    "Full-cover clause semantics differ from the direct matching check")
            counts["survives_geometry" if covers else "excluded"] += 1
        counts["positive_heavy_clauses"] += len(forbidden)
        cases.append({"mask": role["mask"], "class": role["class"], "clauses": [
            {"positive_heavy": sorted(light), "missing_direction": missing}
            for light, missing in forbidden
        ]})
    return {"scope": "S13, exact maximum 14 or 15, marked hub zero, total at most 93",
            "counts_per_maximum": counts, "cases": cases}


def support14_two_missing(coverage):
    counts = {}
    for row in coverage["maximum11_open_affine_classes"]["14"]:
        support = set(points(row["mask"]))
        tally = Counter()
        for light in combinations(sorted(support), 4):
            heavy = support - set(light)
            missing = sorted(DIRECTIONS - {a ^ b for a, b in combinations(heavy, 2)})
            if len(missing) == 2:
                tally["two_missing"] += 1
                if all(a ^ d in heavy for a in light for d in missing):
                    tally["two_missing_all_partners_present"] += 1
        counts[row["class"]] = dict(tally)
    return counts


def controls():
    require(capacity(3, 7) == 15 and capacity(7, 3) == 15
            and capacity(4, 4) == 16 and capacity(1, 7) == 7, "Invalid edge bounds")
    edges = matchings({0, 1, 2, 3})
    a = active_edges(edges, {0: {1}, 1: {2}})
    require((0, 1) not in a[1] and (1, 3) in a[2], "Light-light activation needs both endpoints")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path)
    parser.add_argument("coverage", type=Path)
    args = parser.parse_args()
    coverage = json.loads(args.coverage.read_text())
    require(coverage == json.loads(json.dumps(audit(args.repo.resolve()))),
            "Coverage input differs from frozen ledger reconstruction")
    controls()
    result = {
        "normalized_two_missing": normalized_two_missing(),
        "one_missing_support13": one_missing(args.repo.resolve(), coverage),
        "two_missing_support14_maximum11_by_unmarked_class": support14_two_missing(coverage),
        "full_cover_clauses": full_cover_cuts(coverage),
        "status": "PASS_NO_SAT",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
