from itertools import combinations
from collections import Counter
from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parent
frame=(0,1,2,4,8,16)
other=[x for x in range(32) if x not in frame]
count=0;minimum=10**9;hist=Counter();missing=Counter();witness=None
for extra in combinations(other,4):
    T=tuple(sorted(frame+extra));pairs=Counter(a^b for a,b in combinations(T,2))
    r=31-len(pairs);u={a:sum(pairs[a^b]==1 for b in T if b!=a) for a in T}
    for a in T:
        remaining=[x for x in T if x!=a]
        D={x^y for x,y in combinations(remaining,2)}
        assert len(D)==31-r-u[a]<=28
        assert u[a]>=max(0,3-r)
    weak=sorted(T,key=lambda a:(u[a],a))[:3]
    needed=4*r+sum(u[a] for a in weak)
    assert needed>=4*r+3*max(0,3-r)>=9
    if needed<minimum:
        minimum=needed;witness={'heavy_residues':T,'weak_residues':weak,'missing_directions':r,'unique_degrees':u,'required_light_mass':needed}
    hist[needed]+=1;missing[r]+=1;count+=1
assert count==14950
result={'status':'PASS','normalized_full_rank_heavy_sets_checked':count,'minimum_required_light_pair_mass':minimum,'profile_C_available_light_pair_mass':8,'profile_C_excluded':True,'required_mass_histogram':dict(sorted(hist.items())),'missing_directions_histogram':dict(sorted(missing.items())),'attaining_geometric_witness':witness,'analytic_proof_sha256':hashlib.sha256((HERE/'TEN_HEAVY_RESIDUES_AND_PROFILE_C.md').read_bytes()).hexdigest(),'scope':'Finite control of an analytic whole-profile exclusion, not an actual Kakeya construction at the lower-bound equality.'}
(HERE/'TEN_HEAVY_INCIDENCE_CONTROLS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
