"""Exact integer-dual replay of the hub-inclusive common-spectrum layer."""
from pathlib import Path
import hashlib
import json
import time

HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def M(p,q):
    a,b=sorted((p,q))
    return b+8 if a==3 and b in(5,6,7) else min(16,p*q)

start=time.time()
cp=HERE/'PAIR_SPECTRUM_CENSUS.json';census=json.loads(cp.read_text())
spectra={int(w):sorted(tuple(r['hist']) for r in rs) for w,rs in census['weights'].items()}
bounds={};dual_count=0;inequality_count=0
dp=HERE/'HUB_COUPLED_MATCHING_DUAL_CERTIFICATES.jsonl'
for line in dp.read_text().splitlines():
    r=json.loads(line);w=r['weight'];f=r['flag'];ell=r['cutoff'];qs=tuple(r['neighbors']);key=(w,f,ell,qs)
    assert key not in bounds and f in(-1,0,1)
    eligible={i for i,h in enumerate(spectra[w]) if f==-1 or (h[0]>0 if f==0 else h[0]<31)}
    seen=set();best=-10**9
    for cert in r['spectra']:
        si=cert['index'];assert si in eligible and si not in seen;seen.add(si)
        h=spectra[w][si];ps=[p for p,n in enumerate(h) for _ in range(n)]
        lam=cert['lambda'];mu=cert['mu'];assert len(lam)==len(qs)+(f>=0) and len(mu)==31
        assert all(isinstance(x,int) for x in lam+mu) and min(mu)>=0
        val=sum(lam)+sum(mu);assert val==cert['bound']
        for i,q in enumerate(qs):
            for j,p in enumerate(ps):
                assert lam[i]+mu[j]>=2*M(p,q)-ell*p
                inequality_count+=1
        if f>=0:
            for j,p in enumerate(ps):
                if (p==0 if f==0 else p>=1):
                    assert lam[-1]+mu[j]>=2*M(p,9)-ell*p
                    inequality_count+=1
        best=max(best,val);dual_count+=1
    assert seen==eligible
    bound=ell*w*(w-1)//2+best;assert bound==r['upper_doubled'];bounds[key]=bound

summary={'status':'PASS_EXACT_INTEGER_HUB_DUAL_AND_PROFILE_REPLAY','census_sha256':sha(cp),'dual_file_sha256':sha(dp),'local_keys':len(bounds),'spectrum_duals':dual_count,'verified_integer_inequalities':inequality_count,'supports':{}}
for s in(11,12):
    block_cuts={json.loads(l)['parent_id'] for l in(HERE/f'S{s}_PAIRED_BLOCK_VERIFIED_CERTIFICATES.jsonl').read_text().splitlines()}
    expected=[l for l in(HERE/f's{s}_after_outside_budget.txt').read_text().splitlines() if int(l.split()[0]) not in block_cuts]
    source=HERE/f's{s}_after_paired_blocks.txt';actual=source.read_text().splitlines();assert actual==expected
    profiles={}
    for line in actual:
        t=list(map(int,line.split()));pid,z,k=t[:3];assert len(t)==3+3*k;rs=[]
        for f,w,n in zip(t[3::3],t[4::3],t[5::3]):rs +=[(f,w)]*n
        assert rs==sorted(rs) and len(rs)==s-1 and 19+sum(w for f,w in rs)==93
        assert z==31-sum(f for f,w in rs) and pid not in profiles
        profiles[pid]=(rs,line)
    seen=set();gap_min=100000;cuts=[]
    for line in(HERE/f'S{s}_HUB_COUPLED_CANDIDATES.jsonl').read_text().splitlines():
        c=json.loads(line);pid=c['parent_id'];assert pid in profiles and pid not in seen;seen.add(pid)
        rs,profile_line=profiles[pid];assert c['required_capacity']==496 and c['support']==s
        ell=c['cutoff'];assert 0<=ell<=8
        hs=tuple(sorted(w//2 for f,w in rs if w//2>ell))
        hubns=tuple(sorted(w//2 for f,w in rs if f and w//2>ell))
        hubbase=sum(M(9,q) for q in hubns)
        plain=2*hubbase+2*sum(M(q,hs[j]) for i,q in enumerate(hs) for j in range(i));light=[];loss=[]
        for f,w in rs:
            if w//2<=ell:
                b=bounds[(w,f,ell,hs)];plain+=b;light.append(b)
            else:
                ns=list(hs);ns.remove(w//2);ns=tuple(ns);b=bounds[(w,f,0,ns)];assert b%2==0
                loss.append(f*M(w//2,9)+sum(M(w//2,q) for q in ns)-b//2)
        hb=bounds[(19,-1,0,hubns)];assert hb%2==0;loss.append(hubbase-hb//2)
        assert min(loss,default=0)>=0
        correction=2*max(max(loss,default=0),(sum(loss)+1)//2);upper=plain-correction;gap=992-upper
        assert light==c['light_bounds'] and loss==c['heavy_losses']
        assert plain==c['hub_plain_doubled'] and correction==c['heavy_correction_doubled'] and upper==c['upper_doubled'] and gap>0
        gap_min=min(gap_min,gap);c['profile_line']=profile_line;c['gap_doubled']=gap;cuts.append(c)
    outfile=HERE/f'S{s}_HUB_COUPLED_VERIFIED_CERTIFICATES.jsonl'
    outfile.write_text(''.join(json.dumps(c,sort_keys=True,separators=(',',':'))+'\n' for c in cuts))
    remaining=[line for line in actual if int(line.split()[0]) not in seen]
    (HERE/f's{s}_after_hub_coupling.txt').write_text('\n'.join(remaining)+'\n')
    summary['supports'][str(s)]={'input_profiles':len(profiles),'input_sha256':sha(source),'new_exclusions':len(cuts),'prior_overlap':0,'remaining':len(remaining),'minimum_gap_doubled':gap_min,'certificate_sha256':sha(outfile)}
    print(summary['supports'][str(s)],flush=True)
summary['total_new_exclusions']=sum(r['new_exclusions'] for r in summary['supports'].values())
summary['total_remaining']=sum(r['remaining'] for r in summary['supports'].values())
summary['seconds']=time.time()-start
(HERE/'HUB_COUPLED_VERIFICATION_RECEIPT.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
