# Cube directions and residual energy close the last three profiles

This proof applies in dimension five over both Z/4Z and F2[epsilon]/(epsilon^2).
It excludes the three complete weight multisets

    C = (12, 8^6, 6^2, 4, 3, 2^7),
    D = (12, 8^6, 6, 5^2, 3, 2^7),
    E = (12, 8^6, 6, 5, 4^2, 2^7).

Each has total weight 93 and support 18. No residue placement or tangent shape
is prescribed. All capacities below mean actual quotient sumset cardinalities;
ring carries translate these sumsets and do not change their cardinalities.

## 1. Pair energy forces at least five affine cubes

For a tangent fibre A, write p_A(d)=|A intersect (A+d)|/2 and

    Q(A) = sum_{d != 0} p_A(d)^2.

Each residue edge ab has direction d=a+b. Its capacity is at most
p_a(d)*p_b(d), hence at most (p_a(d)^2+p_b(d)^2)/2. At any vertex, different
neighbors give different directions. Therefore a necessary condition for
covering all 31*16=496 lifted directions is

    sum_A Q(A) >= 992.                                      (1)

We use the following established energy upper bounds:

| fibre weight | 2 | 3 | 4 | 5 | 6 | 8 | 12 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| maximum Q | 1 | 3 | 12 | 16 | 33 | 112 | 300 |

For an eight-point fibre which is not an affine three-flat, Q is at most 70.
Indeed, its augmented point matrix has rank at least five, so its binary
relation code has dimension at most three and at most seven weight-four
words. The identity Q(A)=binom(8,2)+6 Z_4(A) gives Q(A)<=28+42=70.
An affine three-flat has Q=7*4^2=112. This analytic gap is proved in
research_round2/middle/HALFSPACE_ENERGY_THROUGH_EIGHTEEN.md.

The energy maxima for weights through six follow either from the elementary
small-fibre arguments in that note or from the independently checked pair
spectrum census. For weight twelve we use the maximum 300 from that census:
research_round2/geometric/PAIR_SPECTRUM_CENSUS.json, independently regenerated
and checked by research_round2/root/verify_pair_spectra.cpp and its receipt
ROOT_VERIFIED_PAIR_SPECTRUM_CENSUS.json. The numerical bound is explicitly
rechecked from every weight-twelve spectrum in the companion verifier.

The sums of the unrestricted per-fibre maxima are respectively

    C: 1060,    D: 1047,    E: 1052.

Two nonflat eight-point fibres would reduce each sum by at least 84, below
992 in every case. Thus at least five of the six eight-point fibres are affine
three-flats. Let r be their actual number, so r is either five or six. If r=5,
the remaining eight-point fibre has Q<=70.

## 2. A general bound for cubes together with other fibres

Select r actual affine three-flat fibres and call all remaining fibres R.
Let E_R be any upper bound for sum_{A in R} Q(A). A selected cube has a
three-dimensional period space, hence exactly seven nonzero directions with
positive pair count. In each such direction its pair count is four.

An edge between two selected cubes is active precisely when its residue
direction belongs to both period spaces. Its actual quotient capacity is
4, 8, or 16. If three cube edges form an active triangle, the three residue
differences span a common two-space contained in all three period spaces.
Every edge of that triangle then has capacity at most eight. Consequently
the graph consisting of cube-cube edges of capacity sixteen is triangle-free,
and has at most floor(r^2/4) edges by Mantel's theorem.

Let e be the number of active cube-cube edges and z the number of active edges
between a selected cube and a fibre in R. Each active cube-cube edge consumes
two of the 7r cube directions, and each active cube-R edge consumes one. Thus

    2e + z <= 7r.                                          (2)

At a cube-R edge, let q be the pair count of its R endpoint. Its capacity is
at most min(16,4q). For R-R edges use the pair-square bound in Section 1.
The R endpoint directions reserved for the active cube-R edges are distinct
from all R-R endpoint directions. Adding the two types of bounds gives

    total capacity <= E_R/2 + C_cube
                         + sum_{active cube-R edges} g(q),  (3)
    g(q) = min(16,4q) - q^2/2,

where C_cube is the sum of actual cube-cube capacities. Unused R directions
can only enlarge this bound; there is no assumption that their energy is zero.

For any real lambda with 4<=lambda<=8, define H_A(r,lambda) as an upper bound
for the sum of (g(p_A(d))-lambda)_+ over any at most r distinct directions d.
Then (2) and (3) imply

    total capacity <= E_R/2 + 7r*lambda
                       + C_cube - 2e*lambda
                       + sum_{A in R} H_A(r,lambda).

A cube edge with capacity at most eight contributes at most zero to
C_cube-2e*lambda. A capacity-sixteen edge contributes 16-2lambda>=0; there
are at most floor(r^2/4) of them. We obtain the reusable inequality

    total capacity <= E_R/2 + 7r*lambda
                 + (16-2lambda)*floor(r^2/4)
                 + sum_{A in R} H_A(r,lambda).              (4)

Only actual affine cubes may be used in this inequality. The other fibres
are unrestricted apart from whichever independently valid energy and
direction-count bounds are used to estimate H_A.

## 3. A half-integer price gives elementary local bounds

Take lambda=11/2. For nonnegative integer pair counts q, twice the positive
part of g(q)-lambda is

    q:                         0  1  2  3  4  5  6 ...
    2*(g(q)-11/2)_+:            0  0  1  4  5  0  0 ...

Every direction therefore contributes at most five in the doubled units.
For weights twelve and eight this gives 2H_A<=5r. A six-point set has at most
one direction with pair count three: two distinct periods would generate a
period group of order four, which cannot divide six. All other counts are at
most two. Thus 2H_A<=4+(r-1)=r+3. For weights four and five, at most three
directions have pair count two, so 2H_A<=3. This is the established
maximal-direction quota; for four points it is the ordinary affine-plane
case, and for five points it follows from the maximal-direction subspace
lemma. Weights two and three contribute zero.

Multiplying (4) by two gives

    2*total capacity <= E_R + 77r + 10*floor(r^2/4)
                              + sum_{A in R} 2H_A.         (5)

All entries in this inequality are integers.

## 4. Exact boundary arithmetic

| profile | cubes r | E_R | 77r | 10 floor(r^2/4) | sum 2H_A | doubled upper |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| C | 5 | 458 | 385 | 60 | 69 | 972 |
| C | 6 | 388 | 462 | 90 | 51 | 991 |
| D | 5 | 445 | 385 | 60 | 64 | 954 |
| D | 6 | 375 | 462 | 90 | 45 | 972 |
| E | 5 | 450 | 385 | 60 | 67 | 962 |
| E | 6 | 380 | 462 | 90 | 48 | 980 |

For example, in the tightest case C with six cubes, the other fibres are
(12,6,6,4,3,2^7). They have energy at most 300+33+33+12+3+7=388, while
their doubled H bounds sum to 30+9+9+3=51. Equation (5) therefore gives

    2*total capacity <= 388+462+90+51 = 991 < 992.

All six branches contradict the required doubled capacity 992. This excludes
each of C, D, E as a whole weight multiset over both target rings.

The conclusion uses the cube-edge geometry simultaneously with the residual
energy. Applying either condition to each edge separately does not supply
this contradiction.
