"""Map an actual marked support to the complete 38-case support contract.

Public API: canonical_case_id(support, distinguished_hub) -> string.
map_marked_support additionally returns a literal invertible affine map,
encoded as [offset,column0,...,column4], taking the supplied hub to 0 and the
supplied support to the named contract representative. Read-only; no solver.
The mapping does not prove that a CNF encodes the supplied support.
"""
from functools import lru_cache
from pathlib import Path
import csv,json,sys

HERE=Path(__file__).resolve().parent


@lru_cache(None)
def _load():
    contract=json.loads((HERE/'M19_MARKED_CASE_CONTRACT.json').read_text())
    rows={}
    with (HERE/'NORMALIZED_SUPPORT_TO_CASE.csv').open() as stream:
        for row in csv.reader(stream):
            mask,case,*basis=map(int,row)
            if mask in rows:raise ValueError('Duplicate normalized support witness')
            rows[mask]=(case,tuple(basis))
    return contract['cases'],rows


def linear(columns,x):
    value=0
    for j in range(5):
        if x>>j&1:value^=columns[j]
    return value


def map_marked_support(support,distinguished_hub):
    if (not isinstance(support,(list,tuple)) or len(support) not in(11,12)
        or any(type(x) is not int or not 0<=x<32 for x in support)
        or len(set(support))!=len(support)):
        raise ValueError('Expected 11 or 12 distinct binary residues encoded 0..31')
    if type(distinguished_hub) is not int or distinguished_hub not in support:
        raise ValueError('The distinguished hub must belong to the support')
    shifted=sorted(x^distinguished_hub for x in support)
    span=[0];basis=[]
    for x in shifted:
        if x in span:continue
        basis.append(x);span+=[y^x for y in span]
        if len(span)==32:break
    if len(span)!=32:raise ValueError('The marked support does not span F2^5')
    inverse={x:i for i,x in enumerate(span)}
    normalized=sum(1<<inverse[x] for x in shifted)
    cases,lookup=_load()
    if normalized not in lookup:raise ValueError('The support does not cover all nonzero differences')
    index,target_basis=lookup[normalized];target=cases[index]
    columns=[linear(target_basis,inverse[1<<j]) for j in range(5)]
    offset=linear(columns,distinguished_hub)
    images={offset^linear(columns,x) for x in support}
    if (images!=set(target['hub_zero_support']) or offset^linear(columns,distinguished_hub)!=0
        or len({linear(columns,x) for x in range(32)})!=32):
        raise ValueError('Mapping witness failed direct verification')
    return {'case_id':target['case_id'],'support_size':len(support),
            'source_support':sorted(support),'distinguished_hub':distinguished_hub,
            'target_support':target['hub_zero_support'],
            'affine_map_to_contract':[offset]+columns,'normalized_mask':normalized,
            'source_normalizing_basis':basis,'contract_basis_witness':list(target_basis),
            'scope':'Support equivalence only; no claim that a particular CNF or proof matches this support.'}


def canonical_case_id(support,distinguished_hub):
    return map_marked_support(support,distinguished_hub)['case_id']


if __name__=='__main__':
    row=json.load(sys.stdin)
    print(json.dumps(map_marked_support(row['support'],row['distinguished_hub']),indent=2))
