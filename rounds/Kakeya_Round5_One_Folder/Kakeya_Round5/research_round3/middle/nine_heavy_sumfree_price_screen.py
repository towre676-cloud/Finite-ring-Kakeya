from pathlib import Path
from functools import lru_cache
from collections import Counter
from itertools import product
import json
HERE=Path(__file__).resolve().parent
M=lambda p,q:max(p,q)+8 if min(p,q)==3 and max(p,q) in(5,6,7) else min(16,p*q)
quota=lambda w:(w&-w)-1 if w%2==0 else max((w-1)&-(w-1),(w+1)&-(w+1))-1
@lru_cache(None)
def row(w,hp,ell):
 c=w//2;m=w*w//4;qr=(quota(w)+1)//2
 dp={(0,0):0}
 for h,price in hp:
  nxt={}
  for(u,f),score in dp.items():
   for x in range(min(c,m-u)+1):
    ff=f+(x==c)
    if ff>qr:continue
    key=(u+x,ff);v=score+2*M(x,h)-ell*x-price*(x>0)
    if v>nxt.get(key,-100000):nxt[key]=v
  dp=nxt
 return ell*m+max(dp.values())
def best(w):
 hs=tuple(v//2 for v in w[:9]);ls=w[9:];ell=max(v//2 for v in ls);n=sum(h>4 for h in hs)
 ans=(10**8,None,None)
 for vals in product(range(0,21,2),repeat=n):
  prices=vals+(0,)*(9-n)
  if sum(prices)>32:continue
  hp=tuple(zip(hs,prices));rows=[row(v,hp,ell) for v in ls];upper=sum(rows)+3*sum(prices)
  if upper<ans[0]:ans=(upper,prices,rows)
 return ans
if __name__=='__main__':
 out=[];cuts=[];remaining=[]
 for line in(HERE/'support18_after_period_bonus.jsonl').open():
  rec=json.loads(line);b=best(rec['weights']);r=dict(rec,nine_heavy_upper_doubled=b[0],nine_heavy_prices=b[1],nine_heavy_rows=b[2]);out.append(r)
  (cuts if b[0]<96 else remaining).append(r)
 (HERE/'NINE_HEAVY_SUMFREE_PRICE_SCREEN.jsonl').write_text(''.join(json.dumps(r,separators=(',',':'))+'\n' for r in out))
 (HERE/'support18_after_sumfree9.jsonl').write_text(''.join(json.dumps(r,separators=(',',':'))+'\n' for r in remaining))
 print('cuts',len(cuts),Counter(r['maximum'] for r in cuts),'remaining',len(remaining),Counter(r['maximum'] for r in remaining))
 for r in remaining:print(r['maximum'],r['weights'],r['nine_heavy_upper_doubled'])
