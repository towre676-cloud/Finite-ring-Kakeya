"""Middle-agent review: check role witnesses and Hall certificates, not the census.

The exhaustive normalized-support census is deliberately not rerun here.
Its completeness is assessed by reading the producer and independent checker.
This separate bounded check reads their frozen outputs without modifying them.
"""
from pathlib import Path
from collections import Counter
from functools import lru_cache
from hashlib import sha256
from math import comb
import json

HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'m19'


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def direct_role(mask):
    points=[a for a in range(32) if mask>>a&1]
    by_direction={d:[] for d in range(1,32)}
    for i,a in enumerate(points):
        for b in points[i+1:]:
            by_direction[a^b].append((a,b))
    assert all(by_direction.values())
    forced_large=set()
    for d,edges in by_direction.items():
        if not (mask>>d&1) and len(edges)==1:
            forced_large.update(edges[0])
    out=[0]*4
    for a in points:
        if a:
            out[int(a in forced_large)+2*int(len(by_direction[a])==1)]+=1
    return tuple(out)


@lru_cache(None)
def hall_obstructions(role,attrs):
    # Enumerate every nonempty subset of the three constrained role TYPES.
    # A role subset containing type0 has every fibre eligible and cannot fail.
    failed=[]
    for mask in range(1,8):
        needs=[j for j in (1,2,3) if mask>>(j-1)&1]
        required=sum(role[j] for j in needs)
        available=sum(attrs[a] for a in range(4) if any(a&j==j for j in needs))
        if required>available:
            failed.append((tuple(needs),required,available))
    four=(role[3]>attrs[3] or role[1]+role[3]>attrs[1]+attrs[3]
          or role[2]+role[3]>attrs[2]+attrs[3]
          or sum(role[1:])>sum(attrs[1:]))
    assert bool(failed)==four
    return tuple(failed)


def run():
    cp=BASE/'UNIQUE_EDGE_ROLE_NORMALIZED_CENSUS.json'
    census=json.loads(cp.read_text())
    rp=BASE/'UNIQUE_EDGE_ROLE_VERIFICATION_RECEIPT.json'
    receipt=json.loads(rp.read_text())
    assert receipt['status']=='PASS_EXACT_NORMALIZED_SUPPORT_CENSUS_AND_HALL_CERTIFICATES'
    assert receipt['census_sha256']==digest(cp)
    total_witnesses=0
    support_results={}
    named={'both':(3,),'large':(1,3),'sole_hub':(2,3),'nonfree':(1,2,3)}
    sources={cp,rp}
    for s in (11,12):
        saved=census['supports'][str(s)]
        assert saved['normalized_sets_visited']==comb(26,s-6)
        assert sum(row['normalized_multiplicity'] for row in saved['patterns'])==saved['covering_normalized_sets']
        roles=[]
        for row in saved['patterns']:
            mask=row['witness_mask']
            assert mask.bit_count()==s and all(mask>>x&1 for x in (0,1,2,4,8,16))
            role=direct_role(mask)
            assert role==tuple(row['counts']) and sum(role)==s-1
            roles.append(role)
        assert roles==sorted(set(roles))
        src=BASE/f's{s}_after_own_periodic.txt'
        cand=BASE/f'S{s}_UNIQUE_EDGE_ROLE_CANDIDATES.jsonl'
        surv=BASE/f's{s}_after_unique_edge_roles.txt'
        sources.update((src,cand,surv))
        rr=receipt['supports'][str(s)]
        assert rr['input_sha256']==digest(src) and rr['candidates_sha256']==digest(cand)
        assert rr['survivors_sha256']==digest(surv)
        profiles={}
        lines=src.read_text().splitlines()
        for line in lines:
            values=list(map(int,line.split()))
            ident,z,groups=values[:3]
            assert len(values)==3+3*groups and ident not in profiles
            fibres=[]
            for i in range(groups):
                flag,weight,n=values[3+3*i:6+3*i]
                assert flag in (0,1) and 2<=weight<=14 and n>=1
                fibres.extend([(flag,weight)]*n)
            assert len(fibres)==s-1 and sum(w for f,w in fibres)==74
            assert z==31-sum(f for f,w in fibres)
            attrs=tuple(sum((int(w>=8)+2*int(f==1 and w>=4))==a for f,w in fibres)
                        for a in range(4))
            profiles[ident]=(line,attrs)
        removed=set()
        witnesses=0
        for line in cand.read_text().splitlines():
            record=json.loads(line)
            ident=record['parent_id']
            assert ident in profiles and ident not in removed
            original,attrs=profiles[ident]
            assert original==record['profile_line'] and attrs==tuple(record['attributes'])
            assert record['support']==s and len(record['hall_witnesses'])==len(roles)
            for role,witness in zip(roles,record['hall_witnesses']):
                need,have,name=witness
                assert (named[name],need,have) in hall_obstructions(role,attrs)
                witnesses+=1
            removed.add(ident)
        for ident,(line,attrs) in profiles.items():
            assert all(hall_obstructions(role,attrs) for role in roles)==(ident in removed)
        expected=''.join(line+'\n' for line in lines if int(line.split()[0]) not in removed)
        assert surv.read_text()==expected
        assert len(removed)==rr['whole_profile_exclusions']
        assert witnesses==rr['hall_witnesses_checked']
        support_results[str(s)]={'profile_inputs':len(profiles),'role_witness_masks_checked':len(roles),
                                 'excluded':len(removed),'remaining':len(profiles)-len(removed),
                                 'hall_witnesses_checked':witnesses}
        total_witnesses+=witnesses
    assert total_witnesses==88370
    result={'status':'PASS_INDEPENDENT_BOUNDED_ROLE_HALL_REVIEW',
            'reviewer':'middle_maxima agent',
            'exhaustive_normalized_support_census_rerun':False,
            'scope':'analytic proof and complete-enumeration code reviewed; all25 witness masks and all88370 Hall witnesses independently checked',
            'four_inequalities':'necessary and sufficient for the two-attribute assignment relaxation; not sufficient for Kakeya',
            'supports':support_results,
            'hall_type_subsets_crosscheck_keys':hall_obstructions.cache_info().currsize,
            'dependencies':{str(p.relative_to(HERE.parent)):digest(p) for p in sorted(sources)}}
    (HERE/'MIDDLE_AGENT_M19_ROLE_REVIEW.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    run()
