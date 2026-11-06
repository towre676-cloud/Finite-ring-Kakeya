"""Verify the complete distinguished-direction invariant and all integer duals.

Completeness of382 affine representatives is inherited; every representative
and every own direction is recomputed with translated intersections here.
"""
from pathlib import Path
import hashlib
import json
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
RROOT=ROOT/'research_round2/root'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def M(p,q):
    a,b=sorted((p,q))
    return b+8 if a==3 and b in(5,6,7) else min(16,p*q)

start=time.time()
cp=HERE/'PAIRED_BLOCK_MAXIMUM_CENSUS.json';census=json.loads(cp.read_text())
source=ROOT/census['source'];assert sha(source)==census['source_sha256']
shapes=json.loads(source.read_text())['all_support_records'];assert len(shapes)==382
spectra={(int(w),int(f)):sorted(tuple(r['hist']) for r in rs) for w,fs in census['weights'].items() for f,rs in fs.items()}
actual={key:set() for key in spectra};own_cases=0

def invariants(mask,w):
    pts={x for x in range(32) if mask>>x&1};assert len(pts)==w
    # Independent translated-intersection count, not unordered-pair updates.
    p=[len(pts & {x^d for x in pts})//2 for d in range(32)]
    for a in range(1,32):
        blocks={frozenset((d,d^a)) for d in range(1,32) if d!=a}
        assert len(blocks)==15
        hist=[0]*10
        for block in blocks:hist[max(p[d] for d in block)]+=1
        yield a,int(p[a]>0),tuple(hist),p[a]

for shape in shapes:
    w=shape['support_size']
    if not 2<=w<=19:continue
    for a,f,h,p in invariants(shape['mask'],w):actual[w,f].add(h);own_cases+=1
assert all(actual[k]==set(v) for k,v in spectra.items())
for w,fs in census['weights'].items():
    for f,rs in fs.items():
        for r in rs:
            inv={a:(fl,h,p) for a,fl,h,p in invariants(r['mask'],int(w))}
            assert inv[r['own_direction']]==(int(f),tuple(r['hist']),r['own_pairs'])

bounds={};dual_count=0;inequality_count=0
dp=HERE/'PAIRED_BLOCK_MATCHING_DUAL_CERTIFICATES.jsonl'
for line in dp.read_text().splitlines():
    r=json.loads(line);w=r['weight'];f=r['flag'];ell=r['cutoff'];qs=tuple(r['neighbors']);key=(w,f,ell,qs)
    assert key not in bounds and len(qs)<=15
    seen=set();best=-10**9
    for cert in r['spectra']:
        si=cert['index'];assert 0<=si<len(spectra[w,f]) and si not in seen;seen.add(si)
        h=spectra[w,f][si];ps=[p for p,n in enumerate(h) for _ in range(n)]
        lam=cert['lambda'];mu=cert['mu'];assert len(lam)==len(qs) and len(mu)==15
        assert all(isinstance(v,int) for v in lam+mu) and min(mu)>=0
        val=sum(lam)+sum(mu);assert val==cert['bound'] and sum(ps)==cert['mass']
        for i,q in enumerate(qs):
            for j,p in enumerate(ps):
                assert lam[i]+mu[j]>=max(0,2*M(p,q)-ell*p)
                inequality_count+=1
        best=max(best,ell*sum(ps)+val);dual_count+=1
    assert seen==set(range(len(spectra[w,f])))
    assert best==r['upper_doubled'];bounds[key]=best

summary={'status':'PASS_EXACT_BLOCK_CENSUS_AND_INTEGER_DUAL_REPLAY','affine_census_completeness':'inherited frozen382 representatives, all cases re-evaluated','source_census_sha256':sha(source),'block_census_sha256':sha(cp),'distinguished_direction_cases_checked':own_cases,'dual_file_sha256':sha(dp),'local_keys':len(bounds),'spectrum_duals':dual_count,'verified_integer_inequalities':inequality_count,'supports':{}}
for s in(11,12):
    root_cuts={json.loads(l)['parent_id'] for l in (RROOT/f'S{s}_OUTSIDE_SUPPORT_CANDIDATES.jsonl').read_text().splitlines()}
    expected=[l for l in (RROOT/f's{s}_after_spectrum.txt').read_text().splitlines() if int(l.split()[0]) not in root_cuts]
    sourcefile=HERE/f's{s}_after_outside_budget.txt';actual=sourcefile.read_text().splitlines();assert actual==expected
    profiles={}
    for line in actual:
        t=list(map(int,line.split()));pid,z,k=t[:3];assert len(t)==3+3*k;rs=[]
        for f,w,n in zip(t[3::3],t[4::3],t[5::3]):rs +=[(f,w)]*n
        assert rs==sorted(rs) and len(rs)==s-1 and 19+sum(w for f,w in rs)==93
        assert z==31-sum(f for f,w in rs) and pid not in profiles
        profiles[pid]=(rs,line)
    seen=set();gap_min=100000;cuts=[]
    for line in(HERE/f'S{s}_PAIRED_BLOCK_CANDIDATES.jsonl').read_text().splitlines():
        c=json.loads(line);pid=c['parent_id'];assert pid in profiles and pid not in seen;seen.add(pid)
        rs,profile_line=profiles[pid];D=16*(32-s);assert c['required_capacity']==D and c['support']==s
        ell=c['cutoff'];hs=tuple(sorted(w//2 for f,w in rs if w//2>ell))
        plain=2*sum(M(q,hs[j]) for i,q in enumerate(hs) for j in range(i));light=[];loss=[]
        for f,w in rs:
            if w//2<=ell:
                b=bounds[(w,f,ell,hs)];plain+=b;light.append(b)
            else:
                ns=list(hs);ns.remove(w//2);ns=tuple(ns);b=bounds[(w,f,0,ns)];assert b%2==0
                loss.append(sum(M(w//2,q) for q in ns)-b//2)
        assert min(loss,default=0)>=0
        correction=2*max(max(loss,default=0),(sum(loss)+1)//2);upper=plain-correction;gap=2*D-upper
        assert light==c['light_bounds'] and loss==c['heavy_losses']
        assert plain==c['block_plain_doubled'] and correction==c['heavy_correction_doubled'] and upper==c['upper_doubled'] and gap>0
        gap_min=min(gap_min,gap);c['profile_line']=profile_line;c['gap_doubled']=gap;cuts.append(c)
    outfile=HERE/f'S{s}_PAIRED_BLOCK_VERIFIED_CERTIFICATES.jsonl'
    outfile.write_text(''.join(json.dumps(c,sort_keys=True,separators=(',',':'))+'\n' for c in cuts))
    summary['supports'][str(s)]={'input_profiles':len(profiles),'input_sha256':sha(sourcefile),'new_exclusions':len(cuts),'prior_overlap':0,'remaining':len(profiles)-len(cuts),'minimum_gap_doubled':gap_min,'certificate_sha256':sha(outfile)}
    print(summary['supports'][str(s)],flush=True)
summary['total_new_exclusions']=sum(r['new_exclusions'] for r in summary['supports'].values())
summary['total_remaining']=sum(r['remaining'] for r in summary['supports'].values())
summary['seconds']=time.time()-start
(HERE/'PAIRED_BLOCK_VERIFICATION_RECEIPT.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
