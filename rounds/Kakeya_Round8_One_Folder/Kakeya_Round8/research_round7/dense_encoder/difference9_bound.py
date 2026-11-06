#!/usr/bin/env python3
"""Complete affine-basis reduction for nine-point differences in F2^5."""
from pathlib import Path
from collections import Counter
import hashlib
import itertools
import json
from difference8_bound import difference_cap as cap8


def difference_cap(h):
    if not 0 <= h <= 9:
        raise ValueError("This cap is supplied only for zero through nine vertices")
    return 28 if h == 9 else cap8(h)


def verify():
    affine_basis = {0, 1, 2, 4, 8, 16}
    remaining = [x for x in range(32) if x not in affine_basis]
    counts, best, cases = Counter(), None, []
    for extra in itertools.combinations(remaining, 3):
        S = sorted(affine_basis | set(extra))
        D = {a ^ b for a, b in itertools.combinations(S, 2)}
        assert len(D) <= 28
        counts[len(D)] += 1
        cases.append([*extra, len(D)])
        if best is None or len(D) > best["difference_count"]:
            best = {"support": S, "difference_count": len(D), "differences": sorted(D)}
    assert len(cases) == 2600 and best["difference_count"] == 28
    return {"status": "PASS_COMPLETE_NINE_POINT_AFFINE_BASIS_DIFFERENCE_BOUND",
            "normalized_rank_five_sets_checked": len(cases),
            "affine_basis": sorted(affine_basis),
            "complete_normalized_extras_and_difference_counts": cases,
            "difference_count_distribution": {str(k): v for k, v in sorted(counts.items())},
            "lower_rank_bound": 15,
            "completeness_argument": "Every rank-five nine-set has an affine basis of six points. Translate one basis point to zero and map the five independent differences to the standard basis. The remaining three points are distinct members of the other twenty-six vectors; all C(26,3)=2600 choices are checked. Lower rank gives at most fifteen nonzero differences.",
            "sharp_example": best,
            "difference_caps_zero_through_nine": [difference_cap(h) for h in range(10)]}


if __name__ == "__main__":
    result = verify()
    result["source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    Path(__file__).with_name("DIFFERENCE9_REPLAY.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items()
                      if key != "complete_normalized_extras_and_difference_counts"}, indent=2))
