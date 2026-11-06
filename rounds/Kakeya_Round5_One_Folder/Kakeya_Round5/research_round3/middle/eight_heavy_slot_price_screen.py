from pathlib import Path
from functools import lru_cache
from collections import Counter
from itertools import product
import json
HERE=Path(__file__).resolve().parent
M=lambda p,q:max(p,q)+8 if min(p,q)==3 and max(p,q) in(5,6,7) else min(16,p*q)
quota=lambda w:(w&-w)-1 if w%2==0 else max((w-1)&-(w-1),(w+1)&-(w+1))-1
@lru_cache(None)
def row(w,hp,ell,half):
 c=w//2;m=w*w//4 if half else w*(w-1)//2;rr=6 if half else 8;qr=quota(w)
 dp={(0,0,0):0}
 for h,price in hp:
  nxt={}
  for(u,f,k),score in dp.items():
   for x in range(min(c,m-u)+1):
    ff=f+(x==c);kk=k+(x>0)
    if ff>qr or kk>rr:continue
    key=(u+x,ff,kk);v=score+2*M(x,h)-ell*x-price*(x>0)
    if v>nxt.get(key,-100000):nxt[key]=v
  dp=nxt
 return ell*m+max(dp.values())
def best(w,half):
 hs=tuple(v//2 for v in w[:8]);ls=w[8:];ell=max(v//2 for v in ls);n=sum(h>4 for h in hs);r=6 if half else 9
 best=(10**8,None,None)
 for vals in product(range(0,21,2),repeat=n):
  prices=vals+(0,)*(8-n)
  if not half and sum(prices)>32:continue
  hp=tuple(zip(hs,prices));rows=[row(v,hp,ell,half) for v in ls]
  upper=sum(rows)+r*sum(prices)
  if upper<best[0]:best=(upper,prices,rows)
 return best
if __name__=='__main__':
 records=[];cuts=[];remaining=[]
 for line in(HERE/'support18_after_twoheavy.jsonl').open():
  rec=json.loads(line);w=rec['weights'];full=best(w,False);half=best(w,True)
  out=dict(rec,slot_full_upper_doubled=full[0],slot_full_prices=full[1],slot_full_rows=full[2],slot_half_upper_doubled=half[0],slot_half_prices=half[1],slot_half_rows=half[2])
  excluded=full[0]<288 and half[0]<192;out['slot_excluded']=excluded
  records.append(out);(cuts if excluded else remaining).append(out)
 (HERE/'EIGHT_HEAVY_SLOT_PRICE_SCREEN.jsonl').write_text(''.join(json.dumps(r,separators=(',',':'))+'\n' for r in records))
 (HERE/'support18_after_slots.jsonl').write_text(''.join(json.dumps(r,separators=(',',':'))+'\n' for r in remaining))
 print('cuts',len(cuts),Counter(r['maximum'] for r in cuts),'remaining',len(remaining),Counter(r['maximum'] for r in remaining))
 for r in remaining:print(r['maximum'],r['weights'],r['slot_full_upper_doubled'],r['slot_half_upper_doubled'])
