"""Independent exact replay of the complete middle-maxima support-18 exclusion.

Standard library only. This checker never imports any round-three producer.
It regenerates all weight partitions, independently replays the inherited
quota bound, checks the needed integer matching duals, and checks all new
certificates with backward recursion or direct enumeration. Analytic geometry
dependencies are documented explicitly in MIDDLE_SUPPORT_AT_MOST_SEVENTEEN.md.
Round-two artifacts are read only and are not modified.
"""
from pathlib import Path
from collections import Counter
from functools import lru_cache
from itertools import product
import hashlib
import importlib.util
import json
import time

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
OLD = BASE/'research_round2/middle'
GEO = BASE/'research_round2/geometric'
ROOT2 = BASE/'research_round2/root'
START = time.monotonic()
THRESHOLD = 992
DEPENDENCIES = set()


def read_records(path):
    DEPENDENCIES.add(path)
    return [json.loads(line) for line in path.open() if line.strip()]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def report(**data):
    print(json.dumps(dict(**data, seconds=round(time.monotonic()-START,3))), flush=True)


def mcap(a,b):
    if min(a,b)==3 and 5<=max(a,b)<=7:
        return max(a,b)+8
    return min(16,a*b)


def quota(w):
    if w%2==0:
        return (w & -w)-1
    return max((w-1) & -(w-1), (w+1) & -(w+1))-1


def indexed(records):
    result = {}
    for rec in records:
        w = tuple(rec['weights'])
        assert len(w)==18 and sum(w)==93 and 12<=w[0]<=18
        assert w==tuple(sorted(w, reverse=True)) and min(w)>=2
        assert w not in result
        result[w]=rec
    return result


@lru_cache(None)
def resource_row(w, hp, ell, mass, maximum_quota, positive_quota):
    """Backward recursion; producers use forward resource state accumulation."""
    c=w//2
    @lru_cache(None)
    def recurse(pos, remaining_mass, remaining_maxima, remaining_positive):
        if pos==len(hp):
            return 0
        h,price=hp[pos]
        best=-10**10
        for x in range(min(c,remaining_mass)+1):
            full=int(x==c)
            positive=int(x>0)
            if full>remaining_maxima or positive>remaining_positive:
                continue
            score=(2*mcap(x,h)-ell*x-price*positive
                   +recurse(pos+1,remaining_mass-x,remaining_maxima-full,
                            remaining_positive-positive))
            best=max(best,score)
        return best
    return ell*mass+recurse(0,min(mass,c*len(hp)),
                            min(maximum_quota,len(hp)),min(positive_quota,len(hp)))


