#!/usr/bin/env python3
"""Exhaustive finite checks of the sharp14-capacity and dense fibre flags."""
from pathlib import Path
import hashlib
import itertools
import json
import time

HERE=Path(__file__).resolve().parent


def require(x,message):
    if not x:raise AssertionError(message)


def span(generators):
    result={0}
    for x in generators:result|={y^x for y in tuple(result)}
    return result


def pair_counts(A,n):
    values=[0]*(1<<n)
    for x,y in itertools.combinations(A,2):values[x^y]+=1
    return values


def quotient_pairs(A,d):
    A=set(A)
    return {min(x,x^d) for x in A if x^d in A}


def plane4(P):
    if len(P)!=4:return False
    total=0
    for x in P:total^=x
    return total==0


def main():
    start=time.monotonic()
    fours=list(itertools.combinations(range(16),4))
    tetrahedra=[P for P in fours if not plane4(P)]
    require(len(tetrahedra)==1680,'Wrong four-set classification')
    fixed={0,1,2,4};hist={}
    for Q in tetrahedra:
        count=len({p^q for p in fixed for q in Q})
        require(count<=14,'Two tetrahedra exceeded14 sums')
        hist[str(count)]=hist.get(str(count),0)+1
    witnessP=[0,1,2,4];witnessQ=[0,7,8,14]
    require(len({p^q for p in witnessP for q in witnessQ})==14,'Sharpness witness failed')
    # Every nonplanar four-set is affinely equivalent to the fixed tetrahedron;
    # applying that same affine map to Q preserves sumset cardinality.
    eleven_cases=eleven_directions=0
    for B in itertools.combinations(range(16),5):
        A=set(range(16))-set(B);p=pair_counts(A,4)
        Q=sum(x*x for x in p[1:])
        if Q!=205:continue
        eleven_cases+=1
        require(len(span(x^B[0] for x in B))==16,'Q205 complement is not affine-independent')
        require(sum(x==4 for x in p[1:])==10,'Wrong Q205 directional histogram')
        for d in range(1,16):
            if p[d]==4:
                P=quotient_pairs(A,d);eleven_directions+=1
                require(len(P)==4 and not plane4(P),'Q205 four-pair quotient unexpectedly planar')
    require(eleven_cases==2688 and eleven_directions==26880,'Unexpected weight11 census')
    eight_cases=0
    for P in tetrahedra:
        A=set(P)|{x^16 for x in P};p=pair_counts(A,5)
        require(p[16]==4 and sum(x==4 for x in p[1:])==1,'Wrong eight-point maximal directions')
        require(sum(x==2 for x in p[1:])==12 and sum(x==0 for x in p[1:])==18,'Wrong eight-point spectrum')
        require(sum(x*x for x in p[1:])==64,'Wrong eight-point energy')
        eight_cases+=1
    twelve_cases=twelve_nonplanar=twelve_planar=0
    for B in tetrahedra:
        A=set(range(16))-set(B);p=pair_counts(A,4)
        require(sum(x*x for x in p[1:])==294,'Wrong twelve-point energy')
        J=span(x^B[0] for x in B);u=0
        for x in B:u^=x
        require(u in J and u!=0,'Invalid missing tetrahedron direction')
        for d in range(1,16):
            if p[d]!=4:continue
            P=quotient_pairs(A,d)
            require(len(P)==4,'Wrong twelve-point pair count')
            if d==u:
                require(plane4(P),'Exceptional twelve-point quotient must be planar');twelve_planar+=1
            else:
                require(d not in J and not plane4(P),'Nonexceptional twelve-point flag failed');twelve_nonplanar+=1
        twelve_cases+=1
    require(twelve_cases==1680 and twelve_planar==1680 and twelve_nonplanar==13440,'Wrong twelve-point flag counts')
    digest=hashlib.sha256((HERE/'FOUR_PAIR_CAPACITY_LEMMA.txt').read_bytes()).hexdigest()
    result={'status':'PASS_FOUR_PAIR_CAPACITY_AND_FIBRE_FLAGS','lemma_sha256':digest,
            'fixed_tetrahedron_partner_cases':len(tetrahedra),'sumset_size_histogram':hist,
            'all_pairs_covered_by_affine_equivalence':True,
            'sharpness_witness':{'P':witnessP,'Q':witnessQ,'sumset_size':14},
            'weight11_Q205_complements':eleven_cases,'weight11_nonplanar_pair_directions':eleven_directions,
            'weight8_period_normalized_tetrahedra':eight_cases,
            'weight12_Q294_complements':twelve_cases,'weight12_nonplanar_pair_directions':twelve_nonplanar,
            'weight12_exceptional_planar_directions':twelve_planar,
            'new_SAT_exclusions_credited':0,'benchmark_speedup_claimed':False,
            'seconds':round(time.monotonic()-start,6)}
    (HERE/'FOUR_PAIR_CAPACITY_REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
