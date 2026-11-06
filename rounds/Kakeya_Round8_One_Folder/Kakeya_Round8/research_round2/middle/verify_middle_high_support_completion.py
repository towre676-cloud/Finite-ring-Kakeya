"""Complete n5 cap12..18, support>=19 reduction, standard-library only.
Run verify_global_spectrum_cuts.py first; its exact certificates are hash-bound.
"""
from pathlib import Path
import json,hashlib,time
from collections import Counter
from verify_global_support_reductions import partitions,bound
HERE=Path(__file__).resolve().parent
start=time.monotonic()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt=json.loads((HERE/'GLOBAL_SPECTRUM_INDEPENDENT_REPLAY.json').read_text())
assert receipt['status']=='PASS'
assert receipt['dependencies']['candidates_sha256']==sha(HERE/'GLOBAL_SPECTRUM_CANDIDATES.jsonl')
assert receipt['dependencies']['dual_sha256']==sha(HERE/'GLOBAL_SPECTRUM_DUAL_CERTIFICATES.jsonl')
spec={tuple(r['weights']):r for r in map(json.loads,(HERE/'GLOBAL_SPECTRUM_CANDIDATES.jsonl').read_text().splitlines())}
assert len(spec)==receipt['new_whole_weight_multiset_exclusions']
previous={}
for line in (HERE/'global_survivors_19_25.txt').open():
    nums=list(map(int,line.split()));s,m,b=nums[:3];w=tuple(nums[3:])
    if m>=12:previous[w]=b

missing_lower={8:6,9:3}
def geometry(w):
    # L1: all light fibres have at most3 points.
    heavy=[v//2 for v in w if v>=4];light=[v for v in w if v<=3]
    if len(heavy) in missing_lower:
        k=missing_lower[len(heavy)];B=sum(v*(v-1)//2 for v in light)
        t=next((i for i in range(1,len(heavy)+1) if sum(heavy[:i])>=16),None)
        if t and k*t>B:
            return dict(method='missing_directions_light_ports',heavy_count=len(heavy),missing_lower=k,ports_per_direction=t,light_budget=B,required=k*t)
    # L2: at most one cap6 heavy, all others cap<=4, light caps<=3.
    for threshold in (6,7,8):
        hh=[v//2 for v in w if v>=threshold];ll=[v for v in w if v<threshold]
        if len(hh) not in missing_lower or not hh or hh[0]!=6 or any(c>4 for c in hh[1:]) or any(v//2>3 for v in ll):continue
        k=missing_lower[len(hh)];B=sum(v*(v-1)//2 for v in ll);b=sum(v>=4 for v in ll)
        if B<4*k-b:
            return dict(method='unique_cap6_hub_savings',heavy_weight_threshold=threshold,heavy_count=len(hh),missing_lower=k,light_budget=B,possible_saving_directions=b,required=4*k-b)
    A=(12,)+(8,)*6+(6,6,3)+(2,)*9
    B=(12,)+(8,)*6+(6,5,4)+(2,)*9
    if w==A:return dict(method='three_missing_directions_triangle_obstruction',heavy_count=9,missing_lower=3,required_light_mass=12,restricted_light_mass_upper=11)
    if w==B:return dict(method='six_missing_directions_halfspace_obstruction',heavy_count=8,missing_forced=6,required_light_mass=22,restricted_light_mass_upper=19)
    raise AssertionError(('UNRESOLVED',w))

counts=Counter();methodcounts=Counter();boundary=[];freshsurv={};digest=hashlib.sha256()
for s in range(32,18,-1):
    for w in partitions(s,93,18):
        m=w[0]
        if m<12:continue
        counts[s,m]+=1;digest.update((' '.join(map(str,w))+'\n').encode())
        for ell in (2,3,1,4,0,5,6,7,8,9):
            upper=bound(w,ell)
            if upper<992:break
        else:
            freshsurv[w]=upper
            if w in spec:
                assert spec[w]['upper_doubled']<992
                cert={'method':'exact_spectrum_matching','upper_doubled':spec[w]['upper_doubled'],'cutoff':spec[w]['cutoff']}
            else:cert=geometry(w)
            methodcounts[cert['method']]+=1
            boundary.append(dict(weights=w,support=s,maximum=m,certificate=cert))
            continue
        methodcounts['global_pair_mass_and_maximum_direction_quota']+=1
    print(json.dumps({'support_finished':s,'boundary_seen':len(boundary),'seconds':time.monotonic()-start}),flush=True)
assert freshsurv.keys()==previous.keys() and len(freshsurv)==55
# The scan source's old bound is its best bound, while this verifier retains
# the last cutoff in a nonexcluded profile, so only the survivor set is compared.
result={'status':'PASS_COMPLETE_MIDDLE_MAXIMA_SUPPORT_REDUCTION','theorem':'In either target ring, no Kakeya set of size<=93 with exact maximum fibre12..18 has pair-active support>=19.','normalized_mass':93,'total_weight_partitions':sum(counts.values()),'partition_stream_sha256':digest.hexdigest(),'by_support_and_maximum':[{'support':s,'maximum':m,'partitions':v} for (s,m),v in sorted(counts.items())],'method_counts':dict(methodcounts),'boundary_profiles':boundary,'remaining_boundary_profiles':0,'dependencies':{'spectrum_replay_sha256':sha(HERE/'GLOBAL_SPECTRUM_INDEPENDENT_REPLAY.json'),'spectrum_duals_sha256':sha(HERE/'GLOBAL_SPECTRUM_DUAL_CERTIFICATES.jsonl'),'analytic_geometric_proof_sha256':sha(HERE/'DIFFERENCE_AND_LIGHT_RESOURCE_LEMMAS.md')},'seconds':time.monotonic()-start,'scope':'Support>=19 only. Every exact maximum12..18 remains open on support<=18.'}
(HERE/'MIDDLE_MAXIMA_SUPPORT_COMPLETION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'partitions':result['total_weight_partitions'],'methods':result['method_counts'],'remaining':0,'seconds':result['seconds']}),flush=True)
