"""Independent small support controls; analytic proofs are separate."""
import itertools,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];records=[]
for w in(8,9):
 counts={};maxdiff=0;total=0;extremal=0
 for r in range(1,6):
  basis={0,*[1<<i for i in range(r)]}
  need=w-len(basis);opts=sorted(set(range(1<<r))-basis)
  if not 0<=need<=len(opts):continue
  for tail in itertools.combinations(opts,need):
   T=basis|set(tail);diff={x^y for x,y in itertools.combinations(T,2)};F=set(range(1,32))-diff
   maxdiff=max(maxdiff,len(diff));counts[len(F)]=counts.get(len(F),0)+1;total+=1
   if w==8:
    assert len(F)>=6
    assert len(F)==6 or len(F)>=9
    if len(F)==6:
     extremal+=1
     chars=[u for u in range(1,32) if all((u&d).bit_count()%2==1 for d in F)]
     assert chars
     assert all((x^y) not in F for x,y in itertools.combinations(F,2))
     assert max(sum((a^d) in T for d in F) for a in range(32))<=3
   else:
    assert len(F)>=3
    if len(F)==3:
     extremal+=1;u,v,t=F;assert u^v^t
 records.append({'weight':w,'complete_normalized_sets':total,'maximum_distinct_nonzero_differences':maxdiff,'missing_count_distribution':dict(sorted(counts.items())),'extremal_sets_checked':extremal})
out={'status':'PASS','method':'all affine-basis-normalized8- and9-subsets in F2^5; unordered differences computed directly','claims':['8-points determine at most25 nonzero differences','8-point missing-direction count is6 or at least9','extremal8-point missing6 directions lie in one affine halfspace','each residue has at most3 neighbors in an extremal8-point support along its6 missing directions','9-points determine at most28 nonzero differences','extremal9-point missing3 directions are linearly independent'],'records':records}
(ROOT/'research_round2/root/ROOT_VERIFIED_SMALL_SUPPORT_GEOMETRY.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
