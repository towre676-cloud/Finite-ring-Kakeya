# Audit: the first five support-10 survivors are excluded by period rigidity

## Verdict and exact scope

**The proposed argument is correct.** It excludes the first five of the
seven profiles in `SUPPORT10_ROLE_SURVIVORS.json`, using their already
verified allowed central-role triples. It applies to both four-element
rings. The argument needs no further fibre-shape census, energy maximum,
SAT result, or assumption that the largest fibre is unique.

This audit does **not** exclude the final two profiles or claim that the
whole support-10 stratum is closed. The structural classification and the
central-role restriction are inputs established in the preceding stage;
the new mathematical implication proved here starts from those inputs.

## 1. Setup and the unique-edge directions

Work in the residue space E = F2^5. The support-10 structural theorem gives

    S = (V minus {0}) union (W minus {0}),

where E = V direct-sum W, dim V = 3, and dim W = 2. The three vertices of
W minus {0} are central; the seven vertices of V minus {0} are ordinary.

Fix a central vertex w. Its incident unique-edge directions are exactly

    F_w = {w+v : v in V minus {0}} union (W minus {0,w}).

There are nine distinct such directions. For a cross edge, the V and W
components of its difference uniquely determine its two endpoints. For a
central-central edge, each nonzero direction in W is represented by
exactly one pair of the three nonzero W-points. No ordinary-ordinary or
cross edge has that same W-only difference. Thus every edge under
discussion really is the only support edge in its direction.

Moreover, **F_w spans all five dimensions**. Choose independent v1,v2 in
V. Then v1+v2 is another nonzero vector of V, and

    (w+v1) + (w+v2) + (w+v1+v2) = w.

Hence w lies in the span of F_w. Every v in V then lies in that span by
v = (w+v)+w. Finally, either point of W minus {0,w}, together with w,
spans W. Therefore span(F_w) = V+W = E.

The previously established sum-free property of F_w is correct, but this
new rigidity argument does not need it.

## 2. A three-point sumset cannot cover the quotient with seven points

For a nonzero direction d, the quotient E/<d> is a four-dimensional binary
space Q with 16 points. For a fibre A, let

    P_A(d) = {u+<d> : u and u+d both belong to A}.

Its cardinality is the unordered pair count p_A(d). If {a,b} is the unique
support edge in direction d, Kakeya coverage forces

    P_(A_a)(d) + P_(A_b)(d) + carry = Q.

The carry is a single translation of the sumset. It does not change
whether that sumset has all 16 points.

We need the elementary implication

    |X| <= 7 and |Y| <= 3  imply  |X+Y| <= 15.       (1)

If |Y| <= 2, the product bound gives |X+Y| <= 14. Otherwise translate Y
so that Y = {0,e,f}, with e,f linearly independent. Put H = span(e,f), a
four-point plane. Addition by Y stays inside each of the four H-cosets
of Q. To cover all four points of any such coset, X must have at least
two points in that coset: zero points cover nothing, and one point covers
only three. Covering all of Q would therefore require |X| >= 8. More
explicitly, with at most seven points of X, at least one H-coset contains
at most one; it contributes at most three covered points, and the other
three cosets contribute at most four each. This proves (1).

The value 15 is sharp, although only the upper bound is used. In a basis
e,f,g,h of Q, take

    Y = {0,e,f},
    X = {0,e,g,g+e,h,h+e,g+h}.

The first three H-cosets then contribute four points apiece and the last
contributes three.

## 3. A weight-6 neighbor forces a period of a weight-16 centre

Let A be a central fibre of weight 16 and B an ordinary neighboring fibre
of weight at most 6. Their edge direction d is unique in the support.
Consequently their quotient pair sets must sum to all of Q, while

    p_A(d) <= 8,      p_B(d) <= 3.

If p_A(d) were at most 7, (1) would forbid that coverage. Therefore

    p_A(d) = 8.

The d-pairs are disjoint and account for all 16 points of A. Equivalently,

    A+d = A.                                         (2)

