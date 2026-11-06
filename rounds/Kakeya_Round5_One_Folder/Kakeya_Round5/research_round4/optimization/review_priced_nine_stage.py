"""Exact cross-check of the bounded single-hub priced-nine-heavy stage.

This imports no producer or inventory verifier. A backward nine-slot recursion
recomputes every supplied active/inactive light-row maximum. It verifies each
price witness and exact subtraction from the frozen276267-profile baseline.
"""
from collections import Counter
from functools import lru_cache
from pathlib import Path
import hashlib
import json
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'research_round4/middle_inventory'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def cap(p,q):
    a,b=sorted((p,q))
    return b+8 if a==3 and 5<=b<=7 else min(16,p*q)


def quota(w):
    return (w&-w)-1 if w%2==0 else max((w-1)&-(w-1),(w+1)&-(w+1))-1


@lru_cache(None)
def row(w,heavy,ell,active):
    c=w//2
    mass=w*w//4
    maximums=(quota(w)+1)//2
    @lru_cache(None)
    def recurse(j,left,remaining_maxima):
        if j<0:
            return 0
        options=[]
        for p in range(min(c,left)+1):
            if j==0 and bool(p)!=active:
                continue
            if p==c and remaining_maxima==0:
                continue
            options.append(2*cap(p,heavy[j])-ell*p+
                           recurse(j-1,left-p,remaining_maxima-int(p==c)))
        # A previously spent budget can make a forced active hub infeasible.
        return max(options,default=-10**8)
    return ell*mass+recurse(8,mass,min(maximums,9))


def main():
    start=time.monotonic()
    cuts={}
    price_counts=Counter()
    cell_cuts=Counter()
    minimum_gap=10**9
    for saved in map(json.loads,(SOURCE/'PRICED_NINE_HEAVY_CUTS.jsonl').open()):
        w=tuple(saved['weights'])
        s,m,t=saved['support'],saved['maximum'],saved['price']
        assert w not in cuts and len(w)==s and sum(w)==93
        assert w==tuple(sorted(w,reverse=True)) and w[0]==m and min(w)>=2
        assert 10<=s<=17 and 12<=m<=18 and 0<=t<=32
        heavy=tuple(v//2 for v in w[:9])
        ell=w[9]//2
        assert all(v//2<=ell for v in w[9:])
        expected_rows=[]
        for v in w[9:]:
            expected_rows.append([v,row(v,heavy,ell,False),row(v,heavy,ell,True)])
        assert expected_rows==saved['light_rows']
        upper=3*t+sum(max(inactive,active-t) for _,inactive,active in expected_rows)
        assert upper==saved['upper_doubled']<96
        improvements=[max(0,active-inactive) for _,inactive,active in expected_rows]
        assert all(gain<=32-ell<=31 for gain in improvements)
        continuous_optimum=sum(inactive for _,inactive,active in expected_rows)+sum(sorted(improvements,reverse=True)[:3])
        assert upper==continuous_optimum
        # Slope proof: for every integer r>=3, subtracting required32r
        # changes the margin by (t-32)(r-3)<=0.
        assert t-32<=0
        cuts[w]=saved
        cell_cuts[s,m]+=1
        price_counts[t]+=1
        minimum_gap=min(minimum_gap,96-upper)
    assert len(cuts)==512

    before=Counter()
    after=Counter()
    occurrences=Counter()
    expected_hash=hashlib.sha256()
    for raw in (SOURCE/'after_cube_weight_survivors.txt').open('rb'):
        s,m,b,*ws=map(int,raw.split())
        w=tuple(ws)
        before[s,m]+=1
        if w in cuts:
            occurrences[w]+=1
        else:
            after[s,m]+=1
            expected_hash.update(raw)
    assert sum(before.values())==276267
    assert sum(after.values())==275755
    assert set(occurrences)==set(cuts) and set(occurrences.values())=={1}
    assert expected_hash.hexdigest()==sha(SOURCE/'after_priced_nine_survivors.txt')
    assert before[17,18]==1 and after[17,18]==0
    closed=[key for key in sorted(before) if before[key]>0 and after[key]==0]
    assert closed==[(17,18)]
    exemplar=(18,)+(8,)*5+(7,6,6)+(2,)*8
    c=cuts[exemplar]
    assert c['price']==10 and c['upper_doubled']==94
    assert c['light_rows']==[[2,8,18]]*8
    for method_file in ('geometry_and_spectrum_cuts.txt','CUBE_JOINT_ENERGY_CUTS.jsonl'):
        for line in (SOURCE/method_file).open():
            if method_file.endswith('.jsonl'):
                w=tuple(json.loads(line)['weights'])
            else:
                fields=line.split();n=int(fields[3]);w=tuple(map(int,fields[4+n:]))
            assert w not in cuts
    result=dict(status='PASS_BOUNDED_PRICED_NINE_CROSS_CHECK',
                baseline_weight_profiles=276267,new_disjoint_weight_profile_exclusions=512,
                remaining_weight_profiles=275755,closed_support_maximum_cells=[[17,18]],
                independent_local_row_modes=row.cache_info().currsize,
                minimum_doubled_gap=minimum_gap,price_counts=dict(sorted(price_counts.items())),
                one_hub_real_price_optimum='sum inactive rows plus the three largest positive(active-inactive) gains; every saved witness attains this exact optimum.',
                exemplar={'weights':list(exemplar),'price':10,'upper_doubled':94,'required_doubled':96},
                new_support_theorem='Together with the complete baseline inventory and inherited higher-support exclusions, exact maximum18 implies pair-active support<=16.',
                scope='Exact supplied-witness replay, closed-form continuous optimum of the single-largest-heavy price family, and byte-identical subtraction; other multi-price families are not optimized.',
                epistemic_scope='Cross-check by another model agent in the same session, not external human review.',
                files_sha256={str(p.relative_to(ROOT)):sha(p) for p in [
                    SOURCE/'screen_priced_nine.cpp',SOURCE/'PRICED_NINE_HEAVY_CUTS.jsonl',
                    SOURCE/'after_cube_weight_survivors.txt',SOURCE/'after_priced_nine_survivors.txt',
                    HERE/'M18_SUPPORT17_BOUNDARY_PROOF.md',Path(__file__).resolve(),
                ]},seconds=round(time.monotonic()-start,3))
    (HERE/'PRICED_NINE_STAGE_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','baseline_weight_profiles','new_disjoint_weight_profile_exclusions','remaining_weight_profiles','closed_support_maximum_cells','independent_local_row_modes','minimum_doubled_gap','seconds')},indent=2))


if __name__=='__main__':
    main()
