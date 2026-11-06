"""Independent exact replay of the complete one-heavy incidence-price family."""
from collections import Counter
from functools import lru_cache
from pathlib import Path
import hashlib,json,time
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def M(p,q):
    return max(p,q)+8 if min(p,q)==3 and 5<=max(p,q)<=7 else min(16,p*q)
def quota(w):
    return (w&-w)-1 if w%2==0 else max((w-1)&-(w-1),(w+1)&-(w+1))-1

@lru_cache(None)
def local_rows(w,heavy,ell):
    cap=w//2;mass=w*w//4;maxima=(quota(w)+1)//2
    rest=tuple(sorted(heavy[1:]))
    @lru_cache(None)
    def rec(j,left,full):
        if j==0:return 0
        return max(2*M(x,rest[j-1])-ell*x+rec(j-1,left-x,full-(x==cap))
                   for x in range(min(cap,left)+1) if x<cap or full)
    inactive=ell*mass+rec(8,mass,maxima)
    active=ell*mass+max(2*M(x,heavy[0])-ell*x+rec(8,mass-x,maxima-(x==cap))
                        for x in range(1,min(cap,mass)+1) if x<cap or maxima)
    # Adding the distinguished edge can gain at most 32-ell<=31 over
    # the inactive optimum; it also consumes resources at the other slots.
    assert active-inactive<=32-ell<=31
    return inactive,active

def rows_and_optimum(w):
    h=tuple(v//2 for v in w[:9]);ell=w[9]//2
    rows=[(v,*local_rows(v,h,ell)) for v in w[9:]]
    gain=sorted((max(0,b-a) for _,a,b in rows),reverse=True)
    optimum=sum(a for _,a,b in rows)+sum(gain[:3])
    return rows,optimum

def profiles(path):
    found={}
    for line in path.open():
        s,m,b,*w=map(int,line.split());w=tuple(w)
        assert len(w)==s and w[0]==m and sum(w)==93 and w==tuple(sorted(w,reverse=True))
        assert 10<=s<=17 and 12<=m<=18 and min(w)>=2 and w not in found
        found[w]=line
    return found

def main():
    started=time.monotonic()
    baseline=json.loads((HERE/'MIDDLE_COMPLETE_INVENTORY.json').read_text())
    assert baseline['status']=='PASS' and baseline['remaining_weight_profiles']==276267
    input_path=HERE/'after_cube_weight_survivors.txt'
    assert baseline['dependencies'][str(input_path.relative_to(ROOT))]==sha(input_path)
    initial=profiles(input_path);assert len(initial)==276267
    cuts={};rows_checked=0;prices=Counter();by=Counter()
    for cert in map(json.loads,(HERE/'PRICED_NINE_HEAVY_CUTS.jsonl').open()):
        w=tuple(cert['weights']);assert w in initial and w not in cuts
        assert cert['support']==len(w) and cert['maximum']==w[0]
        t=cert['price'];assert type(t) is int and 0<=t<=32
        rows,optimum=rows_and_optimum(w)
        assert [list(r) for r in rows]==cert['light_rows']
        value=sum(max(a,b-t) for _,a,b in rows)+3*t
        assert value==cert['upper_doubled']==optimum<96
        # Independently check the complete integer price bank against the
        # closed-form LP optimum for every credited exclusion.
        assert min((sum(max(a,b-p) for _,a,b in rows)+3*p,p) for p in range(33))==(value,t)
        cuts[w]=cert;rows_checked+=len(rows);prices[t]+=1;by[len(w),w[0]]+=1
    assert len(cuts)==512
    final_path=HERE/'after_priced_nine_survivors.txt';final=profiles(final_path)
    assert len(final)==275755 and set(final)==set(initial)-set(cuts)
    assert final_path.read_text()==''.join(line for w,line in initial.items() if w not in cuts)
    for w in final:
        assert final[w]==initial[w]
        _,optimum=rows_and_optimum(w)
        assert optimum>=96
    declared=json.loads((HERE/'PRICED_NINE_PRODUCER_COUNTS.json').read_text())
    assert (declared['input'],declared['cuts'],declared['remaining'])==(276267,512,275755)
    actual_input=Counter((len(w),w[0]) for w in initial);actual_final=Counter((len(w),w[0]) for w in final)
    records=[]
    for row in declared['records']:
        key=row['support'],row['maximum']
        assert row['input']==actual_input[key] and row['cuts']==by[key] and row['remaining']==actual_final[key]
        records.append(row)
    assert len(records)==56
    closed=[(r['support'],r['maximum']) for r in records if r['remaining']==0]
    assert closed==[(17,18)]
    unique=(18,)+(8,)*5+(7,6,6)+(2,)*8
    assert [w for w in initial if len(w)==17 and w[0]==18]==[unique]
    cert=cuts[unique];assert cert['price']==10 and cert['upper_doubled']==94
    assert cert['light_rows']==[[2,8,18]]*8
    supports=[{'support':s,'input_profiles':sum(r['input'] for r in records if r['support']==s),
               'new_cuts':sum(r['cuts'] for r in records if r['support']==s),
               'remaining_profiles':sum(r['remaining'] for r in records if r['support']==s)} for s in range(10,18)]
    deps=[HERE/'screen_priced_nine.cpp',HERE/'PRICED_NINE_HEAVY_CUTS.jsonl',HERE/'PRICED_NINE_PRODUCER_COUNTS.json',input_path,final_path,
          HERE/'MIDDLE_COMPLETE_INVENTORY.json',Path(__file__).resolve(),ROOT/'research_round3/middle/RESOURCE_COMPATIBILITY_LEMMAS.md',
          ROOT/'research_round2/middle/DIFFERENCE_AND_LIGHT_RESOURCE_LEMMAS.md']
    receipt={'status':'PASS','scope':'Full residual middle inventory after the frozen276267-profile baseline, both rings.',
             'input_profiles':276267,'new_whole_profile_exclusions':512,'remaining_weight_profiles':275755,
             'light_endpoint_rows_recomputed':rows_checked,'local_row_keys':local_rows.cache_info().currsize,
             'integer_price_histogram':dict(sorted(prices.items())),'supports':supports,'records':records,
             'new_empty_weight_cells':[{'support':s,'maximum':m} for s,m in closed],
             'new_support_theorem':'Dimension5, both rings, |K|<=93 and exact maximum18 imply pair-active support<=16, combining the earlier support>=18 exclusions.',
             'boundary_certificate':cert,
             'optimization_scope':'Complete nonnegative-real one-distinguished-heavy price family: optimum equals sum inactive bounds plus the three largest positive active gains; an integer price in0..31 attains it.',
             'inherited_scope':'All other middle56-cell inventory data is retained as a frozen preceding stage. The other55 cells remain nonempty.',
             'dependencies':{str(p.relative_to(ROOT)):sha(p) for p in deps},'seconds':time.monotonic()-started}
    (HERE/'PRICED_NINE_INDEPENDENT_REPLAY.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ['status','input_profiles','new_whole_profile_exclusions','remaining_weight_profiles','light_endpoint_rows_recomputed','local_row_keys','new_empty_weight_cells','seconds']},indent=2))

if __name__=='__main__':main()
