"""Independent exact replay of support-role completeness and Hall certificates.

The C++ producer counts unordered differences. This verifier instead forms
translated support masks and uses intersection cardinalities. It does not
import the producer, the 382 affine classes, or the 44/96 marked-case lists.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import time

BASE = Path(__file__).resolve().parent
FIXED = (0, 1, 2, 4, 8, 16)
EXTRA = tuple(x for x in range(32) if x not in FIXED)
FIXED_MASK = sum(1 << x for x in FIXED)
SWAPS = ((1, 0x55555555), (2, 0x33333333), (4, 0x0F0F0F0F),
         (8, 0x00FF00FF), (16, 0x0000FFFF))


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def translated_mask(mask, d):
    for shift, low in SWAPS:
        if d & shift:
            mask = ((mask & low) << shift) | ((mask >> shift) & low)
    return mask


def derive_role(mask):
    pairs = [0] * 32
    unique_outside_vertices = 0
    for d in range(1, 32):
        inter = mask & translated_mask(mask, d)
        count = inter.bit_count()
        assert count % 2 == 0
        if not count:
            return None
        pairs[d] = count // 2
        if count == 2 and not ((mask >> d) & 1):
            unique_outside_vertices |= inter
    role = [0, 0, 0, 0]
    for a in range(1, 32):
        if (mask >> a) & 1:
            role[int(bool((unique_outside_vertices >> a) & 1)) + 2 * int(pairs[a] == 1)] += 1
    return tuple(role)


def replay_census(saved):
    assert saved["schema"] == "unique-edge-role-census-v1"
    assert saved["normalization_base"] == list(FIXED)
    counts = {}
    for s in (11, 12):
        found = Counter()
        first_masks = {}
        visited = 0
        for extra in combinations(EXTRA, s - 6):
            visited += 1
            mask = FIXED_MASK | sum(1 << x for x in extra)
            role = derive_role(mask)
            if role is not None:
                found[role] += 1
                first_masks.setdefault(role, mask)
        row = saved["supports"][str(s)]
        assert visited == comb(26, s - 6) == row["normalized_sets_visited"]
        assert sum(found.values()) == row["covering_normalized_sets"]
        listed = row["patterns"]
        assert [tuple(x["counts"]) for x in listed] == sorted(found)
        for x in listed:
            r = tuple(x["counts"])
            assert x["normalized_multiplicity"] == found[r]
            assert x["witness_mask"] == first_masks[r]
            assert x["witness_mask"].bit_count() == s
            assert derive_role(x["witness_mask"]) == r
        counts[str(s)] = {"normalized_sets_visited": visited,
                          "covering_normalized_sets": sum(found.values()),
                          "role_patterns": len(found)}
    return counts


def read_profile(line, s):
    values = [int(x) for x in line.split()]
    assert len(values) == 3 + 3 * values[2]
    fibres = []
    for i in range(values[2]):
        flag, weight, multiplicity = values[3 + 3 * i:6 + 3 * i]
        assert flag in (0, 1) and 2 <= weight <= 14 and multiplicity >= 1
        fibres += [(flag, weight)] * multiplicity
    assert len(fibres) == s - 1
    assert sum(w for f, w in fibres) + 19 == 93
    assert 31 - sum(f for f, w in fibres) == values[1]
    attrs = [sum((int(w >= 8) + 2 * int(f and w >= 4)) == t for f, w in fibres) for t in range(4)]
    return values[0], attrs


def inequalities(role, attrs):
    return {
        "both": (role[3], attrs[3]),
        "large": (role[1] + role[3], attrs[1] + attrs[3]),
        "sole_hub": (role[2] + role[3], attrs[2] + attrs[3]),
        "nonfree": (sum(role) - role[0], sum(attrs) - attrs[0]),
    }


def replay_profiles(s, census, prior):
    source = BASE / f"s{s}_after_own_periodic.txt"
    lines = source.read_text().splitlines()
    assert len(lines) == prior["remaining_profiles"]
    assert digest(source) == prior["survivors_sha256"]
    by_id, attrs_by_id = {}, {}
    for line in lines:
        ident, attrs = read_profile(line, s)
        assert ident not in by_id
        by_id[ident], attrs_by_id[ident] = line, attrs
    roles = [r["counts"] for r in census["supports"][str(s)]["patterns"]]
    candidates = BASE / f"S{s}_UNIQUE_EDGE_ROLE_CANDIDATES.jsonl"
    verified = []
    removed = set()
    witness_checks = 0
    for encoded in candidates.read_text().splitlines():
        row = json.loads(encoded)
        ident = row["parent_id"]
        assert ident not in removed and ident in by_id
        assert row["support"] == s and row["profile_line"] == by_id[ident]
        attrs = attrs_by_id[ident]
        assert row["attributes"] == attrs
        assert len(row["hall_witnesses"]) == len(roles)
        for role, witness in zip(roles, row["hall_witnesses"]):
            need, have, name = witness
            assert (need, have) == inequalities(role, attrs)[name]
            assert need > have
            witness_checks += 1
        removed.add(ident)
        verified.append({"parent_id": ident, "support": s,
                         "candidate_line_sha256": sha256(encoded.encode()).hexdigest(),
                         "profile_line_sha256": sha256(by_id[ident].encode()).hexdigest(),
                         "covering_support_role_patterns": len(roles)})
    # Check that this is exactly the screen's complement, not merely a subset.
    for ident, attrs in attrs_by_id.items():
        impossible = all(any(need > have for need, have in inequalities(r, attrs).values()) for r in roles)
        assert impossible == (ident in removed)
    survivors = BASE / f"s{s}_after_unique_edge_roles.txt"
    expected = "".join(line + "\n" for line in lines if int(line.split()[0]) not in removed)
    assert survivors.read_text() == expected
    out = BASE / f"S{s}_UNIQUE_EDGE_ROLE_VERIFIED_PROFILES.jsonl"
    out.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in verified))
    return {"input_profiles": len(lines), "whole_profile_exclusions": len(removed),
            "remaining_profiles": len(lines) - len(removed), "hall_witnesses_checked": witness_checks,
            "input_sha256": digest(source), "candidates_sha256": digest(candidates),
            "verified_profiles_sha256": digest(out), "survivors_sha256": digest(survivors),
            "simple_two_unqualified_fibre_exclusions": sum(attrs_by_id[i][0] >= 2 for i in removed)}


def main():
    started = time.time()
    census_file = BASE / "UNIQUE_EDGE_ROLE_NORMALIZED_CENSUS.json"
    census = json.loads(census_file.read_text())
    census_counts = replay_census(census)
    prior = json.loads((BASE / "OWN_PERIODIC_VERIFICATION_RECEIPT.json").read_text())
    rows = {str(s): replay_profiles(s, census, prior["supports"][str(s)]) for s in (11, 12)}
    receipt = {"status": "PASS_EXACT_NORMALIZED_SUPPORT_CENSUS_AND_HALL_CERTIFICATES",
               "census_sha256": digest(census_file), "census": census_counts,
               "supports": rows,
               "total_whole_profile_exclusions": sum(x["whole_profile_exclusions"] for x in rows.values()),
               "total_remaining_profiles": sum(x["remaining_profiles"] for x in rows.values()),
               "total_hall_witnesses_checked": sum(x["hall_witnesses_checked"] for x in rows.values()),
               "seconds": time.time() - started}
    (BASE / "UNIQUE_EDGE_ROLE_VERIFICATION_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
