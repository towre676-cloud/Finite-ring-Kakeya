from pathlib import Path
from functools import lru_cache
from collections import Counter
import json
HERE=Path(__file__).resolve().parent
M=lambda p,q:max(p,q)+8 if min(p,q)==3 and max(p,q) in(5,6,7) else min(16,p*q)
quota=lambda w:(w&-w)-1 if w%2==0 else max((w-1)&-(w-1),(w+1)&-(w+1))-1
@lru_cache(None)
def row(w,hs,ell,qmax):
 c=w//2;m=w*(w-1)//2
 @lru_cache(None)
 def opt(i,left,full):
  if i==len(hs):return 0
  return max(2*M(x,hs[i])-ell*x+opt(i+1,left-x,full-(x==c)) for x in range(min(c,left)+1) if x<c or full)
 return ell*m+opt(0,m,qmax)
records=[];cuts=[];rem=[]
for line in(HERE/'support18_after_gap.jsonl').open():
 r=json.loads(line);w=r['weights'];hs=tuple(v//2 for v in w[:3]);ls=w[3:];ell=max(v//2 for v in ls)
 base=2*sum(M(a,b) for i,a in enumerate(hs) for b in hs[:i]);details=[];uplifts=[]
 for v in ls:
  q=quota(v);val=row(v,hs,ell,min(q,2) if q==3 else q);un=row(v,hs,ell,q)
  details.append({'weight':v,'restricted':val,'unrestricted':un});base+=val
  if q==3:uplifts.append(un-val)
 upper=base+max(uplifts,default=0)
 c=dict(r,period3_upper_doubled=upper,period3_rows=details,period3_cutoff=ell,period3_single_uplift=max(uplifts,default=0));records.append(c)
 (cuts if upper<992 else rem).append(c)
(HERE/'THREE_HEAVY_PERIOD_SCREEN.jsonl').write_text(''.join(json.dumps(x,separators=(',',':'))+'\n' for x in records))
(HERE/'support18_after_period3.jsonl').write_text(''.join(json.dumps(x,separators=(',',':'))+'\n' for x in rem))
print('cuts',len(cuts),Counter(x['maximum'] for x in cuts),'remain',len(rem),Counter(x['maximum'] for x in rem))
for x in rem[:15]:print(x['maximum'],x['weights'],x['period3_upper_doubled'])
