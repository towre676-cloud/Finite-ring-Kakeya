"""Independent missing-direction geometry and resource-certificate replay.

No producer is imported. All normalized nine-point sets are enumerated;
local resources use backward recursion, and light placement uses a multiset
recursion, instead of the producer's forward resource/bitmask assignment DPs.
"""
from collections import Counter
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import json
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = ROOT/'research_round4/middle_inventory/after_priced_nine_survivors.txt'


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def enumerate_geometry():
    types = Counter()
    witnesses = {}
    rank_counts = Counter()
    for rank in (4, 5):
        basis = (0,) + tuple(1 << i for i in range(rank))
        options = tuple(x for x in range(1 << rank) if x not in basis)
        for extra in combinations(options, 9-len(basis)):
            heavy = set(basis + extra)
            differences = {a ^ b for a, b in combinations(heavy, 2)}
            missing = set(range(1, 32)) - differences
            assert all(a ^ b not in missing for a, b in combinations(missing, 2))
            histogram = Counter(sum((x ^ d) in heavy for d in missing)
                                for x in range(32) if x not in heavy)
            hist = tuple(histogram[k] for k in range(10))
            key = len(missing), hist
            assert sum(hist) == 23 and sum(k*c for k, c in enumerate(hist)) == 9*len(missing)
            types[key] += 1
            rank_counts[rank] += 1
            witnesses.setdefault(key, {'heavy': sorted(heavy), 'missing': sorted(missing)})
    assert rank_counts == {4:330, 5:2600}
    expected = {
        3: ((1,18,3,1,0,0,0,0,0,0),260),
        4: ((7,0,12,4,0,0,0,0,0,0),750),
        6: ((3,0,12,2,6,0,0,0,0,0),660),
        8: ((0,8,2,0,9,0,4,0,0,0),810),
        9: ((0,0,15,0,0,0,7,0,0,1),60),
        10: ((1,0,0,8,12,0,0,0,0,2),60),
        16: ((7,0,0,0,0,0,0,0,0,16),330),
    }
    assert types == {(r,h):n for r,(h,n) in expected.items()}
    records = [dict(missing_count=r, outside_degree_histogram=list(h),
                    normalized_sets=types[r,h], **witnesses[r,h])
               for r,h in sorted(types)]
    data = {'status':'PASS_COMPLETE_NORMALIZED_NINE_POINT_CENSUS',
            'normalized_sets':2930, 'rank_counts':dict(rank_counts), 'records':records,
            'completeness':'Every nine-point subset of F2^5 has rank4 or5; translate a selected point to0 and map a selected affine basis to the coordinate basis. All remaining point choices are enumerated. Missing-direction neighbour histograms are affine invariant.',
            'scope':'Complete seven-row missing-direction geometry, not a census of all fibre shapes or Kakeya constructions.'}
    (HERE/'NINE_MISSING_DEGREE_CENSUS.json').write_text(json.dumps(data,indent=2)+'\n')
    return tuple((r,h) for r,h in sorted(types))


def capacity(p,q):
    a,b = sorted((p,q))
    return b+8 if a==3 and 5<=b<=7 else min(16,p*q)


def maximum_quota(w):
    return (w & -w)-1 if w%2==0 else max((w-1)&-(w-1),(w+1)&-(w+1))-1


@lru_cache(None)
def local_rows(w,heavy,ell):
    mass,cap,quota = w*w//4,w//2,(maximum_quota(w)+1)//2
    @lru_cache(None)
    def backward(k,left,full_left):
        if k==0:
            return 0
        return max(2*capacity(p,heavy[k-1])-ell*p+
                   backward(k-1,left-p,full_left-int(p==cap))
                   for p in range(min(cap,left)+1) if p<cap or full_left>0)
    result = tuple(ell*mass+backward(k,mass,quota) for k in range(10))
    assert all(a<=b for a,b in zip(result,result[1:]))
    return result


@lru_cache(None)
def assign_rows(rows,slots):
    levels = tuple(sorted(set(slots)))
    multiplicities = tuple(slots.count(k) for k in levels)
    @lru_cache(None)
    def place(i,remaining):
        if i==len(rows):
            assert sum(remaining)==0
            return 0
        choices=[]
        for j,k in enumerate(levels):
            if remaining[j]:
                reduced=list(remaining);reduced[j]-=1
                choices.append(rows[i][k]+place(i+1,tuple(reduced)))
        return max(choices)
    return place(0,multiplicities)


