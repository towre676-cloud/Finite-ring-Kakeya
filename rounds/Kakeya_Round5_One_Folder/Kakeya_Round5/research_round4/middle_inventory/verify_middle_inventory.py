"""Replay the complete middle range and every credited additional cut.

The independent C++ checker regenerates all profiles by frequency vectors and
uses backward recursion for the global quota bound. This Python checker uses
backward resource recursion/direct plane-coset convolution for the new cuts,
checks all cube-mode branches with exact joint spectrum maxima, and verifies
that the final list is exactly the complement of all credited exclusions.
"""
from collections import Counter,defaultdict
from functools import lru_cache
from pathlib import Path
import argparse,hashlib,json,subprocess,time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OLD=ROOT/'research_round2/middle'
GEO=ROOT/'research_round2/geometric'
START=time.monotonic()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def cap(p,q):
    a,b=sorted((p,q))
    return b+8 if a==3 and 5<=b<=7 else min(16,p*q)
def quota(w):
    return (w&-w)-1 if w%2==0 else max((w-1)&-(w-1),(w+1)&-(w+1))-1
def progress(stage,**kw):
    print(json.dumps(dict(stage=stage,seconds=round(time.monotonic()-START,3),**kw)),flush=True)

@lru_cache(None)
def local(w,heavy,ell,mass,maxima,positive):
    c=w//2
    # The independent recursion processes a sorted heavy list backwards in index.
    heavy=tuple(sorted(heavy))
    @lru_cache(None)
    def rec(j,left,full,pos):
        if j==0:return 0
        return max(2*cap(p,heavy[j-1])-ell*p+rec(j-1,left-p,full-(p==c),pos-(p>0))
                   for p in range(min(c,left)+1) if (p<c or full) and (p==0 or pos))
    return ell*mass+rec(len(heavy),min(mass,c*len(heavy)),min(maxima,len(heavy)),min(positive,len(heavy)))

