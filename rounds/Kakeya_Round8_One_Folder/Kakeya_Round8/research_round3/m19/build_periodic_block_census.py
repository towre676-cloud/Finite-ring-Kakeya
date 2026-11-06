"""Exact own-periodic block spectra via subsets of the four-dimensional quotient."""
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
out={w:{} for w in range(2,20,2)};counts={w:0 for w in range(2,20,2)}
for mask in range(1<<16):
    c=mask.bit_count()
    if not 1<=c<=9:continue
    w=2*c;counts[w]+=1;points=[x for x in range(16) if mask>>x&1];pairs=[0]*16
    for i,x in enumerate(points):
        for y in points[:i]:pairs[x^y]+=1
    hist=[0]*10
    for d in range(1,16):hist[2*pairs[d]]+=1
    out[w].setdefault(tuple(hist),{'hist':hist,'quotient_mask':mask})
result={'quotient_dimension':4,'method':'Every subset of F2^4 of cardinality1 through9; periodic block maxima are twice quotient pair counts','subset_counts':counts,'weights':{str(w):[v for h,v in sorted(rows.items())] for w,rows in out.items()}}
(HERE/'OWN_PERIODIC_BLOCK_CENSUS.json').write_text(json.dumps(result,indent=2)+'\n')
with(HERE/'own_periodic_blocks.hpp').open('w') as f:
    f.write('#pragma once\n#include <map>\n#include <array>\n#include <vector>\ninline const std::map<int,std::vector<std::array<int,10>>> own_period_blocks={\n')
    for w,rows in out.items():f.write('{'+str(w)+',{'+','.join('{{'+','.join(map(str,h))+'}}' for h in sorted(rows))+'}},\n')
    f.write('};\n')
print(json.dumps({'quotient_subsets':sum(counts.values()),'block_spectrum_counts':{w:len(rows) for w,rows in out.items()}}))
