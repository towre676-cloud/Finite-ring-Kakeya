#!/usr/bin/env python3
"""Exact integer audit of the short dual excluding the ten-heavy pattern.

This implementation reads the raw census independently of the SAT encoder.
It also recomputes the bounded integer optimum with separate dynamic code.
The support-classification and rank lemmas are separate mathematical inputs.
"""
import csv
import hashlib
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "research_round6/imported_claude_round4/data/spec32.csv"
PIN = "a61140936f55aa278de40d1b66e537138048322d152141ccc436d42c0f8fefab"
PRICE = (0, 1, 4, 9, 16, 17)


def elementary_capacity(p, q):
    p, q = max(p, q), min(p, q)
    if q == 0:
        return 0
    if q == 1:
        return p
    if q == 2:
        return min(2 * p, 16)
    if q == 3:
        return min(3 * p, p + 8, 16)
    return 16


def resource(histogram, slots):
    entries = [PRICE[p] for p in range(6) for _ in range(histogram[p])]
    return sum(sorted(entries, reverse=True)[:slots])


def dynamic_maximum(rows, hub_role):
    options = {
        "U": [(w, 0, resource(h, 9), line) for line, w, h, r in rows if r == 5],
        "W": [(w, int(r == 3), resource(h, 3), line)
              for line, w, h, r in rows if r >= 3],
    }
    roles = ["U"] * 3 + ["W"] * 7
    hub_index = roles.index(hub_role) if hub_role is not None else -1
    states = {(0, 0): (0, [])}
    for index, role in enumerate(roles):
        following = {}
        for (mass, small_rank), (value, witness) in states.items():
            for w, low, score, line in options[role]:
                if index == hub_index and w != 11:
                    continue
                key = mass + w, small_rank + low
                if key[0] > 87 or key[1] > 2:
                    continue
                new_value = value + score
                if key not in following or new_value > following[key][0]:
                    following[key] = (new_value, witness + [{
                        "role": role, "weight": w, "rank_three": bool(low),
                        "resource": score, "raw_census_line": line}])
        states = following
    best = None
    for (mass, small_rank), (value, witness) in states.items():
        for threes in range(4):
            light_mass = 6 + threes
            if mass + light_mass > 93:
                continue
            light_resource = 10 * (3 + 2 * threes)
            score = value + light_resource
            if best is None or score > best["maximum_resource"]:
                best = {"maximum_resource": score,
                        "total_weight": mass + light_mass,
                        "rank_three_W_vertices": small_rank,
                        "light_weights": [3] * threes + [2] * (3 - threes),
                        "heavy_witness": witness}
    return best


def main():
    started = time.monotonic()
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == PIN
    rows = []
    for line, row in enumerate(csv.reader(DATA.open()), 1):
        values = list(map(int, row))
        assert len(values) == 19
        w, hist, rank = values[0], values[1:-1], values[-1]
        assert sum(hist) == 31
        assert sum(p*c for p, c in enumerate(hist)) == w*(w-1)//2
        if 4 <= w <= 11:
            assert not any(hist[6:])
            rows.append((line, w, hist, rank))

    capacity_checks = []
    for p in range(6):
        for q in range(6):
            cap = elementary_capacity(p, q)
            assert 2*cap <= PRICE[p] + PRICE[q]
            capacity_checks.append([p, q, cap, PRICE[p] + PRICE[q] - 2*cap])

    table = {"U_rank5_top9": {}, "W_rank3_top3": {}, "W_rank_ge4_top3": {}}
    checked_rows = 0
    for line, w, hist, rank in rows:
        if rank == 5:
            value = resource(hist, 9)
            assert 4*value <= 45*w + 6
            old = table["U_rank5_top9"].get(w, -1)
            table["U_rank5_top9"][w] = max(old, value)
            checked_rows += 1
        if rank >= 3:
            value = resource(hist, 3)
            assert 4*value <= 45*w - 213 + 45*int(rank == 3)
            kind = "W_rank3_top3" if rank == 3 else "W_rank_ge4_top3"
            table[kind][w] = max(table[kind].get(w, -1), value)
            checked_rows += 1
    for w in (2, 3):
        assert 4*(10*w*(w-1)//2) <= 45*w - 15

    total_fourfold = 45*93 + 3*6 - 7*213 + 2*45 - 3*15
    assert total_fourfold == 2757
    assert total_fourfold < 4*768
    dynamic = {str(hub): dynamic_maximum(rows, hub) for hub in (None, "W", "U")}
    assert dynamic["W"]["maximum_resource"] == 663
    assert dynamic["U"]["maximum_resource"] == 685
    assert dynamic["None"]["maximum_resource"] <= total_fourfold // 4

    result = {
        "status": "PASS_EXACT_INTEGER_DUAL_AND_INDEPENDENT_DP",
        "seconds": round(time.monotonic() - started, 3),
        "pair_prices": PRICE,
        "elementary_capacity_checks": capacity_checks,
        "checked_raw_census_role_rows": checked_rows,
        "resource_table": table,
        "dual_inequalities": [
            "4 R_U <= 45 w + 6 (rank5, nine slots)",
            "4 R_W <= 45 w - 213 + 45 [rank=3] (rank>=3, three slots)",
            "4 R_L <= 45 w - 15 (w=2 or3, R_L=10*choose(w,2))"],
        "total_fourfold_upper": total_fourfold,
        "integer_resource_upper": total_fourfold // 4,
        "required_resource": 768,
        "exact_fourfold_gap": 4*768 - total_fourfold,
        "independent_dynamic_maxima": dynamic,
        "required_geometric_premises": [
            "Three U vertices, seven W vertices, three light vertices",
            "Twenty-four directions have a unique heavy-heavy edge",
            "Each U fibre is rank5 and contributes on nine such edges",
            "Each W fibre has rank>=3 and contributes on three such edges",
            "At most two W fibres have rank3",
            "Every fibre has weight<=11; total weight<=93"],
        "mathematical_status": "Exact dual conditional on the separate geometry and complete fibre census; no SAT premise.",
        "source_sha256": {
            str(DATA.relative_to(ROOT)): PIN,
            str(Path(__file__).relative_to(ROOT)): hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            str((HERE / "TEN_HEAVY_INTEGER_DUAL.txt").relative_to(ROOT)):
                hashlib.sha256((HERE / "TEN_HEAVY_INTEGER_DUAL.txt").read_bytes()).hexdigest()
        }
    }
    (HERE / "TEN_HEAVY_DUAL_REPLAY.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ["status", "seconds", "resource_table",
          "total_fourfold_upper", "integer_resource_upper", "required_resource", "exact_fourfold_gap"]}, indent=2))


if __name__ == "__main__":
    main()
