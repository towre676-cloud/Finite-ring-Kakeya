"""Independent affine-automorphism/hub-orbit replay for the inherited supports.

The producer enumerates all full ordered affine bases, then checks the image.
This checker builds a partial affine map and prunes as soon as any known
support point maps outside the support. No producer function is imported.
Catalogue completeness is inherited and explicitly distinguished from this
complete automorphism computation on the twelve supplied representatives.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import json
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'research_sources/extracted/Kakeya_Reconciled_Proofs_2026-10-27/halfspace_extension/M11_BOUNDED_GEOMETRIC_REDUCTION.json'


def all_automorphisms(points):
    support=set(points)
    found=set()
    nodes=0
    def extend(t,images,columns):
        nonlocal nodes
        nodes+=1
        width=len(images)
        if width==32:
            assert {images[x] for x in support}==support
            found.add((t,)+columns)
            return
        used=set(images)
        relevant=[x for x in range(width) if x+width in support]
        for y in points:
            if y in used:continue
            column=t^y
            new=[x^column for x in images]
            if any(new[x] not in support for x in relevant):continue
            extend(t,images+new,columns+(column,))
    for t in points:extend(t,[t],())
    return found,nodes


def apply(code,x):
    out=code[0]
    for j in range(5):
        if x>>j&1:out^=code[j+1]
    return out


def main():
    start=time.monotonic()
    raw=json.loads(SOURCE.read_text())['all_support_records']
    selected={r['global_orbit']:r for r in raw if r['support_size'] in(11,12)
              and len({a^b for a,b in combinations(r['support'],2)})==31}
    census=json.loads((HERE/'MARKED_SUPPORT_CENSUS.json').read_text())
    assert census['schema']=='affine-marked-support-census-v1'
    assert len(census['records'])==len(selected)==12
    assert {r['global_orbit'] for r in census['records']}==set(selected)
    entries=[];counts=Counter();auttotal=0;node_count=0;marked=[]
    for row in census['records']:
        original=selected[row['global_orbit']]
        points=original['support'];mask=original['mask'];s=len(points)
        assert s==row['support_size'] and mask==row['mask']
        assert sum(1<<x for x in points)==mask
        actual,nodes=all_automorphisms(points)
        declared={tuple(code) for code in row['affine_automorphisms']}
        assert actual==declared and len(actual)==len(row['affine_automorphisms'])==row['automorphism_count']
        assert (0,1,2,4,8,16) in actual
        orbits=[];remaining=set(points)
        while remaining:
            a=min(remaining)
            orbit=sorted({apply(code,a) for code in actual})
            assert set(orbit)<=remaining
            orbits.append(orbit);remaining-=set(orbit)
        assert orbits==row['hub_orbits']
        for orbit in orbits:
            h=orbit[0];shifted=sorted(x^h for x in points)
            transports=[]
            for vertex in orbit:
                code=min(c for c in actual if apply(c,vertex)==h)
                transports.append({'hub':vertex,'to_representative_affine_map':list(code)})
            marked.append({'case_id':f's{s}_orbit{row["global_orbit"]}_hub{h}',
                'support_size':s,'unmarked_global_orbit':row['global_orbit'],
                'original_support':points,'hub_orbit':orbit,'selected_original_hub':h,
                'hub_zero_support':shifted,'hub_zero_mask':sum(1<<x for x in shifted),
                'hub_transports':transports})
        counts[s]+=len(orbits);auttotal+=len(actual);node_count+=nodes
        entries.append({'global_orbit':row['global_orbit'],'support_size':s,
            'automorphisms':len(actual),'hub_orbits':orbits,'independent_partial_nodes':nodes})
    assert dict(counts)=={11:13,12:25} and len(marked)==38
    assert census['total_marked_orbits']==38
    cases={'schema':'maximum19-marked-support-contract-v1','case_count':38,
        'counts_by_support':dict(counts),'cases':marked,
        'meaning':'One distinguished maximum-weight residue moved to zero; every other fibre may also attain the same maximum. The actual Claude cases have not been supplied or compared.',
        'catalogue_dependency':'Completeness of the inherited382-representative affine catalogue is assumed here; every automorphism and hub orbit of the selected12 representatives is independently recomputed.'}
    (HERE/'M19_MARKED_CASE_CONTRACT.json').write_text(json.dumps(cases,indent=2)+'\n')
    receipt={'status':'PASS_COMPLETE_AUTOMORPHISMS_ON_INHERITED_REPRESENTATIVES',
        'unmarked_difference_covering_supports':12,'counts_unmarked':{'11':4,'12':8},
        'marked_hub_orbits':38,'counts_marked':dict(counts),
        'affine_automorphisms_checked':auttotal,'independent_partial_map_nodes':node_count,
        'records':entries,'claude_artifact_comparison':'NOT_PERFORMED_ARTIFACTS_UNAVAILABLE',
        'catalogue_completeness_reproved':False,
        'source_sha256':sha256(SOURCE.read_bytes()).hexdigest(),
        'census_sha256':sha256((HERE/'MARKED_SUPPORT_CENSUS.json').read_bytes()).hexdigest(),
        'case_contract_sha256':sha256((HERE/'M19_MARKED_CASE_CONTRACT.json').read_bytes()).hexdigest(),
        'seconds':round(time.monotonic()-start,6)}
    (HERE/'MARKED_SUPPORT_REPLAY.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ['status','unmarked_difference_covering_supports','marked_hub_orbits','counts_marked','affine_automorphisms_checked','independent_partial_map_nodes','seconds']},indent=2))


if __name__=='__main__':main()
