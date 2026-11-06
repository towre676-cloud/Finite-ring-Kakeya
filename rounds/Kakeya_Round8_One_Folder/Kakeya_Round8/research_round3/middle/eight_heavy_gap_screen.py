from pathlib import Path
from functools import lru_cache
from collections import Counter
import json
HERE=Path(__file__).resolve().parent
M=lambda p,q:max(p,q)+8 if min(p,q)==3 and max(p,q) in(5,6,7) else min(16,p*q)
quota=lambda w:(w&-w)-1 if w%2==0 else max((w-1)&-(w-1),(w+1)&-(w+1))-1
@lru_cache(None)
def local(w,hs,ell,half):
 c=w//2;m=w*w//4 if half else w*(w-1)//2;rr=6 if half else 8;qr=quota(w)
 dp={(0,0,0):0}
 for h in hs:
  nxt={}
  for(u,f,k),score in dp.items():
   for x in range(min(c,m-u)+1):
    ff=f+(x==c);kk=k+(x>0)
    if ff>qr or kk>rr:continue
    state=(u+x,ff,kk);v=score+2*M(x,h)-ell*x
    if v>nxt.get(state,-100000):nxt[state]=v
  dp=nxt
 return ell*m+max(dp.values())
def capacity(w,half):
 hs=tuple(v//2 for v in w[:8]);ls=w[8:];ell=max(v//2 for v in ls)
 vals=[local(v,hs,ell,half) for v in ls]
 return sum(vals),ell,vals
out=[];cut=[];rem=[]
for l in(HERE/'support18_after_round2.jsonl').open():
 r=json.loads(l);w=r['weights'];full=capacity(w,False);half=capacity(w,True)
 c=dict(r,full_missing_capacity_doubled=full[0],halfspace_missing_capacity_doubled=half[0],cutoff=full[1],full_rows=full[2],halfspace_rows=half[2])
 c['excluded']=full[0]<32*9 and half[0]<32*6
 out.append(c);(cut if c['excluded'] else rem).append(c)
(HERE/'EIGHT_HEAVY_GAP_SCREEN.jsonl').write_text(''.join(json.dumps(r,separators=(',',':'))+'\n' for r in out))
(HERE/'support18_after_gap.jsonl').write_text(''.join(json.dumps(r,separators=(',',':'))+'\n' for r in rem))
print('cuts',len(cut),Counter(r['maximum'] for r in cut),'remaining',len(rem),Counter(r['maximum'] for r in rem))
for r in rem[:20]:print(r['maximum'],r['weights'],r['full_missing_capacity_doubled'],r['halfspace_missing_capacity_doubled'])
