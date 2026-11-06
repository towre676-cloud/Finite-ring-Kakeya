#!/usr/bin/env python3
"""Prepare the exact remaining maximum12/13 S13 roles; claim no exclusion."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "research_round8"


def main():
    catalogue_path = ROOT / "research_round6/next_frontier/SUPPORT13_CASE_QUEUE.json"
    prior_path = ROOT / "research_round7/support13/SUPPORT13_CERTIFICATE_MANIFEST.json"
    mapping_path = ROOT / "research_round7/geometry/SUPPORT13_MARKING_MAP.json"
    catalogue, prior, mapping = [json.loads(p.read_text()) for p in (catalogue_path, prior_path, mapping_path)]
    affine = {r["marked_nonzero_mask"]: r["unmarked_affine_orbit_id"] for r in mapping["marked_cases"]}
    cases = []
    counts = {}
    for maximum in (12, 13):
        excluded = {r["nonzero_support_mask"] for r in prior["cases"]
                    if r["maximum_interval"][0] <= maximum <= r["maximum_interval"][1]}
        assert len(excluded) == 28
        remaining = sorted((r for r in catalogue["cases"] if r["nonzero_support_mask"] not in excluded),
                           key=lambda r: r["nonzero_support_mask"])
        assert len(remaining) == 27
        counts[str(maximum)] = len(remaining)
        for r in remaining:
            mask = r["nonzero_support_mask"]
            cases.append({"case_id": f"s13_T{mask}_m{maximum}_incidence_pending",
                          "nonzero_support_mask": mask, "support": r["support"],
                          "unmarked_affine_class": affine[mask], "distinguished_hub": 0,
                          "maximum_interval": [maximum, maximum], "total_upper_bound": 93,
                          "ring_scope": "common_necessary_relaxation_both_rings",
                          "status": "PENDING_NEW_EXACT_CNF_AND_CHECKED_REFUTATION",
                          "new_available_cuts": ["at_least_ten_heavy", "missing_direction_light_incidence_budget",
                                                 "eleven_heavy_implies_full_difference_cover", "all_edge_tetrahedron14"],
                          "proof_search_performed_in_this_queue": False, "exclusion_credited": False})
    assert len(cases) == 54
    result = {"status": "COMPLETE_PENDING_MAX12_13_SUPPORT13_ROLE_QUEUE",
              "cases": cases, "counts_by_exact_maximum": counts, "total_pending_cases": 54,
              "proof_search_performed": False, "new_exclusions_credited": 0,
              "separate_maximum11_support14_remaining_affine_classes": [126, 130, 131, 132, 133, 134, 139, 141, 142],
              "support14_class_count_is_not_a_marked_case_count": True,
              "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in (catalogue_path, prior_path, mapping_path, Path(__file__))}}
    (HERE / "NEXT_ATTACK_QUEUE.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "counts_by_exact_maximum", "total_pending_cases", "new_exclusions_credited")}, indent=2))


if __name__ == "__main__":
    main()
