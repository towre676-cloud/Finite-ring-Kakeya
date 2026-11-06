"""Separate direct-set cross-check of the seven nine-heavy geometry types."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import json

EXPECTED={
 (3,((0,1),(1,18),(2,3),(3,1))):260,
 (4,((0,7),(2,12),(3,4))):750,
 (6,((0,3),(2,12),(3,2),(4,6))):660,
 (8,((1,8),(2,2),(4,9),(6,4))):810,
 (9,((2,15),(6,7),(9,1))):60,
 (10,((0,1),(3,8),(4,12),(9,2))):60,
 (16,((0,7),(9,16))):330,
}


def main():
    actual=Counter()
    rank_counts=Counter()
    for rank in (4,5):
        basis=(0,)+tuple(1<<i for i in range(rank))
        choices=[x for x in range(1<<rank) if x not in basis]
        for extra in combinations(choices,9-len(basis)):
            heavy=set(basis+extra)
            differences={a^b for a,b in combinations(heavy,2)}
            missing=set(range(1,32))-differences
            assert len(missing)>=3
            assert not any(a^b in missing for a,b in combinations(missing,2))
            degrees=Counter(sum((x^a) in missing for a in heavy)
                            for x in range(32) if x not in heavy)
            assert sum(degrees.values())==23
            assert sum(k*n for k,n in degrees.items())==9*len(missing)
            actual[len(missing),tuple(sorted(degrees.items()))]+=1
            rank_counts[rank]+=1
    assert dict(actual)==EXPECTED and sum(actual.values())==2930
    result={
        'status':'PASS_SEPARATE_DIRECT_SET_GEOMETRY_CROSSCHECK',
        'normalized_nine_sets':2930,
        'rank_counts':dict(rank_counts),
        'geometry_types':[{'missing':r,'outside_degree_counts':dict(h),'normalized_multiplicity':n}
                          for (r,h),n in sorted(actual.items())],
        'scope':'Verifies the geometry table by complete affine-basis normalization and direct set differences; does not replay the full resource-profile cut list.',
    }
    path=Path(__file__).resolve().with_name('NINE_DEGREE_TABLE_CROSSCHECK.json')
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'normalized_nine_sets':2930,
                      'geometry_types':len(actual)},indent=2))


if __name__=='__main__':main()
