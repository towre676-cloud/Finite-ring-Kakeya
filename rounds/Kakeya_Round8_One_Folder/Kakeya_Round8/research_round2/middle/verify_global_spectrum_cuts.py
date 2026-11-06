"""Verify exact dual certificates, then all new global weight-profile cuts.
No Hungarian algorithm or floating point is used by this checker.
"""
from pathlib import Path
from collections import Counter
import hashlib,json,time
HERE=Path(__file__).resolve().parent
GEO=HERE.parent/'geometric'
M=lambda p,q: max(p,q)+8 if min(p,q)==3 and max(p,q) in (5,6,7) else min(16,p*q)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
start=time.monotonic()
census=json.loads((GEO/'PAIR_SPECTRUM_CENSUS.json').read_text())
spectra={int(w):sorted(tuple(r['hist']) for r in rs) for w,rs in census['weights'].items()}
expanded={w:[tuple(p for p,n in enumerate(h) for _ in range(n)) for h in hs] for w,hs in spectra.items()}
for w,hs in spectra.items():
    for h in hs:assert sum(h)==31 and sum(p*n for p,n in enumerate(h))==w*(w-1)//2
bounds={};dualcount=0;ineq=0
for line in (HERE/'GLOBAL_SPECTRUM_DUAL_CERTIFICATES.jsonl').open():
    r=json.loads(line);w,flag,ell=r['weight'],r['flag'],r['cutoff'];qs=tuple(r['neighbors'])
    assert flag==-1 and tuple(sorted(qs))==qs
    key=(w,ell,qs);assert key not in bounds
    assert len(r['spectra'])==len(spectra[w])
    seen=set();best=-10**9
    for c in r['spectra']:
        si=c['index'];assert 0<=si<len(spectra[w]) and si not in seen;seen.add(si)
        ps=expanded[w][si];lam=c['lambda'];mu=c['mu']
        assert len(lam)==len(qs) and len(mu)==31
        assert all(type(a) is int for a in lam+mu) and min(mu)>=0
        obj=sum(lam)+sum(mu);assert obj==c['bound']
        for i,q in enumerate(qs):
            scores=[2*M(p,q)-ell*p for p in range(10)]
            a=lam[i]
            assert all(a+b>=scores[p] for b,p in zip(mu,ps))
            ineq+=31
        best=max(best,obj);dualcount+=1
    b=ell*w*(w-1)//2+best
    assert b==r['upper_doubled'];bounds[key]=b
print(json.dumps({'dual_stage':'PASS','keys':len(bounds),'duals':dualcount,'inequalities':ineq,'seconds':time.monotonic()-start}),flush=True)

previous={}
for fn in ('global_survivors_19_25.txt','global_survivors_15_18.txt'):
    for line in (HERE/fn).open():
        vals=list(map(int,line.split()));s,m,old=vals[:3];weights=tuple(vals[3:])
        assert len(weights)==s and sum(weights)==93 and weights[0]==m and weights==tuple(sorted(weights,reverse=True))
        assert weights not in previous;previous[weights]=old
seen=set();by=Counter();minimum_gap=100000;verified=[]
for line in (HERE/'GLOBAL_SPECTRUM_CANDIDATES.jsonl').open():
    r=json.loads(line);weights=tuple(r['weights']);ell=r['cutoff']
    assert weights in previous and weights not in seen;seen.add(weights)
    assert previous[weights]==r['old_bound']>=992
    assert len(weights)==r['support'] and weights[0]==r['maximum'] and 12<=weights[0]<=18
    hs=tuple(sorted(w//2 for w in weights if w//2>ell))
    plain=2*sum(M(a,b) for i,a in enumerate(hs) for b in hs[:i]);loss=[];light=[]
    for w in weights:
        if w//2<=ell:
            b=bounds[w,ell,hs];plain+=b;light.append(b)
        else:
            ns=list(hs);ns.remove(w//2);ns=tuple(ns)
            b=bounds[w,0,ns];assert b%2==0
            loss.append(sum(M(w//2,q) for q in ns)-b//2)
    assert min(loss,default=0)>=0
    correction=2*max(max(loss,default=0),(sum(loss)+1)//2)
    upper=plain-correction
    assert plain==r['plain_doubled'] and correction==r['correction_doubled'] and upper==r['upper_doubled']<992
    assert light==r['light_bounds'] and loss==r['heavy_losses']
    by[r['support'],r['maximum']]+=1;minimum_gap=min(minimum_gap,992-upper);verified.append(r)
result={'status':'PASS','new_whole_weight_multiset_exclusions':len(seen),'by_support_and_maximum':[{'support':s,'maximum':m,'cuts':v} for (s,m),v in sorted(by.items())],'local_matching_keys':len(bounds),'spectrum_duals':dualcount,'verified_integer_inequalities':ineq,'minimum_gap_doubled':minimum_gap,'dependencies':{'pair_spectrum_census_sha256':sha(GEO/'PAIR_SPECTRUM_CENSUS.json'),'dual_sha256':sha(HERE/'GLOBAL_SPECTRUM_DUAL_CERTIFICATES.jsonl'),'candidates_sha256':sha(HERE/'GLOBAL_SPECTRUM_CANDIDATES.jsonl')},'seconds':time.monotonic()-start,'scope':'New cuts relative to this round global quota screen; not counts from the old M19 census and not whole maximum-fibre closures.'}
(HERE/'GLOBAL_SPECTRUM_INDEPENDENT_REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2),flush=True)
