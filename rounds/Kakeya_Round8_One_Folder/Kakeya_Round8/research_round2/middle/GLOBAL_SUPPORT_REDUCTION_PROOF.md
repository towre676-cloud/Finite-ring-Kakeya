# Global support reductions for the open middle maxima

## Statement

Let R be Z/4Z or F2[epsilon]/(epsilon^2). Suppose K is a Kakeya subset of R^5
of total size at most93. Delete all singleton residue fibres, and let s count
the remaining nonempty (pair-active) fibres. If the exact maximum fibre size
is m in12..18, then the following necessary support bounds hold:

| exact maximum m | necessary upper bound on s |
|---|---:|
| 12 or13 | 20 |
| 14,15 or16 | 19 |
| 17 or18 | 18 |

These are uniform over all placements of the residue support and all tangent
fibre subsets. They are finite arithmetic consequences of the proved local
maximal-pair-direction quotas, using a complete graph resource bound. They
do not close any entire maximum-fibre case.

The independent replay checks560,918 normalized weight partitions in the
excluded ranges. It uses no earlier support census, no actual-fibre census,
no own-direction flags, and no numerical optimization solver. The producer
and verifier have different local dynamic-programming recurrences.

## Normalization

A primitive four-point line occupies two points in each of two residue fibres,
so deleting singleton fibres preserves all primitive lines. The pair-active
support is a difference basis in F2^5, hence has size at least9. Retain a
fibre of maximum size m. Since s*m>=9*12>93, if needed one may add points
inside the existing occupied fibres up to total93, never exceeding m.
This preserves Kakeya coverage, s and exact maximum m.

Thus every counterexample in the asserted ranges yields a nonincreasing
integer weight partition w_1>=...>=w_s>=2 with w_1=m and sum_i w_i=93.
Enumerating these partitions is a complete, elementary normalization; it
makes no assertion that all enumerated partitions have geometric realizations.

## Pair resources and total demand

For each residue base i, let A_i be its tangent fibre, w_i=|A_i|,
c_i=floor(w_i/2), and b_i=binom(w_i,2). For d!=0 write
p_i(d)=|A_i intersect(A_i+d)|/2. Then

    0<=p_i(d)<=c_i,          sum_{d!=0}p_i(d)=b_i.

For distinct residue bases i,j, put d=i+j. Define M(p,q) as min(16,pq),
except that M(3,5)=13, M(3,6)=14, M(3,7)=15 and symmetric values.
The three-point sumset theorem proves this is a uniform upper bound on the
number of lifted directions covered by that edge.

Each of the31 residue directions must cover16 lifted directions, so

    sum_{i<j} M(p_i(i+j),p_j(i+j)) >=496.                 (1)

The directions to distinct neighbors of one residue base are distinct.
Therefore its allocations along those edges obey the same total budget b_i.
Moreover at most r(w_i) selected directions can have p_i(d)=c_i, where

    r(w)=2^v2(w)-1                                  if w is even,
    r(w)=max(2^v2(w-1),2^v2(w+1))-1                 if w is odd>=3.

For even w, the maximal directions plus zero are the translation stabilizer,
whose order divides w. For odd w, the already-proved nearperiod subspace
has order dividing w-1 or w+1. Only the upper quota is used; a selected
subset is not incorrectly required to have power-of-two-minus-one size.

## The complete graph upper bound

Choose an integer cutoff ell>=0. Let H={i:c_i>ell}, L its complement,
and C0=sum_{i<j in H}M(c_i,c_j).

For a light vertex i define

    F_i=ell*b_i+max sum_{j in H}[2M(t_j,c_j)-ell*t_j],

where the maximum ranges over integer t_j satisfying

    0<=t_j<=c_i, sum_j t_j<=b_i, #{j:t_j=c_i}<=r(w_i).

For a heavy vertex i define

    L_i=sum_{j in H,j!=i}M(c_i,c_j)
        -max sum_{j in H,j!=i}M(t_j,c_j),

with the same budget and quota constraints.

Then twice the left side of(1) is at most

    B_ell=2C0+sum_{i in L}F_i
          -2 max(max_{i in H}L_i,ceil((sum_{i in H}L_i)/2)).       (2)

Empty heavy sets use correction zero.

Proof: For light-light edges the actual counts p,q<=ell obey
2M(p,q)<=2pq<=ell(p+q). Charge their counts to the corresponding endpoint
budgets. Maximizing how each light vertex can use its remaining counts on
heavy neighbors gives F_i. For each heavy-heavy edge define its nonnegative
deficit from M(c_i,c_j). At vertex i the incident deficit is at least L_i.
The sum of all heavy-heavy deficits is therefore at least each L_i and at
least half their sum, with integer rounding. Subtract twice this loss from
the doubled baseline. All separate endpoint optimizations enlarge the true
feasible set, so no simultaneous attainability is assumed.

Thus any ell with B_ell<992 gives a certificate of exclusion.

## Exhaustive finite arithmetic

The producer scan_global_budget.cpp visits every nonincreasing weight
partition of93, weights2..18, support15..32. It tests ell in
(2,3,1,4,0,5,6,7,8,9), stopping at the first strict exclusion.

The independent verifier verify_global_support_reductions.py regenerates
all partitions in the theorem's excluded ranges from scratch. It computes
each local maximum by backward recursion on the neighbor index, unused
pair mass and remaining maximal-count quota. The producer instead uses a
forward dynamic program indexed by used mass and used quota. Every one of
the560,918 partitions receives an independently recomputed B_ell<992.

GLOBAL_SUPPORT_INDEPENDENT_REPLAY.json records counts, chosen-cutoff
histograms and the maximum certified upper bound for each(s,m) pair.
The source is standard-library Python; run

    python verify_global_support_reductions.py

from any working directory. It writes its replay receipt next to itself.

## Boundary profiles

At s=20 the weaker resource relaxation leaves exactly three weight
partitions with maxima12..18:

    (13,8,8,8,8,8,8,8,2,2,2,2,2,2,2,2,2,2,2,2),
    (12,9,8,8,8,8,8,8,2,2,2,2,2,2,2,2,2,2,2,2),
    (12,8,8,8,8,8,8,8,3,2,2,2,2,2,2,2,2,2,2,2).

Their survival is a limitation of the resource inequality, not evidence
that any corresponding Kakeya set exists. Exact spectrum constraints and
common subspace geometry are appropriate next layers.
