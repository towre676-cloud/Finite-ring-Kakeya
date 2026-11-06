#!/usr/bin/env python3
"""Replay the final950 matching/three-direction price profile certificates.

Exactly276 subsets of cubes of dimensions1,2,3 determine the local edge
tables. Exact integer max-plus convolution over their F2^5 cosets determines
E_k(w). Prices1..9 are checked with the smallest-price tie convention.
The frozen745 stage is included without duplicate credit. No SAT is run.
"""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research_round7/charging/after_integer_dual_survivors.txt"
SOURCE_SHA256 = "1c493598b5586dec62b736df01c10df441751a222e0926691a20c330853c2df5"
LATEST_PRIOR_PINS = {
    "research_round8/incidence/verify_matching_incidence_profiles.py":
        "2c396594633cd743d86bd165a4edfb0588eb6bc7df7a61217ce09036ca278e23",
    "research_round8/incidence/MATCHING_INCIDENCE_PROFILE_EXCLUSIONS.json":
        "bd9a618e5743ecd1564770e09ab69b018b1e30c2c15d85803aeca7aa5fa9a681",
    "research_round8/incidence/after_matching_incidence_survivors.txt":
        "1996a016795c5494c29a07558fb1204306cfb081de5257d7668d2c9e377d2cfd",
}
PROOF_PINS = {
    "research_round8/incidence/THREE_DIRECTION_PRICE_LEMMA.md":
        "2363be25c67adc6cbe0cbc563904491e0290a9a9a4ba375c180a94237ab6316c",
    "research_round8/incidence/MISSING_DIRECTION_INCIDENCE.md":
        "4d52fcdb7b60b09cc52934ab3fab575d07b4320789879de664592c3a129c9034",
    "research_round7/dense_encoder/NINE_POINT_DIFFERENCE_ANALYTIC_PROOF.md":
        "cb5671d36c1b857023aee9481491881d56cf9aef27734b104208b6fbbb6b5ba8",
}
CERTIFICATE = HERE / "THREE_DIRECTION_PROFILE_EXCLUSIONS.json"
SURVIVORS = HERE / "after_three_direction_survivors.txt"
RECEIPT = HERE / "THREE_DIRECTION_PROFILE_REPLAY.json"
SCOPE = "Every placement and actual fibre shape of these950 whole profiles, in both rings. Matching and three-direction price certificates are combined without duplicate credit; no SAT role is added."
EXPECTED_SURVIVOR_SHA256 = "1eaf4e100d9b9a4a65556c5251249fd1e7062d51e8771b7af83761ffabbd4423"
EXPECTED_REMAINING_SUPPORT = {13: 84946, 14: 74039, 15: 19362, 16: 3793, 17: 386}
EXPECTED_REMOVED_MAXIMUM = {12: 129, 13: 68, 14: 191, 15: 108, 16: 250, 17: 94, 18: 110}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, indent=2) + "\n").encode("utf-8")


def atomic_write(path, data):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def read_inputs():
    for path, expected in {**LATEST_PRIOR_PINS, **PROOF_PINS}.items():
        require(digest((ROOT / path).read_bytes()) == expected, "Changed pinned input: " + path)
    require(digest((ROOT / SOURCE).read_bytes()) == SOURCE_SHA256, "Changed original Round7 frontier")
    spec = importlib.util.spec_from_file_location("frozen_round8_incidence745", HERE / "verify_matching_incidence_profiles.py")
    previous = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(previous)
    raw, profiles, first16, prior128, prior175, frontier175, older_proof_pins = previous.read_inputs()
    old_payload, frontier745 = previous.build_expected(raw, profiles, first16, prior128, prior175, frontier175)
    require(previous.CERTIFICATE.read_bytes() == json_bytes(old_payload), "Frozen745 certificate does not reproduce")
    require(previous.SURVIVORS.read_bytes() == frontier745, "Frozen745 frontier does not reproduce")
    rows = {}
    for row in old_payload["certificates"]:
        number = previous.check_row(row, raw, profiles, first16, prior128, prior175)
        require(number not in rows, "Duplicated frozen matching certificate")
        rows[number] = row
    require(len(rows) == 745, "Frozen matching count differs")
    return raw, profiles, rows, frontier745.splitlines(keepends=True), {
        **previous.PRIOR_PINS, **LATEST_PRIOR_PINS}, {**older_proof_pins, **previous.PROOF_PINS}


