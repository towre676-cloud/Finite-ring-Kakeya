"""Exact verification of rank-mode censuses, matching duals, and all profile branches."""
from pathlib import Path
from itertools import combinations,product
from collections import Counter
import hashlib,json,time

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];OLD=ROOT/'research_round2/geometric'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def M(p,q):
    a,b=sorted((p,q));return b+8 if a==3 and b in(5,6,7) else min(16,p*q)
def cap(p,q,low,partnerlow):return min(M(p,q),8) if low and partnerlow else M(p,q)
def lowhist(w,h):return (w==6 and h[2]==6 and h[3]==1) or (w==7 and h[3]==7) or (w==8 and h[4]==7)
def normalize_ns(ns,mode):return tuple(sorted(((q,low if mode==1 else 0) for q,low in ns),key=lambda x:(x[1],x[0])))

start=time.time();oldmanifest=json.loads((OLD/'M19_ROUND2_FINAL_MANIFEST.json').read_text());assert oldmanifest['status']=='ROOT_VERIFIED'
fullpath=OLD/'PAIR_SPECTRUM_CENSUS.json';blockpath=OLD/'PAIRED_BLOCK_MAXIMUM_CENSUS.json'
assert sha(fullpath)==oldmanifest['complete_censuses']['full_pair_spectra']['data']['sha256']
assert sha(blockpath)==oldmanifest['complete_censuses']['paired_direction_blocks']['data']['sha256']
full={int(w):sorted(tuple(r['hist']) for r in rows) for w,rows in json.loads(fullpath.read_text())['weights'].items()}
blocks={(int(w),int(f)):sorted(tuple(r['hist']) for r in rows) for w,fs in json.loads(blockpath.read_text())['weights'].items() for f,rows in fs.items()}
newpath=HERE/'POSITIVE_LOW_RANK_BLOCK_CENSUS.json';new=json.loads(newpath.read_text())
rankblocks={(int(w),int(mode)):sorted(tuple(r['hist']) for r in rows) for w,ms in new['weights'].items() for mode,rows in ms.items()}
observed={k:set() for k in rankblocks};counts={};owncases=0
for rank in(3,4,5):
    basis={0,*[1<<i for i in range(rank)]};available=sorted(set(range(1<<rank))-basis)
    for w in(6,7,8):
        extra=w-len(basis)
        if not 0<=extra<=len(available):continue
        visited=0
        for addition in combinations(available,extra):
            A=basis|set(addition);ps={d:len(A&{x^d for x in A})//2 for d in range(1,32)}
            h=tuple(sum(v==p for v in ps.values()) for p in range(10));mode=1 if rank==3 else 2
            assert lowhist(w,h)==(mode==1)
            for a in ps:
                if ps[a]==0:continue
                partition={frozenset((d,d^a)) for d in range(1,32) if d!=a};assert len(partition)==15
                maxima=[max(ps[d] for d in pair) for pair in partition]
                observed[w,mode].add(tuple(maxima.count(p) for p in range(10)));owncases+=1
            visited+=1
        counts[f'rank{rank}_weight{w}']=visited
assert counts==new['counts'] and sum(counts.values())==594
assert all(observed[k]==set(v) for k,v in rankblocks.items())
for w in(6,7,8):assert observed[w,1]|observed[w,2]==set(blocks[w,1])

def allowed_spectra(w,f,mode,ch):
    assert mode in(0,1,2) and (mode==0 or f==1 and w in(6,7,8))
    if ch==1:return rankblocks[w,mode] if mode else blocks[w,f]
    return [h for h in full[w] if (not mode or lowhist(w,h)==(mode==1)) and (f==-1 or (h[0]>0 if f==0 else h[0]<31))]

bounds={};duals=0;inequalities=0;dualpath=HERE/'COMMON_SHAPE_INTEGER_DUALS.jsonl'
for line in dualpath.read_text().splitlines():
    row=json.loads(line);w=row['weight'];f=row['flag'];mode=row['mode'];ell=row['cutoff'];ch=row['channel'];ns=tuple(tuple(q) for q in row['neighbors']);key=(w,f,mode,ell,ch,ns)
    assert key not in bounds and ch in(0,1) and 0<=ell<=8
    assert all(1<=q<=9 and lo in(0,1) and (not lo or q in(3,4)) for q,lo in ns)
    assert ns==normalize_ns(ns,mode)
    if f==-1:assert (w,mode,ell,ch)==(19,0,0,0)
    spectra=allowed_spectra(w,f,mode,ch);seen=set();best=-10**9
    for cert in row['spectra']:
        si=cert['index'];assert 0<=si<len(spectra) and si not in seen;seen.add(si)
        h=spectra[si];ps=[p for p,n in enumerate(h) for _ in range(n)];lam=cert['lambda'];mu=cert['mu']
        assert len(ps)==(15 if ch else 31) and len(lam)==len(ns)+(ch==0 and f>=0) and len(mu)==len(ps)
        assert all(isinstance(v,int) for v in lam+mu) and min(mu)>=0
        value=sum(lam)+sum(mu);assert value==cert['bound']
        constant=ell*(sum(ps) if ch else w*(w-1)//2);assert constant==cert['constant']
        for i,(q,lo) in enumerate(ns):
            for j,p in enumerate(ps):
                score=2*cap(p,q,mode==1,lo)-ell*p
                if ch:score=max(0,score)
                assert lam[i]+mu[j]>=score;inequalities+=1
        if ch==0 and f>=0:
            for j,p in enumerate(ps):
                if (p==0 if f==0 else p>=1):assert lam[-1]+mu[j]>=2*M(p,9)-ell*p;inequalities+=1
        best=max(best,value+constant);duals+=1
    assert seen==set(range(len(spectra))) and best==row['upper_doubled'];bounds[key]=best

summary={'status':'PASS_EXACT_COMMON_SHAPE_BRANCH_VERIFICATION','new_rank_catalogue_normalized_sets':sum(counts.values()),'new_rank_catalogue_own_cases':owncases,'new_rank_catalogue_sha256':sha(newpath),'input_round2_manifest_sha256':sha(OLD/'M19_ROUND2_FINAL_MANIFEST.json'),'dual_sha256':sha(dualpath),'local_keys':len(bounds),'spectrum_duals':duals,'integer_inequalities':inequalities,'supports':{}}
totalbranches=0;channels=Counter();cutoffs=Counter()
for support in(11,12):
    infile=HERE/f's{support}_initial_profiles.txt';assert infile.read_bytes()==(OLD/f's{support}_final_round2_survivors.txt').read_bytes()
    profiles={}
    for line in infile.read_text().splitlines():
        t=list(map(int,line.split()));pid,z,k=t[:3];assert len(t)==3+3*k;rs=[(w,f) for f,w,n in zip(t[3::3],t[4::3],t[5::3]) for _ in range(n)]
        assert len(rs)==support-1 and 19+sum(w for w,f in rs)==93 and z==31-sum(f for w,f in rs) and pid not in profiles
        assert all(2<=w<=19 and f in(0,1) for w,f in rs);profiles[pid]=(rs,line)
    seen=set();gap_min=10**9;records=[];branch_count=0;candfile=HERE/f'S{support}_COMMON_SHAPE_CANDIDATES.jsonl'
    for raw in candfile.read_text().splitlines():
        c=json.loads(raw);pid=c['parent_id'];assert pid in profiles and pid not in seen and c['support']==support;seen.add(pid)
        source,profile_line=profiles[pid];multiplicities=[sum(f and w==ww for w,f in source) for ww in(6,7,8)]
        expected=set(product(*(range(n+1) for n in multiplicities)));actual=set();profile_gap=10**9
        for b in c['branches']:
            modes=tuple(b['low_counts']);assert modes in expected and modes not in actual;actual.add(modes);left=dict(zip((6,7,8),modes));rs=[]
            for w,f in source:
                mode=0
                if f and w in left:
                    mode=1 if left[w]>0 else 2
                    if mode==1:left[w]-=1
                rs.append((w,f,mode))
            assert not any(left.values());ell=b['cutoff'];ch=b['channel'];assert 0<=ell<=8 and ch in(0,1)
            heavy=[r for r in rs if r[0]//2>ell];hs=[(w//2,int(mode==1)) for w,f,mode in heavy]
            hubbase=sum(M(w//2,9) for w,f,mode in heavy if f) if ch==0 else 0
            plain=2*hubbase+2*sum(cap(q,hs[j][0],lo,hs[j][1]) for i,(q,lo) in enumerate(hs) for j in range(i))
            lights=[];losses=[];outside=[];nlow=0
            for w,f,mode in rs:
                if w//2<=ell:
                    val=bounds[(w,f,mode,ell,ch,normalize_ns(hs,mode))];plain+=val;lights.append(val)
            for w,f,mode in heavy:
                ns=hs.copy();ns.remove((w//2,int(mode==1)));base=(f*M(w//2,9) if ch==0 else 0)+sum(cap(w//2,q,mode==1,lo) for q,lo in ns)
                val=bounds[(w,f,mode,0,ch,normalize_ns(ns,mode))];assert val%2==0;loss=base-val//2;assert loss>=0;losses.append(loss)
                if mode==1:nlow+=1
                else:outside.append(loss)
            if ch==0:
                ns=tuple(sorted((w//2,0) for w,f,mode in heavy if f));val=bounds[(19,-1,0,0,0,ns)];assert val%2==0;loss=hubbase-val//2;assert loss>=0;losses.append(loss)
            group=0;lower=max(max(losses,default=0),(sum(losses)+1)//2)
            if ch:
                group=8*nlow*(nlow-1)//2-4*(nlow*nlow//2);assert group>=0
                lower=max(lower,group+max(max(outside,default=0),(sum(outside)+1)//2))
            correction=2*lower;upper=plain-correction;need=992 if ch==0 else 32*(32-support);gap=need-upper
            assert lights==b['light_bounds'] and losses==b['heavy_losses'] and group==b['group_deficit']
            assert plain==b['plain_doubled'] and correction==b['correction_doubled'] and upper==b['upper_doubled'] and gap>0
            profile_gap=min(profile_gap,gap);branch_count+=1;channels[ch]+=1;cutoffs[ell]+=1
        assert actual==expected;gap_min=min(gap_min,profile_gap)
        records.append({'parent_id':pid,'support':support,'profile_line':profile_line,'covering_branch_count':len(actual),'minimum_gap_doubled':profile_gap,'candidate_line_sha256':hashlib.sha256(raw.encode()).hexdigest()})
    verified=HERE/f'S{support}_COMMON_SHAPE_VERIFIED_PROFILES.jsonl';verified.write_text(''.join(json.dumps(r,sort_keys=True,separators=(',',':'))+'\n' for r in records))
    survivors=HERE/f's{support}_after_common_shapes.txt';survivors.write_text(''.join(line+'\n' for pid,(rs,line) in profiles.items() if pid not in seen))
    summary['supports'][str(support)]={'input_profiles':len(profiles),'input_sha256':sha(infile),'whole_profile_exclusions':len(seen),'covering_branch_certificates':branch_count,'remaining_profiles':len(profiles)-len(seen),'minimum_gap_doubled':gap_min,'candidate_sha256':sha(candfile),'verified_profiles_sha256':sha(verified),'survivors_sha256':sha(survivors)}
    totalbranches+=branch_count;print(json.dumps(summary['supports'][str(support)]),flush=True)
summary['total_whole_profile_exclusions']=sum(r['whole_profile_exclusions'] for r in summary['supports'].values());summary['total_remaining_profiles']=sum(r['remaining_profiles'] for r in summary['supports'].values());summary['total_covering_branches']=totalbranches;summary['certificate_channels']=dict(channels);summary['certificate_cutoffs']=dict(cutoffs);summary['seconds']=time.time()-start
(HERE/'COMMON_SHAPE_VERIFICATION_RECEIPT.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