Thus d is a period of A. This reasoning also handles a neighbor whose
actual pair count is less than its weight-based cap; no assumption that
the neighbor attains three pairs was made.

Different ordinary neighbors give different directions w+v. Four such
neighbors therefore give **four distinct nonzero periods** of A.

## 4. Four distinct periods force a 16-point fibre to be an affine 4-flat

The periods

    Per(A) = {d in E : A+d = A}

form a linear subspace: zero is a period, and the sum of two periods is
a period. A binary subspace of dimension at most two contains at most
three nonzero points. Hence four distinct nonzero periods contain three
linearly independent ones. Let H be their three-dimensional span.

Since every h in H is a period, A is a union of full H-cosets. Each coset
has eight points, so |A| = 16 means that A consists of exactly two
distinct cosets, say

    A = (x+H) union (y+H).

Because x+y is not in H, their union is precisely

    A = x + (H + span(x+y)).                         (3)

The subspace L = H + span(x+y) has dimension four. Equation (3) proves
that A is an affine 4-flat. This step does not require the four original
periods to be linearly independent. It uses only the guaranteed three
independent periods; any additional period is automatically compatible
with the resulting flat.

For such a flat,

    p_A(d) = 8  if d is in L minus {0},
    p_A(d) = 0  if d is outside L.

Indeed, the difference of any two points of x+L belongs to L, and every
nonzero translation in L pairs all 16 points.

## 5. The rank contradiction

Every direction in F_w is the direction of a unique support edge incident
to the central fibre A. Each such edge must cover all 16 quotient labels,
so its central endpoint must supply at least one tangent pair. Therefore

    F_w is contained in {d : p_A(d) > 0}.

If A is the affine 4-flat obtained above, the right-hand set is
L minus {0}. This would put F_w in a four-dimensional linear subspace.
Section 1 proved that F_w spans dimension five. This is impossible.

We have proved the following reusable statement:

**In the canonical support-10 geometry, a central fibre of weight 16
cannot have four or more ordinary neighbors of weight at most 6.**

No choice of tangent translations, orientation of pairs, or ring carry
can evade the contradiction, since the coverage step used exact sumset
cardinality and the period step concerned the actual fibre.

## 6. Applying the statement to the five residual profiles

The preceding role verifier leaves only the indicated central triple
for each of these profiles. Select any central fibre of weight 16.
Every central vertex is adjacent by unique edges to all seven ordinary
vertices, so the following counts are enough:

| Whole weight profile | Forced central weights | Ordinary weights | Ordinary weight-6 neighbors |
|---|---|---|---:|
| 17,16,16,8,6,6,6,6,6,6 | 17,16,16 | 8,6,6,6,6,6,6 | 6 |
| 17,16,16,7,7,6,6,6,6,6 | 17,16,16 | 7,7,6,6,6,6,6 | 5 |
| 16,16,16,9,6,6,6,6,6,6 | 16,16,16 | 9,6,6,6,6,6,6 | 6 |
| 16,16,16,8,7,6,6,6,6,6 | 16,16,16 | 8,7,6,6,6,6,6 | 5 |
| 16,16,16,7,7,7,6,6,6,6 | 16,16,16 | 7,7,7,6,6,6,6 | 4 |

Every row has the required central weight 16 and at least four qualifying
ordinary neighbors. **All five profiles are excluded.**

The two remaining role survivors,

    13,12,12,8,8,8,8,8,8,8
    12,12,12,9,8,8,8,8,8,8,

have no central weight-16 fibre. They are outside this argument's scope
and require a separate exclusion.

## Audit status

The proofs above were re-derived directly from the line-to-pair quotient
description and the stated support geometry. The first five profiles and
their unique allowed central triples were checked against the actual
`SUPPORT10_ROLE_SURVIVORS.json` in this workspace. This is an analytic audit
within the same model-assisted project, not independent human review or
a Lean formalization of the new rigidity theorem. No existing source,
certificate, or result file was changed by this audit.
