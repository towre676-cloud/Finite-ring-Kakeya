"""Independent standard-library audit of the uploaded four-element-ring code.

Ring lines are built in coordinate tuples, independently of the producer's
bit-packing arithmetic. Every subset in dimension two is enumerated. The
complete fibre-correlation tables through dimension four are regenerated.
"""
from __future__ import annotations
from collections import Counter
from itertools import product
import json
from math import comb
from pathlib import Path
import random
import sys
import time

HERE=Path(__file__).resolve().parent
INPUT=HERE.parents[1]/'kakeya_sharp'
sys.path.insert(0,str(INPUT))
from kakeya_sharp.rings import covers_via_fibre_identity, K_star, directions, lines_in_direction
from spectral_relaxation import exact_fibre_table, profile_from_mask, walsh


def add(r,a,b):
    return (a+b)%4 if r=='Z4' else a^b


def mul(r,a,b):
    if r=='Z4': return a*b%4
    return ((a&1)&(b&1)) | ((((a&1)*(b>>1))^((a>>1)*(b&1)))<<1)


def pack_tuple(x):
    n=len(x)
    return sum((z&1)<<i for i,z in enumerate(x)) | sum((z>>1)<<(n+i) for i,z in enumerate(x))


def line_table(r,n):
    points=list(product(range(4),repeat=n))
    representatives={}
    for v in points:
        if not any(x&1 for x in v): continue
        key=min(v,tuple(mul(r,3,x) for x in v))
        representatives[key]=key
    out={}
    for v in sorted(representatives):
        masks=set()
        for x in points:
            line={tuple(add(r,a,mul(r,t,b)) for a,b in zip(x,v)) for t in range(4)}
            assert len(line)==4
            masks.add(sum(1<<pack_tuple(y) for y in line))
        out[pack_tuple(v)]=tuple(sorted(masks))
    return out


def is_kakeya_mask(mask,table):
    return all(any(mask&line==line for line in ls) for ls in table.values())


def census_n2(r):
    table=line_table(r,2)
    # Normalize producer direction representatives by complete line partition.
    expected={tuple(sorted(sum(1<<x for x in L) for L in lines_in_direction(r,b,2))) for b in directions(2)}
    assert set(table.values())==expected
    counts=Counter(); extrema=[]
    for mask in range(1<<16):
        yes=is_kakeya_mask(mask,table)
        K=[i for i in range(16) if mask>>i&1]
        assert yes==covers_via_fibre_identity(r,K,2)
        if yes:
            counts[mask.bit_count()]+=1
            if mask.bit_count()==10: extrema.append(mask)
    assert min(counts)==10 and counts[10]==32
    profs=Counter()
    for mask in extrema:
        sizes=tuple(sorted((sum(bool(mask>>(a+4*u)&1) for u in range(4)) for a in range(4)),reverse=True))
        profs[sizes]+=1
    assert set(profs)=={(4,2,2,2)}
    # The two rings actually have the identical family of minimum sets.
    return {'subsets_checked':1<<16,'minimum':min(counts),'minimum_sets':len(extrema),
            'counts_by_size':dict(sorted(counts.items())),
            'equality_profiles':{'4,2,2,2':32},'extremal_masks':extrema,
            'line_partitions':len(table),'fibre_identity_disagreements':0}


def main():
    t=time.perf_counter()
    out={'method':'independent tuple arithmetic, exhaustive finite census, exact integer transforms',
         'rings':{r:census_n2(r) for r in ['Z4','D2']}}
    assert out['rings']['Z4']['extremal_masks']==out['rings']['D2']['extremal_masks']
    out['same_minimum_family']=True
    tables={R:line_table(R,2) for R in ['Z4','D2']}
    comparison={name:Counter() for name in ['Z4_only','D2_only','both']}
    for mask in range(1<<16):
        mixed=is_kakeya_mask(mask,tables['Z4']);flat=is_kakeya_mask(mask,tables['D2'])
        name='both' if mixed and flat else ('Z4_only' if mixed else ('D2_only' if flat else None))
        if name:comparison[name][mask.bit_count()]+=1
    assert comparison['Z4_only']=={12:64} and not comparison['D2_only']
    out['complete_ring_comparison']={name:dict(sorted(counts.items())) for name,counts in comparison.items()}
    out['local_tables']={}
    for n in range(1,5):
        rows=exact_fibre_table(n)
        for row in rows:
            s=row[0]; C=[s,*[2*x for x in row[1:]]]; spectrum=walsh(C)
            # Direct indicator transform provides the square identity for
            # every mask, below; this loop checks complete distinct profiles.
            from math import isqrt
            assert all(x>=0 and isqrt(x)**2==x for x in spectrum)
        N=1<<n
        for mask in range(1<<N):
            f=[(mask>>u)&1 for u in range(N)]
            row=profile_from_mask(mask,n)
            assert walsh([row[0],*[2*x for x in row[1:]]])==[x*x for x in walsh(f)]
        out['local_tables'][str(n)]={'subsets_checked':1<<N,'distinct_profiles':len(rows),
            'counts_by_size':dict(sorted(Counter(x[0] for x in rows).items()))}
    out['equality_count_correction']={'range_n_ge_2':'2^n * 2^((n-1)*(2^n-1))','n1_actual':1,'n1_unrestricted_formula':2}
    out['seconds']=round(time.perf_counter()-t,6)
    p=HERE/'audit_receipt.json';p.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('rings',)},indent=2))
    print('Saved',p)


if __name__=='__main__': main()
