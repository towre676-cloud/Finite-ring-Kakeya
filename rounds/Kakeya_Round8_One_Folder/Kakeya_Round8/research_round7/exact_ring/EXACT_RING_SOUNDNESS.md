# Exact membership encoding over the two four-element rings

## Scope

`encode_exact_ring.py` models actual point membership, with exact coverage
of every primitive direction in Rⁿ, for either R=Z/4Z or
R=F₂[ε]/(ε²). It uses neither the spectrum census nor a sumset-capacity
table. Subject to the stated support, weight, and optional common affine
normalization, the formula is satisfiable **if and only if** the requested
Kakeya set exists.

Its Boolean and geometric interpretation is proved here by hand and checked
in finite instances. This is not a proof-assistant formalization.

## Residue and tangent coordinates

Write π=2 in Z/4Z and π=ε in the dual-number ring. Every point has unique
coordinates a+πx with a,x∈F₂ⁿ, using the representatives 0 and 1 in each
coordinate. A primitive direction has the form d+πu with d≠0.

The two units in either ring identify u and u+d. Thus for each of the
2ⁿ−1 nonzero residue directions d there are 2ⁿ⁻¹ primitive direction
classes. We identify the quotient F₂ⁿ/⟨d⟩ with the vectors whose highest
nonzero coordinate of d is zero, by the linear projection

    q_d(x)=min(x,x+d).

The minimum compares the integer labels of binary vectors. The map clears
the highest set bit of d, is linear, and has kernel {0,d}.

Fix a pair-active support S containing zero. For each a∈S, Boolean
membership variables X(a,x) describe the actual tangent fibre A_a. Every
fibre has weight at least two. Zero is distinguished as a largest fibre;
ties are allowed. The maximum weight is bounded by the requested upper
limit and the distinguished weight is bounded below by the requested
lower limit.

## Four-point lines and the ring-specific carry

For d≠0, a primitive line joins the two residue fibres a and b=a+d. Its
two points over a have tangent coordinates x,x+d. If the direction is
d+πu, its two points over b have tangent coordinates

    x+u+c_R(a,d), x+u+c_R(a,d)+d,

where

    c_R(a,d)=a AND d  for Z/4Z,
    c_R(a,d)=0        for F₂[ε]/(ε²).

For Z/4Z, this is the coordinate carry in adding two binary residue
representatives: a+d=(a XOR d)+2(a AND d). For the dual numbers residue
addition is characteristic two and has no carry. Multiplying the direction
by π adds d to the tangent coordinate within a residue fibre in both rings.

Define a d-pair variable P(a,d,x), for x=q_d(x), by the exact equivalence

    P(a,d,x) ↔ X(a,x) AND X(a,x+d).

For an unordered support edge {a,b} with b=a+d, choose the orientation
a<b. A pair class x in A_a and a pair class y in A_b cover exactly the
lift class

    u=q_d(x+y+c_R(a,d)).

Reversing the edge does not change that class: in Z/4Z the carry changes
by d, killed by q_d, and in the dual numbers both carries are zero.

The encoder introduces an exact AND witness for each pair of pair classes,
P(a,d,x) AND P(b,d,y). For each (d,u), one clause says that at least one
of its witnesses is true. These are the actual **union-coverage**
conditions; capacities or sums of sizes are not substituted for coverage.
All relative translations of the fibres remain represented by the
membership variables.

## Equivalence with Kakeya sets

Given a genuine set on S, assign the membership variables from its points.
Assign each pair and witness variable its actual conjunction. If the set
is Kakeya, every primitive direction class has a four-point line in the
set; its two residue pairs provide a true witness in the corresponding
coverage clause. Conversely, a true witness in a coverage clause provides
the four points of a line in exactly that direction, by the coordinate
calculation above. Satisfying every clause therefore gives a line in every
primitive direction class.

