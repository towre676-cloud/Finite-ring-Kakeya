"""Exact Hall obstructions for the complete normalized support-role census."""
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def parse_profile(line):
    v = list(map(int, line.split()))
    parent, z, ng = v[:3]
    assert len(v) == 3 + 3 * ng
    fibres = []
    for k in range(3, len(v), 3):
        flag, weight, multiplicity = v[k:k + 3]
        assert flag in (0, 1) and 2 <= weight <= 14 and multiplicity > 0
        fibres.extend([(flag, weight)] * multiplicity)
    assert sum(w for f, w in fibres) == 74
    assert z == 31 - sum(f for f, w in fibres)
    return parent, fibres


def attributes(fibres):
    out = [0, 0, 0, 0]
    for f, w in fibres:
        out[int(w >= 8) + 2 * int(f == 1 and w >= 4)] += 1
    return out


def obstruction(role, attrs):
    r, a = role, attrs
    inequalities = [
        (r[3], a[3], "both"),
        (r[1] + r[3], a[1] + a[3], "large"),
        (r[2] + r[3], a[2] + a[3], "sole_hub"),
        (sum(r[1:]), sum(a[1:]), "nonfree"),
    ]
    return next(([need, have, name] for need, have, name in inequalities if need > have), None)


def main():
    census = json.loads((BASE / "UNIQUE_EDGE_ROLE_NORMALIZED_CENSUS.json").read_text())
    summary = {"status": "CANDIDATES_REGENERATED_FROM_NORMALIZED_CENSUS", "supports": {}}
    for s in (11, 12):
        src = BASE / f"s{s}_after_own_periodic.txt"
        lines = src.read_text().splitlines()
        roles = [row["counts"] for row in census["supports"][str(s)]["patterns"]]
        assert roles == sorted(roles)
        candidates, survivors = [], []
        for line in lines:
            parent, fibres = parse_profile(line)
            assert len(fibres) == s - 1
            attrs = attributes(fibres)
            witnesses = [obstruction(r, attrs) for r in roles]
            if all(w is not None for w in witnesses):
                candidates.append({"parent_id": parent, "support": s, "profile_line": line,
                                   "attributes": attrs, "hall_witnesses": witnesses})
            else:
                survivors.append(line)
        dst = BASE / f"S{s}_UNIQUE_EDGE_ROLE_CANDIDATES.jsonl"
        dst.write_text("".join(json.dumps(x, separators=(",", ":")) + "\n" for x in candidates))
        (BASE / f"s{s}_after_unique_edge_roles.txt").write_text("".join(x + "\n" for x in survivors))
        summary["supports"][str(s)] = {"input_profiles": len(lines), "exclusions": len(candidates),
                                        "remaining_profiles": len(survivors),
                                        "input_sha256": hashlib.sha256(src.read_bytes()).hexdigest()}
    (BASE / "UNIQUE_EDGE_ROLE_PRODUCER_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
