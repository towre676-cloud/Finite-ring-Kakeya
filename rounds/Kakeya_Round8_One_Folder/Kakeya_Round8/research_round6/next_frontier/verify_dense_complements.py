#!/usr/bin/env python3
"""Exhaustive complement check in one binary4-flat; no SAT search."""
from pathlib import Path
import collections
import itertools
import json
import sys
import time

HERE=Path(__file__).resolve().parent

def span(xs):
    out={0}
    for x in xs: out|={a^x for a in out}
    return out

def rank(xs):
    return len(span(xs)).bit_length()-1

def affine_rank(A):
    x=next(iter(A))
    return rank(a^x for a in A)

def pairs(A,d):
    return sum((a^d) in A for a in A)//2

def xor_all(xs):
    out=0
    for x in xs:out^=x
    return out

def main():
    if sys.flags.optimize:
        raise SystemExit("Run without -O: this finite verifier uses assertions.")
    started=time.monotonic()
    H=set(range(16));counts=collections.Counter();profiles=collections.defaultdict(set)
    checked=0
    for bsize in (4,5):
        for comb in itertools.combinations(range(16),bsize):
            B=set(comb);A=H-B;w=len(A);br=affine_rank(B)
            p={d:pairs(A,d) for d in range(1,32)}
            for d in range(1,16):
                assert p[d]==w-8+pairs(B,d)
            assert all(p[d]==0 for d in range(16,32))
            assert affine_rank(A)==4
            Q=sum(v*v for v in p.values())
            counts[w,Q]+=1
            profiles[w,Q].add(tuple(p[d] for d in range(1,16)))
            if (w,Q)==(12,300):
                assert br==2
                J={0}|{d for d in range(1,16) if p[d]==6}
                assert len(J)==4 and span(J)==J
                assert all(p[d]==4 for d in H-J)
            elif (w,Q)==(12,294):
                assert br==3
                P={d for d in range(1,16) if p[d]==5};J=span(P)
                assert len(P)==6 and len(J)==8
                missing=J-{0}-P
                assert len(missing)==1
                assert {d for d in J-{0} if p[d]==4}==missing
                assert all(p[d]==4 for d in H-J)
                for triple in itertools.combinations(P,3):
                    if rank(triple)==3:
                        assert sum(p[d]==4 for d in span(triple)-{0})==1
            elif (w,Q)==(11,211):
                assert br==3
                J={0}|{d for d in range(1,16) if p[d]==5}
                L=J|{d for d in range(1,16) if p[d]==4}
                assert len(J)==4 and span(J)==J and len(L)==8 and span(L)==L
                assert all(p[d]==3 for d in H-L)
            elif (w,Q)==(11,205):
                assert br==4
                C={d for d in range(1,16) if p[d]==3}
                assert len(C)==5 and xor_all(C)==0
                assert {a^b for a,b in itertools.combinations(B,2)}=={d for d in range(1,16) if p[d]==4}
                for k in range(1,5):
                    assert all(rank(t)==k for t in itertools.combinations(C,k))
            else:raise AssertionError((w,Q,br))
            maximal={0}|{d for d in range(1,32) if p[d]==w//2}
            assert len(maximal)==(1 if Q in (294,205) else 4)
            checked+=1
    expected={(12,300):140,(12,294):1680,(11,211):1680,(11,205):2688}
    expected_profiles={(12,300):35,(12,294):105,(11,211):105,(11,205):168}
    assert dict(counts)==expected
    assert {key:len(value) for key,value in profiles.items()}==expected_profiles
    report={
        "status":"PASS","scope":"All weight4/5 complements inside one fixed F2^4; affine invariance gives the stated universal lemmas.",
        "subsets_checked":checked,
        "types":[{"weight":w,"Q":Q,"subsets":counts[w,Q],"distinct_labelled_pair_profiles":len(profiles[w,Q])} for w,Q in expected],
        "conditions_checked":["exact complement identity","zero pair counts outside the4-space","subspace flags","rank3 support of the six p5 directions","unique p4 direction in that3-space","five-circuit dependence and all proper-subset independence","maximal-pair subspace is trivial exactly for the two targeted types"],
        "new_support_exclusions":0,"SAT_search_performed":False,"formalization":"Hand proof plus complete finite corroboration; no Lean claim.",
        "seconds":round(time.monotonic()-started,6),
    }
    (HERE/"DENSE_COMPLEMENT_REPLAY.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))

if __name__=="__main__":main()
