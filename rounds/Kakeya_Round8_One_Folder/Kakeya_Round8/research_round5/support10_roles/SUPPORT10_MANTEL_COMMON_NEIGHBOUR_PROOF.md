# The weight-12 centre obstruction on the support of size 10

**Theorem.** Let G = F₂⁵ = V ⊕ W, where dim V = 3 and dim W = 2. For any nonzero w ∈ W, set

\[
F=\bigl(w+(V\setminus\{0\})\bigr)\cup\bigl(W\setminus\{0,w\}\bigr).
\]

Then every set A ⊂ G with |A| = 12 satisfies

\[
\boxed{\sum_{d\in F}p_A(d)\le 35},
\qquad
p_A(d)=\frac{|A\cap(A+d)|}{2}.
\]

Consequently, **a 12-point fibre cannot satisfy p_A(d) ≥ 4 in all nine directions d ∈ F.**

The proof is elementary. The separate computation below verifies the small finite common-neighbour statement directly, without SAT and without reading any earlier census.

## 1. The nine directions are sum-free

Choose u ∈ W \ {0,w}, so W = {0,w,u,u+w}. Write

\[
B=w+(V\setminus\{0\}),\qquad E=\{u,u+w\},\qquad F=B\cup E.
\]

Thus |B| = 7, |E| = 2 and |F| = 9. We claim F ∩ (F+F) is empty.

The sum of two points of B lies in V, whereas F is disjoint from V. Sums of two points of E are either 0 or w, both outside F. Finally, a point of B has a nonzero V-component, whereas each point of E has zero V-component. The sum of a point of B and a point of E lies in one of the two E-cosets of V, with a nonzero V-component, and hence is outside F. These cover all pairs and prove the claim.

Therefore the Cayley graph on G with edges {x,y} whenever x+y ∈ F is a simple triangle-free graph. A triangle would give three members x+y, y+z, z+x of F, the first two summing to the third.

## 2. Its large common-neighbour sets are impossible

**Lemma.** For every six-element subset Y ⊂ F,

\[
N(Y)=\{z\in G:z+y\in F\ \text{for every }y\in Y\}
\]

has size at most 2. More precisely:

\[
N(Y)=
\begin{cases}
\{0,z\},&Y=w+(V\setminus\{0,z\})\text{ for some }z\in V\setminus\{0\},\\
\{0\},&\text{otherwise.}
\end{cases}
\]

**Proof.** The point 0 is always a common neighbour because Y ⊂ F. If z is another common neighbour, then

\[
Y\subseteq F\cap(F+z).
\]

We compute this overlap.

If z ∈ V \ {0}, translation by z preserves each coset of V. The seven-point set B is the coset w+V with w deleted, so

\[
B\cap(B+z)=w+(V\setminus\{0,z\}).
\]

Neither singleton in E overlaps its own translate by a nonzero element of V. Consequently,

\[
F\cap(F+z)=w+(V\setminus\{0,z\}),
\]

which has exactly six points.

If z ∉ V, consider the quotient G/V, which has four points. The three occupied cosets of F are the three nonzero quotient points; their occupancies are 7, 1, 1. Translation by a nonzero quotient element pairs the four cosets into two pairs. Exactly one pair has both cosets occupied. At least one coset in that pair is a singleton, so each orientation of the pair contributes at most one point to the intersection. Hence

\[
|F\cap(F+z)|\le 2\qquad(z\notin V).
\]

A six-element Y therefore forces any nonzero common neighbour z to lie in V, and then forces

\[
Y=w+(V\setminus\{0,z\}).
\]

The missing nonzero V-element determines z uniquely. There can be at most one common neighbour besides 0, proving the lemma. Conversely, every six-element subset of B has exactly the indicated two common neighbours. ∎

In particular, the Cayley graph contains **no K₃,₆**, and hence no K₆,₆. Indeed, translate one vertex of the three-vertex class to 0; its six neighbours then form a subset Y of F, while all three vertices of the other class are common neighbours of Y, contradicting the bound 2.

## 3. Mantel's equality case applies exactly

Given a 12-set A, let H be the subgraph induced on A using the differences in F. Each unordered pair of distinct points has one nonzero difference, so there is no double counting:

\[
e(H)=\sum_{d\in F}p_A(d).
\]

The graph is triangle-free by Section 1. Mantel's bound gives e(H) ≤ 12²/4 = 36. If all nine values p_A(d) were at least 4, this would force equality e(H) = 36.

For completeness, the equality characterization here has a short direct proof. In any triangle-free graph on n vertices, the two neighbourhoods of an edge's endpoints are disjoint, so d(x)+d(y) ≤ n for each edge {x,y}. Summing this inequality and applying Cauchy–Schwarz gives