def check_priced_branch(rec, heavy_count, half, positive_quota, prefix,
                        missing, sumfree=False):
    w=tuple(rec['weights'])
    h=tuple(v//2 for v in w[:heavy_count])
    lights=w[heavy_count:]
    ell=max(v//2 for v in lights)
    prices=tuple(rec[prefix+'_prices'])
    assert len(prices)==heavy_count and all(type(x) is int and x>=0 for x in prices)
    if not half:
        assert sum(prices)<=32
    hp=tuple(zip(h,prices))
    rows=[]
    for v in lights:
        mass=v*v//4 if half or sumfree else v*(v-1)//2
        q=(quota(v)+1)//2 if sumfree else quota(v)
        rows.append(resource_row(v,hp,ell,mass,q,positive_quota))
    upper=sum(rows)+missing*sum(prices)
    assert rows==rec[prefix+'_rows']
    assert upper==rec[prefix+'_upper_doubled']
    return upper


def regenerate_plane_triples():
    # Directly enumerate all sixteen subsets of an actual four-point coset.
    patterns=set()
    for mask in range(16):
        pts=[x for x in range(4) if mask>>x&1]
        pairs=[sum(1 for a in pts for b in pts if a<b and a^b==d)
               for d in (1,2,3)]
        patterns.add((len(pts),*pairs))
    states={(0,0,0,0)}
    for _ in range(8):
        states={tuple(a+b for a,b in zip(state,pat))
                for state in states for pat in patterns}
    by_weight={}
    for w,p,q,t in states:
        by_weight.setdefault(w,set()).add((p,q,t))
    path=HERE/'BINARY_PLANE_PAIR_TRIPLES.json'
    DEPENDENCIES.add(path)
    producer=json.loads(path.read_text())
    assert set(map(int,producer))==set(by_weight)
    for w,triples in by_weight.items():
        assert triples==set(map(tuple,producer[str(w)]))
    return by_weight


def initial_quota_stage():
    # This is the earlier independent checker, not its C++ producer.
    p=OLD/'verify_global_support_reductions.py'
    DEPENDENCIES.add(p)
    spec=importlib.util.spec_from_file_location('independent_round2_quota',p)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    total=0
    surviving={}
    by_max=Counter()
    cutoff_counts=Counter()
    for w in mod.partitions(18,93,18):
        if w[0]<12:
            continue
        total+=1
        by_max[w[0]]+=1
        best=10**9
        for ell in (2,3,1,4,0,5,6,7,8,9):
            b=mod.bound(w,ell)
            best=min(best,b)
            if b<THRESHOLD:
                cutoff_counts[ell]+=1
                break
        else:
            surviving[w]=best
        if total%50000==0:
            report(stage='regenerate_partitions_progress',partitions=total,
                   survivors=len(surviving))
    assert total==239246 and len(surviving)==502
    old_rows={}
    path=OLD/'global_survivors_15_18.txt'
    DEPENDENCIES.add(path)
    for line in path.open():
        s,m,b,*ws=map(int,line.split())
        if s==18 and 12<=m<=18:
            assert tuple(ws) not in old_rows
            old_rows[tuple(ws)]=b
    assert surviving==old_rows
    report(stage='complete_quota_replay',partitions=total,excluded=total-len(surviving),
           survivors=len(surviving))
    return surviving,dict(by_max),dict(cutoff_counts)


def inherited_spectrum_stage(surviving):
    cp=GEO/'PAIR_SPECTRUM_CENSUS.json'
    DEPENDENCIES.add(cp)
    census=json.loads(cp.read_text())
    receipt=ROOT2/'ROOT_VERIFIED_PAIR_SPECTRUM_CENSUS.json'
    DEPENDENCIES.add(receipt)
    receipt_data=json.loads(receipt.read_text())
    assert receipt_data['status']=='PASS' and receipt_data['census_sha256']==sha(cp)
    spectra={int(w):sorted(tuple(row['hist']) for row in rs)
             for w,rs in census['weights'].items()}
    expanded={w:[tuple(p for p,n in enumerate(hist) for _ in range(n)) for hist in hs]
              for w,hs in spectra.items()}
    for w,hs in spectra.items():
        for hist in hs:
            assert sum(hist)==31 and sum(p*n for p,n in enumerate(hist))==w*(w-1)//2
    candidates=[r for r in read_records(OLD/'GLOBAL_SPECTRUM_CANDIDATES.jsonl')
                if r['support']==18]
    assert len(candidates)==217
    needed=set()
    for rec in candidates:
        ws=tuple(rec['weights']);ell=rec['cutoff']
        assert ws in surviving and rec['old_bound']==surviving[ws]
        hs=tuple(sorted(v//2 for v in ws if v//2>ell))
        for w in ws:
            if w//2<=ell:
                needed.add((w,ell,hs))
            else:
                ns=list(hs);ns.remove(w//2)
                needed.add((w,0,tuple(ns)))
    bounds={}
    duals=inequalities=0
    dp=OLD/'GLOBAL_SPECTRUM_DUAL_CERTIFICATES.jsonl'
    DEPENDENCIES.add(dp)
    for line in dp.open():
        r=json.loads(line)
        key=(r['weight'],r['cutoff'],tuple(r['neighbors']))
        if key not in needed:
            continue
        assert key not in bounds and r['flag']==-1
        w,ell,qs=key
        assert qs==tuple(sorted(qs)) and len(r['spectra'])==len(spectra[w])
        seen=set();best=-10**9
        for dual in r['spectra']:
            ix=dual['index']
            assert 0<=ix<len(spectra[w]) and ix not in seen
            seen.add(ix)
            ps=expanded[w][ix]
            lam=dual['lambda'];mu=dual['mu']
            assert len(lam)==len(qs) and len(mu)==31
            assert all(type(a) is int for a in lam+mu) and min(mu)>=0
            objective=sum(lam)+sum(mu)
            assert objective==dual['bound']
            for q,a in zip(qs,lam):
                for p,b in zip(ps,mu):
                    assert a+b>=2*mcap(p,q)-ell*p
                    inequalities+=1
            best=max(best,objective);duals+=1
        upper=ell*w*(w-1)//2+best
        assert upper==r['upper_doubled']
        bounds[key]=upper
    assert set(bounds)==needed
    remaining=set(surviving)
    for rec in candidates:
        ws=tuple(rec['weights']);ell=rec['cutoff']
        assert ws in remaining
        hs=tuple(sorted(v//2 for v in ws if v//2>ell))
        plain=2*sum(mcap(a,b) for i,a in enumerate(hs) for b in hs[:i])
        losses=[];light=[]
        for w in ws:
            if w//2<=ell:
                row=bounds[w,ell,hs];plain+=row;light.append(row)
            else:
                ns=list(hs);ns.remove(w//2);ns=tuple(ns)
                row=bounds[w,0,ns]
                assert row%2==0
                loss=sum(mcap(w//2,q) for q in ns)-row//2
                assert loss>=0
                losses.append(loss)
        correction=2*max(max(losses,default=0),(sum(losses)+1)//2)
        upper=plain-correction
        assert plain==rec['plain_doubled'] and correction==rec['correction_doubled']
        assert upper==rec['upper_doubled']<THRESHOLD
        assert losses==rec['heavy_losses'] and light==rec['light_bounds']
        remaining.remove(ws)
    initial=indexed(read_records(HERE/'support18_after_round2.jsonl'))
    assert set(initial)==remaining and len(remaining)==285
    for ws,rec in initial.items():
        assert rec['quota_bound_doubled']==surviving[ws]
    report(stage='inherited_spectrum_duals',excluded=217,survivors=285,
           local_keys=len(bounds),duals=duals,integer_inequalities=inequalities)
    return remaining,spectra,dict(local_keys=len(bounds),duals=duals,
                                  integer_inequalities=inequalities)


def replay_new_stages(remaining):
    stage_counts=[]
    all_cuts={}

    def stage(name,filename,survivor_filename,checker,expected):
        nonlocal remaining
        rows=indexed(read_records(HERE/filename))
        assert set(rows)==remaining
        excluded=set()
        for ws,rec in rows.items():
            if checker(rec):
                excluded.add(ws)
        assert len(excluded)==expected,(name,len(excluded),expected)
        remaining-=excluded
        declared=indexed(read_records(HERE/survivor_filename))
        assert set(declared)==remaining
        for ws in excluded:
            assert ws not in all_cuts
            all_cuts[ws]=name
        stage_counts.append(dict(stage=name,input=len(rows),excluded=len(excluded),
                                 remaining=len(remaining),
                                 cuts_by_maximum=dict(sorted(Counter(w[0] for w in excluded).items()))))
        report(**stage_counts[-1])

    def gap(rec):
        w=tuple(rec['weights']);hs=tuple(v//2 for v in w[:8]);ls=w[8:]
        ell=max(v//2 for v in ls)
        hp=tuple((c,0) for c in hs)
        full=[resource_row(v,hp,ell,v*(v-1)//2,quota(v),8) for v in ls]
        half=[resource_row(v,hp,ell,v*v//4,quota(v),6) for v in ls]
        assert ell==rec['cutoff'] and full==rec['full_rows'] and half==rec['halfspace_rows']
        assert sum(full)==rec['full_missing_capacity_doubled']
        assert sum(half)==rec['halfspace_missing_capacity_doubled']
        cut=sum(full)<288 and sum(half)<192
        assert cut==rec['excluded']
        return cut
    stage('eight_heavy_missing_gap','EIGHT_HEAVY_GAP_SCREEN.jsonl',
          'support18_after_gap.jsonl',gap,188)

    @lru_cache(None)
    def three_row(v,hs,ell,maxima):
        c=v//2;mass=v*(v-1)//2
        return ell*mass+max(sum(2*mcap(x,h)-ell*x for x,h in zip(xs,hs))
                            for xs in product(range(c+1),repeat=3)
                            if sum(xs)<=mass and sum(x==c for x in xs)<=maxima)

    def three(rec):
        w=tuple(rec['weights']);hs=tuple(v//2 for v in w[:3]);ls=w[3:]
        ell=max(v//2 for v in ls)
        upper=2*sum(mcap(a,b) for i,a in enumerate(hs) for b in hs[:i])
        uplifts=[];rows=[]
        for v in ls:
            q=quota(v)
            restricted=three_row(v,hs,ell,2 if q==3 else q)
            unrestricted=three_row(v,hs,ell,q)
            rows.append(dict(weight=v,restricted=restricted,unrestricted=unrestricted))
            upper+=restricted
            if q==3:
                uplifts.append(unrestricted-restricted)
        uplift=max(uplifts,default=0);upper+=uplift
        assert rows==rec['period3_rows'] and ell==rec['period3_cutoff']
        assert uplift==rec['period3_single_uplift']
        assert upper==rec['period3_upper_doubled']
        return upper<992
    stage('three_heavy_single_exception','THREE_HEAVY_PERIOD_SCREEN.jsonl',
          'support18_after_period3.jsonl',three,12)

    triples=regenerate_plane_triples()
    def two(rec):
        w=tuple(rec['weights']);h1,h2=w[0]//2,w[1]//2;ls=w[2:]
        ell=max(v//2 for v in ls)
        rows=[]
        for v in ls:
            mass=v*(v-1)//2
            row=max((ell*(mass-t)+2*mcap(p,h1)+2*mcap(q,h2)-ell*(p+q),(p,q,t))
                    for p,q,t in triples[v])
            rows.append([row[0],list(row[1])])
        upper=sum(row[0] for row in rows)
        assert rows==rec['two_heavy_deleted_rows'] and ell==rec['two_heavy_deleted_cutoff']
        assert upper==rec['two_heavy_deleted_upper_doubled']
        return upper<960
    stage('two_heavy_deleted_direction','TWO_HEAVY_DELETED_DIRECTION_SCREEN.jsonl',
          'support18_after_twoheavy.jsonl',two,13)

    def eight_prices(rec,khalf):
        full=check_priced_branch(rec,8,False,8,'slot_full',9)
        half=check_priced_branch(rec,8,True,khalf,'slot_half',6)
        cut=full<288 and half<192
        assert cut==rec['slot_excluded']
        return cut
    stage('eight_heavy_slot_prices','EIGHT_HEAVY_SLOT_PRICE_SCREEN.jsonl',
          'support18_after_slots.jsonl',lambda r:eight_prices(r,6),42)
    stage('missing_six_three_neighbors','THREE_NEIGHBOR_SLOT_PRICE_SCREEN.jsonl',
          'support18_after_three_neighbor.jsonl',lambda r:eight_prices(r,3),12)

    def nine(rec):
        return check_priced_branch(rec,9,False,9,'nine_heavy',3)<96
    stage('nine_heavy_slot_prices','NINE_HEAVY_SLOT_PRICE_SCREEN.jsonl',
          'support18_after_nine_heavy.jsonl',nine,1)

    def bonus(rec):
        w=tuple(rec['weights']);hs=w[:8];ls=w[8:]
        assert max(v//2 for v in ls)<=8
        mass=sum(v*v//4 for v in ls)
        caps=sorted((v//2 for v in ls),reverse=True)
        x=sum(caps[:6]);details=[]
        for v in hs:
            c=v//2
            if c>4:
                q=min(6,(quota(v)+1)//2);y=sum(caps[:q])
                details.append(dict(weight=v,maximal_directions_in_halfspace=q,
                                    pair_mass_upper=x,maximal_direction_pair_mass_upper=y,
                                    bonus=(c-5)*x+y))
        upper=4*mass+sum(row['bonus'] for row in details)
        assert mass==rec['halfspace_low_pair_mass_upper']
        assert details==rec['halfspace_period_bonuses']
        assert upper==rec['halfspace_period_bonus_capacity']
        # Replay the inherited full branch rather than trusting the recorded value.
        full=check_priced_branch(rec,8,False,8,'slot_full',9)
        return full<288 and upper<96
    stage('halfspace_maximal_direction_bonus','HALFSPACE_MAXIMAL_DIRECTION_BONUS_SCREEN.jsonl',
          'support18_after_period_bonus.jsonl',bonus,8)

    def sumfree(rec):
        return check_priced_branch(rec,9,False,9,'nine_heavy',3,sumfree=True)<96
    stage('nine_heavy_sumfree_resource','NINE_HEAVY_SUMFREE_PRICE_SCREEN.jsonl',
          'support18_after_sumfree9.jsonl',sumfree,1)
    return remaining,stage_counts,all_cuts


def final_analytic_stage(remaining,spectra):
    rows=indexed(read_records(HERE/'FINAL_ANALYTIC_SUPPORT18_CERTIFICATES.jsonl'))
    assert set(rows)==remaining and len(rows)==8
    energy={w:max(sum(p*p*n for p,n in enumerate(hist)) for hist in hs)
            for w,hs in spectra.items()}
    for w,b in ((2,1),(3,3),(4,12),(5,16),(6,33),(8,112),(12,300)):
        assert energy[w]==b
    # Inspect every actual local spectrum, not just the asserted formula for H.
    for r in (5,6):
        for w in (2,3,4,5,6,8,12):
            claimed=5*r if w in (8,12) else r+3 if w==6 else 3 if w in (4,5) else 0
            for hist in spectra[w]:
                gains=sorted((max(0,2*min(16,4*p)-p*p-11)
                              for p,n in enumerate(hist) for _ in range(n)),reverse=True)
                assert sum(gains[:r])<=claimed
    assert max(sum(p*p*n for p,n in enumerate(hist))
               for hist in spectra[8] if hist[4]!=7)==70
    c=(12,)+(8,)*6+(6,6,4,3)+(2,)*7
    d=(12,)+(8,)*6+(6,5,5,3)+(2,)*7
    e=(12,)+(8,)*6+(6,5,4,4)+(2,)*7
    b16=(16,)+(8,)*6+(5,4,4)+(2,)*8
    counts=Counter()
    cube_upper=[]
    for ws,rec in rows.items():
        assert rec['excluded'] is True
        method=rec['method'];counts[method]+=1
        if method=='cube_direction_energy':
            assert ws in (c,d,e)
            total=sum(energy[w] for w in ws)
            assert total==rec['unrestricted_energy']
            assert total-84==rec['energy_with_two_noncubes']<992
            assert len(rec['branches'])==2
            for r,branch in zip((5,6),rec['branches']):
                assert branch['cubes']==r
                other=list(ws)
                for _ in range(r):other.remove(8)
                er=sum(70 if w==8 else energy[w] for w in other)
                gain=sum(5*r if w in (8,12) else r+3 if w==6 else 3 if w in (4,5) else 0
                         for w in other)
                upper=er+77*r+10*(r*r//4)+gain
                assert er==branch['residual_energy'] and gain==branch['surplus_doubled']
                assert upper==branch['upper_doubled']<992
                cube_upper.append(upper)
        elif method=='ten_heavy_weak_unique_directions':
            hs=ws[:10];ls=ws[10:]
            assert hs[0]==12 and all(v//2<=4 for v in hs[1:])
            assert all(v<=3 for v in ls)
            weak=sum(v//2<=3 for v in hs)
            mass=sum(v*(v-1)//2 for v in ls)
            demand=min(4*r+weak*max(0,3-r) for r in range(32))
            assert demand==min(3*weak,12)
            assert weak==rec['weak_vertices'] and mass==rec['light_pair_mass']
            assert demand==rec['required_pair_mass'] and mass<demand
            assert mcap(3,6)==14 and mcap(3,3)+6<16 and 6+4+4<16
        elif method=='hub16_equality_actual_sumset':
            assert ws==b16
            ls=ws[8:]
            full_mass=sum(v*(v-1)//2 for v in ls)
            all_cap=sum(v//2 for v in ls)
            full=4*full_mass+4*all_cap
            half_mass=sum(v*v//4 for v in ls)
            top6=sum(sorted((v//2 for v in ls),reverse=True)[:6])
            half=4*half_mass+4*top6
            assert full==rec['missing9_capacity_upper']==128<144
            assert half==rec['missing6_capacity_upper']==96
            assert rec['hub_pair_counts']==[8]*6
            assert rec['forced_light4_edge_product']==16
            assert rec['forced_light4_edge_actual']==8
        else:
            raise AssertionError(method)
    assert counts=={'cube_direction_energy':3,'ten_heavy_weak_unique_directions':4,
                    'hub16_equality_actual_sumset':1}
    report(stage='final_analytic_boundaries',excluded=8,remaining=0,
           methods=dict(counts),maximum_cube_upper_doubled=max(cube_upper))
    return dict(counts),cube_upper


def run():
    survivors,by_max,cutoffs=initial_quota_stage()
    remaining,spectra,duals=inherited_spectrum_stage(survivors)
    remaining,stages,cuts=replay_new_stages(remaining)
    methods,cube_upper=final_analytic_stage(remaining,spectra)
    assert len(cuts)==277 and len(remaining)==8
    proof_dependencies=[
        HERE/'RESOURCE_COMPATIBILITY_LEMMAS.md',
        HERE/'CUBE_ENERGY_SUPPORT18_EXCLUSIONS.md',
        HERE/'BOUNDARY16_ACTUAL_SUMSET_EXCLUSION.md',
        OLD/'DIFFERENCE_AND_LIGHT_RESOURCE_LEMMAS.md',
        OLD/'HALFSPACE_ENERGY_THROUGH_EIGHTEEN.md',
        OLD/'GLOBAL_SUPPORT_REDUCTION_PROOF.md',
        OLD/'MIDDLE_MAXIMA_SUPPORT_THEOREM.md',
        OLD/'MIDDLE_MAXIMA_SUPPORT_COMPLETION.json',
        BASE/'research_round2/structural/m11_support/M11_SUPPORT_AT_MOST_SEVENTEEN.md',
        ROOT2/'CUBE_FIBRE_EDGE_CAPACITY_THEOREM.txt',
        Path(__file__).resolve(),
    ]
    DEPENDENCIES.update(proof_dependencies)
    result=dict(status='PASS',scope='dimension five, both rings, total weight <=93, maximum12..18',
                normalization='remove singleton fibres, then enlarge existing fibres to total93 without exceeding the given maximum',
                support_checked=18,all_weight_partitions=239246,
                partitions_by_maximum=by_max,quota_cuts=238744,
                quota_first_successful_cutoffs=cutoffs,quota_survivors=502,
                inherited_exact_spectrum_cuts=217,inherited_spectrum_dual_replay=duals,
                round3_input_profiles=285,round3_resource_cuts=277,
                round3_final_analytic_cuts=8,round3_final_methods=methods,
                remaining_weight_profiles=0,stages=stages,
                final_cube_branch_uppers_doubled=cube_upper,
                conclusion='Together with the frozen round2 support>=19 theorem: maximum12..18 implies support<=17.',
                caveat='No exclusion is claimed for middle maxima on support17 or lower; no proof of the full94 lower bound is claimed.',
                dependencies={str(p.relative_to(BASE)):sha(p) for p in sorted(DEPENDENCIES)},
                seconds=round(time.monotonic()-START,3))
    (HERE/'MIDDLE_SUPPORT18_INDEPENDENT_REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
    report(status='PASS',partitions=239246,round3_new_exclusions=285,remaining=0,
           conclusion='middle maxima12..18 imply support<=17')


if __name__=='__main__':
    run()
