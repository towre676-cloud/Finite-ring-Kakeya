# Audit: a complete analytic exclusion of support 10

## Verdict and strengthened theorem

**The analytic role reduction is correct, and its extension removes the
fibre-weight cap entirely.** No enumeration of the 102,842 weight profiles,
no inherited profile screen, and no separate list of allowed central
triples is needed for this conclusion.

**Theorem.** In either R = Z/4Z or R = F2[epsilon]/(epsilon^2), a Kakeya set
in R^5 whose residue support has size 10 has at least 94 points.

The proof uses the separately established classification of difference-
covering supports of size 10 and the three analytic fibre obstructions
listed below. The support classification is still a finite-computation
dependency. This audit does not claim a purely analytic proof of that
classification or a proof-assistant formalization of this new theorem.

There is one boundary detail when the total is at most 93 rather than
exactly 93: the low-centre branch also allows the numerical profile
(12,12,12,8,8,8,8,8,8,8), of total 92. The same weight-12 obstruction
excludes it directly. Padding is unnecessary.

## 1. Geometric and local inputs

Suppose for contradiction that K has at most 93 points and support size
10. Every primitive residue direction needs a support edge, so the
support is difference-covering. By the support classification and the
valid affine normalization over either ring, we may take

    S = (V minus {0}) union (W minus {0}),

where dim V=3, dim W=2, and V direct-sum W=F2^5. Call the three vertices
of W minus {0} central and the seven vertices of V minus {0} ordinary.

Every central-central and central-ordinary edge is unique in its
direction. Thus every central vertex has nine incident unique-edge
directions; these form a sum-free set F_w spanning F2^5. Every ordinary
vertex has three incident unique-edge directions, which are independent.
The Cayley graph in those three directions is four disjoint cubes Q3.

Every support vertex has an incident unique edge and must supply a
tangent pair on it. In particular, every fibre has at least two points.
Every fibre also has at most 32 points because its tangent ambient space
is F2^5. These intrinsic bounds, rather than any hypothesized cap 18 or
19, are the only general fibre-size bounds used below.

For a unique edge with quotient pair-set sizes p,q, coverage requires
that the two sets sum, up to a fixed carry translation, to all 16 points
of F2^4. We repeatedly use three necessary implications:

    if q <= 3, then p >= 8;
    if q <= 7, then p >= 4;
    if q <= 15, then p >= 2.                         (1)

The first two follow from the three-point coset lemma: a set of at most
three points plus one of at most seven points cannot cover F2^4. The
last is the product bound. The usual pair cap is p_A(d)<=floor(|A|/2).

For any central fibre of weight t, sum-freeness of its nine directions
makes the corresponding induced graph triangle-free, so

    sum over those nine directions of p_A(d) <= floor(t^2/4).  (2)

For an ordinary fibre, its three-direction cube graph supplies at most
four edges on at most four vertices, and at most five edges on at most
five vertices. The latter bound is proved in
`ADDITIONAL_RIGIDITY_AUDIT.md`.

We also use these already audited analytic obstructions:

* A central weight-12 fibre has total pair mass at most 35 in its nine
  unique directions. See `SUPPORT10_MANTEL_COMMON_NEIGHBOUR_PROOF.md`.
* A central weight-16 fibre cannot have four ordinary neighbors of
  weight at most six. See `FIRST_FIVE_RIGIDITY_AUDIT.md`.
* The central triple (17,17,17) with seven ordinary weights six is
  impossible. See `ADDITIONAL_RIGIDITY_AUDIT.md`.

These are shape-independent statements about actual fibres and exact
unique-edge coverage. Their use below does not assume a numerical
profile list or a previously certified role assignment.

## 2. The smallest central weight is at least 12

Let a<=b<=c be the three central weights, and let x1,...,x7 be the
ordinary weights. We have

    a+b+c+x1+...+x7 <= 93.                           (3)

### Case a<=7

The centre of weight a has pair cap at most three. By the first
implication in (1), each of its seven ordinary neighbors must have at
least eight pairs in the corresponding direction. Hence every xi>=16.
The ordinary fibres alone would have at least 112 points, contradicting
(3). Thus a>=8.

### Case 8<=a<=11

The centre of weight a has pair cap at most five, hence at most seven.
By the second implication in (1), each ordinary neighbor must supply
at least four pairs and therefore has xi>=8. The other two central
weights are also at least eight. All nine neighbors of this centre
therefore have weight at least eight.

At most one of these nine neighbors has weight at least 16. Otherwise
the total weight would be at least

    a + 9*8 + 2*(16-8) = a+88 >= 96,

contradicting (3).

Furthermore, any one neighbor has weight at most

    93-a-8*8 = 29-a <= 21.                          (4)