Weight counters are exact threshold counters, so their clauses are
equivalent to the stated size restrictions. The two implications prove
the asserted equivalence before normalization.

## Exact cardinalities and the budget

For each fibre the totalizer outputs T(a,j) mean |A_a|≥j. They enforce
|A_a|≥2, the requested upper bound, the distinguished lower bound, and

    T(a,j) ⇒ T(0,j)

for all other fibres and 3≤j≤maximum. Since all fibres have weight at
least two, these implications make zero largest, including ties.

The total number of points is exactly

    2|S| + sum over a∈S and j=3,…,maximum of T(a,j).

The global budget counts these shared threshold bits. It counts the
distinguished fibre and every other active fibre once.

The bidirectional totalizer retains only thresholds up to a requested
limit. For each retained threshold t, the usual forward clauses force it
whenever the two child counts sum to at least t, and the backward clauses
forbid it whenever their sum is smaller than t. Child counts are needed
only up to t, so omitting larger thresholds preserves exactness. An
induction over the binary merge tree proves every retained output has its
stated meaning. Finite controls exhaust small instances including all
auxiliary assignments and check larger canonical assignments.

## A valid six-fibre normalization

Independent translations of all fibres would generally change the covered
lift classes differently on different edges and are **not** used here.

Instead choose 0 and five linearly independent support residues a₁,…,a₅
(or a basis of the support span in smaller dimension). Choose an arbitrary
point x_i in each corresponding tangent fibre, including x₀∈A₀. There
is a common affine tangent function a↦t+La with

    t=x₀,       La_i=x_i+x₀.

The same transformation of the entire ring space is

    z ↦ (I+πL)z+πt.

Since π²=0, I+πL is invertible, with inverse I−πL. In the two rings here
the minus sign agrees on π-coefficients. This affine automorphism sends
every line to a line and permutes primitive directions. It fixes the
residue a of every point, and its action on tangent coordinates is

    x ↦ x+t+La.

Each selected x_i consequently becomes zero in its anchor fibre. Every
fibre cardinality, the support, and the position of the largest fibre are
unchanged. The direction lift u changes uniformly, for fixed d, to
u+Ld modulo ⟨d⟩. Thus coverage of all lifts is preserved.

Requiring zero membership in these six anchor fibres loses no Kakeya set.
The remaining fibres are not individually normalized. If a support has
lower rank, extending L arbitrarily from a residue basis gives the same
valid argument on that span. A support covering every residue direction
necessarily has full affine rank.

## A complete dimension-two test

For n=2, a pair-active support must have at least three points: every
nonzero residue direction must be a difference of two support points,
and at most two support points supply only one of the three directions.
There is one affine support orbit of size three and one of size four.
After translating a chosen largest vertex to zero, the other two vectors
of a triangle are independent, so a linear residue map takes it to
{0,1,2}. The full support is {0,1,2,3}. Binary invertible matrices lift
to invertible matrices over either local ring, and residue translations
lift to ring affine translations. These changes preserve Kakeya sets.

Accordingly, checked UNSAT at budget nine for these two supports in each
ring excludes every nine-point counterexample. A directly checked ten-point
SAT witness then gives the global minimum ten in dimension two. The
separate certificate ledger must establish those outcomes before this
conclusion is credited; the reduction itself does not assume them.

## Independent finite checks

`verify_exact_ring.py` uses literal ring multiplication and addition to
enumerate primitive directions and line sets. It compares their complete
four-point membership terms with the encoder's carry-based terms on both
dimension-two supports and a dimension-five support13 representative.
Equality of these finite line families checks coverage for **every**
membership assignment on those supports, including relative translations.

It also checks every common affine tangent map in dimension two, actual
mapped lines, randomized dimension-five normalizations, and both
94-point stars against every generated clause and a direct ring-line
Kakeya test. Corrupted conjunction values are rejected. None of these
tests replaces the general proof above or a checked refutation for any
claimed finite exclusion.
