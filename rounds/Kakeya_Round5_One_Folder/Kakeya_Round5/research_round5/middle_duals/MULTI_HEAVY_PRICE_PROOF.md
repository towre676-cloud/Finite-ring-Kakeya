# All-nine-heavy incidence prices: a systematic exact certificate family

## Scope

This continuation starts from the complete Round4 list of275,755 middle
weight profiles. It concerns dimension5, both four-element target rings,
size at most93, and exact maximum fibre size12 through18. It does not rerun
Claude's SAT sweep and does not use or audit the reported maximum19 proofs.

The new family extends the Round4 price on one heavy vertex to nonnegative
prices on all nine selected heavy vertices. The proof below establishes a
valid exclusion for every certificate. Discovery uses a floating-point LP;
acceptance uses separately recomputed exact rational upper bounds. The
independent checker imports neither the producer nor an optimization solver.

The full discovery pass considered all186,779 residual profiles on
supports13..17 and produced240 new exclusions. Their exact backward-DP
replay passed, leaving275,515 profiles under this family alone. All240
also have the elementary closed-form proof in SMALL_LIGHT_CAPACITY_PROOF.md;
the final accepted profile contradictions do not need an LP solver or a
local DP. No additional support/maximum cell closes.

| Support | New profile exclusions | Remaining under this family |
|---|---:|---:|
| 10 | 0 | 3,220 |
| 11 | 0 | 24,708 |
| 12 | 0 | 61,048 |
| 13 | 54 | 85,859 |
| 14 | 99 | 75,766 |
| 15 | 53 | 20,438 |
| 16 | 25 | 4,051 |
| 17 | 9 | 425 |
| Total | 240 | 275,515 |

## 1. The necessary local state space

Let T consist of the nine largest pair-active residue fibres, and let
F be the nonzero directions absent from T+T. Write r=|F|. The inherited
nine-point difference theorem gives r>=3. Since T has more than eight points,
F is sum-free: if d,e,d+e were missing, T could occupy at mostone point in
each coset of their two-space, of which there are onlyeight.

For a light fibre A_i of weight w_i, the graph joining two points whose
difference belongs to F is triangle-free. Mantel therefore gives the pair
budget B_i=floor(w_i^2/4). The inherited maximal-direction subspace theorem
also gives at most q_i=(q(w_i)+1)/2 directions in F attaining the maximal
pair count c_i=floor(w_i/2). Here

    q(w)=2^v2(w)-1                           if w is even,
    q(w)=max(2^v2(w-1),2^v2(w+1))-1          if w is odd.

These facts are the same analytic dependencies used in the verified Round4
nine-heavy stage. They are not newly inferred from a numerical census.

Number the heavy residues0,...,8, and put c_j=floor(w_j/2). The possible
pair allocation x=(x_0,...,x_8) of light fibre i satisfies

    0<=x_j<=c_i,
    sum_j x_j<=B_i,
    #{j:x_j=c_i}<=q_i.

Let X_i be exactly this relaxed finite domain. It can contain nonrealizable
allocations; this enlarges an upper bound and is safe for exclusion. The
same allocation must supply all nine contributions of the light fibre.

Use the accepted sumset-capacity bound

    M(p,q)=min(16,pq),

with the sharper values M(3,5)=13, M(3,6)=14, M(3,7)=15 and their symmetric
counterparts. The ring carry translates a single-edge label set and does
not change any of these cardinality upper bounds.

## 2. The multi-price inequality

Let ell=max_i c_i over the light fibres. Choose prices t_0,...,t_8>=0 and
write P=sum_j t_j. Define the local row

    R_i(t)=ell*B_i+
       max_(x in X_i) sum_j [2M(x_j,c_j)-ell*x_j-t_j*[x_j>0]].

Then twice the total actual capacity in F satisfies

    2C_F <= sum_i R_i(t)+rP.                              (1)

For the proof, a light-light edge obeys2M(p,q)<=ell(p+q), because p,q<=ell
and M<=pq. Charge these pair counts to their two light endpoint budgets.
A light-heavy edge contributes at most2M(x_j,c_j); subtract the ell*x_j
already reserved in the light budget. At heavy vertex j, the incident
directions are distinct, so at most r incidences toward lights in F can be
positive. Restoring all price charges costs at most r*t_j. Summing proves(1).

Prices may charge a positive light count even if the heavy endpoint has
no pair. This is an overcount; there are still at most r such incidences.
No common orientation or shape is assumed at this scalar relaxation level.

Coverage requires2C_F>=32r. Therefore the following is a sufficient exact
certificate, valid for every possible r>=3:

    t_j>=0,    P<=32,    sum_i R_i(t)+3P<96.               (2)

