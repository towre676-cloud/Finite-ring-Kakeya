# Shared-direction resource inequalities for the support-eighteen frontier

This note proves the new tests used in the round-three middle-maxima sweep.
They apply to both target rings through necessary lift-cardinality bounds.
Write M(p,q)=min(16,pq), except M(3,5)=13,M(3,6)=14,M(3,7)=15 and their
symmetric values. Let w_i be fibre weights, c_i=floor(w_i/2), and b_i=binom(w_i,2).
The inherited maximal-pair quota r(w) is the order of the largest possible
maximal-direction subspace minus one. It equals2^v2(w)-1 for even w, and
max(2^v2(w-1),2^v2(w+1))-1 for odd w>=3.

## 1. Resources on directions missing from a selected heavy support

Let T be a selected collection of heavy residues, and let F be the nonzero
directions missing from T+T. In every d in F all contributing residue edges
have a light endpoint. Set ell to any upper bound for the light pair caps.
Suppose m_i bounds the total pair count of light fibre i over F. For each
heavy h select a nonnegative integer price lambda_h. For a light fibre i,
let X_i be any superset of its possible pair allocations t_h to its heavy
neighbors through F. Then twice the total covered capacity in F is at most

    sum_light [ell*m_i + max_{t in X_i}
                  sum_h(2M(t_h,c_h)-ell*t_h-lambda_h*[t_h>0])]
       + |F|*sum_h lambda_h.                              (1)

Indeed, every light-light edge obeys2M(p,q)<=ell(p+q). Charge those pair
counts to the light endpoint budgets. Each positive light-heavy edge at h
uses a distinct direction in F, so at most|F| such edges occur at h. The
price terms cancel after this endpoint bound. Independent local maxima
only enlarge the feasible set.

In the implemented relaxation, X_i satisfies

    0<=t_h<=c_i,  sum_h t_h<=m_i,
    #{h:t_h=c_i}<=r(w_i),  #{h:t_h>0}<=k_i.

The producer computes the exact finite integer maximum. An independent
backward recursion verifies each supplied certificate without trusting
that the selected prices are optimal.

## 2. Eight heavy residues

The previously proved analytic geometry gives:

* Eight residues miss either exactly six directions or at least nine.
* In the six-direction case, F lies in a character halfspace.
* In that case every residue outside T has at most three neighbors in T
  through F. The proof is in the round-two M11 support-seventeen theorem.

For the at-least-nine case use m_i=b_i and k_i=|T|=8. With prices satisfying
sum lambda_h<=32, evaluating(1) with |F|=9 yields a sufficient exclusion:
if the resulting upper is less than288, all|F|>=9 are excluded. Increasing
|F| by one increases the upper by at most32 while required doubled capacity
increases by32.

For the six-direction case use m_i=floor(w_i^2/4), because a fibre has at
most that many pairs crossing any character halfspace. Initially k_i=6 is
a safe cardinality relaxation; the sharper analytic neighbor bound gives
k_i=3. A doubled upper below192 excludes the case.

The first missing-direction pass uses all prices zero. The later pass
chooses integer prices but certifies the resulting exact bounds directly.

## 3. Three heavy residues: only one exceptional light vertex

Choose three heavy bases h_1,h_2,h_3. Consider light fibres whose global
maximal-direction quota equals3. Their maximal directions, when there are
three, are precisely the nonzero points of a two-dimensional subspace.
If light base a attains its maximal pair count toward all three heavy
neighbors, then

    (a+h_1)+(a+h_2)+(a+h_3)=0,
    a=h_1+h_2+h_3.

Therefore at most one light residue can attain all three maxima. This is a
simultaneous constraint across different fibres.

Set ell to the largest light pair cap. Compute the usual complete-graph
resource upper using2*sum_{heavy pairs}M(c_i,c_j) as its heavy baseline.
For quota-three light rows, first restrict their number of maximal counts
toward the three heavy neighbors to at most two. Then add back only the
largest single difference between a row's unrestricted and restricted
maximum. Other light rows retain their ordinary quotas. This bounds every
actual configuration and is valid independently of where the unique
exceptional residue is located or whether it is present.

A resulting doubled upper below992 excludes the whole weight multiset.
No heavy endpoint correction is needed for validity of this test.

## 4. Two heavy residues: delete their connecting direction

Choose two heavy residues h_1,h_2 and let e=h_1+h_2. The remaining thirty
residue directions require total capacity480. No heavy-heavy edge contributes
there.

For a light fibre A at base a, put

    p=p_A(a+h_1), q=p_A(a+h_2), t=p_A(e).

These are counts in the three nonzero directions of one two-dimensional
subspace. Its eight four-point cosets give an exact finite description:

| points in a coset | contributions to(p,q,t) |
|---|---|
| 0 or1 | (0,0,0) |
| 2 | any permutation of(1,0,0) |
| 3 | (1,1,1) |
| 4 | (2,2,2) |

Summing eight such coset patterns, with total point count w, gives precisely
all feasible triples for a w-point subset of F2^5. This local catalogue is
independently regenerated from the sixteen subsets of a four-point plane.

