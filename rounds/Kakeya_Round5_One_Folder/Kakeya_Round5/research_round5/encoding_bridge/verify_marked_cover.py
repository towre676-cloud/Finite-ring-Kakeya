"""Check a complete 38-case covering certificate without an orbit catalogue.

Every normalized difference-covering size 11/12 support must appear, with a
literal invertible-linear-map witness from one of 38 hub-zero representatives.
The checker enumerates normalized subsets independently and uses translated
bit intersections for coverage, rather than the producer's unordered pairs.
It does not import a producer or read the inherited 382-class catalogue.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations
from functools import lru_cache
from pathlib import Path
import csv,json,time

HERE=Path(__file__).resolve().parent
FIXED=(0,1,2,4,8,16)
FIXED_MASK=sum(1<<x for x in FIXED)
EXTRA=tuple(x for x in range(32) if x not in FIXED)
SWAPS=((1,0x55555555),(2,0x33333333),(4,0x0F0F0F0F),(8,0x00FF00FF),(16,0x0000FFFF))


def shifted(mask,d):
    for step,low in SWAPS:
        if d&step:mask=((mask&low)<<step)|((mask>>step)&low)
    return mask


def covering(mask):
    return all(mask&shifted(mask,d) for d in range(1,32))


def ordered_basis_count(points):
    @lru_cache(None)
    def complete(span):
        if span==0xFFFFFFFF:return 1
        value=0
        for x in points:
            if span>>x&1:continue
            value+=complete(span|shifted(span,x))
        return value
    return complete(1)


def linear_automorphism_count(points):
    original=set(points)
    source_basis_span=[0]
    for x in points:
        if x not in source_basis_span:
            source_basis_span+=[y^x for y in source_basis_span]
        if len(source_basis_span)==32:break
    assert len(source_basis_span)==32
    points=[i for i,x in enumerate(source_basis_span) if x in original]
    support=set(points)
    assert set(FIXED)<=support
    def extend(images):
        width=len(images)
        if width==32:return 1
        used=set(images);relevant=[x for x in range(width) if x+width in support]
        total=0
        for y in points:
            if y in used:continue
            new=[x^y for x in images]
            if any(new[x] not in support for x in relevant):continue
            total+=extend(images+new)
        return total
    return extend([0])


def main():
    start=time.monotonic()
    contract=json.loads((HERE/'M19_MARKED_CASE_CONTRACT.json').read_text())
    cases=contract['cases']
    assert len(cases)==38 and len({r['case_id'] for r in cases})==38
    assert Counter(r['support_size'] for r in cases)=={11:13,12:25}
    for row in cases:
        points=row['hub_zero_support']
        assert 0 in points and len(points)==row['support_size'] and len(set(points))==len(points)
        assert sum(1<<x for x in points)==row['hub_zero_mask'] and covering(row['hub_zero_mask'])
    observed={};by_case=Counter();by_support=Counter()
    with (HERE/'NORMALIZED_SUPPORT_TO_CASE.csv').open() as stream:
        for row in csv.reader(stream):
            mask,index,*basis=map(int,row)
            assert mask not in observed and 0<=index<38 and len(basis)==5
            points=cases[index]['hub_zero_support']
            assert set(basis)<=set(points)
            image=[]
            for x in range(32):
                y=0
                for j in range(5):
                    if x>>j&1:y^=basis[j]
                image.append(y)
            assert len(set(image))==32
            actual=sum(1<<x for x in range(32) if image[x] in points)
            assert actual==mask and mask&FIXED_MASK==FIXED_MASK
            assert mask.bit_count()==len(points) and covering(mask)
            observed[mask]=index;by_case[index]+=1;by_support[len(points)]+=1
    assert len(observed)==102324 and by_support=={11:7676,12:94648}
    assert set(by_case)==set(range(38))
    sizes=[]
    for i,row in enumerate(cases):
        points=row['hub_zero_support']
        bases=ordered_basis_count(points)
        automorphisms=linear_automorphism_count(points)
        assert automorphisms>0 and bases%automorphisms==0
        # Each normalized image has exactly Aut_linear(S) ordered source
        # bases producing it. Thus the supplied distinct witnesses attain
        # the full normalized image count for this marked orbit.
        assert bases//automorphisms==by_case[i]
        sizes.append({'case_id':row['case_id'],'ordered_bases':bases,
                      'linear_automorphisms':automorphisms,'normalized_orbit_size':by_case[i]})
    visited=Counter();found=Counter();missing=0
    for s in (11,12):
        for extra in combinations(EXTRA,s-6):
            visited[s]+=1
            mask=FIXED_MASK|sum(1<<x for x in extra)
            covered=covering(mask)
            assert covered==(mask in observed)
            found[s]+=covered
    assert visited=={11:65780,12:230230} and found==by_support
    receipt={'status':'PASS_COMPLETE_38_CASE_COVER_WITHOUT_INHERITED_CATALOGUE',
        'candidate_cases':38,'marked_cases_by_support':{'11':13,'12':25},
        'normalized_sets_checked':sum(visited.values()),
        'normalized_all':dict(visited),'normalized_covering':dict(found),
        'explicit_linear_map_witnesses':len(observed),'missing_normalized_covering_sets':0,
        'cross_case_normalized_orbit_overlaps':0,
        'exact_marked_orbit_sizes':sizes,
        'by_case':[{'case_id':r['case_id'],'normalized_witnesses':by_case[i]} for i,r in enumerate(cases)],
        'catalogue_completeness_dependency':False,
        'mathematical_normalization':'A difference-covering support spans F2^5. Translate a distinguished maximum-weight vertex to 0; select a linear basis from the support and send it to the coordinate basis. Every normalized support is exhaustively checked here.',
        'orbit_size_argument':'For each marked support, ordered source bases map it to supports containing the coordinate basis. Every resulting support has exactly the linear automorphism group size many such source bases. Both counts are independently recomputed; each supplied mask belongs to the claimed orbit and the supplied count exhausts its entire normalized orbit. The unique mask assignment therefore also proves the 38 orbits disjoint.',
        'scope':'This proves the 38 representatives cover all hub-marked difference-covering supports of sizes 11/12. It does not verify Claude CNFs, proofs, A-E, or the inherited restriction of maximum 19 to these support sizes.',
        'sha256':{p.name:sha256(p.read_bytes()).hexdigest() for p in [HERE/'M19_MARKED_CASE_CONTRACT.json',HERE/'NORMALIZED_SUPPORT_TO_CASE.csv',Path(__file__).resolve()]},
        'seconds':round(time.monotonic()-start,6)}
    (HERE/'NORMALIZED_COVER_REPLAY.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ['status','candidate_cases','normalized_sets_checked','normalized_covering','explicit_linear_map_witnesses','catalogue_completeness_dependency','seconds']},indent=2))


if __name__=='__main__':main()
