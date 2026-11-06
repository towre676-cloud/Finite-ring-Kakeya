"""Exhaustive check of shared-period capacity and the 24-point phantom."""
from __future__ import annotations
import itertools,json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'kakeya_sharp'))
from kakeya_sharp.rings import covers_via_fibre_identity
from spectral_relaxation import profile_from_mask,period_mask,common_period_size


def pairset(mask,v,N):
    return {min(u,u^v) for u in range(N) if mask>>u&1 and mask>>(u^v)&1}


def main():
    start=time.perf_counter();N=8;H=4
    rows=[profile_from_mask(mask,3) for mask in range(256)]
    periods=[period_mask(row) for row in rows]
    checks=improvements=0
    for v in range(1,N):
        ps=[pairset(mask,v,N) for mask in range(256)]
        for a in range(256):
            for b in range(256):
                product=len(ps[a])*len(ps[b])
                j=common_period_size(periods[a],periods[b],v,N)
                assert product%j==0
                bound=min(H,product//j)
                actual=len({min(x^y,(x^y)^v) for x in ps[a] for y in ps[b]})
                assert actual<=bound
                checks+=1;improvements+=bound<min(H,product)
    source=json.loads((HERE/'nonfull_exact_local_n3.json').read_text())
    choices=[[mask for mask,row in enumerate(rows) if row==(s,*p)] for s,p in zip(source['sizes'],source['pairs'])]
    count=0;liftable={'Z4':0,'D2':0}
    for masks in itertools.product(*choices):
        K=[a+N*u for a,mask in enumerate(masks) for u in range(N) if mask>>u&1]
        count+=1
        for R in liftable:liftable[R]+=covers_via_fibre_identity(R,K,3)
    assert count==128 and not any(liftable.values())
    v=6;capacities=[]
    for a in range(N):
        b=a^v
        if a>=b:continue
        ra=(source['sizes'][a],*source['pairs'][a]);rb=(source['sizes'][b],*source['pairs'][b])
        j=common_period_size(period_mask(ra),period_mask(rb),v,N)
        capacities.append({'a':a,'b':b,'pair_counts':[ra[v],rb[v]],'common_period_order':j,'discounted_capacity':min(H,ra[v]*rb[v]//j)})
    assert sum(x['discounted_capacity'] for x in capacities)==2
    out={'n':3,'ordered_subset_pair_direction_checks':checks,'strict_capacity_improvements':improvements,
         'capacity_violations':0,'phantom_size':24,'phantom_local_realization_counts':[len(x) for x in choices],
         'phantom_total_realizations':count,'phantom_kakeya_realizations':liftable,
         'failing_direction':v,'required_coverage':H,'edge_capacities':capacities,
         'seconds':round(time.perf_counter()-start,6)}
    (HERE/'period_receipt.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()
