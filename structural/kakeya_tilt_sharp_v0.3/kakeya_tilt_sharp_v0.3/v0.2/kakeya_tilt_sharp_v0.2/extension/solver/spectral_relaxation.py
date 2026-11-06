"""Strengthened, exportable Kakeya pair-count relaxations.

T: pair budget and defect triangles, as in the uploaded v0.1.
S: T plus integer-square Walsh spectrum of every fibre autocorrelation.
S4: S plus the exact four-frequency XOR phase-completion rule in dimension 4.
E: T plus the complete exact autocorrelation table of subsets of F_2^n.
EP: E with common-stabilizer discounts in every directional edge capacity.

The solver is optional. Receipt checking and fibre table enumeration use only
the standard library. No solver timeout or feasible incumbent is a proof of a
minimum. Singleton fibres are removed WLOG: they serve no primitive line.
"""
from __future__ import annotations
import argparse
from collections import Counter
from functools import lru_cache
import hashlib
import json
from math import isqrt
from pathlib import Path
import time


def walsh(values):
    a=list(values)
    step=1
    while step<len(a):
        for start in range(0,len(a),2*step):
            for j in range(start,start+step):
                x,y=a[j],a[j+step]
                a[j],a[j+step]=x+y,x-y
        step*=2
    return a


def profile_from_mask(mask,n):
    N=1<<n
    points=[u for u in range(N) if mask>>u&1]
    p=[0]*N
    for i,u in enumerate(points):
        for w in points[i+1:]:
            p[u^w]+=1
    return (len(points),*p[1:])


def period_mask(row):
    return 1+sum(1<<v for v in range(1,len(row)) if 2*row[v]==row[0])


def common_period_size(sa,sb,v,N):
    A={min(w,w^v) for w in range(N) if sa>>w&1}
    B={min(w,w^v) for w in range(N) if sb>>w&1}
    return len(A&B)


@lru_cache(None)
def exact_fibre_table(n):
    if n>4:
        raise ValueError('Exact local table restricted to n<=4')
    N=1<<n
    return tuple(sorted({profile_from_mask(mask,n) for mask in range(1<<N)}))