For any ell at least every light pair cap, the doubled capacity outside e
is bounded by the sum, over light weights w, of

    max_{feasible(p,q,t)} [ell*(binom(w,2)-t)
                 +2M(p,c_1)+2M(q,c_2)-ell*(p+q)].           (2)

The subtraction of t removes the pair budget spent in the deleted direction.
The other subtraction reserves the two light-heavy allocations; every
remaining light-light edge is bounded by2pq<=ell(p+q).

Thus a sum below960 excludes the entire weight multiset. This test retains
a genuine relation among three directions of each same fibre.

## 5. Nine heavy residues

Every nine-point residue set misses at least three directions. In(1), use
|T|=9, m_i=b_i and k_i=9. With sum lambda_h<=32, an upper below96 evaluated
at|F|=3 excludes every possible|F|>=3 by the same slope argument as above.

## 6. Maximal-direction bonuses inside the missing halfspace

Return to eight heavy residues and the case|F|=6. Let Q=sum_light floor(w_i^2/4),
and let d_1>=d_2>=... be the light pair caps. Put

    X=sum_{j=1}^{min(6,number of lights)} d_j.

Each heavy residue can be paired with at most six distinct light residues
through F, so the light pair mass on its incident edges is at most X.

The maximal-pair directions of a heavy fibre of weight w, together with zero,
form a subspace of order at most r(w)+1. Its intersection with a character
halfspace is either empty or has half its order. Therefore at most

    s(w)=min(6,(r(w)+1)/2)

directions of F can have maximal pair count. The corresponding incident
light pair mass is at mostY_w=sum_{j<=s(w)}d_j.

Assume all light caps are at most eight. Light-light capacity is at most four
times its endpoint pair mass. Every heavy cap at most four also contributes
at most four times its light pair mass. For a heavy cap c>4, its count is
at most c-1 except at the maximal directions, so its extra contribution
over this base is at most

    (c-5)*X+Y_w.

Thus total capacity over F is at most

    4Q + sum_{heavy w:c_w>4} [(c_w-5)*X+Y_w].              (3)

An upper below96 excludes the halfspace case. This is used only after the
at-least-nine case was separately excluded. Ignoring clipping at16 and
allowing different heavies to optimize independently can only enlarge(3).

## 7. Every missing set for more than eight heavy bases is sum-free

Let T have more than eight points. If its missing direction set contained
distinct d,e,d+e, then no two points of T could lie in one coset of the
two-space generated by d,e. There are only eight such cosets, a contradiction.
Thus F is sum-free. For any light fibre A, join two points when their difference
belongs to F. This graph is triangle-free, so Mantel's theorem gives

    sum_{d in F} p_A(d) <= floor(|A|^2/4).

Also a sum-free subset of a nonzero finite binary subspace has size at most
half its order: translate it by one of its elements to obtain a disjoint set.
Thus at most (r(w)+1)/2 maximal-pair directions can lie in F. The nine-heavy
resource test can use both refinements simultaneously in(1). This does not
require F to lie in one character halfspace, or to have exactly three points.

## 8. Ten heavy bases and weak unique edges

Suppose ten selected heavy fibres have one cap six and all other caps at most
four, while all light fibres have weights at most three. Let L be the light
fibres' total pair mass, and let k of the selected heavy fibres have cap at
most three. Then a necessary condition is

    L >= min(3k,12).                                      (4)

To prove it, let r be the number of missing heavy-support directions. A
missing direction needs at least four light pair units. Indeed each light
pair count in a direction is at most one. At most one light-heavy edge can
meet the cap-six hub, and three units can therefore provide at most
6+4+4=14 capacity. A light-light edge uses two units for at most one capacity
and cannot improve this upper bound.

For each heavy vertex a, let u(a) count incident heavy-heavy edges whose
direction has no other heavy-heavy edge. Deleting a leaves nine heavy bases,
which miss at least three directions. Exactly the r original missing
directions and these u(a) unique incident directions are missing after
deletion. Hence u(a)>=max(0,3-r).

A unique heavy-heavy edge touching one of the k weak vertices has capacity
at most M(3,6)=14 and thus needs at least one light pair unit in its direction.
If both endpoints are weak, its capacity is at most nine. One light pair unit
adds at most six, so at least two units are needed. These requirements count
the weak incidences without undercharging an edge with two weak endpoints.
Unique directions and missing directions are disjoint; therefore

    L >= 4r + sum_{a weak} u(a)
      >= 4r + k*max(0,3-r)
      >= min(3k,12).

The sharp cap M(3,6)=14 is essential in the one-weak-endpoint case. Replacing
it by the unclipped product 18 would not prove this lemma.

The final three cube profiles use the stronger simultaneous actual-geometry
argument in CUBE_ENERGY_SUPPORT18_EXCLUSIONS.md. The maximum-sixteen boundary
uses equality rigidity in BOUNDARY16_ACTUAL_SUMSET_EXCLUSION.md.