def bounds_for(weights,geometry):
    heavy=tuple(w//2 for w in weights[:9]);ell=weights[9]//2
    rows=tuple(local_rows(w,heavy,ell) for w in weights[9:])
    result=[]
    for missing,hist in geometry:
        slots=tuple(k for k in reversed(range(10)) for _ in range(hist[k]))[:len(rows)]
        bound=assign_rows(rows,slots)
        result.append(bound)
        if bound>=32*missing:
            return tuple(result),False
    return tuple(result),True


def main():
    if sys.flags.optimize:
        raise SystemExit('Run without -O; assertions are part of the verifier.')
    started=time.monotonic()
    geometry=enumerate_geometry()
    # Independently check the monotonicity needed to replace actual heavy
    # neighbours by the k largest pair caps.
    assert all(capacity(p,q)<=capacity(p,q+1) for p in range(10) for q in range(9))
    saved={}
    for row in map(json.loads,(HERE/'NINE_GEOMETRY_CUTS.jsonl').open()):
        weights=tuple(row['weights'])
        assert weights not in saved
        assert row['support']==len(weights) and row['maximum']==weights[0]
        assert row['cutoff']==weights[9]//2
        saved[weights]=row
    seen=set();cuts=Counter();initial=Counter();survivors=Counter()
    output_hash=sha256();minimum_gap=10**9
    for raw in INPUT.open('rb'):
        support,maximum,old_bound,*values=map(int,raw.split());w=tuple(values)
        assert len(w)==support and sum(w)==93 and min(w)>=2
        assert 10<=support<=17 and 12<=maximum<=18 and w[0]==maximum
        assert w==tuple(sorted(w,reverse=True)) and w not in seen
        seen.add(w);initial[support,maximum]+=1
        bounds,excluded=bounds_for(w,geometry)
        assert excluded==(w in saved)
        if excluded:
            assert list(bounds)==saved[w]['doubled_bounds']
            assert len(bounds)==7
            cuts[support,maximum]+=1
            minimum_gap=min(minimum_gap,*(32*r-b for (r,_),b in zip(geometry,bounds)))
        else:
            survivors[support,maximum]+=1
            output_hash.update(raw)
    target=HERE/'after_nine_geometry_survivors.txt'
    assert len(seen)==275755 and set(saved)<=seen and len(saved)==4088
    assert sum(survivors.values())==271667
    assert output_hash.hexdigest()==digest(target)
    assert len(survivors)==55
    receipt={
        'status':'PASS_COMPLETE_NINE_GEOMETRY_SCREEN',
        'input_weight_profiles':275755,'new_whole_weight_profile_exclusions':4088,
        'remaining_weight_profiles':271667,'new_empty_cells':[],
        'geometry_types':7,'normalized_nine_sets':2930,
        'local_resource_keys':local_rows.cache_info().currsize,
        'assignment_keys':assign_rows.cache_info().currsize,
        'minimum_doubled_gap':minimum_gap,
        'by_support':[{'support':s,'initial':sum(v for (n,m),v in initial.items() if n==s),
                       'excluded':sum(v for (n,m),v in cuts.items() if n==s),
                       'remaining':sum(v for (n,m),v in survivors.items() if n==s)} for s in range(10,18)],
        'by_cell':[{'support':s,'maximum':m,'initial':initial[s,m],
                    'excluded':cuts[s,m],'remaining':survivors[s,m]}
                   for s in range(10,18) for m in range(12,19)],
        'dependencies':{str(p.relative_to(ROOT)):digest(p) for p in [INPUT,HERE/'screen_nine_geometry.cpp',
              HERE/'NINE_GEOMETRY_CUTS.jsonl',HERE/'NINE_MISSING_DEGREE_CENSUS.json',target,Path(__file__).resolve()]},
        'scope':'Complete replay of this degree-slot necessary-condition family on the Round4 middle residual. Every geometry branch is covered; remaining profiles are not constructions. Analytic validity uses the included resource proof and maximal-direction subgroup lemma.',
        'seconds':round(time.monotonic()-started,3),
    }
    (HERE/'NINE_GEOMETRY_REPLAY.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('status','input_weight_profiles','new_whole_weight_profile_exclusions',
                    'remaining_weight_profiles','local_resource_keys','assignment_keys','minimum_doubled_gap','seconds')},indent=2))


if __name__=='__main__':
    main()
