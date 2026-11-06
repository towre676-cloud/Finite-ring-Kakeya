# Ten heavy residues and the last support-eighteen profile

## General incidence lemma

Let K be a Kakeya set in either target ring in dimension five. Partition its
pair-active residue support into a set T of ten heavy residues and light
fibres of sizes at most three. Suppose every heavy fibre has size at most
eleven, and k of the heavy fibres have size at most six. Then the total
light pair mass satisfies

    sum_light binom(|A_a|,2) >= min(3k,12).                 (1)

More precisely, if r is the number of nonzero residue directions absent from
the heavy difference set T+T, then

    sum_light binom(|A_a|,2) >=4r+k*max(0,3-r).             (2)

This is an analytic necessary condition for both rings. It uses the analytic
nine-point difference bound in
../middle/DIFFERENCE_AND_LIGHT_RESOURCE_LEMMAS.md: every nine-point subset of
F2^5 determines at most twenty-eight nonzero differences.

## Proof

Let u(a) count directions in which there is exactly one heavy-heavy edge and
that edge is incident to a in T. Removing a from T deletes precisely those
u(a) represented differences: in every fixed binary direction the pairs are
disjoint, so removing one vertex cannot remove a direction represented by two
or more heavy pairs. Therefore

    |(T\{a})+(T\{a}) minus {0}|=31-r-u(a)<=28,
    u(a)>=max(0,3-r).                                     (3)

A light fibre of size two or three has directional pair count zero or one.
One unit of light pair mass can contribute at most five covered lift classes
through a light-heavy edge, since heavy pair counts are at most floor(11/2)=5.
A light-light edge covers at most one class while consuming two light pair
units, so it cannot violate this per-unit bound.

Every direction absent from T+T requires all sixteen lifted classes from
edges involving light fibres. At least four light pair units are required,
because three units can cover at most fifteen classes.

Now consider a direction with exactly one heavy-heavy edge. If one endpoint
is among the selected k weak heavy fibres, that endpoint has pair count at
most three. Its partner has pair count at most five. The heavy edge covers
at most fifteen classes, so at least one light pair unit is necessary.
If both endpoints are selected weak fibres, the heavy edge covers at most
nine classes. One light pair unit contributes at most five more, for at most
fourteen, so at least two light pair units are necessary.

Thus these directions spend at least one light pair unit per incident
selected weak vertex, and the total cost from uniquely represented heavy
directions is at least sum_weak u(a). These directions are disjoint from the
r missing directions. The same light fibre may contribute in several
directions, but the sum of all its directional pair counts is exactly its
binomial pair mass, so this accounting remains valid. Consequently

    sum_light binom(|A_a|,2) >=4r+sum_weak u(a)
                           >=4r+k*max(0,3-r).

For0<=r<=3 the last expression is3k+(4-k)r; for r>=3 it is at least12.
Its minimum over all nonnegative integer r is min(3k,12), proving(1).

## Exclusion of the final profile C

The fibre-weight multiset is

    (11,8,8,8,8,8,8,6,6,6,2,2,2,2,2,2,2,2)
      =(11,8^6,6^3,2^8).

It has total weight93 and support18. Choose the ten fibres of weights at
least six as heavy. Their maximum is eleven; three have size six. Thus k=3,
and(1) requires at least nine units of light pair mass.

The eight light fibres each contain two points and supply exactly one pair,
so their total pair mass is eight. This contradiction excludes the entire
weight multiset, uniformly over every residue support and every tangent-fibre
shape, in both rings.

The stronger form makes the strict gap explicit:

| missing heavy directions r | necessary light pair mass |
|---|---:|
| 0 | at least9 |
| 1 | at least10 |
| 2 | at least11 |
| at least3 | at least12 |

No carry phase is suppressed: only necessary upper bounds on the number of
classes an edge can cover are used. The lemma does not assert existence of
a Kakeya set at any equality case of its resource bound.

## Independent finite controls

verify_ten_heavy_incidence.py checks all14,950 normalized full-rank ten-point
sets containing the affine frame{0,1,2,4,8,16}. Every full-rank ten-point set
has such a normalization. Lower-rank sets have at most fifteen nonzero
differences and hence r>=16, which already makes the light resource bound
far larger than eight.

For each normalized set, the checker recomputes all pair multiplicities,
every unique-edge degree, the exact removal identity, and the minimum
resource bound over all choices of three weak heavy vertices. The minimum
is nine, attained by an explicit geometric example. These finite controls
corroborate the analytic proof; completeness of the proof does not depend
on them.
