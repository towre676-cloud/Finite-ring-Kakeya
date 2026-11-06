from pathlib import Path
from collections import Counter
import json
import hashlib

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'research_sources/extracted/Kakeya_Reconciled_Proofs_2026-10-27/halfspace_extension/M11_BOUNDED_GEOMETRIC_REDUCTION.json'
shapes=json.loads(SOURCE.read_text())['all_support_records'];result={}
for s in(11,12):
    records=[];hist=Counter()
    for r in shapes:
        if r['support_size']!=s:continue
        S=set(r['support'])
        if len({x^y for x in S for y in S})<32:continue
        for h in S:
            T={x^h for x in S};vs=sorted(T-{0})
            deg=[sum((a^b)not in T for b in vs if b!=a) for a in vs]
            hist[tuple(sorted(deg))]+=1
            records.append({'orbit':r['global_orbit'],'hub':h,'vertices':vs,'outside_degrees':deg,'edges':[[a,b] for i,a in enumerate(vs) for b in vs[:i] if(a^b)not in T]})
    result[str(s)]={'hub_marked_cases':len(records),'degree_patterns':[{'degrees':list(ds),'multiplicity':k} for ds,k in sorted(hist.items())],'records':records}
(HERE/'OUTSIDE_SUPPORT_DEGREE_PATTERNS.json').write_text(json.dumps(result,indent=2)+'\n')
manifest={'source_path':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'source_affine_orbits':len(shapes),'degree_census_completeness':'Inherited382 orbit census; direct normalized support census can independently verify.'}
(HERE/'DEGREE_CENSUS_SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
with(HERE/'outside_degree_patterns.hpp').open('w') as f:
    f.write('#pragma once\n#include <vector>\n#include <map>\ninline const std::map<int,std::vector<std::vector<int>>> outside_degree_patterns = {\n')
    for s in(11,12):f.write('{'+str(s)+',{'+','.join('{'+','.join(map(str,r['degrees']))+'}' for r in result[str(s)]['degree_patterns'])+'}},\n')
    f.write('};\n')
