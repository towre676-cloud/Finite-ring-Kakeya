"""Bind the four disjoint M19 stages and freeze the current profile frontier.

This performs exact ID and hash bookkeeping; the four mathematical certificate
verifiers are separate and their receipts are bound in the manifest.
"""
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT / "research_round2/geometric"

STAGES = (
    ("common_affine_rank_modes", "COMMON_SHAPE_VERIFICATION_RECEIPT.json",
     "COMMON_SHAPE", "after_common_shapes", "COMMON_SHAPE_RESOURCE_PROOF.md",
     "verify_common_shape_certificates.py", "ROOT_VERIFIED_M19_COMMON_SHAPES.json"),
    ("analytic_deleted_direction", "DELETED_DIRECTION_PROFILE_VERIFICATION.json",
     "TWO_HEAVY_OWN", "after_two_heavy_own", "PROFILE63342_DELETED_DIRECTION_PROOF.md",
     "verify_deleted_direction_profile.py", "ROOT_VERIFIED_M19_DELETED_AND_PERIODIC.json"),
    ("common_own_periodic_modes", "OWN_PERIODIC_VERIFICATION_RECEIPT.json",
     "OWN_PERIODIC", "after_own_periodic", "OWN_PERIODIC_RESOURCE_PROOF.md",
     "verify_own_periodic_certificates.py", "ROOT_VERIFIED_M19_DELETED_AND_PERIODIC.json"),
    ("actual_unique_edge_support_roles", "UNIQUE_EDGE_ROLE_VERIFICATION_RECEIPT.json",
     "UNIQUE_EDGE_ROLE", "after_unique_edge_roles", "UNIQUE_EDGE_ROLE_PROOF.md",
     "verify_unique_edge_roles.py", "ROOT_VERIFIED_M19_UNIQUE_EDGE_ROLES.json"),
)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def record(path):
    return {"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size,
            "sha256": digest(path)}


def profiles(path, support):
    out = {}
    for line in path.read_text().splitlines():
        v = list(map(int, line.split()))
        ident, z, groups = v[:3]
        assert ident not in out and len(v) == 3 + 3 * groups
        fibres = [(f, w) for f, w, count in zip(v[3::3], v[4::3], v[5::3]) for _ in range(count)]
        assert len(fibres) == support - 1
        assert sum(w for f, w in fibres) == 74
        assert all(f in (0, 1) and 2 <= w <= 19 for f, w in fibres)
        assert z == 31 - sum(f for f, w in fibres)
        out[ident] = line
    return out


