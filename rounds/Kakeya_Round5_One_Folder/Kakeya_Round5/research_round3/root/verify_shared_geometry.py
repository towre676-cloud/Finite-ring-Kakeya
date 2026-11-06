"""Independent finite controls for the shared-period and rooted-rank proofs."""
from pathlib import Path
from itertools import combinations, product
import json

HERE=Path(__file__).resolve().parent

def span(gens):
    values={0}
    for g in gens:
        values |= {x^g for x in values}
    return frozenset(values)

def rep(x,d):
    return min(x,x^d)

def pairs(A,d):
    return {rep(x,d) for x in A if (x^d) in A}

def capacity(A,B,d):
    P,Q=pairs(A,d),pairs(B,d)
    return len({rep(x^y,d) for x in P for y in Q})

def periodic_sets(n,h):
    representatives=sorted({rep(x,h) for x in range(1<<n)})
    for mask in range(1<<len(representatives)):
        A=set()
        for i,x in enumerate(representatives):
            if mask>>i&1:A|={x,x^h}
        yield A

As=list(periodic_sets(4,1));Bs=list(periodic_sets(4,2));periodic_checks=0
for A in As:
    P=pairs(A,3)
    assert len(P)%2==0 and {rep(x^1,3) for x in P}==P
    for B in Bs:
        Q=pairs(B,3)
        assert len(Q)%2==0 and {rep(x^2,3) for x in Q}==Q
        output={rep(x^y,3) for x in P for y in Q}
        assert 2*len(output)<=len(P)*len(Q)
        assert len({rep(x^1,3) for x in output})==len(output)
        periodic_checks+=1

spaces=sorted({span(g) for g in combinations(range(1,32),3) if len(span(g))==8},key=lambda h:tuple(sorted(h)))
assert len(spaces)==155
own={a:[H for H in spaces if a in H] for a in (1,2,4)}
assert all(len(v)==35 for v in own.values())
edge_checks=0;active_edges=0;maximum_edge=0
for A in own[1]:
    for B in own[2]:
        c=capacity(A,B,3);edge_checks+=1
        assert c<=8
        if c:
            active_edges+=1
            assert {0,1,2,3}<=A&B
            assert c==2**(5-(len(A&B).bit_length()-1))
        maximum_edge=max(maximum_edge,c)
triangle_checks=0;positive_triangles=0
for A,B,C in product(own[1],own[2],own[4]):
    triangle_checks+=1
    if not (3 in A&B and 5 in A&C and 6 in B&C):continue
    positive_triangles+=1
    assert A==B==C==span((1,2,4))
    assert capacity(A,B,3)==capacity(A,C,5)==capacity(B,C,6)==4

graph_results=[]
for n in range(1,6):
    edges=list(combinations(range(n),2));valid=0;best=0
    for weights in product(range(3),repeat=len(edges)):
        adjacency=[set() for _ in range(n)]
        for (u,v),w in zip(edges,weights):
            if w:adjacency[u].add(v);adjacency[v].add(u)
        if any(w==2 and adjacency[u]&adjacency[v] for (u,v),w in zip(edges,weights)):continue
        valid+=1;score=sum(weights);assert score<=n*n//2;best=max(best,score)
    graph_results.append({'vertices':n,'graphs_checked':3**len(edges),'admissible':valid,'maximum_normalized_weight':best,'theorem_bound':n*n//2})

out={'status':'PASS','scope':'Finite controls supplement the analytic arbitrary-dimensional proofs. No profile-count credit is taken here.','periodic_pairs_F2_4':periodic_checks,'three_spaces_F2_5':len(spaces),'rooted_edge_checks':edge_checks,'active_rooted_edges':active_edges,'maximum_rooted_edge_capacity':maximum_edge,'rooted_triangle_checks':triangle_checks,'positive_outside_triangles':positive_triangles,'weighted_graphs':graph_results}
(HERE/'SHARED_GEOMETRY_CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
