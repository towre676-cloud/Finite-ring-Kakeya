#!/usr/bin/env python3
"""Independent read-only review of the final950 profile certificate.

The reviewed producer is not imported. Local cube records are checked
directly, and E_k is independently reconstructed from all65536 subsets
of F2^4 followed by a two-coset convolution. The only output is this
review's own receipt; no source, certificate or survivor file is changed.
"""
from collections import Counter
from copy import deepcopy
from itertools import combinations
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "research_round8/incidence"
PINS = {
    "research_round7/charging/after_integer_dual_survivors.txt": "1c493598b5586dec62b736df01c10df441751a222e0926691a20c330853c2df5",
    "research_round8/incidence/verify_three_direction_profiles.py": "6b44cc7c7955cc5067ae1a1924907042dacb56a2e1ef3767f0d7248ffd50abcd",
    "research_round8/incidence/THREE_DIRECTION_PROFILE_EXCLUSIONS.json": "5878aa56c776066aff4ffe63e99e99cacaa50d8e4abdf3710c5f679ce11bfa91",
    "research_round8/incidence/after_three_direction_survivors.txt": "1eaf4e100d9b9a4a65556c5251249fd1e7062d51e8771b7af83761ffabbd4423",
    "research_round8/incidence/THREE_DIRECTION_PRICE_LEMMA.md": "2363be25c67adc6cbe0cbc563904491e0290a9a9a4ba375c180a94237ab6316c",
    "research_round8/geometry/MATCHING_PROFILE_REVIEW.json": "0fde41c7ad9fdc94a3afbae3800d897213bbf02d7612d789cc72be829fec0f20",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def equal(a, b):
    # This preserves the distinction between Boolean and integer fields.
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def check_tables(table):
    E16 = [[0]*17 for _ in range(4)]
    for mask in range(1 << 16):
        w = mask.bit_count()
        pair_counts = [(mask & (mask >> d) & low).bit_count()
                       for d, low in ((1, 0x5555), (2, 0x3333), (4, 0x0f0f))]
        total = 0
        for k, value in enumerate(pair_counts, 1):
            total += value
            E16[k][w] = max(E16[k][w], total)
    E32 = [[max(E16[k][a] + E16[k][w-a]
                for a in range(max(0, w-16), min(16, w)+1))
            for w in range(33)] for k in range(4)]
    require(table["ambient_dimension"] == 5 and table["ambient_vertices"] == 32,
            "Incorrect cube ambient space")
    require(table["enumerated_cube_dimensions"] == [1, 2, 3] and table["total_local_subsets"] == 276,
            "Incorrect local subset inventory")
    require(table["E_k_for_weights0_through32"] == {str(k): E32[k] for k in range(4)},
            "E table differs from independent actual F2^4 subset enumeration")
    checked_masks = 0
    checked_layer_entries = 0
    require(len(table["dimensions"]) == 3, "Unexpected cube dimension records")
    for k, row in enumerate(table["dimensions"], 1):
        n = 1 << k
        edges = [(a, b) for a, b in combinations(range(n), 2)
                 if (a ^ b).bit_count() == 1]
        require(row["dimension"] == k and row["cube_vertices"] == n and
                row["ambient_cosets"] == 32//n and row["subsets_enumerated"] == 1 << n,
                "Malformed cube record scope")
        require(set(map(tuple, row["cube_edges"])) == set(edges) and len(row["cube_edges"]) == len(edges),
                "Cube edge record differs")
        g = [-1]*(n+1)
        witness = [None]*(n+1)
        require(len(row["complete_subset_census"]) == 1 << n, "Incomplete local cube census")
        for mask, record in enumerate(row["complete_subset_census"]):
            chosen = {v for v in range(n) if mask & (1 << v)}
            count = sum(a in chosen and b in chosen for a, b in edges)
            expected = {"subset_mask": mask, "occupancy": len(chosen), "induced_edges": count}
            require(equal(record, expected), "Incorrect local subset record")
            if count > g[len(chosen)]:
                g[len(chosen)] = count
                witness[len(chosen)] = mask
            checked_masks += 1
        require(row["local_edge_maxima_by_occupancy"] == g and row["smallest_maximizing_subset_masks"] == witness,
                "Incorrect local maximum or witness")
        layers = row["max_plus_layers_including_zero_cosets"]
        choices = row["smallest_last_coset_occupancy_at_each_maximum"]
        require(len(layers) == len(choices) == 32//n+1 and layers[0] == [0]+[None]*32
                and choices[0] == [None]*33, "Incorrect zero-coset initialization")
        previous = {0: 0}
        checked_layer_entries += 33
        for layer in range(1, 32//n+1):
            now, last = {}, {}
            for old_weight, old_value in previous.items():
                for z, local in enumerate(g):
                    weight = old_weight+z
                    if weight > 32:
                        continue
                    value = old_value+local
                    if weight not in now or value > now[weight] or (value == now[weight] and z < last[weight]):
                        now[weight], last[weight] = value, z
            require(layers[layer] == [now.get(w) for w in range(33)], "Incorrect exact coset layer")
            require(choices[layer] == [last.get(w) for w in range(33)], "Incorrect maximizing coset choice")
            previous = now
            checked_layer_entries += 33
        require([previous[w] for w in range(33)] == E32[k], "Cube convolution differs from independent enumeration")
    require(checked_masks == 276, "Not all local subsets were checked")
    return E32, {"complete_local_cube_masks_checked": checked_masks,
                 "coset_layer_entries_including_unreachable_states_checked": checked_layer_entries,
                 "independent_actual_F2_4_subsets_checked": 1 << 16,
                 "independent_E_method": "Fixed directions1,2,4 in all F2^4 subsets, followed by two4-flat cosets.",
                 "E_k_for_weights0_through32": {str(k): E32[k] for k in range(4)}}


def main():
    certificate = json.loads((DATA / "THREE_DIRECTION_PROFILE_EXCLUSIONS.json").read_text())
    pins = {**PINS, **certificate["prior_stage_pins"], **certificate["analytic_proof_pins"]}
    for path, expected in pins.items():
        require(sha(ROOT / path) == expected, "Changed frozen review input: " + path)
    table = certificate["cube_tables"]
    table_hash = hashlib.sha256((json.dumps(table, indent=2)+"\n").encode()).hexdigest()
    require(table_hash == certificate["cube_tables_sha256"] == "bbba4cfd3db6d976a7410347ba0f5fcc05b83bb9fc5c0a6e7ef690e14f29bea2",
            "Cube table hash differs")
    E, table_controls = check_tables(table)
    old = json.loads((DATA / "MATCHING_INCIDENCE_PROFILE_EXCLUSIONS.json").read_text())
    prior = {row["source_line"]: row for row in old["certificates"]}
    stored = {row["source_line"]: row for row in certificate["certificates"]}
    require(len(prior) == 745 and len(stored) == len(certificate["certificates"]) == 950,
            "Wrong or duplicated certificate counts")
    raw = (ROOT / "research_round7/charging/after_integer_dual_survivors.txt").read_bytes().splitlines(keepends=True)
    before, removed, old_counts = Counter(), Counter(), Counter()
    prices, bounds_seen, heavy_counts = Counter(), Counter(), Counter()
    unique, dual, union = set(), set(), set()
    kept, intermediate, staged = [], [], []
    for number, line in enumerate(raw, 1):
        s, m, energy, *weights = map(int, line.split())
        require(line.endswith(b"\n") and len(weights) == s and 13 <= s <= 17 and 12 <= m <= 18,
                "Malformed original profile dimensions")
        require(weights == sorted(weights, reverse=True) and max(weights) == m and min(weights) >= 2
                and sum(weights) <= 93 and tuple(weights) not in unique, "Invalid or duplicated original weight profile")
        unique.add(tuple(weights))
        before[s, m] += 1
        heavy = [(i, w) for i, w in enumerate(weights) if w >= 4]
        heavy_counts[len(heavy)] += 1
        if len(heavy) != 9:
            require(number not in stored and number not in prior, "Non-nine-heavy profile credited")
            kept.append(line); intermediate.append(line); staged.append(line)
            continue
        n2, n3 = weights.count(2), weights.count(3)
        B = n2+2*n3
        price_values = [{"lambda": price, "capacity_upper_bound": price*B +
                        sum(max(E[k][w]-price*k for k in range(4)) for _, w in heavy)}
                        for price in range(1, 10)]
        best = min(price_values, key=lambda x: (x["capacity_upper_bound"], x["lambda"]))
        price, bound = best["lambda"], best["capacity_upper_bound"]
        new_dual = bound < 48
        if new_dual:
            dual.add(number); prices[price] += 1; bounds_seen[bound] += 1
        if number in prior:
            expected = deepcopy(prior[number])
            require(expected["weights"] == weights and expected["source_line_ascii"] == line.decode("ascii")
                    and expected["source_line_sha256"] == hashlib.sha256(line).hexdigest(),
                    "Earlier matching certificate is not bound to this original row")
            expected.update(chosen_method="matching", already_in_previous745_stage=True,
                            three_direction_price_minimum=bound, three_direction_price_smallest_argmin=price,
                            three_direction_price_also_excludes=new_dual)
            old_counts[s, m] += 1
        else:
            intermediate.append(line)
            if not new_dual:
                require(number not in stored, "Unexcluded original profile removed")
                kept.append(line); staged.append(line)
                continue
            resources = []
            for position, w in heavy:
                local = [E[k][w] for k in range(4)]
                excess = [local[k]-price*k for k in range(4)]
                maximum = max(excess)
                resources.append({"profile_position_zero_based": position, "weight": w,
                                  "E_k_for_k0_through3": local, "E_k_minus_lambda_k": excess,
                                  "maximum_excess": maximum, "smallest_maximizing_k": excess.index(maximum)})
            expected = {
                "source_line": number, "source_line_sha256": hashlib.sha256(line).hexdigest(),
                "source_line_ascii": line.decode("ascii"), "support_size": s, "maximum": m,
                "inherited_energy_metadata_not_used": energy, "weights": weights, "total_weight": sum(weights),
                "heavy_count": 9, "heavy_positions_zero_based": [i for i, _ in heavy],
                "chosen_method": "three_direction_price", "already_in_previous745_stage": False,
                "heavy_difference_upper_bound": 28, "missing_direction_lower_bound": 3,
                "selected_independent_missing_directions": 3, "required_total_capacity": 48,
                "price_lambda": price, "capacity_upper_bound": bound, "all_integer_price_bounds": price_values,
                "light_incidence_budget": B, "light_weight2_count": n2, "light_weight3_count": n3,
                "strict_gap": 48-bound, "price_tie_rule": "Minimum capacity upper bound; smallest integer lambda among ties.",
                "checked_integer_prices": list(range(1, 10)), "heavy_resources": resources,
                "heavy_excess_sum": sum(x["maximum_excess"] for x in resources), "priced_light_budget": price*B,
            }
        require(number in stored and equal(stored[number], expected), "Incorrect complete final certificate row")
        union.add(number); removed[s, m] += 1
    require(len(raw) == 183476 and heavy_counts[9] == 2187 and len(dual) == 488 and len(union) == 950,
            "Final scan totals differ")
    require(union == set(prior) | dual and len(dual & set(prior)) == 283 and len(dual-set(prior)) == 205,
            "Matching/price union double-counted or omitted a profile")
    require(len(kept) == 182526 and b"".join(kept) == b"".join(staged) == (DATA / "after_three_direction_survivors.txt").read_bytes(),
            "Direct950 and staged745+205 frontier bytes differ")
    require(b"".join(intermediate) == (DATA / "after_matching_incidence_survivors.txt").read_bytes(),
            "Earlier matching survivor bytes differ")

    def fields(original, previous, cumulative):
        return {"original": original, "previously_excluded": previous, "newly_excluded": cumulative-previous,
                "cumulative_excluded": cumulative, "remaining": original-cumulative}

    def aggregate(index):
        return {str(value): fields(sum(n for cell, n in before.items() if cell[index] == value),
                                  sum(n for cell, n in old_counts.items() if cell[index] == value),
                                  sum(n for cell, n in removed.items() if cell[index] == value))
                for value in sorted({cell[index] for cell in before})}

    by_support, by_maximum = aggregate(0), aggregate(1)
    cells = [{"support_size": s, "maximum": m, **fields(before[s, m], old_counts[s, m], removed[s, m])}
             for s, m in sorted(before)]
    require(certificate["by_support"] == by_support and certificate["by_maximum"] == by_maximum
            and certificate["by_support_and_maximum"] == cells, "Aggregate final ledger table differs")
    scan = certificate["exhaustive_scan"]
    for key, value in {"all_original_profiles_scanned": 183476, "nine_heavy_profiles_checked": 2187,
                       "matching_profiles_excluded": 745, "price_profiles_excluded": 488, "overlap_profiles": 283,
                       "new_price_profiles": 205, "union_profiles_excluded": 950,
                       "nine_heavy_profiles_passing_both_screens": 1237}.items():
        require(type(scan[key]) is int and scan[key] == value, "Incorrect exhaustive scan statistic")
    require(scan["all_price_successes_by_smallest_lambda"] == {str(k): n for k, n in sorted(prices.items())}
            and scan["all_price_successes_by_upper_bound"] == {str(k): n for k, n in sorted(bounds_seen.items())}
            and scan["chosen_certificate_methods"] == {"matching": 745, "three_direction_price": 205},
            "Incorrect price distribution or method partition")
    pins[str(Path(__file__).relative_to(ROOT))] = sha(Path(__file__))
    report = {
        "status": "PASS_INDEPENDENT_THREE_DIRECTION_PROOF_TABLE_AND_950_PROFILE_REVIEW",
        "reviewer": "Separate model agent /root/support13_geometry; not independent human review or proof-assistant formalization",
        "source_hashes": pins, "cube_tables_sha256": table_hash, "table_controls": table_controls,
        "original_profiles": 183476, "nine_heavy_profiles_checked": 2187,
        "prior_matching_exclusions": 745, "three_direction_price_exclusions": 488,
        "overlap": 283, "additional_exclusions": 205, "cumulative_exclusions": 950,
        "remaining_profiles": 182526, "by_support": by_support, "by_maximum": by_maximum,
        "complete_producer_source_read_only_review": True,
        "analytic_proof_review": [
            "At least nine heavy residues make the missing set plane-free; any three distinct missing directions are independent.",
            "For each heavy fibre the selected active heavy-light directions form an independent subset, so their pair-count sum is at most E_k(w).",
            "Heavy-light incidences plus twice the number of active light-light edges are bounded by n2+2n3.",
            "The exact price identity has remainder (1-2*lambda)*u, which is nonpositive for every real lambda>=1/2.",
            "All local cube subsets, exact coset decomposition and the example giving46<48 are correct; k0 is the explicit zero-edge case.",
            "The producer correctly scopes new rows to nine heavy fibres, scans all original profiles, keeps original matching witnesses, and selects integer-price minima with the declared tie rule."
        ],
        "all950_complete_rows_and_all_aggregate_tables_recomputed": True,
        "direct_and_staged_survivors_byte_identical": True,
        "all_frozen_semantic_inputs_preserved": True,
        "review_imports_producer_or_verifier": False,
        "spectrum_sumset_or_SAT_files_read": False,
        "SAT_or_proof_checker_calls": 0,
        "blocking_issues_found": [],
    }
    output = HERE / "THREE_DIRECTION_FINAL_REVIEW.json"
    output.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({"status": report["status"], "remaining_profiles": report["remaining_profiles"],
                      "local_cube_masks": table_controls["complete_local_cube_masks_checked"],
                      "independent_actual_subsets": table_controls["independent_actual_F2_4_subsets_checked"],
                      "review_receipt_sha256": sha(output)}, indent=2))


if __name__ == "__main__":
    main()
