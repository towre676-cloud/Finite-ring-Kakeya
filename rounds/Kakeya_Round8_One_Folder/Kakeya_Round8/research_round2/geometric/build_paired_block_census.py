"""Build the distinguished-direction block-maximum census from382 frozen affine representatives."""
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'research_sources/extracted/Kakeya_Reconciled_Proofs_2026-10-27/halfspace_extension/M11_BOUNDED_GEOMETRIC_REDUCTION.json'
data=json.loads(SOURCE.read_text())
out={w:{f:{} for f in(0,1)} for w in range(2,20)}
for r in data['all_support_records']:
    w=r['support_size']
    if w not in out:continue
    pts=r['support'];pairs=[0]*32
    for i,x in enumerate(pts):
        for y in pts[:i]:pairs[x^y]+=1
    for a in range(1,32):
        hist=[0]*10
        for d in range(1,32):
            if d<(d^a):hist[max(pairs[d],pairs[d^a])]+=1
        assert sum(hist)==15
        f=int(pairs[a]>0)
        out[w][f].setdefault(tuple(hist),{'hist':hist,'mask':r['mask'],'own_direction':a,'own_pairs':pairs[a],'source_orbit':r['global_orbit']})
result={'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'source_affine_orbits':len(data['all_support_records']),'description':'Every distinguished own direction; histogram of15 paired-direction block maxima','weights':{str(w):{str(f):[v for k,v in sorted(rs.items())] for f,rs in fs.items()} for w,fs in out.items()}}
(HERE/'PAIRED_BLOCK_MAXIMUM_CENSUS.json').write_text(json.dumps(result,indent=2)+'\n')
with(HERE/'paired_block_spectra.hpp').open('w') as f:
    f.write('#pragma once\n#include <array>\n#include <vector>\ninline const std::array<std::array<std::vector<std::array<int,10>>,2>,20> block_spectra = {{\n{},{}')
    for w in range(2,20):
        f.write(',\n{{'+','.join('{'+','.join('{{'+','.join(map(str,h))+'}}' for h in sorted(out[w][flag]))+'}' for flag in(0,1))+'}}')
    f.write('\n}};\n')
print(json.dumps({w:{f:len(rs) for f,rs in fs.items()} for w,fs in out.items()}))
