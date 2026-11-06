"""Exact dual checks for local degree-capped block matchings and degree placements."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def M(p,q):
    a,b=sorted((p,q))
    return b+8 if a==3 and b in(5,6,7) else min(16,p*q)

start=time.time()
bcpath=HERE/'PAIRED_BLOCK_MAXIMUM_CENSUS.json';bc=json.loads(bcpath.read_text())
spectra={(int(w),int(f)):sorted(tuple(r['hist']) for r in rs) for w,fs in bc['weights'].items() for f,rs in fs.items()}
patternpath=HERE/'OUTSIDE_SUPPORT_DEGREE_PATTERNS.json';pattern_data=json.loads(patternpath.read_text())
patterns={int(s):[tuple(r['degrees']) for r in entry['degree_patterns']] for s,entry in pattern_data.items()}
manifest=json.loads((HERE/'DEGREE_CENSUS_SOURCE_MANIFEST.json').read_text())
source=ROOT/manifest['source_path'];assert sha(source)==manifest['source_sha256']
shapes=json.loads(source.read_text())['all_support_records']
for s in(11,12):
    counter=Counter();cases=0
    for r in shapes:
        if r['support_size']!=s:continue
        S=set(r['support'])
        if {x^y for x in S for y in S}!=set(range(32)):continue
        for hub in S:
            T={x^hub for x in S};vs=T-{0};ds=tuple(sorted(sum((a^b)not in T for b in vs if b!=a) for a in vs))
            counter[ds]+=1;cases+=1
    assert cases==pattern_data[str(s)]['hub_marked_cases']
    assert counter==Counter({tuple(r['degrees']):r['multiplicity'] for r in pattern_data[str(s)]['degree_patterns']})

bounds={};dual_count=0;inequality_count=0
dp=HERE/'DEGREE_BLOCK_MATCHING_DUAL_CERTIFICATES.jsonl'
for line in dp.read_text().splitlines():
    r=json.loads(line);w=r['weight'];f=r['flag'];degree=r['degree'];qs=tuple(r['neighbors']);key=(w,f,degree,qs)
    assert key not in bounds and 0<=degree<=len(qs)
    dummy=len(qs)-degree;seen=set();best=-10**9
    for cert in r['spectra']:
        si=cert['index'];assert 0<=si<len(spectra[w,f]) and si not in seen;seen.add(si)
        h=spectra[w,f][si];ps=[p for p,n in enumerate(h) for _ in range(n)]
        lam=cert['lambda'];mu=cert['mu'];assert len(lam)==len(qs) and len(mu)==15+dummy
        assert all(isinstance(v,int) for v in lam+mu) and min(mu)>=0
        val=sum(lam)+sum(mu);assert val==cert['bound']
        for i,q in enumerate(qs):
            for j,p in enumerate(ps):
                assert lam[i]+mu[j]>=M(p,q);inequality_count+=1
            for j in range(15,15+dummy):
                assert lam[i]+mu[j]>=1000;inequality_count+=1
        best=max(best,val-1000*dummy);dual_count+=1
    assert seen==set(range(len(spectra[w,f])))
    assert best==r['incident_upper'];bounds[key]=best

summary={'status':'PASS_EXACT_DEGREE_BLOCK_AND_ASSIGNMENT_DUAL_REPLAY','block_census_sha256':sha(bcpath),'degree_patterns_sha256':sha(patternpath),'degree_census_completeness':'frozen382 representatives; root normalized-support audit separately','dual_file_sha256':sha(dp),'local_keys':len(bounds),'block_spectrum_duals':dual_count,'verified_local_integer_inequalities':inequality_count,'supports':{}}
pattern_duals=0;pattern_inequalities=0
for s in(11,12):
    hub_cuts={json.loads(l)['parent_id'] for l in(HERE/f'S{s}_HUB_COUPLED_VERIFIED_CERTIFICATES.jsonl').read_text().splitlines()}
    expected=[l for l in(HERE/f's{s}_after_paired_blocks.txt').read_text().splitlines() if int(l.split()[0]) not in hub_cuts]
    sourcefile=HERE/f's{s}_after_hub_coupling.txt';actual=sourcefile.read_text().splitlines();assert actual==expected
    profiles={}
    for line in actual:
        t=list(map(int,line.split()));pid,z,k=t[:3];assert len(t)==3+3*k;rs=[]
        for f,w,n in zip(t[3::3],t[4::3],t[5::3]):rs +=[(f,w)]*n
        assert rs==sorted(rs) and len(rs)==s-1 and 19+sum(w for f,w in rs)==93
        assert z==31-sum(f for f,w in rs) and pid not in profiles;profiles[pid]=(rs,line)
    seen=set();gap_min=None;cuts=[]
    for line in(HERE/f'S{s}_DEGREE_BLOCK_CANDIDATES.jsonl').read_text().splitlines():
        c=json.loads(line);pid=c['parent_id'];assert pid in profiles and pid not in seen;seen.add(pid)
        rs,profile_line=profiles[pid];n=len(rs);need=32*(32-s);assert c['required_doubled']==need and c['support']==s
        caps=sorted(w//2 for f,w in rs);special=[f==0 or w<=3 for f,w in rs];nspecial=sum(special);local=[]
        for f,w in rs:
            qs=caps.copy();qs.remove(w//2);qs=tuple(qs)
            local.append({d:bounds[(w,f,d,qs)] for d in range((s-2)%2,s-1,2)})
        pats=c['patterns'];assert len(pats)==len(patterns[s]);worst=-10**9
        for j,pat in enumerate(pats):
            assert pat['index']==j;degrees=patterns[s][j];places=sum(d<n-1 for d in degrees)
            if places<nspecial:
                assert pat['bound']==-1 and pat['lambda']==pat['mu']==[];continue
            lam=pat['lambda'];mu=pat['mu'];assert len(lam)==len(mu)==n and min(mu)>=0
            assert all(isinstance(v,int) for v in lam+mu)
            val=sum(lam)+sum(mu);assert val==pat['bound']
            for i in range(n):
                for k,d in enumerate(degrees):
                    if special[i] and d==n-1:continue
                    assert lam[i]+mu[k]>=local[i][d];pattern_inequalities+=1
            worst=max(worst,val);pattern_duals+=1
        assert worst==c['upper_doubled'] and worst<need
        gap=need-worst;gap_min=gap if gap_min is None else min(gap_min,gap)
        c['profile_line']=profile_line;c['gap_doubled']=gap;cuts.append(c)
    outfile=HERE/f'S{s}_DEGREE_BLOCK_VERIFIED_CERTIFICATES.jsonl'
    outfile.write_text(''.join(json.dumps(c,sort_keys=True,separators=(',',':'))+'\n' for c in cuts))
    remaining=[line for line in actual if int(line.split()[0]) not in seen]
    (HERE/f's{s}_final_round2_survivors.txt').write_text('\n'.join(remaining)+'\n')
    summary['supports'][str(s)]={'input_profiles':len(profiles),'input_sha256':sha(sourcefile),'new_exclusions':len(cuts),'prior_overlap':0,'remaining':len(remaining),'minimum_gap_doubled':gap_min,'certificate_sha256':sha(outfile)}
summary['pattern_assignment_duals']=pattern_duals;summary['verified_pattern_integer_inequalities']=pattern_inequalities
summary['total_new_exclusions']=sum(r['new_exclusions'] for r in summary['supports'].values());summary['total_remaining']=sum(r['remaining'] for r in summary['supports'].values());summary['seconds']=time.time()-start
(HERE/'DEGREE_BLOCK_VERIFICATION_RECEIPT.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