Indeed the excess over required coverage is bounded by

    [sum_i R_i(t)+3P-96]+(r-3)(P-32)<0.

The total-price restriction, rather than an individual bound on each price,
is essential to this extrapolation. The implementation checks it exactly.

## 3. Equal pair caps may use equal prices

Partition the nine heavy vertices into groups of equal pair cap. The local
domain X_i is symmetric under permuting heavy vertices within such a group,
and the unpriced edge scores are equal under those permutations. Each R_i
is a maximum of affine functions of the prices, so the full objective

    sum_i R_i(t)+3sum_j t_j

is convex and invariant under these group permutations. Averaging any
feasible price vector over the permutations preserves nonnegativity and
total price, and cannot increase the objective. Thus the grouped-price LP
has the same infimum as the nine-coordinate LP for this local relaxation.

This symmetry uses only the pair caps. It remains valid when two heavy
weights differ by one but have the same cap; the relaxation has deliberately
discarded their other geometric information.

For each light weight and each vector z of active counts by heavy-cap group,
the producer computes the maximum unpriced score subject to the common pair
budget and maximal-direction quota. Call this integer score s_(w,z), including
the constant ell*B. Introduce one beta_w per distinct light weight. The LP is

    minimize  sum_w n_w*beta_w +3sum_g k_g*t_g,
    subject to beta_w >= s_(w,z)-sum_g z_g*t_g for every feasible z,
               t_g>=0, sum_g k_g*t_g<=32.

Here k_g is the number of heavy vertices in group g. Every local pattern is
included by finite forward dynamic programming; this is not column generation
over a restricted type list. It is still only the stated scalar allocation
relaxation, not the full embedded-fibre type program.

## 4. Exact verification is separate from optimization

The discovery solver proposes a price vector. Its coordinates are converted
to rational numbers with a common denominator D. Before writing a cut, the
producer checks every local active-count row at those rational prices.

The independent checker takes only the integer price numerators and D. It
does not trust the LP objective, the producer's local table, its active-count
grouping, or a numerical infeasibility flag. Instead it computes each row
by a backward recursion through all nine heavy slots, retaining remaining
pair mass and remaining maximal-count quota. Its scaled score is

    D*[2M(p,c_j)-ell*p]-price_numerator_j*[p>0].

All comparisons are integer comparisons. The checker verifies the price
budget sum_j price_numerator_j<=32D and the strict upper bound<96D. It then
checks every cut's membership in the Round4 survivor list, uniqueness, and
the byte-identical subtraction producing the new survivor list.

The checker proves the accepted exclusions. Floating optimization results
on the other profiles are discovery diagnostics, not exact certificates of
LP optimality or evidence of realizable Kakeya sets.

## 5. An elementary new two-heavy example

The Round4 survivor

    (17,10,8^4,6^3,2^8)

has mass93, support17, and heavy caps(8,5,4^4,3^3). Its eight light fibres
each provide at mostone pair unit in F. Charge four units of undoubled
capacity per light pair. The cap-eight heavy can add at mostfour per
incident edge, and the cap-five heavy at mostone. Each has at most r
incidences. Hence

    C_F<=4*8+(4+1)r=32+5r<16r   for every r>=3.

At r=3 this is47<48. In the doubled LP, prices(8,2,0,...,0) give every
light row8, with upper8*8+3*(8+2)=94<96.

This is a whole weight-profile exclusion: every residue placement and
every fibre shape with these weights is covered in both rings. It does
not close the full maximum17 or support17 stratum.

## 6. Why supports10 through12 are unchanged by this family

There are at mostthree light vertices at these supports. For any independent
selection of their local allocations, every heavy vertex automatically has
at mostthree positive light incidences. Thus the r=3 incidence-cap constraints
already hold in the independent local relaxation. Adding nonnegative prices
cannot improve the zero-price optimum there.

Equivalently, for any t>=0 choose a zero-price maximizing allocation at each
light. The aggregate price penalty is at most3sum_j t_j, which the global
term restores. Therefore the priced objective is at least its zero-price
value. These profiles already survived the zero-price nine-heavy screen.

The full discovery pass can consequently be restricted to supports13..17
without overlooking any exclusion from this family at lower supports.

## Reproduction

Discovery requires NumPy and SciPy. Exact replay needs only Python3:

    python3 discover_multi_prices.py --minimum-support 13 --tag full
    python3 verify_multi_prices.py --tag full
    python3 verify_small_light_analytic.py

The full cut list, survivor list, and exact replay receipts are supplied.
Earlier Round4 files are unchanged. AUTHORITATIVE_FILES.txt lists the
essential sources and outputs for this branch.
