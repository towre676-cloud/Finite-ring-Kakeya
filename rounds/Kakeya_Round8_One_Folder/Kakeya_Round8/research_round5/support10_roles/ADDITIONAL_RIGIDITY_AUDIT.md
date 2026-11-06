# Audit: the ordinary weight-5 obstruction and the all-17 support-10 profile

## Verdict and scope

**Both proposed lemmas are correct.** The ordinary three-direction graph
gives at most five pairs for a weight-5 fibre, whereas unique-edge coverage
requires at least six. The all-17 central profile forces a 17-point fibre
to have a full affine 4-flat plus one exterior point, which cannot supply
the central-central unique directions.

The exact arithmetic in the latter argument is

    max over k=2,...,8 of [e(k)+e(17-k)] = 53 < 56,
    e(t) = min(floor(t^2/4), floor(7t/2)).

Here e(t) is a valid upper bound, not an asserted exact extremal function.
The proof does not use an odd-weight maximal-direction closure lemma.

This document also applies the existing weight-16 rigidity theorem to
the three additional weight-16 profiles found by the standalone weight
universe. It does not recheck that universe or replace the separate proof
for the two profiles with central weights 13,12,12 and 12,12,12. No frozen
script or previous result file was changed.

## 1. Ordinary unique directions are independent

Use the already proved support normal form

    S = (V minus {0}) union (W minus {0}),

with dim V=3, dim W=2, and V direct-sum W = F2^5. For an ordinary support
vertex v in V minus {0}, write W minus {0} as {w1,w2,w1+w2}. Its three
incident unique-edge directions are

    d1=v+w1,   d2=v+w2,   d3=v+w1+w2.

They are distinct and nonzero, and their sum is v, which is nonzero.
Over F2, a dependence among three distinct nonzero vectors would have
to use all three. Consequently d1,d2,d3 are linearly independent.

Let H be their three-dimensional span. The Cayley graph with these three
directions has four connected components, the four H-cosets. Using
d1,d2,d3 as a basis of H identifies each component with the ordinary
three-dimensional cube Q3. For a tangent fibre A, the number of induced
edges in this graph is exactly

    p_A(d1)+p_A(d2)+p_A(d3).

Each unordered pair is counted once and has exactly one of the displayed
directions.

## 2. Five vertices in disjoint three-cubes span at most five edges

Inside a single Q3, the maximum induced edge counts at sizes 0 through 5
are

    0, 0, 1, 2, 4, 5.

The bounds up to size four follow from bipartiteness. For size five,
remove the three complementary vertices from the 12-edge, 3-regular cube.
If those three removed vertices span r edges, the five retained vertices
span

    12 - 3*3 + r = 3+r.

The removed three vertices span at most two edges, since a cube contains
no triangle. Thus the retained five span at most five edges. Equality
is attained by taking the complement of a three-vertex path.

If the five vertices are distributed among several cube components,
the possible nonzero component-size partitions give:

| Component sizes | Induced-edge upper bound |
|---|---:|
| 5 | 5 |
| 4+1 | 4 |
| 3+2 | 3 |
| 3+1+1 | 2 |
| 2+2+1 | 2 |
| 2+1+1+1 | 1 |

There are only four cube components, so no further partition is needed.
In particular, every weight-5 fibre A satisfies

    p_A(d1)+p_A(d2)+p_A(d3) <= 5.                    (1)

For the local coverage lower bound, assume all fibre weights are at most
18. Every neighbor has pair count at most floor(18/2)=9 in a direction.
An edge whose local pair count is at most one can cover at most nine
quotient labels, fewer than the required 16. Each of the three unique
edges therefore forces the ordinary fibre to supply at least two pairs.
This gives a lower bound of six in (1), a contradiction.

**An ordinary support-10 fibre of weight 5 is therefore impossible when
the maximum fibre weight is at most 18.** This conclusion uses only the
product upper bound on sumset size; it is unchanged by either ring carry.

## 3. The seven outer directions at a weight-17 centre

Consider the profile

    (17,17,17,6,6,6,6,6,6,6),

with its allowed central triple (17,17,17). Fix a central residue w and
let A be its 17-point tangent fibre. The seven ordinary neighbors have
weight six. Their unique-edge directions form

    F = w+(V minus {0}).

For each d in F, the central pair count is at most floor(17/2)=8 and the
ordinary pair count is at most three. The three-point quotient-sumset
lemma proved in `FIRST_FIVE_RIGIDITY_AUDIT.md` says that a pair set of at
most seven points and one of at most three points cannot sum to all of
F2^4. Hence every one of these seven edges forces

    p_A(d)=8,

and therefore

    sum over d in F of p_A(d) = 56.                  (2)