def main():
    prior_manifest = OLD / "M19_ROUND2_FINAL_MANIFEST.json"
    old = json.loads(prior_manifest.read_text())
    assert old["status"] == "ROOT_VERIFIED"
    initial, current, input_path, removed_all = {}, {}, {}, {}
    for s in (11, 12):
        path = HERE / f"s{s}_initial_profiles.txt"
        assert path.read_bytes() == (OLD / f"s{s}_final_round2_survivors.txt").read_bytes()
        initial[s] = profiles(path, s)
        current[s] = initial[s].copy()
        input_path[s] = path
        removed_all[s] = set()
    entries = []
    cut_index = []
    root_complete = True
    for name, receipt_name, tag, suffix, proof_name, verifier_name, root_name in STAGES:
        receipt_path = HERE / receipt_name
        receipt = json.loads(receipt_path.read_text())
        assert receipt["status"].startswith("PASS")
        entry = {"name": name, "proof": record(HERE / proof_name),
                 "verifier": record(HERE / verifier_name), "local_replay": record(receipt_path),
                 "supports": {}}
        for s in (11, 12):
            summary = receipt["supports"][str(s)]
            assert summary["input_profiles"] == len(current[s])
            assert summary["input_sha256"] == digest(input_path[s])
            cuts_path = HERE / f"S{s}_{tag}_CANDIDATES.jsonl"
            cuts = [json.loads(line) for line in cuts_path.read_text().splitlines()]
            ids = [x["parent_id"] for x in cuts]
            cut_ids = set(ids)
            assert len(ids) == len(cut_ids)
            assert cut_ids <= set(current[s])
            assert not (cut_ids & removed_all[s])
            number = summary.get("whole_profile_exclusions", summary.get("new_exclusions"))
            assert len(ids) == number
            expected_hash = summary.get("candidate_sha256", summary.get("candidates_sha256"))
            assert digest(cuts_path) == expected_hash
            for ident in ids:
                cut_index.append({"support": s, "parent_id": ident, "stage": name})
            next_path = HERE / f"s{s}_{suffix}.txt"
            remaining = profiles(next_path, s)
            expected = {i: line for i, line in current[s].items() if i not in cut_ids}
            assert remaining == expected
            assert next_path.read_text() == "".join(line + "\n" for line in expected.values())
            assert len(remaining) == summary["remaining_profiles"]
            assert digest(next_path) == summary["survivors_sha256"]
            entry["supports"][str(s)] = {"input_profiles": len(current[s]),
                                         "new_whole_profile_exclusions": number,
                                         "remaining_profiles": len(remaining),
                                         "input": record(input_path[s]),
                                         "certificates": record(cuts_path),
                                         "survivors": record(next_path)}
            current[s], input_path[s] = remaining, next_path
            removed_all[s] |= cut_ids
        entry["total_new_exclusions"] = sum(x["new_whole_profile_exclusions"] for x in entry["supports"].values())
        entry["total_remaining_profiles"] = sum(x["remaining_profiles"] for x in entry["supports"].values())
        root_path = ROOT / "research_round3/root" / root_name
        if root_path.exists():
            review = json.loads(root_path.read_text())
            assert review["status"].startswith("PASS")
            entry["root_review"] = {**record(root_path), "status": review["status"]}
        else:
            root_complete = False
            entry["root_review"] = {"status": "AWAITING_INDEPENDENT_ROOT_REVIEW"}
        entries.append(entry)
    cut_index.sort(key=lambda x: (x["support"], x["parent_id"]))
    index_path = HERE / "M19_ROUND3_DISJOINT_EXCLUSIONS.jsonl"
    index_path.write_text("".join(json.dumps(x, separators=(",", ":")) + "\n" for x in cut_index))
    supports = {}
    for s in (11, 12):
        assert set(initial[s]) == (set(current[s]) | removed_all[s])
        assert not (set(current[s]) & removed_all[s])
        final_path = HERE / f"s{s}_final_round3_survivors.txt"
        final_path.write_bytes(input_path[s].read_bytes())
        supports[str(s)] = {"initial_profiles": len(initial[s]),
                            "new_whole_profile_exclusions": len(removed_all[s]),
                            "remaining_profiles": len(current[s]),
                            "final_survivors": record(final_path)}
    data_files = ["POSITIVE_LOW_RANK_BLOCK_CENSUS.json", "COMMON_SHAPE_INTEGER_DUALS.jsonl",
                  "OWN_PERIODIC_BLOCK_CENSUS.json", "OWN_PERIODIC_INTEGER_DUALS.jsonl",
                  "UNIQUE_EDGE_ROLE_NORMALIZED_CENSUS.json"]
    dependencies = [OLD / "PAIR_SPECTRUM_CENSUS.json", OLD / "PAIRED_BLOCK_MAXIMUM_CENSUS.json",
                    ROOT / "research_round3/root/SHARED_PERIOD_AND_ROOTED_RANK_THEOREMS.txt"]
    source_files = ["build_positive_rank_block_census.py", "common_shape_screen.cpp",
                    "build_common_shape_dual_keys.py", "build_periodic_block_census.py",
                    "own_periodic_screen.cpp", "build_periodic_dual_keys.py",
                    "build_unique_edge_role_census.cpp", "build_unique_edge_role_certificates.py",
                    "build_m19_round3_manifest.py"]
    manifest = {
        "title": "M19 common geometry and actual support roles: round3 frozen checkpoint",
        "status": "ROOT_VERIFIED" if root_complete else "EXACT_LOCAL_REPLAY_COMPLETE",
        "scope": "Tracked size93, exact-maximum19 weight/own-direction profiles, support11 or12; every exclusion is uniform over residue placement and tangent fibre shape, for both project rings.",
        "unrestricted_dimension5_closed": False, "maximum19_closed": False,
        "prior_checkpoint": record(prior_manifest), "stages": entries, "supports": supports,
        "total_initial_profiles": sum(len(x) for x in initial.values()),
        "total_new_whole_profile_exclusions": sum(len(x) for x in removed_all.values()),
        "total_remaining_selected_profiles": sum(len(x) for x in current.values()),
        "disjoint_exclusion_index": record(index_path),
        "exact_certificate_data": [record(HERE / f) for f in data_files],
        "inherited_proof_dependencies": [record(p) for p in dependencies],
        "reproduction_sources": [record(HERE / f) for f in source_files],
        "next_frontier": record(HERE / "M19_ROUND3_FRONTIER.md"),
        "not_counted_as_proof_dependencies": ["UNIQUE_EDGE_ROLE_CANDIDATE_CENSUS.json", "pilot outputs", "floating-point optimizer output"]
    }
    assert manifest["total_initial_profiles"] == 30471
    assert manifest["total_new_whole_profile_exclusions"] == 26673
    assert manifest["total_remaining_selected_profiles"] == 3798
    target = HERE / "M19_ROUND3_FINAL_MANIFEST.json"
    target.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"status": manifest["status"], "new_exclusions": 26673,
                      "remaining": 3798, "supports": supports, "manifest_sha256": digest(target)}))


if __name__ == "__main__":
    main()
