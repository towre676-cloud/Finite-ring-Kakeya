"""Solver-free exhaustive proof for the n=3 local-profile relaxation.

Each local domain is the complete autocorrelation table of all 256 subsets.
Propagation uses integer size, energy, affine-flag ordering, and directional
capacity bounds only. Branching partitions a domain into its singleton choices.
Every rejected state has an explicit violated necessary inequality.
"""
from __future__ import annotations
import argparse,json,time
from pathlib import Path
from spectral_relaxation import exact_fibre_table,period_mask,common_period_size
from functools import lru_cache


def prove(n=3,ub=21,cap=None,exclude=None,node_limit=2000000,use_period=False):
    N=1<<n; H=N//2
    rows=tuple(r for r in exact_fibre_table(n) if r[0]!=1 and (cap is None or r[0]<=cap))
    sizes=[r[0] for r in rows]
    energy=[sum(x*x for x in r[1:]) for r in rows]
    order=[(0,a) for a in range(1,N)]+[(1,a) for a in range(2,N)]
    for k in range(1,n): order.extend((1<<k,a) for a in range((1<<k)+1,N))
    pairs={v:[(a,a^v) for a in range(N) if a<(a^v)] for v in range(1,N)}
    if use_period:
        periods=[period_mask(row) for row in rows]
        caps={v:[[min(H,ra[v]*rb[v]//common_period_size(periods[i],periods[j],v,N)) for j,rb in enumerate(rows)] for i,ra in enumerate(rows)] for v in range(1,N)}
    @lru_cache(maxsize=65536)
    def edgecap(da,db,v):
        return max(caps[v][r][s] for r in da for s in db)
    nodes=0;cuts={};start=time.perf_counter();memo=set()

    def fail(reason):
        cuts[reason]=cuts.get(reason,0)+1
        return None

    def reduce(dom):
        while True:
            before=dom
            mins=[min(sizes[r] for r in d) for d in dom]
            maxs=[max(sizes[r] for r in d) for d in dom]
            if sum(mins)>ub: return fail('size')
            hmin=sum(x>2 for x in mins);hmax=sum(x>2 for x in maxs)
            hallowed=[]
            for h in range(hmin,hmax+1):
                if ub<3*N-2 and h<3:continue
                for maximum in {sizes[r] for r in dom[0]}:
                    if maximum<2:continue
                    q=(H+maximum//2-1)//(maximum//2)
                    if q*max(0,N-1-h*(h-1)//2)<=N-h:
                        hallowed.append(h);break
            if not hallowed:return fail('external resources')
            maxe=[max(energy[r] for r in d) for d in dom]
            if sum(maxe)<N*(N-1): return fail('energy')
            maxp=[[0]+[max(rows[r][v] for r in d) for v in range(1,N)] for d in dom]
            req=[[0]*N for _ in range(N)]
            forced_caps=[[0]*N for _ in range(N)]
            for v,edges in pairs.items():
                edgeuppers=[edgecap(dom[a],dom[b],v) if use_period else maxp[a][v]*maxp[b][v] for a,b in edges]
                upper=sum(edgeuppers)
                if upper<H: return fail('direction')
                for (a,b),edgeupper in zip(edges,edgeuppers):
                    need=H-upper+edgeupper
                    if need>0:
                        if maxp[b][v]==0 or maxp[a][v]==0: return fail('direction')
                        req[a][v]=max(req[a][v],(need+maxp[b][v]-1)//maxp[b][v])
                        req[b][v]=max(req[b][v],(need+maxp[a][v]-1)//maxp[a][v])
                        if use_period:forced_caps[a][v]=forced_caps[b][v]=need
            lo=mins[:];hi=[min(maxs[a],ub-sum(mins)+mins[a]) for a in range(N)]
            for a,b in order:
                lo[a]=max(lo[a],mins[b]);hi[b]=min(hi[b],maxs[a])
            new=[]
            for a,d in enumerate(dom):
                neede=N*(N-1)-sum(maxe)+maxe[a]
                dd=tuple(r for r in d if lo[a]<=sizes[r]<=hi[a] and energy[r]>=neede and all(rows[r][v]>=req[a][v] for v in range(1,N)))
                if use_period:
                    dd=tuple(r for r in dd if all(not forced_caps[a][v] or edgecap((r,),dom[a^v],v)>=forced_caps[a][v] for v in range(1,N)))
                if hmin==max(hallowed):dd=tuple(r for r in dd if sizes[r]<=2 or mins[a]>2)
                if hmax==min(hallowed):dd=tuple(r for r in dd if sizes[r]>2 or maxs[a]<=2)
                if not dd: return fail('domain')
                new.append(dd)
            dom=tuple(new)
            if dom==before: return dom

    def search(dom):
        nonlocal nodes
        nodes+=1
        if nodes>node_limit: raise TimeoutError('declared node limit')
        dom=reduce(dom)
        if dom is None:return None
        if dom in memo:return None
        if all(len(d)==1 for d in dom):
            rs=[rows[d[0]] for d in dom]
            if exclude is not None and sorted([r[0] for r in rs],reverse=True)==list(exclude):
                return fail('excluded profile')
            return rs
        # Prefer a heavily constrained fibre and larger mass when tied.
        a=min((a for a in range(N) if len(dom[a])>1),key=lambda a:(len(dom[a]),-max(sizes[r] for r in dom[a]),a))
        for r in dom[a]:
            child=list(dom);child[a]=(r,)
            ans=search(tuple(child))
            if ans is not None:return ans
        memo.add(dom)
        return None

    status='INFEASIBLE'
    try:
        witness=search(tuple(tuple(range(len(rows))) for _ in range(N)))
        if witness is not None:status='FEASIBLE'
    except TimeoutError:
        status='NODE_LIMIT';witness=None
    return {'n':n,'upper_constraint':ub,'max_fibre_constraint':cap,'excluded_profile':exclude,
            'method':'standard-library exhaustive domain branching over exact local autocorrelations',
            'common_period_capacities':use_period,
            'status':status,'nodes':nodes,'memoized_states':len(memo),'pruning_counts':cuts,
            'seconds':round(time.perf_counter()-start,6),'local_rows':len(rows),'witness':witness}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ub',type=int,default=21)
    ap.add_argument('--cap',type=int);ap.add_argument('--exclude-star',action='store_true')
    ap.add_argument('--nodes',type=int,default=2000000);ap.add_argument('--output',type=Path)
    ap.add_argument('--period',action='store_true')
    a=ap.parse_args();r=prove(3,a.ub,a.cap,[8,2,2,2,2,2,2,2] if a.exclude_star else None,a.nodes,a.period)
    raw=json.dumps(r,indent=2)+'\n';print(raw)
    if a.output:a.output.write_text(raw)


if __name__=='__main__':main()
