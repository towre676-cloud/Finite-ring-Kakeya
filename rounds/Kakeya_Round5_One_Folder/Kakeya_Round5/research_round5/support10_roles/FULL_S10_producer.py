"""Standalone bounded-weight universe: no prior profile-screen inputs."""
from collections import Counter
from itertools import combinations
from pathlib import Path
from hashlib import sha256
import json
import time

HERE=Path(__file__).resolve().parent

def partitions(n,total,cap,prefix=()):
    if not n:
        if total==0:yield prefix
        return
    lo=max(2,(total+n-1)//n)
    for x in range(min(cap,total-2*(n-1)),lo-1,-1):
        yield from partitions(n-1,total-x,x,prefix+(x,))

def required(w):
    return 2 if w>=16 else 4 if w>=8 else 8 if w>=4 else 16

def cube_resources():
    one=[-1]*9
    for mask in range(256):
        vertices=[x for x in range(8) if mask>>x&1]
        edges=sum((a^b) in (1,2,4) for a,b in combinations(vertices,2))
        one[len(vertices)]=max(one[len(vertices)],edges)
    table=[0]
    for _ in range(4):
        new=[-1]*(len(table)+8)
        for n,old in enumerate(table):
            for k,e in enumerate(one):new[n+k]=max(new[n+k],old+e)
        table=new
    return one,table

def test(weights,centers,E):
    rest=list(weights)
    for w in centers:rest.remove(w)
    local=tuple(map(required,centers));total=sum(map(required,weights))
    if rest[-1]//2<max(local):return False,False
    if rest[-1]**2//4<sum(local):return False,False
    placed=centers+tuple(rest)
    for i,w in enumerate(centers):
        if total-required(w)>w*w//4:return False,False
        if max(required(x) for j,x in enumerate(placed) if i!=j)>w//2:return False,False
    return True, all(E[w]>=sum(local) for w in rest)

def main():
    start=time.monotonic();one,E=cube_resources()
    counts=Counter();bare=[];final=[];digest=sha256();cases=0
    for weights in partitions(10,93,18):
        counts[weights[0]]+=1
        digest.update((' '.join(map(str,weights))+'\n').encode())
        bare_roles=[];final_roles=[]
        for central in sorted({tuple(weights[i] for i in ii) for ii in combinations(range(10),3)}):
            cases+=1;ok,strong=test(weights,central,E)
            if ok:bare_roles.append(central)
            if strong:final_roles.append(central)
        if bare_roles:bare.append({'weights':weights,'allowed_central_triplets':bare_roles})
        if final_roles:final.append({'weights':weights,'allowed_central_triplets':final_roles})
    assert sum(counts.values())==102842 and sum(v for m,v in counts.items() if m>=12)==102620
    assert len(bare)==174 and len(final)==11
    (HERE/'FULL_S10_BARE_ROLE_SURVIVORS.json').write_text(json.dumps(bare,indent=2)+'\n')
    (HERE/'FULL_SUPPORT10_ROLE_SURVIVORS.json').write_text(json.dumps(final,indent=2)+'\n')
    report={'status':'PASS_FULL_SUPPORT10_UNIVERSE_PRODUCER',
            'total_weight':93,'support':10,'minimum_weight':2,'maximum_weight':18,
            'all_profiles':102842,'middle_profiles_maximum_12_to_18':102620,
            'maximum_at_most_11_profiles':222,'bare_role_survivors':174,
            'cube_role_survivors':11,'distinct_role_cases':cases,
            'by_maximum':dict(sorted(counts.items())),
            'one_cube_edge_resources':one,'four_cube_edge_resources':E,
            'complete_universe_sha256':digest.hexdigest(),
            'scope':'Independent partition generation; no Round4 or Round5 prior survivor list used. The11 remaining profiles require the separate rigidity theorem.',
            'seconds':round(time.monotonic()-start,3)}
    (HERE/'FULL_S10_PRODUCER_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