\[
\frac{(2e)^2}{n}\le\sum_xd(x)^2
=\sum_{\{x,y\}\in E(H)}\bigl(d(x)+d(y)\bigr)
\le ne.
\]

For n = 12 and e = 36, both inequalities are equalities. Every vertex therefore has degree 6. Fix an edge {x,y}. Its two disjoint neighbourhoods have size 6 and cover the 12 vertices. Each neighbourhood is independent because H is triangle-free. Degree 6 now forces every possible edge between the two parts, so H = K₆,₆.

Section 2 rules this out. Hence e(H) ≠ 36; as it is an integer, e(H) ≤ 35. This proves the theorem. ∎

## 4. Relevance to the support-10 role problem

Suppose the support is

\[
S=(V\setminus\{0\})\cup(W\setminus\{0\}).
\]

For a support vertex w ∈ W \ {0}, its nine incident directions are exactly

\[
\{w+s:s\in S\setminus\{w\}\}=F.
\]

Every one of these directions has exactly one residue edge in S. For a cross direction w+v, its V-component and W-component determine the cross edge uniquely. A nonzero direction in W has exactly one edge among the three nonzero points of W, and no edges involving V. Thus each of the nine directions at w must obtain all 16 required quotient labels from its single edge.

Here is the needed strengthening of the product bound, including the two centre-centre edges. For a fixed direction d, the disjoint d-pairs in a fibre define a subset P of G/⟨d⟩ ≅ F₂⁴, with |P| = p_A(d). The other endpoint defines Q with |Q| = p_{A'}(d). The unique-edge coverage condition requires P+Q, up to its fixed translation, to be all of F₂⁴. A fixed carry translation in the ring-specific formulation does not affect this condition.

**Three-point coset lemma.** If P ⊂ F₂⁴ has three points and P+Q = F₂⁴, then |Q| ≥ 8. Translate P to {0,a,b}. Its two nonzero vectors are independent, so P lies in a 2-dimensional subspace H of size 4. Each of the four H-cosets must contain at least two points of Q: one point could supply only three of that coset's four points, while points in other cosets contribute nothing there. Hence |Q| ≥ 2·4 = 8.

In the last two role-surviving profiles, every fibre has size at most 13. Therefore |Q| ≤ ⌊13/2⌋ = 6 at every neighbour. If |P| ≤ 2, then |P+Q| ≤ 12. If |P| = 3, the three-point lemma again rules out coverage. **Consequently p_A(d) ≥ 4 in each of the nine unique directions, including both centre-centre directions.** Product capacity alone would only force 3 on those two edges; the coset lemma is essential here.

The separate role certificate places the three centre fibres on W \ {0}. Its last two profiles and allowed centre weights are:

| All ten fibre weights | Three centre weights |
|---|---|
| (13,12,12,8,8,8,8,8,8,8) | (13,12,12) |
| (12,12,12,9,8,8,8,8,8,8) | (12,12,12) |

Choose a weight-12 centre in either row. The argument just given forces all nine p_A(d) to be at least 4, contradicting the theorem. **Both listed residual profiles are excluded.** This application uses the unique-edge quotient coverage condition and the centre placements certified by the separate support-role argument. It does not rely on an unavailable SAT encoding.

All choices of complementary subspaces V,W and nonzero w are equivalent under an invertible linear map of G. Such a map preserves unordered pair counts, sum-freeness, common-neighbour counts and the conclusion, so one coordinate representative suffices for the replay.

## 5. Independent finite replay

Choose V = {0,…,7}, w = 8 and u = 16. Then

\[
F=\{9,10,11,12,13,14,15,16,24\}.
\]

The script `verify_support10_mantel_obstruction.py` checks sum-freeness, verifies every translate-overlap bound, and independently enumerates all 84 subsets Y ⊂ F of size 6. For each it examines every candidate common neighbour among the 32 points, using the definition directly.

The exact distribution is:

| Common neighbours | Number of six-subsets Y |
|---:|---:|
| 1 | 77 |
| 2 | 7 |

The seven extremal sets are precisely the six-subsets of the seven-point set {9,…,15}. The complete list of all 84 subsets and their common neighbours is retained in `SUPPORT10_MANTEL_COMMON_NEIGHBOUR_REPLAY.json`.

Run from the workspace root:

```bash
python3 research_round5/support10_roles/verify_support10_mantel_obstruction.py
```

This computation is an independently reproducible finite check. The hand proof above establishes the general statement and the applicability of Mantel's equality case; neither claims a proof-assistant formalization.
