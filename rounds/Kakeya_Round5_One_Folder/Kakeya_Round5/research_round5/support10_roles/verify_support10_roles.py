"""Separate exact checker: bitsets for supports, power-of-two edge demands.

Does not import the producer or rely on Qmax, LP, SAT, or a fibre census.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'research_round5/nine_geometry/after_nine_geometry_survivors.txt'

def enumerate_supports():
    base={0,1,2,4,8,16}; found={}
    for extra in combinations(sorted(set(range(32))-base),4):
        vertices=sorted(base|set(extra)); mask=sum(1<<x for x in vertices)
        multiplicity={d:sum(bool(mask&(1<<(x^d))) for x in vertices)//2 for d in range(1,32)}
        if 0 in multiplicity.values():continue
        unique={d for d,c in multiplicity.items() if c==1}
        deg={x:sum((x^y) in unique for y in vertices if x!=y) for x in vertices}
        assert Counter(deg.values())=={3:7,9:3}
        centers={x for x in vertices if deg[x]==9}
        leaves=set(vertices)-centers
        assert all(((a^b) in unique)==(a in centers or b in centers) for a,b in combinations(vertices,2))
        possible_origins=[]
        for origin in range(32):
            V={0}|{origin^x for x in leaves};W={0}|{origin^x for x in centers}
            if len(V)!=8 or len(W)!=4 or V&W!={0}:continue
            if any(a^b not in V for a,b in combinations(V,2)):continue
            if any(a^b not in W for a,b in combinations(W,2)):continue
            possible_origins.append(origin)
        assert len(possible_origins)==1
        for x in vertices:
            directions={x^y for y in vertices if (x^y) in unique}
            assert not any((a^b) in directions for a,b in combinations(directions,2))
        found[tuple(vertices)]=(tuple(sorted(centers)),possible_origins[0])
    assert len(found)==80
    saved=json.loads((HERE/'SUPPORT10_STRUCTURAL_CENSUS.json').read_text())
    assert {tuple(r['support']):(tuple(r['central']),r['deleted_origin']) for r in saved['records']}==found
    return len(found)

def necessary_count(neighbor_weight):
    cap=neighbor_weight//2
    # A unique edge covers 16 quotient points. Product counting and the
    # three-point sumset lemma force these thresholds for caps at most9.
    return 2 if cap>=8 else 4 if cap>=4 else 8 if cap>=2 else 16

def main():
    assert not sys.flags.optimize
    n=enumerate_supports()
    recorded={tuple(r['weights']):r for r in map(json.loads,(HERE/'SUPPORT10_ROLE_CUTS.jsonl').open())}
    saved_surv={tuple(r['weights']):{tuple(c) for c in r['allowed_central_triplets']}
                for r in json.loads((HERE/'SUPPORT10_ROLE_SURVIVORS.json').read_text())}
    cuts=set();seen=set();surv={};raw_surv=[];assignments=0
    for raw in SOURCE.read_text().splitlines(keepends=True):
        s,m,b,*values=map(int,raw.split())
        if s!=10:continue
        w=tuple(values);assert sum(w)==93 and w not in seen;seen.add(w)
        allowed=set();failed={}
        for ii in combinations(range(10),3):
            assignments+=1;central=set(ii);key=tuple(w[i] for i in ii)
            reasons=[]
            for i in range(10):
                needs=[necessary_count(w[j]) for j in range(10) if i!=j and (i in central or j in central)]
                if max(needs)>w[i]//2 or sum(needs)>w[i]*w[i]//4:reasons.append(i)
            if not reasons:allowed.add(key)
            else:failed[key]=reasons
        if allowed:surv[w]=allowed;raw_surv.append(raw)
        else:
            cuts.add(w);row=recorded[w]
            assert {tuple(r['central']) for r in row['all_role_failures']}==set(failed)
            for cert in row['all_role_failures']:
                central=tuple(cert['central']);rest=list(w)
                for v in central:rest.remove(v)
                placed=central+tuple(rest);i=cert['failed_vertex'];x=placed[i]
                neighbors=[v for j,v in enumerate(placed) if i!=j and (i<3 or j<3)]
                needs=[necessary_count(v) for v in neighbors]
                assert cert['weight']==x and cert['neighbor_weights']==neighbors
                assert cert['maximum_mass']==x*x//4
                assert max(needs)>x//2 or sum(needs)>x*x//4
    assert len(seen)==648 and len(cuts)==641 and len(surv)==7
    assert cuts==set(recorded) and surv==saved_surv
    assert ''.join(raw_surv)==(HERE/'after_support10_roles_survivors.txt').read_text()
    result={'status':'PASS_COMPLETE_INDEPENDENT_SUPPORT10_REPLAY','normalized_supports':n,
            'input_profiles':len(seen),'new_exclusions':len(cuts),'remaining_profiles':len(surv),
            'indexed_role_assignments_checked':assignments,
            'input_sha256':sha256(SOURCE.read_bytes()).hexdigest(),
            'scope':'Exact necessary-condition exclusions; seven survivors are not constructions. Separate implementation, not proof-assistant formalization.'}
    (HERE/'SUPPORT10_ROLE_INDEPENDENT_REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
