# Nine heavy residues: a complete missing-direction degree constraint

## Mathematical scope

This theorem family applies to both target rings in dimension five. It uses
only necessary upper bounds on actual quotient-sumset capacities. It does
not depend on Claude's unavailable CNF encoder or on a SAT result.

Select the nine largest fibres as heavy, with residue set H and pair caps
c_1>=...>=c_9. Let F be the nonzero directions absent from H+H, and r=|F|.
Every capacity-contributing residue edge in F has at least one light endpoint.
The light fibres occupy distinct vertices of F2^5 outside H.

## 1. Complete finite geometry

For x outside H define k_H(x)=#{h in H : x+h in F}. This is the number of
possible heavy neighbours of x along missing directions. There are exactly
seven possible pairs (r, outside-degree histogram):

| r | Nonzero histogram entries (degree: number of vertices) |
|---|---|
| 3 | 0:1, 1:18, 2:3, 3:1 |
| 4 | 0:7, 2:12, 3:4 |
| 6 | 0:3, 2:12, 3:2, 4:6 |
| 8 | 1:8, 2:2, 4:9, 6:4 |
| 9 | 2:15, 6:7, 9:1 |
| 10 | 0:1, 3:8, 4:12, 9:2 |
| 16 | 0:7, 9:16 |

Every row has23 outside vertices and sum_x k_H(x)=9r.

The complete finite proof enumerates every nine-set containing a coordinate
affine basis in its affine hull. Rank below4 is impossible; rank4 requires
choosing4 additional points from11, and rank5 requires choosing3 from26.
Thus there are330+2600=2930 normalized sets. Every actual nine-set is affine
equivalent to at least one of them. The missing set and outside-neighbour
degrees are transported by that affine equivalence, so the enumeration is
complete. It does not require an affine-orbit catalogue. The Python verifier
recomputes all differences and degrees directly from these sets.

The normalized multiplicities for r=3,4,6,8,9,10,16 are respectively
260,750,660,810,60,60,330. These are normalized-representative counts, not
counts of affine orbits.

In particular, if r=3, only one light residue can have three heavy neighbours
and only three further light residues can have two. This information was
discarded by the earlier independent endpoint-resource maxima.

## 2. The restricted local resource

F is sum-free. Otherwise d,e,d+e in F would force H to meet each coset of
their two-space in at most one point, but there are only eight cosets.
For any light fibre A of weight w, its difference graph in F is therefore
triangle-free. Hence its pair mass in F is at most B(w)=floor(w^2/4).

Let c(w)=floor(w/2) and let q(w) be the maximal-direction quota:

    q(w)=2^v2(w)-1                                  if w is even,
    q(w)=max(2^v2(w-1),2^v2(w+1))-1                 if w is odd.

The directions attaining c(w), together with zero, form a binary subspace.
Its order is at most q(w)+1. Consequently the sum-free set F contains at
most (q(w)+1)/2 maximal-pair directions.

For clarity, closure of the maximal-direction set can be proved directly.
For two independent maximal directions d,e, inspect the four-point cosets
of their span. A two-point partial coset contributes at least two unmatched
points in one of these directions, which is impossible when the total
unmatched count is zero (even w) or one (odd w). The allowed occupancies
therefore also give a maximal count for d+e. In the even case the fibre is
a union of period-subspace cosets, so its order divides w. In the odd case,
the order-one subspace satisfies the bound trivially. If its order N is
greater than one, summing symmetric differences gives
sum_cosets k(N-k)=N-1. Every partial coset contributes at least N-1, with
equality only at k=1 or N-1. Thus there is exactly one such coset and
w is congruent to1 or-1 modulo N. This proves the stated quota bounds.

Let ell be the largest light pair cap. Use

    M(p,q)=min(16,p*q),

with the established improvements M(3,5)=13, M(3,6)=14, M(3,7)=15 and
symmetry in p,q. This function is nondecreasing in both arguments.

For a light fibre with at most k heavy neighbours, define

    R(w,k)=ell*B(w) + max sum_{j=1}^k [2M(p_j,c_j)-ell*p_j],

where0<=p_j<=c(w), sum p_j<=B(w), and at most (q(w)+1)/2 of the p_j
attain c(w). The caps c_j are the k largest heavy caps. This is an upper
relaxation: any actual k-neighbour cap multiset is coordinatewise bounded
by those k caps. Direction incidences at one residue are distinct, and the
same pair-mass and maximal-count budgets hold jointly.

The doubled heavy/light accounting gives

    2C_F <= sum_i R(w_i,k_H(x_i)).

Indeed, for light-light edges2pq<=ell*(p+q). Reserve ell times each light
endpoint pair count, then pay the extra2M(p,c_j)-ell*p for heavy-light
edges. There are no heavy-heavy edges in F. Replacing the total reserved
mass by ell*B(w) and maximizing the extra allocation gives the displayed
row. Unused mass and unrealizable pair allocations only enlarge this bound.

## 3. Distinct outside vertices impose a matching bound

R(w,k) is nondecreasing in k, since an added slot may receive p=0. Suppose
there are L light fibres. For each of the seven geometry rows, retain its
L largest outside degrees k_1,...,k_L. Any actual distinct L outside
vertices have sorted degrees bounded coordinatewise by these values.

Let U_r be the maximum of sum_i R(w_i,k_{pi(i)}) over bijections pi.
Then2C_F<=U_r for every actual placement in that geometry row. Thus

    U_r <32r for every one of the seven rows

excludes the complete weight profile, irrespective of support placement,
fibre shapes, or ring carry. The row's value of r and its degree histogram
are kept together; no degree information from one case is spent in another.

## 4. Finite replay

The C++ producer computes local rows by a forward pair-budget/maximal-count
DP and the assignment bound by a subset DP. The separate Python verifier
imports no producer. It enumerates all2930 nine-point geometries, recomputes
local rows by backward recursion, and computes assignments by a recursion
over degree multiplicities. It checks every strict certificate and the
complete survivor complement, then verifies byte-identical subtraction.

On the275755-profile Round4 residual this family excludes4088 profiles and
leaves271667. It closes no additional support/maximum cell. These counts
are before combination with the separate Round5 multi-price family; any
overlap must be removed explicitly in the merged ledger.

The main gain is at support10:2572 of its3220 previous weight profiles are
excluded, leaving648. The other disjoint support counts are1234 at support11,
225 at support12, and57 at support13. This demonstrates a geometric method
that improves the low-support region where the three-incidence price family
is redundant. Remaining weight profiles are necessary-condition survivors,
not constructions or complete assignments of embedded shapes.

Replay from the archive root:

    python3 research_round5/nine_geometry/verify_nine_geometry.py

The finite geometry and resource computations are exact, but this whole
theorem family has not been formalized in a proof assistant. The analytic
arguments and separate implementations are available for review.
