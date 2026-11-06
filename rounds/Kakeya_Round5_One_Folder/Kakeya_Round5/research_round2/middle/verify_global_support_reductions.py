"""Independent exhaustive verifier: standard-library only, no producer result trusted."""
from functools import lru_cache
from collections import Counter,defaultdict
import json, pathlib, time, hashlib
ROOT=pathlib.Path(__file__).resolve().parent

def cap(a,b):
    ans=min(16,a*b)
    if min(a,b)==3 and 5<=max(a,b)<=7: ans=min(ans,max(a,b)+8)
    return ans

def quota(w):
    low=lambda x:x&-x
    return low(w)-1 if w%2==0 else max(low(w-1),low(w+1))-1

@lru_cache(None)
def local(w, neighbours, ell):
    c=w//2; mass=w*(w-1)//2; qr=quota(w)
    # Backward recursion chooses selected direction counts; unused mass is permitted.
    @lru_cache(None)
    def rec(pos,left,fullleft):
        if pos==len(neighbours): return 0
        h=neighbours[pos]
        return max(2*cap(t,h)-ell*t+rec(pos+1,left-t,fullleft-(t==c))
                   for t in range(min(c,left)+1) if t<c or fullleft)
    return ell*mass+rec(0,min(mass,c*len(neighbours)),min(qr,len(neighbours)))

def bound(weights,ell):
    hist=Counter(weights)
    heavy=tuple(sorted(w//2 for w in weights if w//2>ell))
    baseline=sum(2*cap(p,q) for i,p in enumerate(heavy) for q in heavy[:i])
    light=sum(cnt*local(w,heavy,ell) for w,cnt in hist.items() if w//2<=ell)
    losses=[]
    for w,cnt in hist.items():
        if w//2<=ell:continue
        ns=list(heavy);ns.remove(w//2);ns=tuple(ns)
        row=local(w,ns,0)
        assert row%2==0
        loss=sum(cap(w//2,h) for h in ns)-row//2
        assert loss>=0
        losses.extend([loss]*cnt)
    correction=max(max(losses,default=0),(sum(losses)+1)//2)
    return baseline+light-2*correction

def partitions(left,total,maxpart,prefix=()):
    if left==0:
        if total==0:yield prefix
        return
    low=max(2,(total+left-1)//left)
    high=min(maxpart,total-2*(left-1))
    for w in range(low,high+1):
        yield from partitions(left-1,total-w,w,prefix+(w,))

def run():
    start=time.monotonic(); table=[]
    limits={12:21,13:21,14:20,15:20,16:20,17:19,18:19}
    aggregate=defaultdict(lambda:{'profiles':0,'max_certified_upper_doubled':0,'cutoffs':Counter()})
    for s in range(32,18,-1):
        scanned=0
        for weights in partitions(s,93,18):
            m=weights[0]
            if m not in limits or s<limits[m]:continue
            scanned+=1
            for ell in (2,3,1,4,0,5,6,7,8,9):
                b=bound(weights,ell)
                if b<992:break
            else:raise AssertionError(('NOT_EXCLUDED',weights))
            rec=aggregate[s,m];rec['profiles']+=1;rec['max_certified_upper_doubled']=max(rec['max_certified_upper_doubled'],b);rec['cutoffs'][ell]+=1
        print(json.dumps({'support_finished':s,'verified_profiles':scanned,'local_keys':local.cache_info().currsize,'elapsed_seconds':round(time.monotonic()-start,3)}),flush=True)
    for (s,m),r in sorted(aggregate.items()):
        r=dict(r);r['cutoffs']=dict(sorted(r['cutoffs'].items()));table.append(dict(support=s,maximum=m,**r))
    result={'status':'PASS','scope':'n5,both target rings,total<=93,maximum12..18','support_exclusion_thresholds':limits,'proof_obligation_doubled':992,'total_verified_profiles':sum(r['profiles'] for r in table),'records':table,'local_optimization_keys':local.cache_info().currsize,'seconds':time.monotonic()-start}
    (ROOT/'GLOBAL_SUPPORT_INDEPENDENT_REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':'PASS','verified_profiles':result['total_verified_profiles'],'seconds':result['seconds']}),flush=True)
if __name__=='__main__':run()