def check_assignment(n,s,p,mode='S'):
    """Check all relaxed constraints independently, using Python integers."""
    N=1<<n; H=N//2
    errors=[]
    if len(s)!=N or len(p)!=N or any(len(row)!=N-1 for row in p):
        return ['bad dimensions']
    table=set(exact_fibre_table(n)) if mode in ('E','EP') else None
    for a in range(N):
        sa=s[a]; row=[0,*p[a]]
        if not 0<=sa<=N: errors.append(f'size {a}')
        if sum(row)!=sa*(sa-1)//2: errors.append(f'pair budget {a}')
        if any(not 0<=x<=sa//2 for x in row): errors.append(f'pair cap {a}')
        d=[0]+[sa-2*x for x in row[1:]]
        if any(not 0<=x<=min(sa,N-sa) for x in d): errors.append(f'defect cap {a}')
        if any(d[v^w]>d[v]+d[w] for v in range(N) for w in range(N)):
            errors.append(f'triangle {a}')
        if mode in ('S','S4','E','EP'):
            spec=walsh([sa,*[2*x for x in row[1:]]])
            if spec[0]!=sa*sa: errors.append(f'zero spectrum {a}')
            for chi,z in enumerate(spec[1:],1):
                if z<0 or isqrt(z)**2!=z or isqrt(z)%2!=sa%2 or isqrt(z)>min(sa,N-sa):
                    errors.append(f'spectrum {a} {chi}: {z}')
            if mode=='S4' and n==4 and sa==8:
                support=[chi for chi,z in enumerate(spec) if chi and z]
                if len(support)==4 and all(spec[chi]==16 for chi in support):
                    from functools import reduce
                    from operator import xor
                    if reduce(xor,support): errors.append(f'four-frequency phase {a}')
        if table is not None and (sa,*row[1:]) not in table:
            errors.append(f'nonrealizable autocorrelation {a}')
    for v in range(1,N):
        cover=0
        for a in range(N):
            b=a^v
            if a>=b:continue
            cap=p[a][v-1]*p[b][v-1]
            if mode=='EP':
                j=common_period_size(period_mask((s[a],*p[a])),period_mask((s[b],*p[b])),v,N)
                assert cap%j==0
                cap=min(H,cap//j)
            cover+=cap
        if cover<H: errors.append(f'cover {v}: {cover}')
    return errors


def solve(n,mode='S',seconds=120,workers=2,ub=None,smax=None,exclude=(),log=False):
    from ortools.sat.python import cp_model
    import ortools
    N=1<<n; H=N//2
    md=cp_model.CpModel()
    sizes=[x for x in range(N+1) if x!=1 and (smax is None or x<=smax)]
    s=[md.NewIntVarFromDomain(cp_model.Domain.FromValues(sizes),f's{a}') for a in range(N)]
    p=[[md.NewIntVar(0,H,f'p{a}_{v}') for v in range(1,N)] for a in range(N)]
    st=None
    if mode=='EP':
        subspaces=sorted({period_mask(row) for row in exact_fibre_table(n)})
        st=[md.NewIntVarFromDomain(cp_model.Domain.FromValues(subspaces),'') for _ in range(N)]
    for a in range(N):
        budget=md.NewIntVar(0,N*(N-1)//2,f'b{a}')
        md.AddAllowedAssignments([s[a],budget],[(x,x*(x-1)//2) for x in sizes])
        md.Add(sum(p[a])==budget)
        for v in range(1,N):
            md.Add(2*p[a][v-1]<=s[a])
            md.Add(p[a][v-1]>=s[a]-H)
        for v in range(1,N):
            for w in range(v+1,N):
                md.Add(2*(p[a][v-1]+p[a][w-1]-p[a][(v^w)-1])<=s[a])
        if mode in ('S','S4'):
            squares=[(x,r*r) for x in sizes for r in range(x%2,min(x,N-x)+1,2)]
            spectral_vars=[]
            for chi in range(1,N):
                z=md.NewIntVar(0,N*N,'')
                md.Add(z==s[a]+2*sum((1 if (chi&v).bit_count()%2==0 else -1)*p[a][v-1] for v in range(1,N)))
                md.AddAllowedAssignments([s[a],z],squares)
                spectral_vars.append(z)
            if mode=='S4' and n==4:
                eight=md.NewBoolVar('')
                md.Add(s[a]==8).OnlyEnforceIf(eight)
                md.Add(s[a]!=8).OnlyEnforceIf(eight.Not())
                flat=[];sixteen=[]
                possible=sorted({z for _,z in squares})
                for z in spectral_vars:
                    f=md.NewBoolVar('');e=md.NewBoolVar('')
                    md.AddAllowedAssignments([z,f],[(v,int(v in (0,16))) for v in possible])
                    md.Add(z==16).OnlyEnforceIf(e)
                    md.Add(z!=16).OnlyEnforceIf(e.Not())
                    flat.append(f);sixteen.append(e)
                for bit in range(n):
                    half_count=md.NewIntVar(0,4,'')
                    md.Add(sum(sixteen[chi-1] for chi in range(1,N) if chi>>bit&1)==2*half_count).OnlyEnforceIf([eight,*flat])
        elif mode=='E':
            md.AddAllowedAssignments([s[a],*p[a]],[row for row in exact_fibre_table(n) if row[0] in sizes])
        elif mode=='EP':
            md.AddAllowedAssignments([s[a],*p[a],st[a]],[(*row,period_mask(row)) for row in exact_fibre_table(n) if row[0] in sizes])
    for v in range(1,N):
        ts=[]
        for a in range(N):
            if a<(a^v):
                z=md.NewIntVar(0,H*H,'')
                md.AddMultiplicationEquality(z,[p[a][v-1],p[a^v][v-1]])
                if mode=='EP':
                    j=md.NewIntVar(1,H,'')
                    md.AddAllowedAssignments([st[a],st[a^v],j],[(ha,hb,common_period_size(ha,hb,v,N)) for ha in subspaces for hb in subspaces])
                    div=md.NewIntVar(0,H*H,'')
                    md.AddDivisionEquality(div,z,j)
                    capacity=md.NewIntVar(0,H,'')
                    md.AddMinEquality(capacity,[div,H])
                    ts.append(capacity)
                else:ts.append(z)
        md.Add(sum(ts)>=H)
    # Simultaneous affine coordinate change: size-order an affine flag.
    for a in range(N):
        md.Add(s[0]>=s[a])
        if a: md.Add(s[1]>=s[a])
    for k in range(1,n):
        for a in range(1<<k,N):
            md.Add(s[1<<k]>=s[a])
    if smax is not None: md.Add(s[0]<=smax)
    if exclude:
        counts={}
        for size in sizes:
            equal=[]
            for a in range(N):
                b=md.NewBoolVar('')
                md.Add(s[a]==size).OnlyEnforceIf(b)
                md.Add(s[a]!=size).OnlyEnforceIf(b.Not())
                equal.append(b)
            counts[size]=sum(equal)
        for profile in exclude:
            different=[]
            for size in sizes:
                b=md.NewBoolVar('')
                md.Add(counts[size]!=profile.count(size)).OnlyEnforceIf(b)
                different.append(b)
            md.AddBoolOr(different)
    total=sum(s)
    if ub is not None: md.Add(total<=ub)
    else: md.Minimize(total)
    # Uniform external-direction resource inequality: if h fibres are heavy,
    # at least N-1-C(h,2) directions have no heavy-heavy edge. Each such
    # direction needs ceil((N/2)/floor(s_max/2)) distinct size-two resources.
    heavy=[]
    for x in s:
        b=md.NewBoolVar('')
        md.Add(x>=3).OnlyEnforceIf(b)
        md.Add(x<=2).OnlyEnforceIf(b.Not())
        heavy.append(b)
    hc=md.NewIntVar(0,N,'heavy_count')
    md.Add(hc==sum(heavy))
    allowed=[]
    for maximum in sizes:
        if maximum<2: continue
        q=(H+maximum//2-1)//(maximum//2)
        for h in range(N+1):
            if q*max(0,N-1-h*(h-1)//2)<=N-h:
                allowed.append((maximum,h))
    md.AddAllowedAssignments([s[0],hc],allowed)
    if ub is not None and ub<3*N-2:
        # Uniform few-heavy-fibre theorem, proved in extension/theory.
        md.Add(sum(heavy)>=3)
    # The universal construction provides a valid hint when not excluded.
    if (ub is None or ub>=3*N-2) and (smax is None or smax==N):
        for a in range(N):
            md.AddHint(s[a],N if a==0 else 2)
            for v in range(1,N): md.AddHint(p[a][v-1],H if a==0 else int(v==a))
    sv=cp_model.CpSolver()
    sv.parameters.max_time_in_seconds=seconds
    sv.parameters.num_workers=workers
    sv.parameters.random_seed=1
    sv.parameters.log_search_progress=log
    t=time.perf_counter(); status=sv.Solve(md); elapsed=time.perf_counter()-t
    out={'n':n,'mode':mode,'status':sv.StatusName(status),'seconds':round(elapsed,6),
         'solver':'OR-Tools CP-SAT','solver_version':ortools.__version__,'workers':workers,
         'upper_constraint':ub,'max_fibre_constraint':smax,'objective_bound':sv.BestObjectiveBound() if ub is None else None,
         'certification':'solver verdict; no independently checked UNSAT trace'}
    if status in (cp_model.OPTIMAL,cp_model.FEASIBLE):
        ss=[sv.Value(x) for x in s]; pp=[[sv.Value(x) for x in row] for row in p]
        errors=check_assignment(n,ss,pp,mode)
        if errors: raise AssertionError(errors)
        out.update(value=sum(ss),profile=sorted(ss,reverse=True),sizes=ss,pairs=pp,witness_integer_rechecked=True)
        out['certification']='exported feasible relaxation point; independently checked in exact integers'
    out['search_branches']=sv.NumBranches(); out['conflicts']=sv.NumConflicts()
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('n',type=int)
    ap.add_argument('--mode',choices=['T','S','S4','E','EP'],default='S')
    ap.add_argument('--seconds',type=float,default=120)
    ap.add_argument('--workers',type=int,default=2)
    ap.add_argument('--ub',type=int)
    ap.add_argument('--smax',type=int)
    ap.add_argument('--output',type=Path)
    ap.add_argument('--log',action='store_true')
    args=ap.parse_args()
    out=solve(args.n,args.mode,args.seconds,args.workers,args.ub,args.smax,log=args.log)
    raw=json.dumps(out,indent=2)+'\n'
    if args.output: args.output.write_text(raw)
    print(raw)


if __name__=='__main__': main()
