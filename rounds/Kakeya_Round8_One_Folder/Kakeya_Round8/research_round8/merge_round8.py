#!/usr/bin/env python3
"""Reconcile exact marked-role coverage into the Round8 theorem ledger."""
import copy
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "research_round8"
EXPECTED = {377850134: 109, 411136406: 111, 671697334: 110, 2185856310: 110}
R7_MANIFEST_SHA = "7646c5f0c2664a9206666cdbf1ff9ae7b920af0badeb952c3ae0aa00e19d9ae9"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def read(relative):
    return json.loads((ROOT / relative).read_text())


def main():
    (HERE / "ROUND8_MERGED_REPLAY.json").write_text(json.dumps({"status": "RUNNING"}, indent=2) + "\n")
    require(sha(ROOT / "MANIFEST_ROUND7.json") == R7_MANIFEST_SHA, "Inherited manifest changed")
    sealed = {r["path"]: r["sha256"] for r in read("MANIFEST_ROUND7.json")["files"]}
    old_paths = ["Kakeya_Research_Frontier_Round7.json",
                 "research_round7/geometry/SUPPORT13_MARKING_MAP.json",
                 "research_round7/support13/SUPPORT13_CERTIFICATE_MANIFEST.json"]
    for p in old_paths:
        require(sha(ROOT / p) == sealed[p], "Inherited accounting source changed: " + p)
    old = read(old_paths[0])
    mapping = read(old_paths[1])
    old_certificates = read(old_paths[2])

    path = HERE / "strengthened/compact/compact_certificates.py"
    spec = importlib.util.spec_from_file_location("round8_compact_binding", path)
    compact_module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = compact_module
    spec.loader.exec_module(compact_module)
    compact, original = compact_module.load()
    replay_path = "research_round8/strengthened/compact/COMPACT_CERTIFICATE_REPLAY.json"
    replay = read(replay_path)
    require(replay["status"] == "PASS_ALL_ROUND8_OUTCOMES_VIA_COMPACT_EXACT_CNF_CAKEML_PROOFS"
            and replay["full_inventory_replayed"] is True, "A complete accepted compact replay is required")
    require(replay["compact_manifest_sha256"] == sha(compact_module.MANIFEST)
            and replay["source_manifest_sha256"] == compact["source_manifest_sha256"]
            and replay["source_hashes"] == compact["source_hashes"], "Fresh replay sources differ")
    checked = {r["case_id"]: r for r in replay["cases"]}
    require(len(checked) == len(replay["cases"]) == 4, "Exactly four checked new cases required")
    require(set(checked) == {r["case_id"] for r in compact["cases"]},
            "Checked-case IDs differ from the compact inventory")
    new = []
    for item in compact["cases"]:
        row = item["original_case"]
        case = checked[item["case_id"]]
        require(row["nonzero_support_mask"] in EXPECTED and row["maximum_interval"] == [11, 11]
                and row["total_upper_bound"] == 93, "Unexpected mathematical scope")
        require(case["status"] == compact_module.V.PASS
                and case["nonzero_support_mask"] == row["nonzero_support_mask"]
                and case["maximum_interval"] == row["maximum_interval"]
                and case["mode"] == row["mode"]
                and case["representation"] == "COMPACT_DRAT"
                and case["checked_proof_sha256"] == item["core_sha256"],
                "Fresh replay row has different status or mathematical meaning")
        require(case["exclusion_credited"] is True
                and case["audit"]["status"] == "PASS_CNF_UNSAT_VIA_CAKEML_LRAT"
                and case["audit"]["input_sha256"] == {"cnf": row["cnf_sha256"], "drat": item["core_sha256"]}
                and case["regeneration"]["cnf_sha256"] == row["cnf_sha256"], "Fresh case lacks exact proof binding")
        new.append(row)
    require({r["nonzero_support_mask"] for r in new} == set(EXPECTED), "Target marked roles are incomplete")

    covered = {r["nonzero_support_mask"] for r in old_certificates["cases"]
               if r["maximum_interval"][0] <= 11 <= r["maximum_interval"][1]}
    require(len(covered) == 35, "Inherited direct exact-eleven count differs")
    require(not (covered & set(EXPECTED)), "A new role was already directly closed")
    covered.update(EXPECTED)
    groups = {g["unmarked_affine_orbit_id"]: g for g in mapping["groups"]}
    for mask, affine_class in EXPECTED.items():
        require(mask in groups[affine_class]["marked_nonzero_masks"], "Wrong largest-fibre orbit mapping")
    direct_closed = sorted(gid for gid, g in groups.items()
                           if set(g["marked_nonzero_masks"]) <= covered)
    previous = old["dimension5_strata"]["maximum11"]
    new_classes = sorted(set(previous["remaining_orbits"]) & set(direct_closed))
    require(new_classes == [109, 110, 111], "Whole-class closure arithmetic differs")
    remaining = [i for i in previous["remaining_orbits"] if i not in new_classes]
    require(len(remaining) == 42, "Wrong maximum-eleven class count")

    # These are whole-profile consequences of the independent incidence
    # theorem, not extrapolations from the four marked SAT refutations.
    profile_input = "research_round7/charging/after_integer_dual_survivors.txt"
    profile_output = "research_round8/incidence/after_incidence_survivors.txt"
    require(sha(ROOT / profile_input) == "1c493598b5586dec62b736df01c10df441751a222e0926691a20c330853c2df5",
            "Prior middle-profile frontier changed")
    original_lines = (ROOT / profile_input).read_bytes().splitlines(keepends=True)
    removed, kept, keys = [], [], set()
    removed_by_maximum = {12: 0, 13: 0}
    for number, line in enumerate(original_lines, 1):
        values = list(map(int, line.split()))
        size, maximum, energy = values[:3]
        weights = values[3:]
        require(len(weights) == size and maximum == max(weights) and min(weights) >= 2
                and weights == sorted(weights, reverse=True) and sum(weights) <= 93,
                "Malformed old profile")
        key = tuple(weights)
        require(key not in keys, "Duplicate whole weight profile")
        keys.add(key)
        heavy = sum(w >= 4 for w in weights)
        if size == 13 and maximum in (12, 13) and heavy < 10:
            require(heavy == 9, "Unexpected incidence exclusion scope")
            removed.append({"source_line": number, "maximum": maximum, "weights": weights})
            removed_by_maximum[maximum] += 1
        else:
            kept.append(line)
    require(len(original_lines) == 183476 and len(removed) == 16 and len(kept) == 183460
            and removed_by_maximum == {12: 10, 13: 6}, "Whole-profile exclusion arithmetic differs")
    require((ROOT / profile_output).read_bytes() == b"".join(kept),
            "New survivor file does not preserve exactly the unexcluded profile bytes")
    profile_replay = read("research_round8/incidence/INCIDENCE_PROFILE_EXCLUSIONS_REPLAY.json")
    require(profile_replay["status"] == "PASS_EXACT_INCIDENCE_PROFILE_REPLAY"
            and profile_replay["profiles_before"] == 183476
            and profile_replay["whole_profiles_excluded"] == 16
            and profile_replay["profiles_remaining"] == 183460,
            "Incidence whole-profile replay has not passed for this exact ledger")
    profile_certificate = "research_round8/incidence/INCIDENCE_PROFILE_EXCLUSIONS.json"
    profile_verifier = "research_round8/incidence/verify_incidence_profile_exclusions.py"
    for file_key, hash_key, expected_path in [
            ("input_file", "input_sha256", profile_input),
            ("certificate_file", "certificate_sha256", profile_certificate),
            ("survivor_file", "survivor_sha256", profile_output)]:
        require(profile_replay[file_key] == expected_path
                and profile_replay[hash_key] == sha(ROOT / expected_path),
                "Incidence receipt has stale or mismatched file binding: " + expected_path)
    require(profile_replay["verifier_sha256"] == sha(ROOT / profile_verifier),
            "Incidence profile verifier changed after its replay")
    proof_paths = {"research_round8/incidence/MISSING_DIRECTION_INCIDENCE.md",
                   "research_round7/dense_encoder/NINE_POINT_DIFFERENCE_ANALYTIC_PROOF.md"}
    require(set(profile_replay["analytic_proof_pins"]) == proof_paths
            and all(sha(ROOT / p) == h for p, h in profile_replay["analytic_proof_pins"].items()),
            "Incidence proof premises differ from the replay")
    profile_coverage = profile_replay["coverage"]
    require(profile_coverage["all_input_profiles_accounted_for"] is True
            and profile_coverage["every_removed_source_line_has_exact_certificate"] is True
            and profile_coverage["every_other_source_line_preserved_byte_identically_and_in_order"] is True
            and profile_coverage["excluded_source_lines"] == [r["source_line"] for r in removed]
            and profile_coverage["energy_metadata_used_in_exclusion"] is False,
            "Incidence receipt coverage differs from the independent complete scan")

    # Preserve the accepted sixteen-profile stage, then bind the separately
    # frozen extension through maximum fifteen. These are cumulative counts.
    first_removed = removed
    first_certificate = profile_certificate
    first_output = profile_output
    first_replay_path = "research_round8/incidence/INCIDENCE_PROFILE_EXCLUSIONS_REPLAY.json"
    removed, kept = [], []
    removed_by_maximum = {12: 0, 13: 0, 14: 0, 15: 0}
    for number, line in enumerate(original_lines, 1):
        values = list(map(int, line.split()))
        size, maximum, energy = values[:3]
        weights = values[3:]
        heavy = sum(w >= 4 for w in weights)
        if size == 13 and maximum in removed_by_maximum and heavy < 10:
            require(heavy == 9, "Unexpected extended incidence scope")
            partner = maximum // 2
            required = (16 + partner - 1) // partner
            available = weights.count(2) + 2 * weights.count(3)
            require(required >= 3 and 3 * required > available,
                    "Extended row lacks its strict incidence contradiction")
            removed.append({"source_line": number, "maximum": maximum, "weights": weights})
            removed_by_maximum[maximum] += 1
        else:
            kept.append(line)
    require(len(removed) == 128 and len(kept) == 183348
            and removed_by_maximum == {12: 10, 13: 6, 14: 69, 15: 43},
            "Extended whole-profile arithmetic differs")
    previous_lines = [r["source_line"] for r in first_removed]
    cumulative_lines = [r["source_line"] for r in removed]
    additional_lines = [n for n in cumulative_lines if n not in previous_lines]
    require(set(previous_lines) <= set(cumulative_lines) and len(additional_lines) == 112,
            "The extension does not preserve exactly the earlier sixteen exclusions")
    profile_output = "research_round8/incidence/after_extended_incidence_survivors.txt"
    profile_certificate = "research_round8/incidence/EXTENDED_INCIDENCE_PROFILE_EXCLUSIONS.json"
    profile_verifier = "research_round8/incidence/verify_extended_incidence_profiles.py"
    profile_replay_path = "research_round8/incidence/EXTENDED_INCIDENCE_PROFILE_REPLAY.json"
    require((ROOT / profile_output).read_bytes() == b"".join(kept),
            "Extended survivor bytes differ from the independent original-frontier scan")
    profile_replay = read(profile_replay_path)
    require(profile_replay["status"] == "PASS_EXTENDED_INCIDENCE_PROFILE_REPLAY"
            and profile_replay["original_profiles"] == 183476
            and profile_replay["intermediate_profiles"] == 183460
            and profile_replay["previously_excluded_profiles"] == 16
            and profile_replay["newly_excluded_profiles"] == 112
            and profile_replay["cumulative_excluded_profiles"] == 128
            and profile_replay["remaining_profiles"] == 183348,
            "Extended profile replay lacks the exact accepted counts")
    for file_key, hash_key, expected_path in [
            ("original_input_file", "original_input_sha256", profile_input),
            ("certificate_file", "certificate_sha256", profile_certificate),
            ("survivor_file", "survivor_sha256", profile_output)]:
        require(profile_replay[file_key] == expected_path
                and profile_replay[hash_key] == sha(ROOT / expected_path),
                "Extended receipt has stale or mismatched file binding: " + expected_path)
    require(profile_replay["verifier_sha256"] == sha(ROOT / profile_verifier),
            "Extended incidence verifier changed after replay")
    expected_scope = ("All support placements and fibre shapes of these128 profiles, "
                      "in both Z/4Z and F2[epsilon]/(epsilon^2). No extra SAT role is credited.")
    require(profile_replay["scope"] == read(profile_certificate)["scope"] == expected_scope,
            "Extended incidence receipt or certificate has the wrong mathematical scope")
    proof_paths = {"research_round8/incidence/SUPPORT13_MAX15_HEAVY_COROLLARY.md",
                   "research_round8/incidence/MISSING_DIRECTION_INCIDENCE.md",
                   "research_round7/dense_encoder/NINE_POINT_DIFFERENCE_ANALYTIC_PROOF.md"}
    prior_paths = {"research_round8/incidence/verify_incidence_profile_exclusions.py",
                   first_certificate, first_output}
    for field, expected_paths in (("analytic_proof_pins", proof_paths),
                                  ("prior_stage_pins", prior_paths)):
        require(set(profile_replay[field]) == expected_paths
                and all(sha(ROOT / p) == h for p, h in profile_replay[field].items()),
                "Extended receipt premise binding changed: " + field)
    coverage = profile_replay["coverage"]
    require(coverage["every_original_source_line_accounted_for"] is True
            and coverage["excluded_original_source_lines"] == cumulative_lines
            and coverage["previously_excluded_original_source_lines"] == previous_lines
            and coverage["newly_excluded_original_source_lines"] == additional_lines
            and coverage["every_retained_original_line_preserved_byte_identically_and_in_order"] is True
            and coverage["direct_and_intermediate_frontier_regeneration_identical"] is True
            and coverage["prior_sixteen_semantic_artifacts_unchanged"] is True
            and coverage["inherited_energy_metadata_used_in_exclusion"] is False,
            "Extended receipt coverage differs from the independent cumulative scan")

    # Independently reconstruct every later weight-only screen. The small
    # cube maxima here are checked independently by the final profile replay.
    small_cubes = {1: (0, 0, 1), 2: (0, 0, 1, 2, 4),
                   3: (0, 0, 1, 2, 4, 5, 7, 9, 12)}
    edge_tables = {0: [0] * 33}
    for dimension, cube in small_cubes.items():
        current = [0] + [-10000] * 32
        for _ in range(32 // (1 << dimension)):
            current = [max(current[w-z] + cube[z]
                           for z in range(min(w, len(cube)-1)+1))
                       for w in range(33)]
        edge_tables[dimension] = current
    excess = {w: {price: max(edge_tables[k][w]-price*k for k in range(4))
                  for price in range(1, 10)} for w in range(4, 19)}
    parsed, general_lines, matching_lines, price_lines = [], set(), set(), set()
    before_support = Counter()
    for number, raw in enumerate(original_lines, 1):
        size, maximum, energy, *weights = map(int, raw.split())
        parsed.append((size, maximum, weights))
        before_support[size] += 1
        heavy_weights = [w for w in weights if w >= 4]
        if len(heavy_weights) != 9:
            continue
        available = weights.count(2) + 2 * weights.count(3)
        uniform = (16 + maximum//2 - 1) // (maximum//2)
        if 3 * uniform > available:
            general_lines.add(number)
        cumulative = 0
        for rho, pair_ceiling in enumerate(sorted((w//2 for w in heavy_weights), reverse=True), 1):
            cumulative += pair_ceiling
            if cumulative >= 16:
                break
        require(cumulative >= 16 and size-9 <= 8, "Matching threshold premise changed")
        if 3 * rho > available:
            matching_lines.add(number)
        bound = min(price*available + sum(excess[w][price] for w in heavy_weights)
                    for price in range(1, 10))
        if bound < 48:
            price_lines.add(number)
    final_lines = matching_lines | price_lines
    require(len(general_lines) == 175 and len(matching_lines) == 745
            and general_lines <= matching_lines
            and len(price_lines) == 488 and len(price_lines & matching_lines) == 283
            and len(final_lines) == 950, "Independent complete incidence/price scan differs")

    common_proofs = {"research_round8/incidence/MISSING_DIRECTION_INCIDENCE.md",
                     "research_round7/dense_encoder/NINE_POINT_DIFFERENCE_ANALYTIC_PROOF.md"}
    prior_pins = {
        "research_round8/incidence/verify_incidence_profile_exclusions.py",
        first_certificate, first_output,
        "research_round8/incidence/verify_extended_incidence_profiles.py",
        profile_certificate, profile_output}
    stage_history = [
        {"cumulative_exclusions": 16, "additional_exclusions": 16, "remaining": 183460,
         "certificate_file": first_certificate, "survivor_file": first_output},
        {"cumulative_exclusions": 128, "additional_exclusions": 112, "remaining": 183348,
         "certificate_file": profile_certificate, "survivor_file": profile_output}]
    stages = [
        ("general", "GENERAL_INCIDENCE", "verify_general_incidence_profiles.py",
         general_lines, 175, 47, "PASS_GENERAL_INCIDENCE_PROFILE_REPLAY",
         "Every placement and fibre shape of these175 whole profiles, in both rings. No support-orbit SAT credit is added.",
         common_proofs | {"research_round8/incidence/GENERAL_WEIGHTED_LIGHT_PROFILE_CERTIFICATES.md"},
         {"every_original_profile_scored", "every_retained_line_preserved_byte_identically_and_in_order",
          "direct_minus175_and_prior128_minus47_regeneration_identical", "both_previous_stages_semantically_unchanged"}),
        ("matching", "MATCHING_INCIDENCE", "verify_matching_incidence_profiles.py",
         matching_lines, 745, 570, "PASS_MATCHING_INCIDENCE_PROFILE_REPLAY",
         "Every placement and actual fibre shape of these745 whole profiles, in both rings. No additional SAT-role credit.",
         common_proofs | {"research_round8/geometry/MATCHING_THRESHOLD_LEMMA.md"},
         {"every_original_profile_scanned", "all_prefix_threshold_brackets_checked_exactly",
          "every_retained_line_preserved_byte_identically_and_in_order",
          "direct_minus745_and_prior175_minus570_regeneration_identical", "all_prior_stage_semantic_artifacts_unchanged"}),
    ]
    # The final source/certificate scope and coverage keys are explicitly
    # bound below, just as in the two preceding cumulative stages.
    stages.append((
        "three_direction", "THREE_DIRECTION", "verify_three_direction_profiles.py",
        final_lines, 950, 205, "PASS_THREE_DIRECTION_PROFILE_REPLAY",
        "Every placement and actual fibre shape of these950 whole profiles, in both rings. Matching and three-direction price certificates are combined without duplicate credit; no SAT role is added.",
        common_proofs | {"research_round8/incidence/THREE_DIRECTION_PRICE_LEMMA.md"},
        {"every_original_profile_scanned", "every_retained_line_preserved_byte_identically_and_in_order",
         "complete_276_local_cube_subsets_verified", "all_exact_coset_knapsack_layers_verified",
         "all_selected_price_minima_and_ties_verified",
         "direct_minus950_and_prior745_minus205_regeneration_identical",
         "all_prior_stage_semantic_artifacts_unchanged"}))
    previous_set = set(cumulative_lines)
    for short, prefix, verifier_name, excluded_set, count, added, status, scope, proofs, truths in stages:
        folder = "research_round8/incidence/"
        profile_output = folder + "after_" + short + "_incidence_survivors.txt"
        if short == "three_direction":
            profile_output = folder + "after_three_direction_survivors.txt"
        profile_certificate = folder + prefix + "_PROFILE_EXCLUSIONS.json"
        profile_replay_path = folder + prefix + "_PROFILE_REPLAY.json"
        profile_verifier = folder + verifier_name
        profile_replay = read(profile_replay_path)
        require(previous_set < excluded_set and len(excluded_set-previous_set) == added,
                "A cumulative stage dropped or double-counted earlier exclusions")
        require(profile_replay["status"] == status
                and profile_replay["original_profiles"] == 183476
                and profile_replay["intermediate_profiles"] == 183476-len(previous_set)
                and profile_replay["previously_excluded_profiles"] == len(previous_set)
                and profile_replay["newly_excluded_profiles"] == added
                and profile_replay["cumulative_excluded_profiles"] == count
                and profile_replay["remaining_profiles"] == 183476-count,
                "Later profile stage has stale or inconsistent cumulative counts: " + short)
        for file_key, hash_key, path in (
                ("original_input_file", "original_input_sha256", profile_input),
                ("certificate_file", "certificate_sha256", profile_certificate),
                ("survivor_file", "survivor_sha256", profile_output)):
            require(profile_replay[file_key] == path and profile_replay[hash_key] == sha(ROOT / path),
                    "Later stage has a mismatched file binding: " + short + "/" + file_key)
        require(profile_replay["verifier_sha256"] == sha(ROOT / profile_verifier),
                "Later stage verifier changed after replay: " + short)
        stage_certificate = read(profile_certificate)
        require(profile_replay["scope"] == stage_certificate["scope"] == scope,
                "Later stage has a different mathematical scope: " + short)
        if short == "three_direction":
            table = stage_certificate["cube_tables"]
            table_hash = hashlib.sha256((json.dumps(table, indent=2) + "\n").encode("utf-8")).hexdigest()
            expected_tables = {str(k): value for k, value in edge_tables.items()}
            require(profile_replay["cube_tables_sha256"] == stage_certificate["cube_tables_sha256"] == table_hash
                    and profile_replay["local_cube_subsets_total"] == table["total_local_subsets"] == 276
                    and profile_replay["local_cube_subset_counts"] == {"1": 4, "2": 16, "3": 256}
                    and profile_replay["E_k_for_weights0_through32"]
                        == table["E_k_for_weights0_through32"] == expected_tables
                    and table["ambient_dimension"] == 5 and table["ambient_vertices"] == 32,
                    "Final cube-table receipt differs from the exact certificate or independent convolution")
        for field, paths in (("analytic_proof_pins", proofs), ("prior_stage_pins", prior_pins)):
            require(set(profile_replay[field]) == paths
                    and all(sha(ROOT / p) == h for p, h in profile_replay[field].items()),
                    "Later stage premises differ: " + short + "/" + field)
        coverage = profile_replay["coverage"]
        require(all(coverage[key] is True for key in truths)
                and coverage["energy_metadata_used_in_exclusion"] is False
                and coverage["excluded_original_source_lines"] == sorted(excluded_set)
                and coverage["previously_excluded_original_source_lines"] == sorted(previous_set)
                and coverage["newly_excluded_original_source_lines"] == sorted(excluded_set-previous_set),
                "Later stage lacks complete exact coverage: " + short)
        kept = [raw for number, raw in enumerate(original_lines, 1) if number not in excluded_set]
        require((ROOT / profile_output).read_bytes() == b"".join(kept),
                "Later survivor bytes differ from the complete independent scan: " + short)
        removed = [{"source_line": number, "maximum": parsed[number-1][1],
                    "weights": parsed[number-1][2]} for number in sorted(excluded_set)]
        removed_support = Counter(parsed[number-1][0] for number in excluded_set)
        removed_maximum = Counter(parsed[number-1][1] for number in excluded_set)
        require({int(s): row["remaining"] for s, row in profile_replay["by_support"].items()}
                == {s: before_support[s]-removed_support[s] for s in before_support}
                and {int(m): row["cumulative_excluded"] for m, row in profile_replay["by_maximum"].items()}
                == {m: removed_maximum[m] for m in range(12, 19)},
                "Later stage aggregate tables disagree with the independent scan")
        stage_history.append({"cumulative_exclusions": count, "additional_exclusions": added,
                              "remaining": 183476-count, "certificate_file": profile_certificate,
                              "survivor_file": profile_output})
        previous_set = excluded_set
        prior_pins = prior_pins | {profile_verifier, profile_certificate, profile_output}

    ledger = copy.deepcopy(old)
    ledger.update(title="Kakeya research frontier — Round8", date="2026-10-29",
                  previous_checkpoint="Kakeya_Research_Frontier_Round7.json")
    target = ledger["dimension5_strata"]["maximum11"]
    target.update(previous_round7_affine_support_classes=45,
                  round8_whole_affine_support_class_exclusions=new_classes,
                  remaining_affine_support_classes=42, remaining_orbits=remaining,
                  support13_remaining_marked_largest_fibre_roles=[], support13_closed=True,
                  pair_active_support_lower_bound=14)
    target["remaining_counts_by_support"]["13"] = 0
    require(sum(target["remaining_counts_by_support"].values()) == 42,
            "Per-support maximum-eleven counts do not sum to42")
    partial = ledger["support13_partial_coverage"]
    partial["certified_marked_cases_by_exact_maximum"]["11"] = len(covered)
    for mask in sorted(EXPECTED):
        partial["partial_maxima_by_mask"].setdefault(str(mask), []).append(11)
        partial["partial_maxima_by_mask"][str(mask)] = sorted(set(partial["partial_maxima_by_mask"][str(mask)]))
    partial["partial_marked_cases"] = len(partial["partial_maxima_by_mask"])
    partial["complete_unmarked_affine_classes_by_exact_maximum"]["11"] = direct_closed
    partial["round8_direct_new_exact_maximum11_cases"] = 4
    partial["closed_exact_maximum_cells_using_inherited_reductions"] = [11]
    inherited_slice = partial["separate_inherited_maximum11_slice"]
    inherited_slice.update(newly_closed_previously_open_affine_classes=[105, 109, 110, 111],
                           remaining_support13_affine_classes=[],
                           remaining_total_maximum11_affine_class_count=42,
                           remaining_support13_marked_roles=[],
                           support13_maximum11_closed_with_inherited_reduction=True,
                           additional_round8_closed_classes=new_classes)
    middle = ledger["dimension5_strata"]["maximum12_through18"]
    middle.update(previous_round7_weight_profiles=183476,
                  round8_whole_weight_profile_exclusions=950,
                  remaining_weight_profiles=182526, survivor_file=profile_output,
                  survivor_sha256=sha(ROOT / profile_output))
    middle["remaining_profiles_by_support"] = {"13": 84946, "14": 74039, "15": 19362, "16": 3793, "17": 386}
    ledger["round7_integer_profile_exclusions"] = ledger.pop("integer_profile_exclusions")
    ledger["round8_incidence_profile_exclusions"] = {
        "before": 183476, "excluded": 950, "remaining": 182526,
        "by_maximum": {"12": 129, "13": 68, "14": 191, "15": 108, "16": 250, "17": 94, "18": 110},
        "support_sizes": [13, 14, 15, 16, 17],
        "by_support": {"13": 394, "14": 334, "15": 152, "16": 60, "17": 10},
        "support13_before": 85340, "support13_remaining": 84946,
        "reason": "These complete nine-heavy profiles violate the matching incidence threshold or the three-independent-direction integer price bound.",
        "cumulative_stage_history": stage_history,
        "matching_threshold_exclusions": 745,
        "three_direction_price_exclusions": 488,
        "overlap_between_matching_and_price": 283,
        "price_exclusions_additional_to_matching": 205,
        "partial_geometry_extrapolation_used": False,
        "source_file": profile_input, "source_sha256": sha(ROOT / profile_input),
        "survivor_file": profile_output, "survivor_sha256": sha(ROOT / profile_output),
        "certificate_file": profile_certificate,
        "replay_file": profile_replay_path,
        "exact_removed_profiles": removed
    }
    ledger["round8_main_result"] = {
        "statement": "No Kakeya set of at most93 points in either ring's dimension5 can have exact maximum fibre11 and pair-active support13, conditional on the inherited reductions and the reviewed encoder.",
        "status": "CLOSED_COMMON_RING_COMPUTER_ASSISTED_BRANCH",
        "direct_new_marked_cases": 4, "new_whole_affine_classes": new_classes,
        "complete_direct_exact11_marked_coverage": {"closed": 39, "catalogue": 55},
        "global_support13_maximum11_closure_uses_inherited_reduction": True,
        "global_dimension5_minimum94_established": False,
        "middle_weight_profiles_removed_by_these_four_sat_cases": 0,
        "proof_search_modes_used": ["heavy_cover_tetrahedral"],
        "later_eleven_heavy_and_incidence_cuts_used_in_these_four_proofs": False,
        "case_search_seconds": {str(r["nonzero_support_mask"]): r["solve_seconds"] for r in new},
        "case_original_production_seconds": {str(r["nonzero_support_mask"]): r["seconds"] for r in new},
        "fresh_compact_proof_replay": replay_path,
        "compact_manifest_sha256": sha(compact_module.MANIFEST),
        "original_inventory_sha256": compact["source_manifest_sha256"]
    }
    ledger["round8_structural_results"] = [
        "S13 and maximum<=11 require at least10 weight>=4 fibres whose residues realize all31 nonzero differences; no total-weight or census premise.",
        "With total<=93, exactly10 heavy fibres are excluded by an elementary integer dual748<768 plus a complete14950-set support classification; no fibre-spectrum or sumset census is a premise.",
        "A separate85184-actual-fibre normalization replay establishes the sharper dual689<768 and independently matches the census-based DP663/685.",
        "For at least9 heavy residues, r*missing_heavy_directions<=number_of_weight2_fibres+2*number_of_weight3_fibres, where r=ceil(16/floor(maximum/2)).",
        "The new incidence bound applies toS13/maximum<=13 andS14/maximum<=11, requiring at least10 heavy fibres and at least29 heavy differences;11 heavy fibres force full difference coverage.",
        "A separately proved extension reachesS13/maximum<=15: at least10 heavy fibres, at least29 heavy differences, and full difference coverage if at least11 are heavy. It excludes128 whole profiles; the frozen next-frontier encoder still has its original exact12/13 scope.",
        "Sorting distinct heavy partner pair ceilings strengthens the missing-direction light-incidence requirement and excludes745 whole profiles across supports13..17.",
        "The three-direction price inequality 48<=lambda*(n2+2*n3)+sum_h max_k(E_k(w_h)-lambda*k) excludes488 profiles,205 beyond the matching screen; the exact small-cube tables require276 subsets. The combined950 exclusions leave1237 of2187 nine-heavy profiles and182526 profiles overall.",
        "Hyperplane crossing-pair budgets and Q211 effective pair-direction spaces are separately tested optional extensions; no accepted proof here depends on them."
    ]
    ledger["next_priorities"] = [
        "Run the new incidence cuts on the54 outstanding marked exact-maximum12/13 support13 cases.",
        "Apply the same missing-direction budget to the nine remaining maximum11 support14 affine classes, with complete largest-fibre role accounting.",
        "Use the optional Q211 paired-space and hyperplane constraints only in separately frozen formula variants with checked exact-CNF proofs.",
        "Promote the new distinct-partner and three-direction price inequalities to geometry-aware role programs; the remaining1237 nine-heavy profiles and all higher-heavy-count profiles remain open unless separately certified.",
        "Keep the middle-maxima whole-profile ledger separate from partial support-placement exclusions."
    ]
    ledger["latest_external_session_scope"] = "Historical session snapshots were reconciled with available artifacts; no newer complete dimension4 closure or unseen live sweep was credited. See Round8 SESSION_RECONCILIATION.txt."
    ledger["dependencies_and_trust_scope"].append("Round8 closes the exact11/support13 cell with four freshly checked strengthened CNFs; the Python encoder and whole geometric bridge are not proof-assistant formalizations.")
    require(ledger["dimension5_strata"]["maximum12_through18"]["remaining_weight_profiles"] == 182526,
            "Only the950 cumulative complete incidence/price exclusions may change middle-profile accounting")
    require(sum(middle["remaining_profiles_by_support"].values()) == 182526,
            "Final middle-profile support counts do not sum to the total")
    require(ledger["dimension4"]["status"] == "OPEN" and ledger["unrestricted_dimension5_theorem"] is False,
            "Unrelated open theorem was promoted")
    output = ROOT / "Kakeya_Research_Frontier_Round8.json"
    output.write_text(json.dumps(ledger, indent=2) + "\n")
    report = {"status": "PASS_EXACT_ROUND8_FRONTIER_ACCOUNTING", "new_roles": sorted(EXPECTED),
              "closed_affine_classes": new_classes, "remaining_maximum11_affine_classes": 42,
              "direct_exact11_marked_coverage": len(covered), "direct_catalogue_size": 55,
              "support13_maximum11_closed_using_inherited_reductions": True,
              "middle_profiles_removed_by_sat_geometry": 0,
              "middle_profiles_removed_by_incidence_and_price_theorems": 950,
              "initial_incidence_profile_exclusions": 16,
              "cumulative_profile_stage_counts": [16, 128, 175, 745, 950],
              "matching_profile_exclusions": 745,
              "three_direction_price_exclusions": 488,
              "matching_price_overlap": 283,
              "middle_profiles_remaining": 182526,
              "whole_profile_certificate_sha256": sha(ROOT / profile_certificate),
              "whole_profile_replay_sha256": sha(ROOT / profile_replay_path),
              "whole_profile_survivor_sha256": sha(ROOT / profile_output),
              "source_sha256": {p: sha(ROOT / p) for p in old_paths},
              "compact_manifest_sha256": sha(compact_module.MANIFEST),
              "compact_replay_sha256": sha(ROOT / replay_path), "ledger_sha256": sha(output),
              "source_code_sha256": sha(Path(__file__))}
    (HERE / "ROUND8_MERGED_REPLAY.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    try:
        main()
    except BaseException as error:
        if isinstance(error, SystemExit) and error.code in (None, 0):
            raise
        destination = HERE / "ROUND8_MERGED_REPLAY.json"
        try:
            report = json.loads(destination.read_text()) if destination.exists() else {}
            report.update(status="FAIL", error=repr(error))
            destination.write_text(json.dumps(report, indent=2) + "\n")
        except OSError:
            pass
        raise
