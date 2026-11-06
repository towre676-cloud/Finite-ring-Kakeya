"""Reproduce the bounded search that located the carry-transfer examples."""
import json
from pathlib import Path
import random
from carry_transfer import (direction_line_masks, is_kakeya_mask,
                            fibres_from_mask, transfer_certificate)


def main():
    n = 3
    rng = random.Random(8148)
    F = direction_line_masks(n, False)
    W = direction_line_masks(n, True)
    out = {"seed": 8148, "trials": 0, "flat_only": 0,
           "mixed_only": 0, "examples": {}}
    for mixed, fams, other in [(False, F, W), (True, W, F)]:
        for _ in range(500):
            K = 0
            order = list(range(len(fams)))
            rng.shuffle(order)
            for i in order:
                costs = [((L & ~K).bit_count(), rng.random(), L) for L in fams[i]]
                K |= min(costs)[2]
            points = [x for x in range(64) if (K >> x) & 1]
            rng.shuffle(points)
            for x in points:
                candidate = K ^ (1 << x)
                if is_kakeya_mask(candidate, fams):
                    K = candidate
            out["trials"] += 1
            if not is_kakeya_mask(K, other):
                key = "mixed_only" if mixed else "flat_only"
                out[key] += 1
                if key not in out["examples"]:
                    A = fibres_from_mask(K, n)
                    out["examples"][key] = {
                        "source_mask_hex": hex(K), "size": K.bit_count(),
                        "profile": [len(a) for a in A],
                        "fibres": [sorted(a) for a in A],
                        "transfer_certificate": transfer_certificate(A, n)}
    Path(__file__).with_name("greedy_transfer_examples.json").write_text(json.dumps(out, indent=2)+"\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
