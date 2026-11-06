"""Produce the final eight analytic support-eighteen certificates.

This file records arithmetic for proved lemmas. Independent replay is in
verify_support18_completion.py; no tangent placement is assumed here.
"""
from pathlib import Path
from collections import Counter
import json

HERE = Path(__file__).resolve().parent
C = (12,) + (8,)*6 + (6,6,4,3) + (2,)*7
D = (12,) + (8,)*6 + (6,5,5,3) + (2,)*7
E = (12,) + (8,)*6 + (6,5,4,4) + (2,)*7
B16 = (16,) + (8,)*6 + (5,4,4) + (2,)*8
ENERGY = {2:1, 3:3, 4:12, 5:16, 6:33, 8:112, 12:300}


def cube_certificate(weights):
    assert weights in (C, D, E)
    total = sum(ENERGY[w] for w in weights)
    assert total-84 < 992
    branches = []
    for r in (5, 6):
        remaining = list(weights)
        for _ in range(r):
            remaining.remove(8)
        residual_energy = sum(70 if w == 8 else ENERGY[w] for w in remaining)
        gain = sum(5*r if w in (8,12) else r+3 if w == 6 else 3 if w in (4,5) else 0
                   for w in remaining)
        upper = residual_energy+77*r+10*(r*r//4)+gain
        assert upper < 992
        branches.append(dict(cubes=r, residual_energy=residual_energy,
                             surplus_doubled=gain, upper_doubled=upper))
    return dict(method='cube_direction_energy', unrestricted_energy=total,
                energy_with_two_noncubes=total-84, branches=branches)


def run():
    out = []
    for line in (HERE/'support18_after_sumfree9.jsonl').open():
        old = json.loads(line)
        w = tuple(old['weights'])
        if w in (C,D,E):
            cert = cube_certificate(w)
        elif w == B16:
            cert = dict(method='hub16_equality_actual_sumset',
                        missing9_capacity_upper=128, missing6_capacity_upper=96,
                        hub_pair_counts=[8]*6, forced_light4_edge_product=16,
                        forced_light4_edge_actual=8)
        else:
            hs = w[:10]
            ls = w[10:]
            assert hs[0] == 12 and all(v//2 <= 4 for v in hs[1:])
            assert all(v <= 3 for v in ls)
            k = sum(v//2 <= 3 for v in hs)
            mass = sum(v*(v-1)//2 for v in ls)
            demand = min(3*k,12)
            assert mass < demand
            cert = dict(method='ten_heavy_weak_unique_directions', weak_vertices=k,
                        light_pair_mass=mass, required_pair_mass=demand)
        out.append(dict(weights=list(w), maximum=w[0], support=len(w), excluded=True,
                        **cert))
    assert len(out)==8
    (HERE/'FINAL_ANALYTIC_SUPPORT18_CERTIFICATES.jsonl').write_text(
        ''.join(json.dumps(r,separators=(',',':'))+'\n' for r in out))
    print(json.dumps(dict(excluded=len(out), methods=dict(Counter(r['method'] for r in out)))))


if __name__ == '__main__':
    run()
