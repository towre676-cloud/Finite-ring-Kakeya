"""Exact support-17 M11 reduction using frozen envelopes and assignment duals.

All weight partitions are regenerated.  The Hungarian calculation is only a
certificate producer: the companion verifier checks every integer dual edge
inequality independently.
"""
from pathlib import Path
from collections import Counter
import json, hashlib, sys, time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'research_round2/structural/m11_support'))
from verify_cap11_support import tails, complete_graph_bound, CUTOFFS
from verify_cap11_support_through18 import geometry_certificate

ORBIT_IDS=(367,373,374,376,377)
SOURCE=ROOT/'research_sources/extracted/Kakeya_Reconciled_Proofs_2026-10-27/late_parallel_2214/extracted/m11_directional/inputs/CAP11_STRUCTURAL_REDUCTION.json'

def max_assignment(cost):
    n=len(cost)
    a=[[-x for x in row] for row in cost]
    u=[0]*(n+1);v=[0]*(n+1);p=[0]*(n+1);way=[0]*(n+1)
    for i in range(1,n+1):
        p[0]=i;j0=0;minimum=[10**12]*(n+1);used=[False]*(n+1)
        while True:
            used[j0]=True;i0=p[j0];delta=10**12;j1=0
            for j in range(1,n+1):
                if used[j]:continue
                current=a[i0-1][j-1]-u[i0]-v[j]
                if current<minimum[j]:minimum[j]=current;way[j]=j0
                if minimum[j]<delta:delta=minimum[j];j1=j
            for j in range(n+1):
                if used[j]:u[p[j]]+=delta;v[j]-=delta
                else:minimum[j]-=delta
            j0=j1
            if p[j0]==0:break
        while True:
            j1=way[j0];p[j0]=p[j1];j0=j1
            if j0==0:break
    assignment=[0]*n
    for j in range(1,n+1):assignment[p[j]-1]=j-1
    alpha=[-x for x in u[1:]];beta=[-x for x in v[1:]]
    bound=sum(alpha)+sum(beta)
    assert bound==sum(cost[i][assignment[i]] for i in range(n))
    assert all(alpha[i]+beta[j]>=cost[i][j] for i in range(n) for j in range(n))
    return bound,alpha,beta,assignment

def nine_heavy_strict(weights):
    low=weights[9:]
    pairmass=sum(w*(w-1)//2 for w in low)
    crossmass=sum(w*w//4 for w in low)
    # Missing set has >=3 directions. P<=15 forces exactly3, which are
    # linearly independent and hence lie in one character halfspace.
    return pairmass<=15 and crossmass<12

def run():
    start=time.monotonic()
    records={r['orbit']:r for r in json.loads(SOURCE.read_text())['records']}
    basic=Counter();remaining=[];geometry=[]
    for tail in tails(16,82,11):
        weights=(11,)+tail;basic['total']+=1
        for cutoff in CUTOFFS:
            if complete_graph_bound(weights,cutoff)<992:
                basic['resource']+=1;break
        else:
            cert=geometry_certificate(weights)
            if cert is not None:basic['inherited_geometry']+=1;geometry.append(cert)
            else:remaining.append(weights)
    assert len(remaining)==110
    output=[];summaries=[]
    for orbit in ORBIT_IDS:
        record=records[orbit];support=record['support'];stats=Counter();survivors=[]
        for weights in remaining:
            cost=[[int(record['local_upper_envelopes'][str(a)][str(w)])
                   if w>=record['minimum_weights'][str(a)] else -100000
                   for w in weights] for a in support]
            bound,alpha,beta,assignment=max_assignment(cost)
            cert=dict(orbit=orbit,weights=weights,maximum_energy=bound,
                      row_dual=alpha,column_dual=beta,assignment=assignment)
            if bound<992:cert['method']='EXACT_ASSIGNMENT_ENVELOPE';stats['envelope']+=1
            elif nine_heavy_strict(weights):
                cert['method']='NINE_HEAVY_INDEPENDENT_MISSING_DIRECTIONS';stats['nine_heavy_geometry']+=1
                cert['low_pair_mass']=sum(w*(w-1)//2 for w in weights[9:])
                cert['low_halfspace_mass']=sum(w*w//4 for w in weights[9:])
            else:cert['method']='UNRESOLVED_PROFILE';stats['unresolved']+=1;survivors.append(weights)
            output.append(cert)
        summaries.append(dict(orbit=orbit,support_size=17,**stats,
                              status='CLOSED' if not survivors else 'OPEN',surviving_weight_profiles=survivors))
    result=dict(status='PASS_EXACT_REDUCTION',scope='n5,both rings,W<=93,exactmax11,support17',
                global_partition_counts=dict(basic),residual_profiles_before_local_envelopes=len(remaining),
                records=summaries,source=dict(path=str(SOURCE.relative_to(ROOT)),
                sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest()),
                seconds=time.monotonic()-start,
                full_spectra_used_in_claimed_exclusions=False)
    (HERE/'S17_ASSIGNMENT_DUAL_CERTIFICATES.json').write_text(json.dumps(output,indent=2)+'\n')
    (HERE/'S17_SUPPORT_REDUCTION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':run()
