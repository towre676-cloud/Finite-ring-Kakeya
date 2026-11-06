#!/usr/bin/env python3
"""Complete marked-support inventory in F2^4 by elementary transvections."""
from pathlib import Path
from collections import Counter, deque
import hashlib
import json
import time

HERE = Path(__file__).resolve().parent


def apply(x, columns):
    result = 0
    for i, c in enumerate(columns):
        if x >> i & 1:
            result ^= c
    return result


def compose(left, right):
    return tuple(apply(x, left) for x in right)


def generators():
    return [tuple((1 << k) ^ ((1 << i) if k == j else 0) for k in range(4))
            for i in range(4) for j in range(4) if i != j]


def full_group(gens):
    identity = (1, 2, 4, 8)
    seen, queue = {identity}, deque([identity])
    while queue:
        columns = queue.popleft()
        for g in gens:
            new = compose(g, columns)
            if new not in seen:
                seen.add(new)
                queue.append(new)
    assert len(seen) == 15 * 14 * 12 * 8 == 20160
    assert all({apply(x, cols) for x in range(16)} == set(range(16)) for cols in seen)
    return sorted(seen)


def mask_maps(gens):
    result = []
    for columns in gens:
        images = [1 << (apply(x, columns) - 1) for x in range(1, 16)]
        table = [0] * (1 << 15)
        for mask in range(1, 1 << 15):
            low = mask & -mask
            table[mask] = table[mask ^ low] | images[low.bit_length() - 1]
        result.append(table)
    return result


def support(mask):
    return [0] + [x for x in range(1, 16) if mask >> (x - 1) & 1]


def covers(S):
    return {a ^ b for a in S for b in S} == set(range(16))


def fixed_subset_coefficients(group):
    totals = [0] * 16
    for columns in group:
        unseen = set(range(1, 16))
        lengths = []
        while unseen:
            x = min(unseen)
            length = 0
            while x in unseen:
                unseen.remove(x)
                length += 1
                x = apply(x, columns)
            lengths.append(length)
        coefficients = [1] + [0] * 15
        for length in lengths:
            for j in range(15, length - 1, -1):
                coefficients[j] += coefficients[j - length]
        totals = [a + b for a, b in zip(totals, coefficients)]
    assert all(value % len(group) == 0 for value in totals)
    return [value // len(group) for value in totals]


def build():
    gens = generators()
    assert len(gens) == 12 and all(compose(g, g) == (1, 2, 4, 8) for g in gens)
    group = full_group(gens)
    maps = mask_maps(gens)
    representative = [-1] * (1 << 15)
    transports = [None] * (1 << 15)
    orbits = []
    for root in range(1 << 15):
        if representative[root] >= 0:
            continue
        representative[root] = root
        transports[root] = (1, 2, 4, 8)
        queue = deque([root])
        members = []
        while queue:
            mask = queue.popleft()
            members.append(mask)
            for g, table in zip(gens, maps):
                other = table[mask]
                if representative[other] < 0:
                    representative[other] = root
                    # If g sends parent to child, g also sends child to
                    # parent. Compose the parent's transport after g.
                    transports[other] = compose(transports[mask], g)
                    queue.append(other)
        S = support(root)
        entry = {"full_mask": (root << 1) | 1, "nonzero_compact_mask": root,
                 "support": S, "support_size": len(S), "orbit_size": len(members),
                 "stabilizer_order": len(group) // len(members), "difference_covering": covers(S)}
        assert len(group) % len(members) == 0
        for mask in members:
            actual = support(mask)
            image = sorted(apply(x, transports[mask]) for x in actual)
            assert image == S
            assert covers(actual) == entry["difference_covering"]
        orbits.append(entry)
    assert all(x >= 0 for x in representative)
    all_counts = Counter(row["support_size"] for row in orbits)
    burnside = fixed_subset_coefficients(group)
    assert all(all_counts.get(k + 1, 0) == burnside[k] for k in range(16))
    covering = [row for row in orbits if row["difference_covering"]]
    covering_counts = Counter(row["support_size"] for row in covering)
    rows = [{"source_full_mask": (mask << 1) | 1,
             "target_full_mask": (representative[mask] << 1) | 1,
             "linear_columns": list(transports[mask])} for mask in range(1 << 15)]
    summary = {"status": "PASS_COMPLETE_DIMENSION4_MARKED_SUPPORT_CATALOGUE",
               "dimension": 4, "all_marked_subsets": 1 << 15,
               "group_order": len(group), "generators": [list(g) for g in gens],
               "group_sorted_columns_sha256": hashlib.sha256(bytes(x for cols in group for x in cols)).hexdigest(),
               "all_marked_orbit_count": len(orbits), "covering_marked_orbit_count": len(covering),
               "covering_marked_subsets": sum(row["orbit_size"] for row in covering),
               "all_orbits_by_support_size": {str(k): all_counts[k] for k in sorted(all_counts)},
               "covering_orbits_by_support_size": {str(k): covering_counts[k] for k in sorted(covering_counts)},
               "burnside_all_orbits_by_support_size": {str(k + 1): count for k, count in enumerate(burnside)},
               "explicit_transports_checked": len(rows),
               "all_orbits": orbits, "covering_cases": covering,
               "scope": "Every binary support containing the distinguished largest residue zero, modulo all GL(4,2) maps. No fibre-shape restriction.",
               "small_support_reduction": "At most five active residues supply at most ten edges, fewer than fifteen nonzero directions.",
               "new_kakeya_exclusions": 0}
    return summary, rows


def main():
    started = time.monotonic()
    summary, transports = build()
    HERE.mkdir(parents=True, exist_ok=True)
    transport_path = HERE / "DIMENSION4_ALL_MARKED_TRANSPORTS.json"
    transport_path.write_text(json.dumps(transports, separators=(",", ":")) + "\n")
    summary["transport_file_sha256"] = hashlib.sha256(transport_path.read_bytes()).hexdigest()
    summary["source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    summary["seconds"] = round(time.monotonic() - started, 6)
    (HERE / "DIMENSION4_SUPPORT_CATALOGUE.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in ["status", "group_order", "all_marked_orbit_count",
          "covering_marked_orbit_count", "covering_marked_subsets", "covering_orbits_by_support_size", "seconds"]}, indent=2))


if __name__ == "__main__":
    main()