Thus even the possible exceptional neighbor has pair cap at most ten,
strictly less than 16. It forces at least two pairs at the centre.
Each of the at least eight other neighbors has weight at most 15 and
pair cap at most seven; it forces at least four central pairs by (1).
The central pair mass is consequently at least

    8*4+2 = 34.

But (2) bounds that mass by floor(a^2/4)<=floor(11^2/4)=30. This is a
contradiction. We conclude that **a>=12**, with no global fibre cap.

## 3. A smallest central weight between 12 and 15 is impossible

Suppose 12<=a<=15. Its pair cap is at most seven, so (1) forces every
ordinary weight to be at least eight. Equation (3) then gives

    36 <= a+b+c <= 93-7*8 = 37.

The central triple is therefore either (12,12,12) or (12,12,13).
Each ordinary weight is at most

    93-36-6*8 = 9.

Choose a central weight-12 fibre. Every one of its nine neighbors has
weight at most 13: the other centres have weight at most 13 and the
ordinary vertices have weight at most nine. Their pair caps are at
most six. By (1), every one of the nine unique directions requires at
least four pairs from the chosen centre.

This forces central pair mass at least 36, contradicting the
weight-12 theorem's bound 35.

This argument handles total 92 as well as total 93. Numerically, the
possibilities at total at most 93 are (12^3,8^7), (12^3,9,8^6), and
(13,12,12,8^7), but no enumeration of them is needed for the proof.

Consequently, the only remaining possibility is **a>=16**.

## 4. Full central fibres are impossible in the high-centre branch

All three central weights are now at least 16. We first remove the
only situation in which a central pair cap could reach 16: a full
weight-32 fibre.

There cannot be two weight-32 centres. The third centre has weight at
least 16, and every ordinary fibre has at least two points, giving

    32+32+16+7*2 = 94 > 93.

Suppose there is exactly one weight-32 centre. The other two centre
weights lie between 16 and 31, so their pair caps are at most 15.
At every ordinary vertex, its two unique edges to those centres
therefore require at least two local pairs each. Its edge to the
weight-32 centre requires at least one local pair. The three-direction
pair mass is at least

    2+2+1 = 5.

At most four vertices of a disjoint union of cubes span at most four
edges. Hence every ordinary fibre has weight at least five. The total
weight is now at least

    32+16+16+7*5 = 99 > 93,

another contradiction.

Thus **all three central weights are at most 31**. This conclusion
has been derived rather than imposed as an input cap.

## 5. The high-centre branch has only three units of slack

Every centre now has pair cap at most 15. Each ordinary vertex must
therefore supply at least two pairs in each of its three independent
unique directions. Its total mass is at least six. The cube bound
rules out every ordinary fibre of weight at most five, so every xi>=6.

We obtain the baseline and slack identity

    a+b+c+x1+...+x7 >= 3*16+7*6 = 90,

    (a-16)+(b-16)+(c-16)+sum_i(xi-6) <= 3.          (5)

If some centre has weight 16, at most three ordinary weights can
exceed six, by (5). At least four ordinary neighbors consequently have
weight exactly six. The weight-16 period-flat theorem excludes this
case immediately.

If no centre has weight 16, all three have weight at least 17. Their
increments already consume all three units allowed in (5). Equality
is forced everywhere:

    (a,b,c)=(17,17,17),   x1=...=x7=6,

and the total weight is 93. The independently audited 17-point graph
split excludes precisely this case.

All branches have now led to contradictions. This proves the stated
support-10 lower bound of 94 without any assumed fibre-weight cap.

## 6. What the new argument removes, and what remains

The analytic argument removes the entire numerical weight-profile and
role-assignment census from the theorem's dependency chain. It also
removes any need to inherit a maximum-weight cutoff from an earlier
round. In particular, the bounded-cap-18 and bounded-cap-19 versions
are immediate special cases of the unrestricted result.

The proof still depends on the complete support-10 structural
classification, whose direct normalized search checks 14,950 sets and
finds 80 difference-covering ones. It also uses the general ring
line-to-pair bridge and the validity of affine residue normalization.
The fibre arguments thereafter are the short analytic implications
given here and in the three named companion documents.

The word "unrestricted" concerns the fibre maximum only. The theorem
is specifically about residue support size 10 in dimension five; it
does not close supports 9, 11, or larger. It establishes a lower bound
94 in this support class and does not assert that a 94-point example
with support exactly 10 exists.

## Audit status

Every case inequality and threshold in this note was re-derived from
the unique-edge sumset conditions, the canonical support geometry, and
the elementary graph bounds. In particular, the potential full-centre
exception to the "at least two pairs" demand was checked separately,
and the total-at-most-93 boundary was retained throughout. No existing
script or result file was edited. This is an analytic audit within
the same model-assisted project, not independent human review or a
proof-assistant formalization of the complete theorem.
