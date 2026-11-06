#!/usr/bin/env python3
"""The sharp eight-point difference bound in F2^5; finite corroboration."""
from pathlib import Path
from collections import Counter
import hashlib
import itertools
import json


def difference_cap(h):
    if not 0 <= h <= 8:
        raise ValueError("This sharp cap is supplied only for zero through eight vertices")
    return 25 if h == 8 else h * (h - 1) // 2


def verify():
    basis = {0, 1, 2, 4, 8, 16}
    extra = [x for x in range(32) if x not in basis]
    counts = Counter()
    best = None
    examined = 0
    for u, v in itertools.combinations(extra, 2):
        S = sorted(basis | {u, v})
        planes = [list(A) for A in itertools.combinations(S, 4) if A[0] ^ A[1] ^ A[2] ^ A[3] == 0]
        assert planes
        D = {a ^ b for a, b in itertools.combinations(S, 2)}
        assert len(D) <= 25
        counts[len(D)] += 1
        examined += 1
        if best is None or len(D) > best["difference_count"]:
            best = {"support": S, "difference_count": len(D), "affine_plane": planes[0]}
    assert examined == 325 and best["difference_count"] == 25
    return {"status": "PASS_SHARP_EIGHT_POINT_DIFFERENCE_BOUND",
            "normalized_rank_five_sets_checked": examined,
            "all_contain_a_four_point_affine_plane": True,
            "difference_count_distribution": {str(k): v for k, v in sorted(counts.items())},
            "lower_rank_argument": "Affine rank at most four confines all differences to a space of at most sixteen points, so at most fifteen nonzero differences.",
            "sharp_example": best, "difference_caps_zero_through_eight": [difference_cap(h) for h in range(9)],
            "manual_proof": "HEAVY_LIGHT_DUAL_LEMMA.md"}


if __name__ == "__main__":
    result = verify()
    result["source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    Path(__file__).with_name("DIFFERENCE8_REPLAY.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