For this odd-weight fibre, the equality p_A(d)=8 is **not** asserted to
make d a period. The rest of the argument uses the actual induced graph
instead.

## 4. The seven-direction graph and its two components

Let L=V+span(w), a four-dimensional subspace. The set F spans L: its
three elements w+v1, w+v2, w+v1+v2 sum to w for independent v1,v2 in V,
after which its elements also generate V.

The Cayley graph in these seven directions consequently has two
components, the two L-cosets. In a component, the two vertex classes are
the V-cosets V and w+V, after translation. A vertex v in the first class
is adjacent to w+v' in the second exactly when

    (w+v')+v is in F, equivalently v' differs from v.

Thus each component is K_(8,8) with a perfect matching removed. It is
bipartite and 7-regular, with 16 vertices and 56 edges.

For any t selected vertices in one component, bipartiteness bounds the
induced edges by floor(t^2/4). The maximum degree seven independently
bounds them by floor(7t/2). Their minimum is the valid upper bound e(t)
stated above.

## 5. Every split other than 16+1 fails the forced pair mass

Let k be the number of points of A in its less populated L-coset. Since
|A|=17 and each L-coset has only 16 points, 1 <= k <= 8. For k=2,...,8,
the exact values of the bounds are:

| k | 17-k | e(k) | e(17-k) | Sum of upper bounds |
|---:|---:|---:|---:|---:|
| 2 | 15 | 1 | 52 | 53 |
| 3 | 14 | 2 | 49 | 51 |
| 4 | 13 | 4 | 42 | 46 |
| 5 | 12 | 6 | 36 | 42 |
| 6 | 11 | 9 | 30 | 39 |
| 7 | 10 | 12 | 25 | 37 |
| 8 | 9 | 16 | 20 | 36 |

Every row is strictly below the 56 edges forced by (2). Thus k=1.
The other L-coset contains 16 points of A, so it is full. We have proved

    A = C union {z},

where C is an affine L-coset and z lies outside C. This form has exactly
56 edges in the seven directions, consistent with (2).

## 6. The remaining central directions contradict coverage

If d is outside L, there are no d-pairs wholly within C, since every
difference of two points of C belongs to L. Also z+d belongs to C,
because E/L has two elements and d changes the coset. Therefore the
only d-pair in A is {z,z+d}, and

    p_A(d)=1  for every d outside L.                 (3)

Take either other central residue u in W minus {0,w}. Its edge to w
has direction d=w+u. This direction belongs to W but not span(w), so it
does not belong to L=V+span(w). The edge is unique in its direction.
Its A endpoint supplies exactly one pair by (3), while the other
17-point central fibre supplies at most eight. Their quotient sumset
has at most eight labels, strictly fewer than 16. This is a contradiction.

**The profile (17,17,17,6^7), with its forced central triple, is excluded
in both rings.** The proof did not use a theorem about closure of
maximal-pair directions for odd-weight sets.

## 7. The three additional weight-16 profiles

The existing first-five audit proved a reusable statement: a central
weight-16 fibre cannot have four or more ordinary neighbors of weight
at most six. It therefore immediately excludes the three additional
profiles in the standalone weight universe:

| Whole profile | Allowed central triple | Ordinary weights | Weight-6 neighbors |
|---|---|---|---:|
| 18,17,16,6,6,6,6,6,6,6 | 18,17,16 | 6,6,6,6,6,6,6 | 7 |
| 18,16,16,7,6,6,6,6,6,6 | 18,16,16 | 7,6,6,6,6,6,6 | 6 |
| 17,17,16,7,6,6,6,6,6,6 | 17,17,16 | 7,6,6,6,6,6,6 | 6 |

Choose a central weight-16 fibre in each row. It meets every ordinary
vertex by a unique edge, so the required four neighbors are present.
The earlier period-flat contradiction applies without change.

These are three additional exclusions, alongside the all-17 exclusion
proved here. Together with the five rows in the first audit, nine of
the eleven standalone survivors are covered by these two documents.
The final two rows are left to the separate central-weight-12 argument.

## Verification boundary

The two graph arguments and the split inequalities were re-derived
analytically. A small independent calculation also enumerated all 256
subsets of Q3, recovering the edge table

    0,0,1,2,4,5,7,9,12,

checked the maximum five-vertex resource across four components is five,
and recomputed the seven split bounds displayed above. It also checked
the model 16+1 set directly, obtaining mass 56 in F and one pair in
each direction outside L. Those calculations support the elementary
proofs; they are not a substitute for them.

This is a second model-assisted analytic audit within the same project,
not independent human review or proof-assistant formalization. The
support classification and the exhaustive allowed-role assignments
remain separately stated inputs. No claim about the final two profiles
is made by this audit.
