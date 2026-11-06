#!/usr/bin/env python3
"""Merge disjoint Round7 progress units without promoting partial coverage.

Weight profiles, affine support classes, marked cases, and refutations are
different units.  Only the whole-profile integer certificates change the
middle-weight profile file.  A maximum11 class is removed only when every
marked largest-fibre role has checked interval coverage.
"""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(relative):
    return json.loads((ROOT / relative).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    old = read("Kakeya_Research_Frontier_Round6.json")
    bindings = read("research_round7/COMPLETED_REPLAY_BINDINGS.json")
    require(bindings["status"] == "PASS_CURRENT_BYTES_BOUND_TO_COMPLETED_FULL_REPLAYS", "Missing current full-replay binding")
    for row in bindings["collections"]:
        require(sha(ROOT / row["receipt"]) == row["receipt_sha256"], "Bound proof replay receipt changed")

    exact = read("research_round7/exact_ring/EXACT_RING_CERTIFICATE_REPLAY.json")
    require(exact["theorems"]["global_dimension2_minimum10_both_rings_certified"]
            and exact["theorems"]["global_dimension3_minimum22_both_rings_certified"], "Small theorem missing")
    hand = read("research_round7/dimension3/DIMENSION3_HAND_REPLAY.json")
    require(hand["status"] == "PASS_ELEMENTARY_DIMENSION3_THEOREM_FINITE_CORROBORATION", "Elementary proof corroboration missing")
    n4 = read("research_round7/dimension4_compact/COMPACT_DIMENSION4_REPLAY.json")["checked_scope"]
    require(n4["complete_ring_cases"] == 14 and n4["remaining_ring_cases"] == 42
            and not n4["global_dimension4_minimum46_established"], "Unexpected dimension4 scope; review before merging")

    support = read("research_round7/compact_support13/COMPACT_SUPPORT13_REPLAY.json")
    coverage = support["certified_inventory_coverage"]
    require(coverage["closed_support13_exact_maximum_cells"] == []
            and not coverage["support13_closed_for_maximum2_through18"], "New whole support cell requires a separate profile merge")
    slice11 = coverage["separate_inherited_maximum11_slice"]
    closed11 = slice11["newly_closed_previously_open_affine_classes"]
    require(len(closed11) == len(set(closed11)) and set(closed11) <= set(old["dimension5_strata"]["maximum11"]["remaining_orbits"]),
            "Invalid or duplicated maximum11 class subtraction")

    dual = read("research_round7/charging/PROFILE_EXCLUSIONS_REPLAY.json")
    require(dual["status"] == "PASS_ROOT_SEPARATE_INTEGER_CERTIFICATE_REPLAY"
            and dual["profiles_before"] == old["dimension5_strata"]["maximum12_through18"]["remaining_weight_profiles"],
            "Wrong integer-certificate starting frontier")
    require(sha(ROOT / dual["survivors_file"]) == dual["survivors_sha256"]
            and sha(ROOT / dual["excluded_file"]) == dual["excluded_sha256"], "Profile payload changed")
    before_lines = (ROOT / old["dimension5_strata"]["maximum12_through18"]["survivor_file"]).read_text().splitlines()
    survivors = (ROOT / dual["survivors_file"]).read_text().splitlines()
    excluded = [json.loads(line) for line in (ROOT / dual["excluded_file"]).read_text().splitlines()]
    line_ids = {row["source_line"] for row in excluded}
    require(len(excluded) == len(line_ids) == dual["whole_profiles_excluded"], "Duplicate excluded profile")
    require(survivors == [line for i, line in enumerate(before_lines, 1) if i not in line_ids], "Incorrect profile subtraction")
    require(len(before_lines) == len(excluded) + len(survivors), "Profile count does not reconcile")
    by_support = Counter(int(line.split()[0]) for line in survivors)
    cells = Counter(tuple(map(int, line.split()[:2])) for line in survivors)

    strata = deepcopy(old["dimension5_strata"])
    m11 = strata["maximum11"]
    m11["previous_round6_affine_support_classes"] = m11["remaining_affine_support_classes"]
    m11["round7_whole_affine_support_class_exclusions"] = closed11
    m11["remaining_orbits"] = [i for i in m11["remaining_orbits"] if i not in set(closed11)]
    m11["remaining_affine_support_classes"] = len(m11["remaining_orbits"])
    m11["remaining_counts_by_support"]["13"] -= len(closed11)
    require(sum(m11["remaining_counts_by_support"].values()) == m11["remaining_affine_support_classes"], "Maximum11 support counts differ")
    m11["support13_remaining_marked_largest_fibre_roles"] = slice11["remaining_support13_marked_roles"]
    m11["support13_closed"] = slice11["support13_maximum11_closed_with_inherited_reduction"]
    middle = strata["maximum12_through18"]
    middle.update(previous_round6_weight_profiles=dual["profiles_before"],
                  round7_whole_weight_profile_exclusions=dual["whole_profiles_excluded"],
                  remaining_weight_profiles=len(survivors), remaining_nonempty_cells=len(cells),
                  remaining_profiles_by_support={str(s): count for s, count in sorted(by_support.items())},
                  survivor_file=dual["survivors_file"], survivor_sha256=dual["survivors_sha256"],
                  geometric_partial_cases_subtracted_as_whole_profiles=0,
                  new_profile_certificate_scope=dual["scope"])
    dependencies = [
        "The existing dimension5 reductions and complete support/census data are inherited from the preserved Round6 checkpoint.",
        "New profile exclusions use the geometric heavy/light lemma, complete fibre spectra, and elementary capacities for q<=3.",
        "Support13 exclusions use the reviewed necessary-condition encoder, exact CNF regeneration, checked interval coverage and pinned CakeML proof checking.",
        "The dimension3 elementary proof needs no spectrum census, SAT solver, or support-orbit enumeration.",
        "Lean formalizes the common affine tangent shear and abstract charging core; it does not formalize the whole theorem, Python encoders, or census."]
    frontier = {
        "title": "Kakeya research frontier — Round7", "date": "2026-10-28",
        "previous_checkpoint": "Kakeya_Research_Frontier_Round6.json",
        "rings": old["rings"], "general_target": old["general_target"],
        "unrestricted_general_theorem": False,
        "exact_small_dimensions": {
            "1": {"minimum_both_rings": 4, "proof": "A primitive line in R is the whole four-element ring."},
            "2": {"minimum_both_rings": 10, "elementary_proof": "research_round7/exact_ring/DIMENSION2_ELEMENTARY_PROOF.md",
                  "exact_ring_refutations": 4, "actual_upper_bound_witnesses": 2},
            "3": {"minimum_both_rings": 22, "elementary_proof": "research_round7/dimension3/DIMENSION3_ELEMENTARY_PROOF.md",
                  "elementary_proof_sha256": sha(HERE / "dimension3/DIMENSION3_ELEMENTARY_PROOF.md"),
                  "elementary_proof_uses_SAT_or_census": False,
                  "separate_complete_exact_ring_refutations": 10, "complete_marked_support_classes": 5,
                  "claimed_literature_novelty": False}},
        "dimension4": {"target": 46, "status": "OPEN", "checked_scope": n4,
                       "certified_all_marked_support_sizes_both_rings": [6, 7, 8],
                       "additional_closed_size9_classes_both_rings": 2,
                       "full_proof_replay": "research_round7/dimension4_compact/COMPACT_DIMENSION4_REPLAY.json"},
        "dimension5_target": 94, "unrestricted_dimension5_theorem": False,
        "minimum_pair_active_support": old["minimum_pair_active_support"],
        "minimum_support_dependencies": old["corollary_dependencies"],
        "dimension5_strata": strata, "support13_partial_coverage": coverage,
        "integer_profile_exclusions": {"before": len(before_lines), "excluded": len(excluded), "remaining": len(survivors),
                                       "by_support": dual["by_support"], "minimum_strict_margin_twice": dual["minimum_strict_margin_twice"],
                                       "sumset_census_mathematical_dependency": False,
                                       "fibre_spectrum_census_dependency": True},
        "new_structural_lemmas": [
            "For support13 and maximum<=18, at least eight fibres have weight>=4, without total93 or a census premise.",
            "In F2^5, an eight-point set has at most25 nonzero differences and a nine-point set at most28; both now have symbolic proofs.",
            "Two nonplanar four-point subsets of F2^4 have sumset size at most14.",
            "The heavy/light charging inequality produces explicit integer certificates for complete weight profiles."],
        "formal_verification": {"new_Lean_modules": ["ShearBridge.lean", "ChargingDual.lean"],
                                "new_statements_or_equivalences": 14, "whole_Kakeya_theorem_formalized": False},
        "dependencies_and_trust_scope": dependencies,
        "latest_external_session_scope": "The supplied Claude Round4 archive and earlier packaged work are preserved in the inherited checkpoint. No claim is made to access unseen live sessions or ongoing remote jobs.",
        "accounting_rules": ["Timeouts contribute no exclusions.", "A marked case fixes a largest-fibre residue; one marked case is not a whole affine support class.",
                             "Partial support coverage is not subtracted from the whole weight-profile count.", "Separate model agents are not independent human referees."],
        "next_priorities": [
            "Close the four remaining support13 maximum11 marked roles, especially the two single-role gaps in classes109 and111, using the heavy-cardinality cut and edge capacities on all edges.",
            "Use actual heavy-residue difference sets and direction-specific charges to strengthen the current universal integer dual.",
            "Extend the tetrahedron capacity14 cut beyond unique-edge directions while retaining exact new-CNF soundness and proof binding.",
            "Use the ring-specific exact-point model where necessary; retain the common affine tangent shear and exact carry.",
            "Formalize the elementary dimension3 proof and the geometric incidence bridge for the charging inequality."]}
    path = ROOT / "Kakeya_Research_Frontier_Round7.json"
    path.write_text(json.dumps(frontier, indent=2, ensure_ascii=False) + "\n")
    receipt = {"status": "PASS_EXACT_ROUND7_FRONTIER_ACCOUNTING", "frontier_sha256": sha(path),
               "whole_weight_profiles_excluded": len(excluded), "middle_weight_profiles_remaining": len(survivors),
               "maximum11_affine_classes_remaining": m11["remaining_affine_support_classes"],
               "support13_joint_marked_cases_closed": coverage["complete_marked_cases"],
               "dimension4_remains_open": True, "dimension5_remains_open": True,
               "source_sha256": sha(Path(__file__))}
    (HERE / "ROUND7_MERGED_REPLAY.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    destination = HERE / "ROUND7_MERGED_REPLAY.json"
    destination.write_text(json.dumps({"status": "RUNNING"}) + "\n")
    try:
        main()
    except BaseException as error:
        destination.write_text(json.dumps({"status": "FAIL", "error": repr(error)}, indent=2) + "\n")
        raise
