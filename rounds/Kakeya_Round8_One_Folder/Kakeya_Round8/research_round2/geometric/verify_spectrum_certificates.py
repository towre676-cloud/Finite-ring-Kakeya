"""Independent exact dual-inequality and whole-profile certificate replay.

The producer uses Hungarian assignment. This checker only verifies integer
dual inequalities, then adds the resulting certified capacity bounds.
"""
from pathlib import Path
import hashlib
import json
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OLD=ROOT/'research_external'/'m19'
BANK=ROOT/'frontier_audit_work'/'m19_lagrange'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def M(p,q):
    a,b=sorted((p,q))
    return b+8 if a==3 and b in(5,6,7) else min(16,p*q)

start=time.time()
census=json.loads((HERE/'PAIR_SPECTRUM_CENSUS.json').read_text())
spectra={int(w):sorted(tuple(r['hist']) for r in rs) for w,rs in census['weights'].items()}
for w,rs in census['weights'].items():
    for r in rs:
        pts=[x for x in range(32) if r['mask']>>x&1]
        assert len(pts)==int(w)
        h=[0]*10
        for d in range(1,32):
            p=sum(bool(r['mask']>>(x^d)&1) for x in pts)//2
            h[p]+=1
        assert h==r['hist']

bounds={};dual_count=0;inequality_count=0
for line in (HERE/'SPECTRUM_MATCHING_DUAL_CERTIFICATES.jsonl').read_text().splitlines():
    r=json.loads(line);w=r['weight'];f=r['flag'];ell=r['cutoff'];qs=tuple(r['neighbors'])
    key=(w,f,ell,qs);assert key not in bounds
    eligible={i for i,h in enumerate(spectra[w]) if (h[0]>0 if f==0 else h[0]<31)}
    seen=set();best=-10**9
    for cert in r['spectra']:
        si=cert['index'];assert si in eligible and si not in seen;seen.add(si)
        h=spectra[w][si];ps=[p for p,n in enumerate(h) for _ in range(n)]
        lam=cert['lambda'];mu=cert['mu'];assert len(lam)==len(qs)+1 and len(mu)==31
        assert all(isinstance(x,int) for x in lam+mu) and min(mu)>=0
        val=sum(lam)+sum(mu);assert val==cert['bound']
        for i,q in enumerate(qs):
            for j,p in enumerate(ps):
                assert lam[i]+mu[j]>=2*M(p,q)-ell*p
                inequality_count+=1
        for j,p in enumerate(ps):
            if (p==0 if f==0 else p>=1):
                assert lam[-1]+mu[j]>=-ell*p
                inequality_count+=1
        best=max(best,val);dual_count+=1
    assert seen==eligible
    bound=ell*w*(w-1)//2+best
    assert bound==r['upper_doubled'];bounds[key]=bound

summary={'status':'PASS_EXACT_INTEGER_DUAL_AND_PROFILE_REPLAY','census_sha256':sha(HERE/'PAIR_SPECTRUM_CENSUS.json'),'dual_file_sha256':sha(HERE/'SPECTRUM_MATCHING_DUAL_CERTIFICATES.jsonl'),'local_keys':len(bounds),'spectrum_duals':dual_count,'verified_integer_inequalities':inequality_count,'supports':{}}

for s in(11,12):
    old_quota={json.loads(l)['parent_id'] for l in (OLD/f's{s}_quota_certificates.jsonl').read_text().splitlines()}
    expected=[l for l in (OLD/f's{s}_after_bank.txt').read_text().splitlines() if int(l.split()[0]) not in old_quota]
    source=HERE/f's{s}_remaining_input.txt';actual=source.read_text().splitlines();assert actual==expected
    profiles={}
    for line in actual:
        t=list(map(int,line.split()));pid,z,k=t[:3];assert len(t)==3+3*k;rs=[]
        for f,w,n in zip(t[3::3],t[4::3],t[5::3]):rs +=[(f,w)]*n
        assert rs==sorted(rs) and len(rs)==s-1 and 19+sum(w for f,w in rs)==93
        assert z==31-sum(f for f,w in rs)
        assert pid not in profiles;profiles[pid]=(z,rs,line)
    prior=set()
    for path in(OLD/f's{s}_plain_certificates.jsonl',OLD/f's{s}_heavy_certificates.jsonl',BANK/f'S{s}_PRICE_BANK_CERTIFICATES.jsonl',OLD/f's{s}_quota_certificates.jsonl'):
        ids={json.loads(l)['parent_id'] for l in path.read_text().splitlines()};assert not prior&ids;prior|=ids
    assert not prior&profiles.keys()
    seen=set();gap_min=100000;cuts=[]
    cp=HERE/f'S{s}_SPECTRUM_CANDIDATES.jsonl'
    for line in cp.read_text().splitlines():
        c=json.loads(line);pid=c['parent_id'];assert pid in profiles and pid not in seen;seen.add(pid)
        z,rs,profile_line=profiles[pid];u=sum(f and w<=3 for f,w in rs);D=16*z+7*u+max(0,u-3)
        assert D==c['required_capacity'] and c['support']==s
        ell=c['cutoff'];hs=tuple(sorted(w//2 for f,w in rs if w//2>ell))
        plain=2*sum(M(q,hs[j]) for i,q in enumerate(hs) for j in range(i))
        light=[];loss=[]
        for f,w in rs:
            if w//2<=ell:
                b=bounds[(w,f,ell,hs)];plain+=b;light.append(b)
            else:
                ns=list(hs);ns.remove(w//2);ns=tuple(ns)
                b=bounds[(w,f,0,ns)];assert b%2==0
                loss.append(sum(M(w//2,q) for q in ns)-b//2)
        assert min(loss,default=0)>=0
        correction=2*max(max(loss,default=0),(sum(loss)+1)//2)
        upper=plain-correction;gap=2*D-upper
        assert light==c['light_bounds'] and loss==c['heavy_losses']
        assert plain==c['spectrum_plain_doubled'] and correction==c['heavy_correction_doubled'] and upper==c['upper_doubled']
        assert gap>0;gap_min=min(gap_min,gap)
        c['profile_line']=profile_line;c['gap_doubled']=gap;cuts.append(c)
    out=HERE/f'S{s}_SPECTRUM_VERIFIED_CERTIFICATES.jsonl'
    out.write_text(''.join(json.dumps(c,sort_keys=True,separators=(',',':'))+'\n' for c in cuts))
    summary['supports'][str(s)]={'input_profiles':len(profiles),'input_sha256':sha(source),'new_exclusions':len(cuts),'prior_overlap':0,'remaining':len(profiles)-len(cuts),'minimum_gap_doubled':gap_min,'certificate_sha256':sha(out)}
    print(summary['supports'][str(s)],flush=True)
summary['total_new_exclusions']=sum(r['new_exclusions'] for r in summary['supports'].values())
summary['total_remaining']=sum(r['remaining'] for r in summary['supports'].values())
summary['seconds']=time.time()-start
(HERE/'SPECTRUM_VERIFICATION_RECEIPT.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
