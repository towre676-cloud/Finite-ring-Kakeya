"""Exact induced-edge budgets for a degree-seven Cayley graph on 32 vertices.

Graph: (K_{4,4} minus a matching, each vertex replaced by two independent
vertices) Cartesian K_2.  For each of four paired blocks, record the selected
counts a0,a1,b0,b1 in {0,1,2}. The cross-layer matching can attain the minimum
of each pair of layer counts independently. The DP records the four aggregate
side counts and the additive within-block correction. All arithmetic is integer.
"""
from itertools import product
from pathlib import Path
import json


def calculate():
    types = list(product(range(3), repeat=4))
    dp = {(0, 0, 0, 0): 0}
    layer_sizes = []
    for block in range(4):
        nxt = {}
        for counts, correction in dp.items():
            for a0, a1, b0, b1 in types:
                key = tuple(x + y for x, y in zip(counts, (a0, a1, b0, b1)))
                score = correction - a0 * b0 - a1 * b1 + min(a0, a1) + min(b0, b1)
                if score > nxt.get(key, -10000):
                    nxt[key] = score
        dp = nxt
        layer_sizes.append(len(dp))
    best = [-1] * 33
    for (a0, a1, b0, b1), correction in dp.items():
        w = a0 + a1 + b0 + b1
        e = a0 * b0 + a1 * b1 + correction
        best[w] = max(best[w], e)
    assert best[32] == 112
    assert all(best[32 - w] == 112 - 7 * w + best[w] for w in range(33))
    return {"status": "PASS_EXACT_INTEGER_DP", "graph": "blowup_2(K4,4-minus-matching) Cartesian K2", "max_induced_edges_by_weight": best, "dp_state_counts": layer_sizes}


if __name__ == '__main__':
    result = calculate()
    Path(__file__).with_suffix('.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
