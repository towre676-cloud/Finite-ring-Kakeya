"""Complete positive-own block histograms split by affine rank for weights6–8."""
from pathlib import Path
from itertools import combinations
import json

HERE=Path(__file__).resolve().parent
out={w:{m:{} for m in(1,2)} for w in(6,7,8)};counts={}
for r in range(3,6):
    base=[0]+[1<<i for i in range(r)];rest=sorted(set(range(1<<r))-set(base))
    for w in(6,7,8):
        k=w-len(base)
        if not 0<=k<=len(rest):continue
        count=0
        for extra in combinations(rest,k):
            A=base+list(extra);mask=sum(1<<x for x in A);ps=[0]*32
            for i,x in enumerate(A):
                for y in A[:i]:ps[x^y]+=1
            full=[ps[1:].count(v) for v in range(10)];mode=1 if r<=3 else 2
            for a in range(1,32):
                if ps[a]==0:continue
                hist=[0]*10
                for d in range(1,32):
                    if d<(d^a):hist[max(ps[d],ps[d^a])]+=1
                out[w][mode].setdefault(tuple(hist),{'hist':hist,'mask':mask,'own_direction':a,'own_pairs':ps[a],'affine_rank':r,'full_hist':full})
            count+=1
        counts[f'rank{r}_weight{w}']=count
result={'normalization':'0,e1,...,er with all extra points in F2^r; every positive own direction examined','counts':counts,'weights':{str(w):{str(m):[v for k,v in sorted(items.items())] for m,items in md.items()} for w,md in out.items()}}
(HERE/'POSITIVE_LOW_RANK_BLOCK_CENSUS.json').write_text(json.dumps(result,indent=2)+'\n')
with(HERE/'positive_low_rank_blocks.hpp').open('w') as f:
    f.write('#pragma once\n#include <map>\n#include <array>\n#include <vector>\ninline const std::map<std::pair<int,int>,std::vector<std::array<int,10>>> rank_block_spectra={\n')
    for w in(6,7,8):
        for m in(1,2):f.write('{{'+str(w)+','+str(m)+'},{'+','.join('{{'+','.join(map(str,h))+'}}' for h in sorted(out[w][m]))+'}},\n')
    f.write('};\n')
