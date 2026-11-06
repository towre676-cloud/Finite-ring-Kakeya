from pathlib import Path
from collections import Counter
import hashlib,json
HERE=Path(__file__).resolve().parent
def M(p,q):
    a,b=sorted((p,q));return b+8 if a==3 and b in(5,6,7) else min(16,p*q)
def R(w,p,q,t):return 4*(w*(w-1)//2-t)+2*M(p,9)+2*M(q,6)-4*(p+q)
bound8=max(R(8,0,q,t) for q in range(5) for t in range(5));assert bound8==128
bound3=max(R(3,1,q,t) for q in range(2) for t in range(2) if q<=t);assert bound3==30
assert 7*bound8+2*bound3==956<960
summary={'status':'PASS_ANALYTIC_DELETED_DIRECTION_PROFILE','proof_uses_census':False,'bounds':{'own_zero_weight8':128,'own_positive_weight3':30,'total_doubled':956,'required_doubled':960},'supports':{}}
for s in(11,12):
    infile=HERE/f's{s}_after_common_shapes.txt';lines=infile.read_text().splitlines();profiles={int(l.split()[0]):l for l in lines}
    candfile=HERE/f'S{s}_TWO_HEAVY_OWN_CANDIDATES.jsonl';rows=[json.loads(l) for l in candfile.read_text().splitlines()]
    assert len(rows)==(1 if s==11 else 0)
    if rows:
        c=rows[0];assert c['parent_id']==63342 and profiles[63342]==c['profile_line'];t=list(map(int,c['profile_line'].split()))
        types=Counter({(f,w):n for f,w,n in zip(t[3::3],t[4::3],t[5::3])});assert types==Counter({(0,8):7,(1,3):2,(1,12):1})
        assert c['second_heavy_weight']==12 and c['second_heavy_flag']==1 and c['cutoff']==4 and c['upper_doubled']==956 and c['required_doubled']==960
    cutids={r['parent_id'] for r in rows};expected=''.join(l+'\n' for l in lines if int(l.split()[0]) not in cutids)
    outfile=HERE/f's{s}_after_two_heavy_own.txt';assert outfile.read_text()==expected
    summary['supports'][str(s)]={'input_profiles':len(lines),'new_exclusions':len(rows),'remaining_profiles':len(lines)-len(rows),'input_sha256':hashlib.sha256(infile.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(candfile.read_bytes()).hexdigest(),'survivors_sha256':hashlib.sha256(outfile.read_bytes()).hexdigest()}
summary['total_remaining_profiles']=sum(r['remaining_profiles'] for r in summary['supports'].values())
(HERE/'DELETED_DIRECTION_PROFILE_VERIFICATION.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
