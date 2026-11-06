#!/usr/bin/env python3
"""Byte-identity and small exhaustive gating controls for the new clause schema."""
from pathlib import Path
import hashlib
import itertools
import json
import tempfile
import time
import encode_four_pair as X

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


def require(condition,message):
    if not condition:raise AssertionError(message)


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    start=time.monotonic();data=ROOT/'research_round6/imported_claude_round4/data'
    SPEC=X.load_spectra(data/'spec32.csv');M=X.load_M(data/'Mtable.txt');SUBS=X.all_subspaces()
    eligible=[i for i,s in enumerate(SPEC) if X.nonplanar_four_pair_type(s)]
    require(len(eligible)==2 and {SPEC[i][0] for i in eligible}=={8,11},'Unexpected eligible census types')
    cube=next(i for i,(w,h,r0,r1) in enumerate(SPEC) if w==8 and sum(k*k*c for k,c in enumerate(h))==112)
    other11=next(i for i,(w,h,r0,r1) in enumerate(SPEC) if w==11 and sum(k*k*c for k,c in enumerate(h))==211)
    tests=negatives=0
    domains=[([cube]+eligible,[cube]+eligible),([other11,eligible[1]],[other11,eligible[1]])]
    for left,right in domains:
        for ia,ib,pa,pb in itertools.product(range(len(left)),range(len(right)),(False,True),(False,True)):
            f=X.E.CNF();f.z={};f.y={}
            for v,choices in ((0,left),(1,right)):
                for i in choices:f.z[v,i]=f.new()
                f.exactly_one([f.z[v,i] for i in choices])
                f.y[v,1,4]=f.new()
            before=f.n;X.append_unique_four_pair_cuts(f,[0,1],SPEC)
            assigned={f.z[0,i]:i==left[ia] for i in left}
            assigned.update({f.z[1,i]:i==right[ib] for i in right})
            assigned[f.y[0,1,4]]=pa;assigned[f.y[1,1,4]]=pb
            sat=False
            for values in itertools.product((False,True),repeat=f.n-before):
                model=dict(assigned);model.update({before+j+1:value for j,value in enumerate(values)})
                if all(any(model[abs(l)] if l>0 else not model[abs(l)] for l in c) for c in f.cl):sat=True;break
            forbidden=X.nonplanar_four_pair_type(SPEC[left[ia]]) and X.nonplanar_four_pair_type(SPEC[right[ib]]) and pa and pb
            require(sat==(not forbidden),'Conditional four-pair gate rejects/accepts wrong assignment')
            tests+=1;negatives+=forbidden
    queue=json.loads((ROOT/'research_round6/next_frontier/SUPPORT13_CASE_QUEUE.json').read_text())
    selected=next(c for c in queue['cases'] if c['nonzero_support_mask']==377850134)
    T=selected['support'][1:]
    with tempfile.TemporaryDirectory(prefix='four_pair_identity_') as directory:
        d=Path(directory);base=X.E.encode(T,11,SPEC,M,SUBS,outtotal=93,hub_min=11)
        X.write_dimacs(base,d/'baseline.cnf')
        disabled=X.encode(T,11,SPEC,M,SUBS,outtotal=93,hub_min=11,enabled=False)
        X.write_dimacs(disabled,d/'disabled.cnf')
        require(digest(d/'baseline.cnf')==digest(d/'disabled.cnf'),'Disabled wrapper changes baseline bytes')
        enabled=X.encode(T,11,SPEC,M,SUBS,outtotal=93,hub_min=11,enabled=True)
        require(enabled.cl[:len(base.cl)]==base.cl,'Extension modified pre-existing clauses')
        X.write_dimacs(enabled,d/'enabled.cnf')
        details={'support_mask':377850134,'baseline_sha256':digest(d/'baseline.cnf'),
                 'disabled_sha256':digest(d/'disabled.cnf'),'enabled_sha256':digest(d/'enabled.cnf'),
                 'extension':enabled.four_pair_metadata}
    receipt={'status':'PASS_FOUR_PAIR_ENCODER_IDENTITY_AND_GATING_CONTROLS',
             'gate_assignments_checked':tests,'negative_controls_rejected':negatives,
             'eligible_census_types':[{'index':i,'weight':SPEC[i][0],'rank_interval':list(SPEC[i][2:])} for i in eligible],
             'disabled_wrapper_byte_identical':True,'actual_case':details,
             'source_sha256':digest(HERE/'encode_four_pair.py'),
             'new_exclusions_credited_by_controls':0,'seconds':round(time.monotonic()-start,6)}
    (HERE/'FOUR_PAIR_ENCODER_CONTROLS.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