def compute_cube_tables():
    E = {0: [0]*33}
    dimensions = []
    subset_count = 0
    for k in (1, 2, 3):
        vertices = 1 << k
        edges = [(v, v ^ (1 << axis)) for v in range(vertices) for axis in range(k)
                 if v < (v ^ (1 << axis))]
        require(len(edges) == k*vertices//2 and len(set(edges)) == len(edges), "Cube edge inventory differs")
        census = []
        g = [-1]*(vertices+1)
        g_witness = [None]*(vertices+1)
        for mask in range(1 << vertices):
            occupancy = mask.bit_count()
            edge_count = sum(bool((mask >> a) & 1) and bool((mask >> b) & 1) for a, b in edges)
            census.append({"subset_mask": mask, "occupancy": occupancy, "induced_edges": edge_count})
            if edge_count > g[occupancy]:
                g[occupancy], g_witness[occupancy] = edge_count, mask
        require(g == {1: [0, 0, 1], 2: [0, 0, 1, 2, 4],
                      3: [0, 0, 1, 2, 4, 5, 7, 9, 12]}[k], "Local cube maxima differ")
        subset_count += len(census)
        cosets = 32//vertices
        layers = [[0] + [None]*32]
        choices = [[None]*33]
        for count in range(1, cosets+1):
            old = layers[-1]
            new, choice = [], []
            for weight in range(33):
                candidates = [(old[weight-z] + g[z], z) for z in range(min(vertices, weight)+1)
                              if old[weight-z] is not None]
                if not candidates:
                    new.append(None); choice.append(None)
                else:
                    best = max(value for value, _ in candidates)
                    new.append(best)
                    choice.append(min(z for value, z in candidates if value == best))
            require(all((value is None) == (w > count*vertices) for w, value in enumerate(new)),
                    "Coset knapsack reachability differs")
            layers.append(new); choices.append(choice)
        E[k] = layers[-1]
        require(all(type(value) is int for value in E[k]), "An ambient occupancy is unreachable")
        for w in range(33):
            require(0 <= E[k][w] <= k*(w//2), "Independent-direction matching ceiling violated")
            require(E[k][32-w] == 16*k-k*w+E[k][w], "Regular-graph complement identity violated")
            # Reconstruct an explicit optimal occupancy vector through the
            # recorded choices, proving feasibility as well as the recurrence.
            remaining, value = w, 0
            for count in range(cosets, 0, -1):
                z = choices[count][remaining]
                require(type(z) is int and 0 <= z <= vertices, "Invalid knapsack witness occupancy")
                value += g[z]; remaining -= z
            require(remaining == 0 and value == E[k][w], "Knapsack witness does not attain its maximum")
        dimensions.append({"dimension": k, "cube_vertices": vertices, "cube_edges": edges,
                           "subsets_enumerated": len(census), "complete_subset_census": census,
                           "local_edge_maxima_by_occupancy": g,
                           "smallest_maximizing_subset_masks": g_witness,
                           "ambient_cosets": cosets,
                           "max_plus_layers_including_zero_cosets": layers,
                           "smallest_last_coset_occupancy_at_each_maximum": choices})
    require(subset_count == 276 and E[1] == [w//2 for w in range(33)], "Complete cube census differs")
    table = {"ambient_dimension": 5, "ambient_vertices": 32,
             "enumerated_cube_dimensions": [1, 2, 3], "total_local_subsets": subset_count,
             "E0_definition": "Zero selected directions give zero edges for every occupancy.",
             "dimensions": dimensions, "E_k_for_weights0_through32": {str(k): E[k] for k in range(4)}}
    return table, E


def validate_cube_tables(candidate):
    expected, E = compute_cube_tables()
    require(json_bytes(candidate) == json_bytes(expected), "Stored cube census or exact knapsack table differs")
    return E


def price_score(profile, E):
    _, _, _, weights = profile
    heavy = [(i, w) for i, w in enumerate(weights) if w >= 4]
    if len(heavy) != 9:
        return None
    n2, n3 = weights.count(2), weights.count(3)
    budget = n2+2*n3
    values = []
    for price in range(1, 10):
        upper = price*budget + sum(max(E[k][w]-price*k for k in range(4)) for _, w in heavy)
        values.append({"lambda": price, "capacity_upper_bound": upper})
    best = min(values, key=lambda row: (row["capacity_upper_bound"], row["lambda"]))
    price, bound = best["lambda"], best["capacity_upper_bound"]
    return {"price_lambda": price, "capacity_upper_bound": bound, "all_integer_price_bounds": values,
            "light_incidence_budget": budget, "light_weight2_count": n2, "light_weight3_count": n3,
            "strict_gap": 48-bound}


def make_row(number, raw, profile, prior_rows, bounds, E):
    require(bounds is not None, "The final screen is scoped to nine heavy fibres")
    if number in prior_rows:
        row = deepcopy(prior_rows[number])
        row.update({"chosen_method": "matching", "already_in_previous745_stage": True,
                    "three_direction_price_minimum": bounds["capacity_upper_bound"],
                    "three_direction_price_smallest_argmin": bounds["price_lambda"],
                    "three_direction_price_also_excludes": bounds["strict_gap"] > 0})
        return row
    require(bounds["strict_gap"] > 0, "New profile has no strict three-direction price contradiction")
    s, maximum, energy, weights = profile
    price = bounds["price_lambda"]
    resources = []
    for position, weight in enumerate(weights):
        if weight < 4:
            continue
        local_E = [E[k][weight] for k in range(4)]
        excess = [local_E[k]-price*k for k in range(4)]
        maximum_excess = max(excess)
        resources.append({"profile_position_zero_based": position, "weight": weight,
                          "E_k_for_k0_through3": local_E, "E_k_minus_lambda_k": excess,
                          "maximum_excess": maximum_excess,
                          "smallest_maximizing_k": excess.index(maximum_excess)})
    heavy_total = sum(row["maximum_excess"] for row in resources)
    light_cost = price*bounds["light_incidence_budget"]
    require(light_cost+heavy_total == bounds["capacity_upper_bound"] < 48, "Displayed dual costs do not refute48")
    return {"source_line": number, "source_line_sha256": digest(raw), "source_line_ascii": raw.decode("ascii"),
            "support_size": s, "maximum": maximum, "inherited_energy_metadata_not_used": energy,
            "weights": list(weights), "total_weight": sum(weights), "heavy_count": 9,
            "heavy_positions_zero_based": [row["profile_position_zero_based"] for row in resources],
            "chosen_method": "three_direction_price", "already_in_previous745_stage": False,
            "heavy_difference_upper_bound": 28, "missing_direction_lower_bound": 3,
            "selected_independent_missing_directions": 3,
            "required_total_capacity": 48, **bounds,
            "price_tie_rule": "Minimum capacity upper bound; smallest integer lambda among ties.",
            "checked_integer_prices": list(range(1, 10)),
            "heavy_resources": resources, "heavy_excess_sum": heavy_total,
            "priced_light_budget": light_cost}


def check_row(row, raw_lines, profiles, prior_rows, E):
    require(isinstance(row, dict), "Certificate row must be an object")
    number = row.get("source_line")
    require(type(number) is int and 1 <= number <= len(profiles), "Invalid original source-line number")
    bounds = price_score(profiles[number-1], E)
    expected = make_row(number, raw_lines[number-1], profiles[number-1], prior_rows, bounds, E)
    require(json_bytes(row) == json_bytes(expected), "Certificate differs from exact source, method, cube table or price derivation")
    return number


def build_expected(raw, profiles, prior_rows, prior_survivors, prior_pins, cube_tables, E):
    scores, dual, h9 = {}, set(), 0
    price_histogram, bound_histogram = Counter(), Counter()
    for number, profile in enumerate(profiles, 1):
        bounds = price_score(profile, E)
        if bounds is None:
            continue
        h9 += 1
        scores[number] = bounds
        if bounds["strict_gap"] > 0:
            dual.add(number)
            price_histogram[bounds["price_lambda"]] += 1
            bound_histogram[bounds["capacity_upper_bound"]] += 1
    matching = set(prior_rows)
    union = matching | dual
    require(len(profiles) == 183476 and h9 == 2187, "Full scan inventory differs")
    require(len(dual) == 488 and len(matching & dual) == 283 and len(dual-matching) == 205 and len(union) == 950,
            "Matching/price union counts differ")
    require(price_histogram == {4: 486, 5: 1, 6: 1}, "Smallest-price minimizer distribution differs")
    rows = [make_row(number, raw[number-1], profiles[number-1], prior_rows, scores[number], E)
            for number in sorted(union)]
    require(Counter(row["chosen_method"] for row in rows) == {"matching": 745, "three_direction_price": 205},
            "Disjoint chosen-method accounting differs")
    survivors = b"".join(line for number, line in enumerate(raw, 1) if number not in union)
    number_by_raw = {line: number for number, line in enumerate(raw, 1)}
    staged = [line for line in prior_survivors if number_by_raw[line] not in dual]
    require(len(staged) == 182526 and b"".join(staged) == survivors,
            "Direct950 and prior745-minus205 byte sequences differ")
    require(digest(survivors) == EXPECTED_SURVIVOR_SHA256, "Independently predicted survivor hash differs")
    before = Counter((p[0], p[1]) for p in profiles)
    removed = Counter((profiles[i-1][0], profiles[i-1][1]) for i in union)
    old = Counter((profiles[i-1][0], profiles[i-1][1]) for i in matching)
    after = before-removed
    def aggregate(index):
        return {str(value): {"original": sum(n for cell, n in before.items() if cell[index] == value),
                            "previously_excluded": sum(n for cell, n in old.items() if cell[index] == value),
                            "newly_excluded": sum(n for cell, n in (removed-old).items() if cell[index] == value),
                            "cumulative_excluded": sum(n for cell, n in removed.items() if cell[index] == value),
                            "remaining": sum(n for cell, n in after.items() if cell[index] == value)}
                for value in sorted({cell[index] for cell in before})}
    by_support, by_maximum = aggregate(0), aggregate(1)
    require({int(k): row["remaining"] for k, row in by_support.items()} == EXPECTED_REMAINING_SUPPORT and
            {int(k): row["cumulative_excluded"] for k, row in by_maximum.items()} == EXPECTED_REMOVED_MAXIMUM,
            "Final support or maximum accounting differs")
    scan = {"all_original_profiles_scanned": 183476, "nine_heavy_profiles_checked": h9,
            "matching_profiles_excluded": 745, "price_profiles_excluded": 488,
            "overlap_profiles": 283, "new_price_profiles": 205,
            "union_profiles_excluded": 950, "nine_heavy_profiles_passing_both_screens": h9-950,
            "all_price_successes_by_smallest_lambda": {str(k): n for k, n in sorted(price_histogram.items())},
            "all_price_successes_by_upper_bound": {str(k): n for k, n in sorted(bound_histogram.items())},
            "chosen_certificate_methods": {"matching": 745, "three_direction_price": 205},
            "scope": "Exhaustive application of these displayed screens to the pinned original ledger; passing does not establish realizability."}
    payload = {"format": "kakeya-round8-three-direction-price-profile-exclusions-v1",
               "original_input_file": SOURCE, "original_input_sha256": SOURCE_SHA256,
               "original_profiles": 183476, "intermediate_profiles": 182731,
               "previously_excluded_profiles": 745, "newly_excluded_profiles": 205,
               "cumulative_excluded_profiles": 950, "remaining_profiles": 182526,
               "earlier_nested_stage_sizes": [16, 128, 175, 745],
               "prior_stage_pins": prior_pins, "analytic_proof_pins": PROOF_PINS,
               "producer_verifier": str(Path(__file__).resolve().relative_to(ROOT)),
               "producer_verifier_sha256": digest(Path(__file__).read_bytes()),
               "survivor_file": str(SURVIVORS.relative_to(ROOT)), "survivor_sha256": digest(survivors),
               "scope": SCOPE,
               "mathematical_dependencies": [
                   "The frozen745 matching exclusions and their pinned analytic matching/difference lemmas.",
                   "Nine heavy residues have at least three independent missing directions; light2/light3 fibres contribute at most1/2 incidences across them.",
                   "The276 local cube subsets and exact coset convolution compute E_k(w) for k0..3 and weights0..32.",
                   "For lambda>=1/2, total capacity is at most lambda*(n2+2*n3)+sum_heavy max_k(E_k(w)-lambda*k); the present certificates use only integer prices1..9.",
                   "No full F2^5 fibre-spectrum census, quotient-sumset table, inherited energy value or SAT solver is used by these new profile inequalities.",
                   "The final950 count is a union, including all earlier stages once. It gives no additional SAT-role credit."
               ],
               "cube_tables": cube_tables, "cube_tables_sha256": digest(json_bytes(cube_tables)),
               "exhaustive_scan": scan, "by_support": by_support, "by_maximum": by_maximum,
               "by_support_and_maximum": [{"support_size": s, "maximum": m, "original": before[s, m],
                   "previously_excluded": old[s, m], "newly_excluded": removed[s, m]-old[s, m],
                   "cumulative_excluded": removed[s, m], "remaining": after[s, m]} for s, m in sorted(before)],
               "certificates": rows}
    return payload, survivors


def negative_controls(rows, raw, profiles, prior_rows, cube_tables, E):
    new = next(row for row in rows if row["chosen_method"] == "three_direction_price")
    bad_resources = deepcopy(new["heavy_resources"])
    bad_resources[0]["E_k_for_k0_through3"][3] += 1
    mutations = [
        ("invalid_source_line", "source_line", 0),
        ("wrong_source_hash", "source_line_sha256", "0"*64),
        ("wrong_chosen_method", "chosen_method", "matching"),
        ("unreviewed_zero_price", "price_lambda", 0),
        ("wrong_price_tie_choice", "price_lambda", new["price_lambda"]+1),
        ("wrong_light_budget", "light_incidence_budget", -1),
        ("wrong_heavy_E_value", "heavy_resources", bad_resources),
        ("wrong_heavy_maximum_sum", "heavy_excess_sum", -1),
        ("nonstrict_capacity_bound", "capacity_upper_bound", 48),
        ("double_counted_matching_stage", "already_in_previous745_stage", True),
        ("boolean_in_integer_field", "strict_gap", True),
    ]
    controls = []
    for label, field, value in mutations:
        row = deepcopy(new); row[field] = value
        try:
            check_row(row, raw, profiles, prior_rows, E)
        except (ValueError, KeyError, TypeError):
            controls.append({"control": label, "rejected": True})
        else:
            raise ValueError("Corrupted dual certificate accepted: " + label)
    old = deepcopy(next(row for row in rows if row["chosen_method"] == "matching"))
    old["prefix_capacity_with_rho_minus_one_lights"] = 16
    try:
        check_row(old, raw, profiles, prior_rows, E)
    except (ValueError, KeyError, TypeError):
        controls.append({"control": "corrupted_inherited_matching_prefix", "rejected": True})
    else:
        raise ValueError("Corrupted matching certificate accepted")
    for label in ("wrong_cube_edge_count", "wrong_knapsack_value"):
        altered = deepcopy(cube_tables)
        if label == "wrong_cube_edge_count":
            altered["dimensions"][2]["complete_subset_census"][-1]["induced_edges"] -= 1
        else:
            altered["dimensions"][2]["max_plus_layers_including_zero_cosets"][-1][15] += 1
        try:
            validate_cube_tables(altered)
        except ValueError:
            controls.append({"control": label, "rejected": True})
        else:
            raise ValueError("Corrupted cube table accepted: " + label)
    return controls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Create missing deterministic final-stage artifacts")
    args = parser.parse_args()
    started = time.monotonic()
    atomic_write(RECEIPT, json_bytes({"status": "RUNNING", "write_mode": args.write}))
    try:
        raw, profiles, prior_rows, prior_survivors, prior_pins, inherited_proof_pins = read_inputs()
        cube_tables, E = compute_cube_tables()
        payload, survivor_bytes = build_expected(raw, profiles, prior_rows, prior_survivors, prior_pins, cube_tables, E)
        payload_bytes = json_bytes(payload)
        if args.write:
            for path, data in ((CERTIFICATE, payload_bytes), (SURVIVORS, survivor_bytes)):
                require(not path.exists() or path.read_bytes() == data,
                        "Refusing to overwrite a different semantic artifact: " + path.name)
            for path, data in ((CERTIFICATE, payload_bytes), (SURVIVORS, survivor_bytes)):
                if not path.exists():
                    atomic_write(path, data)
        require(CERTIFICATE.read_bytes() == payload_bytes, "Stored950 certificate differs from exact regeneration")
        require(SURVIVORS.read_bytes() == survivor_bytes, "Stored950 frontier differs in bytes or order")
        stored = json.loads(CERTIFICATE.read_text())
        validate_cube_tables(stored["cube_tables"])
        checked = [check_row(row, raw, profiles, prior_rows, E) for row in stored["certificates"]]
        require(len(set(checked)) == len(checked) == 950, "Duplicated or missing final certificate")
        controls = negative_controls(stored["certificates"], raw, profiles, prior_rows, cube_tables, E)
        for path, expected in prior_pins.items():
            require(digest((ROOT / path).read_bytes()) == expected, "Prior semantic artifact changed during replay")
        receipt = {key: payload[key] for key in (
            "original_input_file", "original_input_sha256", "original_profiles", "intermediate_profiles",
            "previously_excluded_profiles", "newly_excluded_profiles", "cumulative_excluded_profiles", "remaining_profiles",
            "by_support", "by_maximum", "by_support_and_maximum", "prior_stage_pins", "analytic_proof_pins",
            "exhaustive_scan", "scope")}
        receipt.update({"status": "PASS_THREE_DIRECTION_PROFILE_REPLAY",
                        "transitive_prior_analytic_pins": inherited_proof_pins,
                        "coverage": {
                            "every_original_profile_scanned": True,
                            "excluded_original_source_lines": checked,
                            "previously_excluded_original_source_lines": sorted(prior_rows),
                            "newly_excluded_original_source_lines": sorted(set(checked)-set(prior_rows)),
                            "complete_276_local_cube_subsets_verified": True,
                            "all_exact_coset_knapsack_layers_verified": True,
                            "all_selected_price_minima_and_ties_verified": True,
                            "every_retained_line_preserved_byte_identically_and_in_order": True,
                            "direct_minus950_and_prior745_minus205_regeneration_identical": True,
                            "all_prior_stage_semantic_artifacts_unchanged": True,
                            "energy_metadata_used_in_exclusion": False},
                        "cube_tables_sha256": payload["cube_tables_sha256"],
                        "local_cube_subset_counts": {"1": 4, "2": 16, "3": 256},
                        "local_cube_subsets_total": 276,
                        "E_k_for_weights0_through32": cube_tables["E_k_for_weights0_through32"],
                        "certificate_file": str(CERTIFICATE.relative_to(ROOT)), "certificate_sha256": digest(CERTIFICATE.read_bytes()),
                        "survivor_file": str(SURVIVORS.relative_to(ROOT)), "survivor_sha256": digest(survivor_bytes),
                        "verifier_sha256": digest(Path(__file__).read_bytes()), "negative_controls": controls,
                        "dependency_boundary": "The pinned hand proofs give the geometric implications. The276 local cube subsets, integer convolution and ledger replay are explicit finite computations, not proof-assistant formalizations. No SAT case is credited.",
                        "elapsed_seconds": round(time.monotonic()-started, 6)})
        atomic_write(RECEIPT, json_bytes(receipt))
        print(json.dumps({key: receipt[key] for key in (
            "status", "original_profiles", "previously_excluded_profiles", "newly_excluded_profiles",
            "cumulative_excluded_profiles", "remaining_profiles", "by_support")}, indent=2))
    except BaseException as error:
        atomic_write(RECEIPT, json_bytes({"status": "FAIL", "exception_type": type(error).__name__,
                                        "message": str(error), "elapsed_seconds": round(time.monotonic()-started, 6)}))
        raise


if __name__ == "__main__":
    main()
