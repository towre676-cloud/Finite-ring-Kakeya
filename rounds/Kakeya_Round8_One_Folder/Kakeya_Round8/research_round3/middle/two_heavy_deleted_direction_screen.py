from pathlib import Path
from collections import defaultdict,Counter
from functools import lru_cache
import json
HERE=Path(__file__).resolve().parent
M=lambda p,q:max(p,q)+8 if min(p,q)==3 and max(p,q) in(5,6,7) else min(16,p*q)
triples=defaultdict(set)
for a in range(9):
 for b in range(9-a):
  for c in range(9-a-b):
   for d in range(9-a-b-c):
    for e in range(9-a-b-c-d):
     for f in range(9-a-b-c-d-e):
      w=4*a+3*b+2*(c+d+e)+f
      triples[w].add((2*a+b+c,2*a+b+d,2*a+b+e))
@lru_cache(None)
def row(w,h1,h2,ell):
 b=w*(w-1)//2
 scores=[(ell*(b-t)+2*M(p,h1)+2*M(q,h2)-ell*(p+q),(p,q,t)) for p,q,t in triples[w]]
 return max(scores)
cut=[];rem=[];out=[]
for line in(HERE/'support18_after_period3.jsonl').open():
 r=json.loads(line);w=r['weights'];h1,h2=w[0]//2,w[1]//2;ls=w[2:];ell=max(v//2 for v in ls)
 vals=[row(v,h1,h2,ell) for v in ls];upper=sum(v[0] for v in vals)
 c=dict(r,two_heavy_deleted_upper_doubled=upper,two_heavy_deleted_cutoff=ell,two_heavy_deleted_rows=vals);out.append(c)
 (cut if upper<960 else rem).append(c)
(HERE/'TWO_HEAVY_DELETED_DIRECTION_SCREEN.jsonl').write_text(''.join(json.dumps(r,separators=(',',':'))+'\n' for r in out))
(HERE/'support18_after_twoheavy.jsonl').write_text(''.join(json.dumps(r,separators=(',',':'))+'\n' for r in rem))
(HERE/'BINARY_PLANE_PAIR_TRIPLES.json').write_text(json.dumps({w:sorted(vs) for w,vs in triples.items()},separators=(',',':'))+'\n')
print('cuts',len(cut),Counter(r['maximum'] for r in cut),'remaining',len(rem),Counter(r['maximum'] for r in rem))
for r in rem[:30]:print(r['maximum'],r['weights'],r['two_heavy_deleted_upper_doubled'])
