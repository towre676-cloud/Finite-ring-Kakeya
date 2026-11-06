"""Independent exact verification of the shared-own-period resource stage."""
from pathlib import Path
from itertools import product
import hashlib,json,time

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];OLD=ROOT/'research_round2/geometric'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def M(p,q):
    a,b=sorted((p,q));return b+8 if a==3 and b in(5,6,7) else min(16,p*q)
def cap(p,q,per,partnerper):return min(M(p,q),p*q//2) if per and partnerper else M(p,q)
def offcap(w,mode):return 2*(w//4) if mode==1 else w//2
def ownmax(w,f,mode):return 0 if f==0 else (w//2-1 if mode==2 else w//2)
def own_allowed(w,f,mode,p):
    if f==0:return p==0
    if mode==1:return p==w//2
    if mode==2:return 1<=p<w//2
    return p>=1
def normalize_ns(ns,mode):return tuple(sorted(((q,per if mode==1 else 0) for q,per in ns),key=lambda x:(x[1],x[0])))

start=time.time();oldmanifest=json.loads((OLD/'M19_ROUND2_FINAL_MANIFEST.json').read_text());assert oldmanifest['status']=='ROOT_VERIFIED'
fullpath=OLD/'PAIR_SPECTRUM_CENSUS.json';blockpath=OLD/'PAIRED_BLOCK_MAXIMUM_CENSUS.json'
assert sha(fullpath)==oldmanifest['complete_censuses']['full_pair_spectra']['data']['sha256']
assert sha(blockpath)==oldmanifest['complete_censuses']['paired_direction_blocks']['data']['sha256']
full={int(w):sorted(tuple(r['hist']) for r in rows) for w,rows in json.loads(fullpath.read_text())['weights'].items()}
blocks={(int(w),int(f)):sorted(tuple(r['hist']) for r in rows) for w,fs in json.loads(blockpath.read_text())['weights'].items() for f,rows in fs.items()}
cataloguepath=HERE/'OWN_PERIODIC_BLOCK_CENSUS.json';catalogue=json.loads(cataloguepath.read_text())
periodblocks={int(w):sorted(tuple(r['hist']) for r in rows) for w,rows in catalogue['weights'].items()}
observed={w:set() for w in periodblocks};counts={w:0 for w in periodblocks}
for mask in range(1<<16):
    c=mask.bit_count()
    if not 1<=c<=9:continue
    w=2*c;A={x for x in range(16) if mask>>x&1}
    # Direct translated intersections equal twice the quotient unordered-pair count.
    values=[len(A&{x^d for x in A}) for d in range(1,16)]
    observed[w].add(tuple(values.count(p) for p in range(10)));counts[w]+=1
assert {str(w):n for w,n in counts.items()}==catalogue['subset_counts']
assert sum(counts.values())==50642 and all(observed[w]==set(hs) for w,hs in periodblocks.items())
for w,hs in full.items():
    if w%2 or not 2<=w<=18:continue
    c=w//2
    for h in hs:
        if not h[c]:continue
        off=list(h);off[c]-=1
        assert all(n%2==0 for n in off) and all(off[p]==0 for p in range(1,10,2))
        assert tuple(n//2 for n in off) in observed[w]

def allowed_spectra(w,f,mode,ch):
    assert mode in(0,1,2) and (mode==0 or f==1 and w%2==0)
    if ch:return periodblocks[w] if mode==1 else blocks[w,f]
    return [h for h in full[w] if f==-1 or any(n and own_allowed(w,f,mode,p) for p,n in enumerate(h))]

bounds={};duals=0;inequalities=0;dualpath=HERE/'OWN_PERIODIC_INTEGER_DUALS.jsonl'
for line in dualpath.read_text().splitlines():
    row=json.loads(line);w=row['weight'];f=row['flag'];mode=row['mode'];ell=row['cutoff'];ch=row['channel'];ns=tuple(tuple(q) for q in row['neighbors']);key=(w,f,mode,ell,ch,ns)
    assert key not in bounds and ch in(0,1) and 0<=ell<=8 and ns==normalize_ns(ns,mode)
    assert all(1<=q<=9 and per in(0,1) and (not per or q%2==0) for q,per in ns)
    if f==-1:assert (w,mode,ell,ch)==(19,0,0,0)
    spectra=allowed_spectra(w,f,mode,ch);seen=set();best=-10**9
    for cert in row['spectra']:
        si=cert['index'];assert 0<=si<len(spectra) and si not in seen;seen.add(si)
        h=spectra[si];ps=[p for p,n in enumerate(h) for _ in range(n)];lam=cert['lambda'];mu=cert['mu']
        assert len(ps)==(15 if ch else 31) and len(lam)==len(ns)+(ch==0 and f>=0) and len(mu)==len(ps)
        assert all(isinstance(v,int) for v in lam+mu) and min(mu)>=0
        value=sum(lam)+sum(mu);assert value==cert['bound'];constant=ell*(sum(ps) if ch else w*(w-1)//2);assert constant==cert['constant']
        for i,(q,per) in enumerate(ns):
            for j,p in enumerate(ps):
                score=2*cap(p,q,mode==1,per)-ell*p
                if ch:score=max(0,score)
                assert lam[i]+mu[j]>=score;inequalities+=1
        if ch==0 and f>=0:
            for j,p in enumerate(ps):
                if own_allowed(w,f,mode,p):assert lam[-1]+mu[j]>=2*M(p,9)-ell*p;inequalities+=1
        best=max(best,value+constant);duals+=1
    assert seen==set(range(len(spectra))) and best==row['upper_doubled'];bounds[key]=best

summary={'status':'PASS_EXACT_OWN_PERIODIC_BRANCH_VERIFICATION','periodic_quotient_subsets_checked':sum(counts.values()),'periodic_catalogue_sha256':sha(cataloguepath),'dual_sha256':sha(dualpath),'local_keys':len(bounds),'spectrum_duals':duals,'integer_inequalities':inequalities,'supports':{}}
totalbranches=0
for support in(11,12):
    infile=HERE/f's{support}_after_two_heavy_own.txt';profiles={}
    for line in infile.read_text().splitlines():
        t=list(map(int,line.split()));pid,z,k=t[:3];assert len(t)==3+3*k;rs=[(w,f) for f,w,n in zip(t[3::3],t[4::3],t[5::3]) for _ in range(n)]
        assert len(rs)==support-1 and 19+sum(w for w,f in rs)==93 and z==31-sum(f for w,f in rs) and pid not in profiles
        profiles[pid]=(rs,line)
    seen=set();gap_min=10**9;records=[];branch_count=0;candfile=HERE/f'S{support}_OWN_PERIODIC_CANDIDATES.jsonl'
    for raw in candfile.read_text().splitlines():
        c=json.loads(raw);pid=c['parent_id'];assert pid in profiles and pid not in seen and c['support']==support;seen.add(pid)
        source,profile_line=profiles[pid];weights=tuple(range(4,20,2));multiplicities=[sum(f and w==ww for w,f in source) for ww in weights]
        expected=set(product(*(range(n+1) for n in multiplicities)));actual=set();profile_gap=10**9
        for b in c['branches']:
            modes=tuple(b['periodic_counts']);assert modes in expected and modes not in actual;actual.add(modes);left=dict(zip(weights,modes));rs=[]
            for w,f in source:
                mode=0
                if f and w%2==0:
                    if w==2:mode=1
                    else:
                        mode=1 if left[w]>0 else 2
                        if mode==1:left[w]-=1
                rs.append((w,f,mode))
            assert not any(left.values());ell=b['cutoff'];ch=b['channel'];assert 0<=ell<=8 and ch in(0,1)
            heavy=[r for r in rs if offcap(r[0],r[2])>ell];hs=[(offcap(w,mode),int(mode==1)) for w,f,mode in heavy]
            hubbase=sum(M(ownmax(w,f,mode),9) for w,f,mode in heavy if f) if ch==0 else 0
            plain=2*hubbase+2*sum(cap(q,hs[j][0],per,hs[j][1]) for i,(q,per) in enumerate(hs) for j in range(i));lights=[];losses=[]
            for w,f,mode in rs:
                if offcap(w,mode)<=ell:
                    val=bounds[(w,f,mode,ell,ch,normalize_ns(hs,mode))];plain+=val;lights.append(val)
            for w,f,mode in heavy:
                ns=hs.copy();ns.remove((offcap(w,mode),int(mode==1)))
                base=(M(ownmax(w,f,mode),9) if ch==0 else 0)+sum(cap(offcap(w,mode),q,mode==1,per) for q,per in ns)
                val=bounds[(w,f,mode,0,ch,normalize_ns(ns,mode))];assert val%2==0;loss=base-val//2;assert loss>=0;losses.append(loss)
            if ch==0:
                ns=tuple(sorted((ownmax(w,f,mode),0) for w,f,mode in heavy if f));val=bounds[(19,-1,0,0,0,ns)];assert val%2==0;loss=hubbase-val//2;assert loss>=0;losses.append(loss)
            correction=2*max(max(losses,default=0),(sum(losses)+1)//2);upper=plain-correction;need=992 if ch==0 else 32*(32-support);gap=need-upper
            assert lights==b['light_bounds'] and losses==b['heavy_losses'] and b['group_deficit']==0
            assert plain==b['plain_doubled'] and correction==b['correction_doubled'] and upper==b['upper_doubled'] and gap>0
            profile_gap=min(profile_gap,gap);branch_count+=1
        assert actual==expected;gap_min=min(gap_min,profile_gap)
        records.append({'parent_id':pid,'support':support,'profile_line':profile_line,'covering_branch_count':len(actual),'minimum_gap_doubled':profile_gap,'candidate_line_sha256':hashlib.sha256(raw.encode()).hexdigest()})
    verified=HERE/f'S{support}_OWN_PERIODIC_VERIFIED_PROFILES.jsonl';verified.write_text(''.join(json.dumps(r,sort_keys=True,separators=(',',':'))+'\n' for r in records))
    survivors=HERE/f's{support}_after_own_periodic.txt';survivors.write_text(''.join(line+'\n' for pid,(rs,line) in profiles.items() if pid not in seen))
    summary['supports'][str(support)]={'input_profiles':len(profiles),'input_sha256':sha(infile),'whole_profile_exclusions':len(seen),'covering_branch_certificates':branch_count,'remaining_profiles':len(profiles)-len(seen),'minimum_gap_doubled':gap_min,'candidate_sha256':sha(candfile),'verified_profiles_sha256':sha(verified),'survivors_sha256':sha(survivors)}
    totalbranches+=branch_count;print(json.dumps(summary['supports'][str(support)]),flush=True)
summary['total_whole_profile_exclusions']=sum(r['whole_profile_exclusions'] for r in summary['supports'].values());summary['total_remaining_profiles']=sum(r['remaining_profiles'] for r in summary['supports'].values());summary['total_covering_branches']=totalbranches;summary['seconds']=time.time()-start
(HERE/'OWN_PERIODIC_VERIFICATION_RECEIPT.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
