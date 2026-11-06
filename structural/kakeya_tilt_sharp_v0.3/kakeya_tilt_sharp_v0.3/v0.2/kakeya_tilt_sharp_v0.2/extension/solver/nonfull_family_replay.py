"""Rebuild and check the 128-set 24-point family without solver receipts."""
from __future__ import annotations
import itertools,json,time
from pathlib import Path
from audit_replay import line_table,is_kakeya_mask


def cosets(subspace,N=8):
    return sorted({tuple(sorted(c^u for u in subspace)) for c in range(N)})


def main():
    t=time.perf_counter();V=set(range(8))
    options=[[(0,V-set(c)) for c in cosets([0,7])],
             [(1,V-set(c)) for c in cosets([0,3])],
             [(2,set(c)) for c in cosets([0,1,2,3])],
             [(4,set(c)) for c in cosets([0,1,4,5])],
             [(7,set(c)) for c in cosets([0,1,6,7])]]
    tables={R:line_table(R,3) for R in ['Z4','D2']}
    masks=set();counts={R:0 for R in tables};example=None
    for fibres in itertools.product(*options):
        points=[a+8*u for a,A in fibres for u in A]
        assert len(points)==24
        mask=sum(1<<x for x in points)
        assert mask not in masks;masks.add(mask)
        for R,table in tables.items():
            assert is_kakeya_mask(mask,table);counts[R]+=1
        if example is None:example=sorted(points)
    assert len(masks)==128
    out={'construction':'two complements of pairs and three affine planes',
         'n':3,'size':24,'maximum_fibre_size':6,'number_of_distinct_sets':len(masks),
         'independent_direct_line_checks':counts,'example':example,
         'seconds':round(time.perf_counter()-t,6)}
    (Path(__file__).resolve().parent/'nonfull_family_receipt.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()
