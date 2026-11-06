"""Exact controls for the full-hub outer-cap12 theorem in all n>=6."""
from pathlib import Path
from functools import lru_cache
from fractions import Fraction
import hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
source=ROOT/'research_round2/geometric/PAIR_SPECTRUM_CENSUS.json'
census=json.loads(source.read_text())
expected={2:1,3:3,4:12,5:16,6:33,7:63,8:112,9:120,10:153,11:211,12:300}
energies={};witnesses={}
for w in range(2,13):
    entries=census['weights'][str(w)]
    energy=lambda row:sum(p*p*num for p,num in enumerate(row['hist']))
    best=max(entries,key=energy);energies[w]=energy(best)
    assert energies[w]==expected[w]
    A={x for x in range(32) if best['mask']>>x&1}
    counts=[len(A&{x^d for x in A})//2 for d in range(1,32)]
    assert len(A)==w and sum(p*p for p in counts)==energies[w]
    witnesses[str(w)]=sorted(A)
    if w>=7:assert w*(w-1)//2+6*((1<<(w-7))-1)<energies[w]

def quota(w):
    values=[w] if w%2==0 else [w-1,w+1]
    return max(x&-x for x in values)-1

assert all(Fraction(energies[w]-1,w-2)<=Fraction(299,10) for w in range(3,13))
assert Fraction(294,5)+Fraction(289,60)==Fraction(3817,60)<64
rows=[]
for z in range(2,13):
    restricted={w:min(energies[w],min(z,quota(w))*(w//2)**2+max(0,z-quota(w))*(w//2-1)**2) for w in range(2,13)}
    B=2*z;forward=[0]*(B+1)
    for b in range(1,B+1):
        forward[b]=max([forward[b-1]]+[forward[b-w+2]+restricted[w]-1 for w in range(3,13) if w-2<=b])
    @lru_cache(None)
    def by_types(w,b):
        if w==13:return 0
        cost=w-2
        return max(k*(restricted[w]-1)+by_types(w+1,b-k*cost) for k in range(b//cost+1))
    independent=by_types(3,B)
    assert forward[B]==independent
    need=64*(z-1)+z+1
    assert independent<need
    rows.append({'low_residues':z,'excess_budget':B,'energy_gain_upper':independent,'required_at_N64':need,'strict_gap':need-independent,'restricted_energies':restricted})
assert [r['energy_gain_upper'] for r in rows]==[14,47,74,157,193,239,343,409,564,609,630]
out={'status':'PASS','theorem':'n>=6, full hub, all outer fibres<=12 => |K|>=3*2^n-2; equality exactly generalized stars','spectrum_census_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'census_completeness_dependency':'research_round2/root/ROOT_VERIFIED_PAIR_SPECTRUM_CENSUS.json','dimension_free_energy_maxima':energies,'attaining_F2_5_sets':witnesses,'small_z_rows':rows,'large_z_cutoff':13,'large_z_N_upper':'3817/60 <64','scope':'Exact finite controls plus the separate analytic proof; no unrestricted Kakeya claim.'}
(HERE/'FULL_HUB_TWELVE_CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'status':out['status'],'energy_maxima':energies,'z_rows':len(rows),'minimum_small_z_gap':min(r['strict_gap'] for r in rows)},indent=2))