def missing(w,h,half=False,sumfree=False,positive=None):
    heavy=tuple(v//2 for v in w[:h]);ell=w[h]//2
    return sum(local(v,heavy,ell,v*v//4 if half or sumfree else v*(v-1)//2,
                     (quota(v)+1)//2 if sumfree else quota(v),positive if positive is not None else h)
               for v in w[h:])

def plane_triples():
    patterns=set()
    for mask in range(16):
        A=[x for x in range(4) if mask>>x&1]
        p=[sum(a<b and a^b==d for a in A for b in A) for d in (1,2,3)]
        patterns.add((len(A),*p))
    states={(0,0,0,0)}
    for _ in range(8):
        states={tuple(a+b for a,b in zip(x,y)) for x in states for y in patterns if x[0]+y[0]<=18}
    answer=defaultdict(set)
    for w,p,q,t in states:answer[w].add((p,q,t))
    return answer
TRIPLES=plane_triples()

@lru_cache(None)
def deleted_row(w,h1,h2,ell):
    return max(ell*(w*(w-1)//2-t)+2*cap(p,h1)+2*cap(q,h2)-ell*(p+q)
               for p,q,t in TRIPLES[w])

def verify_method(method,w,values,energy):
    if method=='TOTAL_PAIR_ENERGY':
        value=sum(energy[v] for v in w);assert values==[value] and value<992
    elif method=='THREE_HEAVY_SINGLE_EXCEPTION':
        heavy=tuple(v//2 for v in w[:3]);ell=w[3]//2
        value=sum(2*cap(a,b) for i,a in enumerate(heavy) for b in heavy[:i]);extra=[]
        for v in w[3:]:
            q=quota(v);mass=v*(v-1)//2
            restricted=local(v,heavy,ell,mass,2 if q==3 else q,3)
            value+=restricted
            if q==3:extra.append(local(v,heavy,ell,mass,3,3)-restricted)
        value+=max(extra,default=0);assert values==[value] and value<992
    elif method=='TWO_HEAVY_DELETED_DIRECTION':
        value=sum(deleted_row(v,w[0]//2,w[1]//2,w[2]//2) for v in w[2:])
        assert values==[value] and value<960
    elif method=='EIGHT_HEAVY_MISSING_DIRECTIONS':
        full=missing(w,8,positive=8);half=missing(w,8,half=True,positive=3)
        assert values==[full,half] and full<288 and half<192
    elif method=='NINE_HEAVY_SUMFREE_DIRECTIONS':
        value=missing(w,9,sumfree=True,positive=9)
        assert values==[value] and value<96
    elif method=='HALFSPACE_MAXIMAL_DIRECTION_BONUS':
        full=missing(w,8,positive=8);lights=w[8:];caps=sorted((v//2 for v in lights),reverse=True)
        assert max(caps)<=8
        value=4*sum(v*v//4 for v in lights);X=sum(caps[:6])
        for v in w[:8]:
            if v//2>4:value+=(v//2-5)*X+sum(caps[:min(6,(quota(v)+1)//2)])
        assert values==[full,value] and full<288 and value<96
    elif method=='TEN_HEAVY_WEAK_UNIQUE_DIRECTIONS':
        assert w[0]//2==6 and all(v//2<=4 for v in w[1:10]) and all(v<=3 for v in w[10:])
        weak=sum(v//2<=3 for v in w[:10]);mass=sum(v*(v-1)//2 for v in w[10:])
        demand=min(4*r+weak*max(0,3-r) for r in range(32))
        assert demand==min(3*weak,12) and values==[mass,demand] and mass<demand
    else:raise AssertionError(method)

def read_profiles(path):
    profiles={}
    for line in path.open():
        s,m,b,*w=map(int,line.split());w=tuple(w)
        assert len(w)==s and sum(w)==93 and w==tuple(sorted(w,reverse=True))
        assert 10<=s<=17 and 12<=m<=18 and w[0]==m and min(w)>=2
        assert w not in profiles;profiles[w]=(s,m,b,line)
    return profiles

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reuse-quota-replay',action='store_true');args=parser.parse_args()
    if not args.reuse_quota_replay:
        binary=HERE/'verify_quota_inventory'
        subprocess.run(['g++','-O3','-std=c++17',str(HERE/'verify_quota_inventory.cpp'),'-o',str(binary)],check=True)
        with (HERE/'independent_quota_counts.jsonl').open('w') as out:
            subprocess.run([str(binary),str(HERE/'quota_survivors.txt')],stdout=out,check=True)
    checked={(r['support'],r['maximum']):r for r in map(json.loads,(HERE/'independent_quota_counts.jsonl').open())}
    produced={(r['support'],r['maximum']):r for r in map(json.loads,(HERE/'quota_counts.jsonl').open())}
    assert set(checked)==set(produced)=={(s,m) for s in range(10,18) for m in range(12,19)}
    for key,r in checked.items():
        assert r['profiles']==produced[key]['profiles']
        assert r['quota_cuts']==produced[key]['excluded']
        assert r['quota_survivors']==r['profiles']-r['quota_cuts']
    assert sum(r['profiles'] for r in checked.values())==2163945
    profiles=read_profiles(HERE/'quota_survivors.txt')
    assert len(profiles)==435832==sum(r['quota_survivors'] for r in checked.values())
    actual_by=Counter((len(w),w[0]) for w in profiles)
    assert all(actual_by[key]==r['quota_survivors'] for key,r in checked.items())
    progress('complete_quota_inventory',profiles=2163945,survivors=len(profiles))

    census_path=GEO/'PAIR_SPECTRUM_CENSUS.json'
    census=json.loads(census_path.read_text())
    spectra={int(w):sorted(tuple(r['hist']) for r in rows) for w,rows in census['weights'].items()}
    energy={w:max(sum(p*p*n for p,n in enumerate(h)) for h in hs) for w,hs in spectra.items()}
    assert [energy[w] for w in range(2,19)]==[1,3,12,16,33,63,112,120,153,211,300,408,553,735,960,976,1041]
    frozen=json.loads((OLD/'GLOBAL_SPECTRUM_INDEPENDENT_REPLAY.json').read_text())
    candidates_path=OLD/'GLOBAL_SPECTRUM_CANDIDATES.jsonl'
    assert frozen['status']=='PASS'
    assert frozen['dependencies']['pair_spectrum_census_sha256']==sha(census_path)
    assert frozen['dependencies']['candidates_sha256']==sha(candidates_path)
    assert frozen['dependencies']['dual_sha256']==sha(OLD/'GLOBAL_SPECTRUM_DUAL_CERTIFICATES.jsonl')
    inherited={tuple(r['weights']) for r in map(json.loads,candidates_path.open()) if 10<=r['support']<=17}
    assert len(inherited)==23164 and inherited<=set(profiles)
    saved_inherited={tuple(map(int,l.split())) for l in (HERE/'inherited_spectrum_cut_weights.txt').open()}
    assert saved_inherited==inherited
    cut_methods={};methods=Counter();by_method=defaultdict(Counter)
    for index,line in enumerate((HERE/'geometry_and_spectrum_cuts.txt').open(),1):
        parts=line.split();method=parts[0];s,m,n=map(int,parts[1:4]);values=list(map(int,parts[4:4+n]));w=tuple(map(int,parts[4+n:]))
        assert len(w)==s and w[0]==m and w in profiles and w not in cut_methods
        if method=='INHERITED_EXACT_SPECTRUM':assert not values and w in inherited
        else:
            assert w not in inherited
            verify_method(method,w,values,energy)
        cut_methods[w]=method;methods[method]+=1;by_method[s,m][method]+=1
        if index%50000==0:progress('geometric_certificate_progress',checked=index,local_keys=local.cache_info().currsize)
    assert {w for w,m in cut_methods.items() if m=='INHERITED_EXACT_SPECTRUM'}==inherited
    before_cube=read_profiles(HERE/'final_weight_survivors.txt')
    assert set(before_cube)==set(profiles)-set(cut_methods) and len(before_cube)==276791
    for w in before_cube:assert before_cube[w]==profiles[w]
    stage_rows={(r['support'],r['maximum']):r['methods'] for r in map(json.loads,(HERE/'geometry_counts.jsonl').open())}
    for key in checked:
        expected=dict(by_method[key]);count=sum((len(w),w[0])==key for w in before_cube)
        if count:expected['SURVIVES']=count
        assert expected==stage_rows[key]
    progress('all_geometric_cuts',new=sum(n for k,n in methods.items() if k!='INHERITED_EXACT_SPECTRUM'),inherited=23164,survivors=len(before_cube))

    def score_hist(h,r,L):
        value=sum(p*p*n for p,n in enumerate(h));left=r
        gains=sorted(((max(0,2*min(16,4*p)-p*p-L),n) for p,n in enumerate(h) if n),reverse=True)
        for gain,n in gains:
            k=min(n,left);value+=k*gain;left-=k
            if not left:break
        return value
    table_data=json.loads((HERE/'CUBE_JOINT_LOCAL_TABLE.json').read_text())
    assert table_data['census_sha256']==sha(census_path)
    table={}
    for row in table_data['rows']:
        w,r,L=row['weight'],row['cubes'],row['twice_price'];key=(w,r,L)
        assert key not in table and 2<=w<=18 and 0<=r<=10 and 8<=L<=16
        allowed=[(i,h) for i,h in enumerate(spectra[w]) if w!=8 or h[4]!=7]
        upper=max(score_hist(h,r,L) for i,h in allowed)
        assert upper==row['bound']
        ix=row['attaining_spectrum_index'];assert any(i==ix and score_hist(h,r,L)==upper for i,h in allowed)
        table[key]=upper
    assert len(table)==17*11*9
    def branch_upper(weights,r,L):
        hist=Counter(weights);hist[8]-=r;assert hist[8]>=0
        return 7*L*r+(32-2*L)*(r*r//4)+sum(n*table[w,r,L] for w,n in hist.items() if n)
    cube_cuts={}
    for row in map(json.loads,(HERE/'CUBE_JOINT_ENERGY_CUTS.jsonl').open()):
        w=tuple(row['weights']);assert w in before_cube and w not in cube_cuts
        assert row['support']==len(w) and row['maximum']==w[0]
        assert [b['cubes'] for b in row['branches']]==list(range(w.count(8)+1))
        for b in row['branches']:
            r,L=b['cubes'],b['twice_price'];assert 8<=L<=16
            upper=branch_upper(w,r,L)
            assert upper==b['upper_doubled']<992
        cube_cuts[w]=row;by_method[len(w),w[0]]['JOINT_SPECTRUM_CUBE_ENERGY']+=1
    assert len(cube_cuts)==524
    final=read_profiles(HERE/'after_cube_weight_survivors.txt')
    assert len(final)==276267 and set(final)==set(before_cube)-set(cube_cuts)
    zero_cube_branch_survivors=0
    for w in final:
        assert final[w]==before_cube[w]
        # Exact complement of the finite price-bank screen: at least one cube
        # count survives every tested price. The most frequent branch is r=0.
        if branch_upper(w,0,8)>=992:
            zero_cube_branch_survivors+=1
            continue
        assert any(min(branch_upper(w,r,L) for L in range(8,17))>=992 for r in range(1,w.count(8)+1))
    progress('joint_spectrum_cube_energy',cuts=524,covering_branches=sum(len(r['branches']) for r in cube_cuts.values()),survivors=len(final))

    final_by=Counter((len(w),w[0]) for w in final)
    records=[]
    for key,r in sorted(checked.items()):
        counts=dict(sorted(by_method[key].items()))
        assert r['profiles']==r['quota_cuts']+sum(counts.values())+final_by[key]
        records.append(dict(r,additional_disjoint_cuts=counts,remaining_weight_profiles=final_by[key]))
    supports=[]
    for s in range(10,18):
        rs=[r for r in records if r['support']==s]
        supports.append({'support':s,'all_weight_profiles':sum(r['profiles'] for r in rs),
                         'quota_survivors':sum(r['quota_survivors'] for r in rs),
                         'remaining_weight_profiles':sum(r['remaining_weight_profiles'] for r in rs)})
    deps=[HERE/'scan_middle_quota.cpp',HERE/'verify_quota_inventory.cpp',HERE/'quota_counts.jsonl',HERE/'independent_quota_counts.jsonl',HERE/'quota_survivors.txt',
          HERE/'screen_geometry.cpp',HERE/'geometry_counts.jsonl',HERE/'geometry_and_spectrum_cuts.txt',HERE/'final_weight_survivors.txt',
          HERE/'inherited_spectrum_cut_weights.txt',HERE/'screen_cube_joint_energy.py',HERE/'CUBE_JOINT_LOCAL_TABLE.json',HERE/'CUBE_JOINT_ENERGY_CUTS.jsonl',HERE/'after_cube_weight_survivors.txt',
          census_path,OLD/'GLOBAL_SPECTRUM_INDEPENDENT_REPLAY.json',candidates_path,OLD/'GLOBAL_SPECTRUM_DUAL_CERTIFICATES.jsonl',
          ROOT/'research_round3/middle/RESOURCE_COMPATIBILITY_LEMMAS.md',ROOT/'research_round3/middle/CUBE_ENERGY_SUPPORT18_EXCLUSIONS.md',
          OLD/'DIFFERENCE_AND_LIGHT_RESOURCE_LEMMAS.md',Path(__file__).resolve()]
    receipt={'status':'PASS','scope':'All total93 weight profiles with exact maximum12..18 and pair-active support10..17, both rings in dimension5.',
             'support9_status':'Excluded by the inherited theorem that nine binary residues have at most28 nonzero differences.',
             'padding':'For all56 cells, support*maximum>=120>93, so every <=93 candidate can be padded at unchanged support and exact maximum.',
             'all_weight_profiles':2163945,'global_quota_cuts':1728113,'quota_survivors':435832,
             'inherited_selected_spectrum_cuts':23164,'additional_generic_geometry_cuts':135877,'additional_joint_cube_energy_cuts':524,
             'total_new_whole_weight_profile_exclusions':136401,'remaining_weight_profiles':276267,
             'supports':supports,'records':records,
             'cube_energy_local_table_rows':len(table),'cube_energy_covering_branches':sum(len(r['branches']) for r in cube_cuts.values()),
             'final_profiles_with_zero_cube_branch_not_excluded':zero_cube_branch_survivors,
             'final_profiles_forcing_at_least_one_cube_by_energy':len(final)-zero_cube_branch_survivors,
             'generic_geometry_method_counts':dict(sorted(methods.items())),
             'global_verification':'Separate C++ frequency-vector enumerator and backward local recursion; exact equality with forward-DP producer survivor list.',
             'geometry_verification':'Python backward recursion/direct plane-coset convolution; every claimed cut recomputed, and exact disjoint survivor subtraction.',
             'inherited_spectrum_verification':'Previously replayed exact dual certificates, identified by their existing verified receipt and unchanged candidate/dual/census hashes; no additional exclusions from unverified solver output.',
             'scope_limit':'This enumerates weight profiles, not residue placements or fibre shapes. A survivor is not a Kakeya set. No whole support or maximum stratum is claimed closed unless its full relevant inventory is empty.',
             'dependencies':{str(p.relative_to(ROOT)):sha(p) for p in deps},'seconds':time.monotonic()-START}
    (HERE/'MIDDLE_COMPLETE_INVENTORY.json').write_text(json.dumps(receipt,indent=2)+'\n')
    progress('PASS',profiles=2163945,remaining=276267,new_cuts=136401)

if __name__=='__main__':main()
