"""Complete normalized support census and exact necessary role screen."""
from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'research_round5/nine_geometry/after_nine_geometry_survivors.txt'

def capacity(p,q):
    return max(p,q)+8 if min(p,q)==3 and 5<=max(p,q)<=7 else min(16,p*q)

def forced(w,other):
    return next((p for p in range(w//2+1) if capacity(p,other//2)==16),100)

def census():
    base=(0,1,2,4,8,16)
    free=tuple(x for x in range(32) if x not in base)
    records=[]
    for extra in combinations(free,4):
        support=tuple(sorted(base+extra))
        edges={d:[] for d in range(1,32)}
        for a,b in combinations(support,2):edges[a^b].append((a,b))
        if any(not ee for ee in edges.values()):continue
        degree={x:sum(len(ee)==1 and x in ee[0] for ee in edges.values()) for x in support}
        central=tuple(x for x in support if degree[x]==9)
        ordinary=tuple(x for x in support if degree[x]==3)
        assert len(central)==3 and len(ordinary)==7
        assert Counter(map(len,edges.values()))=={1:24,3:7}
        assert all(len(edges[a^b])==1 for a,b in combinations(support,2) if a in central or b in central)
        missing=0
        for x in ordinary:missing^=x
        V={0}|{x^missing for x in ordinary}
        W={0}|{x^missing for x in central}
        assert len(V)==8 and len(W)==4 and V&W=={0}
        assert all(a^b in V for a in V for b in V)
        assert all(a^b in W for a in W for b in W)
        assert {a^b for a in V for b in W}==set(range(32))
        for x in support:
            directions={d for d,ee in edges.items() if len(ee)==1 and x in ee[0]}
            assert all(a^b not in directions for a,b in combinations(directions,2))
        records.append({'support':support,'central':central,'ordinary':ordinary,
                        'deleted_origin':missing,'V':sorted(V),'W':sorted(W)})
    assert len(records)==80
    (HERE/'SUPPORT10_STRUCTURAL_CENSUS.json').write_text(json.dumps({
        'status':'PASS_COMPLETE_NORMALIZED_SUPPORT10_CENSUS','normalized_supports':80,
        'normalization_candidates':14950,'records':records},indent=2)+'\n')

def role_case(weights,central):
    ordinary=list(weights)
    for w in central:ordinary.remove(w)
    placed=central+tuple(ordinary)
    for i,w in enumerate(placed):
        neighbors=[v for j,v in enumerate(placed) if j!=i and (i<3 or j<3)]
        needs=[forced(w,v) for v in neighbors]
        if sum(needs)>w*w//4:
            return {'central':central,'failed_vertex':i,'weight':w,
                    'neighbor_weights':neighbors,'forced_counts':needs,
                    'required_mass':sum(needs),'maximum_mass':w*w//4}
    return None

def main():
    census()
    initial=[];cuts=[];survivors=[];surviving_raw=[]
    for raw in SOURCE.read_text().splitlines(keepends=True):
        s,m,b,*w=map(int,raw.split())
        if s!=10:continue
        w=tuple(w);assert len(w)==10 and sum(w)==93 and w[0]==m and 12<=m<=18
        initial.append(w)
        central_options=sorted({tuple(w[i] for i in ii) for ii in combinations(range(10),3)})
        failures=[];allowed=[]
        for central in central_options:
            bad=role_case(w,central)
            if bad is None:allowed.append(central)
            else:failures.append(bad)
        if allowed:
            survivors.append({'weights':w,'allowed_central_triplets':allowed})
            surviving_raw.append(raw)
        else:cuts.append({'weights':w,'support':10,'maximum':w[0],'all_role_failures':failures})
    assert len(initial)==648 and len(set(initial))==648 and len(cuts)==641 and len(survivors)==7
    (HERE/'SUPPORT10_ROLE_CUTS.jsonl').write_text(''.join(json.dumps(r,separators=(',',':'))+'\n' for r in cuts))
    (HERE/'SUPPORT10_ROLE_SURVIVORS.json').write_text(json.dumps(survivors,indent=2)+'\n')
    (HERE/'after_support10_roles_survivors.txt').write_text(''.join(surviving_raw))
    result={'status':'PASS_EXACT_ROLE_PRODUCER','input_profiles':648,'new_exclusions':641,'remaining_profiles':7,
            'by_maximum':[{'maximum':m,'initial':sum(w[0]==m for w in initial),
                          'excluded':sum(r['maximum']==m for r in cuts),
                          'remaining':sum(r['weights'][0]==m for r in survivors)} for m in range(12,19)],
            'input':str(SOURCE.relative_to(ROOT)),'input_sha256':sha256(SOURCE.read_bytes()).hexdigest(),
            'dependencies':'No Qmax census, maximum-direction quota, LP, or SAT. Uses unique-edge coverage, three-point sumset lemma, and sum-free Mantel bound.'}
    (HERE/'SUPPORT10_ROLE_PRODUCER.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
