# Full-hub Kakeya theorems from an exact defect-energy budget

Internal mathematical continuation. These are conditional theorems for a Kakeya set with one full residue fibre. They do not establish that an arbitrary small Kakeya set has such a fibre.

## 1. Statements

Let R be either Z/4Z or F_2[epsilon]/(epsilon^2), let V=F_2^n and N=2^n, and write the residue fibres of K as A_a subset V. A generalized star consists of one full fibre A_0=V and, at every nonzero residue a, exactly a pair {b_a,b_a+a}.

**Theorem A.** If n>=4, A_0=V, and |A_a|<=6 for every a!=0, then

    |K| >= 3N-2.

**Theorem B.** If n>=5, A_0=V, and |A_a|<=7 for every a!=0, then

    |K| >= 3N-2,

and equality holds if and only if K is a generalized star.

The sharp upper bound is immediate from the star construction. Both lower bounds and Theorem B's equality assertion are proved below without an exhaustive search or a pre-existing small-dimensional minimum.

## 2. The defect-energy inequality

For nonzero d, let p_A(d) count the unordered d-pairs in A. Put

    E(A) = sum_{d!=0} p_A(d)^2.

For every d!=0, Kakeya coverage requires

    sum_{unordered {a,a+d}} p_{A_a}(d) p_{A_{a+d}}(d) >= N/2.   (2.1)

The carry term over Z/4Z changes lifted-direction labels but does not change this necessary cardinality bound.

Let

    L = {a!=0 : |A_a|<=1},       z=|L|,
    D = {d!=0 : p_{A_d}(d)=0},   Z=|D|.

Thus L subset D. For d in D, the edge {0,d} contributes zero. Applying 2xy<=x^2+y^2 to all remaining residue edges gives

    N <= sum_{a!=0} p_{A_a}(d)^2.

Consequently, for any nonempty T subset D,

    N |T| <= sum_{a!=0} sum_{d in T} p_{A_a}(d)^2.             (2.2)

This is stronger than the special case T=L used below; it also controls fibres whose own pair is absent even when their size is at least two.

Let w_a=|A_a|, and define the total positive excess above two points by

    B = sum_{a!=0, w_a>=3} (w_a-2).

If |K|<=3N-2-delta, where delta>=0, then

    B <= 2z - sum_{a in L} w_a - delta <= 2z-delta.             (2.3)

Indeed, there are N-1-z outer fibres of size at least two, whose total size is 2(N-1-z)+B.

Suppose e_T(w) is any upper bound on sum_{d in T} p_A(d)^2 for |A|=w, with e_T(2)=1. Then (2.2), with T=L and z>=1, implies

    Nz <= N-1-z + sum_{a!=0,w_a>=3} (e_L(w_a)-1).              (2.4)

The expression on the right treats every outer fibre of size at least two as contributing a base amount one, plus its possible energy gain from extra points.

## 3. Small-fibre energy bounds

The following bounds hold in every binary vector space large enough to contain the indicated set:

| w | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---:|---:|---:|---:|---:|---:|
| E(A) upper bound e(w) | 1 | 3 | 12 | 16 | 33 | 63 |
| e(w)-1 | 0 | 2 | 11 | 15 | 32 | 62 |
| excess cost w-2 | 0 | 1 | 2 | 3 | 4 | 5 |

For w=2 and 3, all pair differences are distinct, giving energies 1 and 3. For w=4, p_A(d)<=2 and sum p_A(d)=6, so E(A)<=12. For w=7, p_A(d)<=3 and sum p_A(d)=21, so E(A)<=63.

For w=5, the directions with p_A(d)=2, together with zero, form a subspace H of size at most four. Here is the needed elementary argument. Define D_A(d)=|A triangle (A+d)|/2=5-2p_A(d). If D_A(d)=D_A(e)=1 and d!=e, then the triangle inequality gives D_A(d+e)<=2; its value is positive odd, so it equals one. Thus the maximal directions close under addition. If h=|H|, and k_i are the occupancies of its cosets, then

    h-1 = sum_{d in H\{0}} D_A(d) = sum_i k_i(h-k_i).

For h>1, every partial coset contributes at least h-1. There is exactly one partial coset, with occupancy 1 or h-1, and all other cosets are full or empty. Hence h divides 4 or 6; since h is a power of two, h<=4. Therefore at most three directions have p=2. Because sum p=10,

    E(A)=10+2 #{d:p_A(d)=2} <=16.

For w=6, a direction with p_A(d)=3 is a translation period of A. The periods form a subgroup whose order divides six, so there is at most one nonzero period. If there is no p=3 direction, p<=2 gives E(A)<=30, and its odd parity actually gives E(A)<=29. If there is one p=3 direction, the remaining pair mass is 12 and p<=2 there, so

    E(A)<=3^2+2*12=33.

This argument also proves the restricted-direction bound

    sum_{d in T} p_A(d)^2 <= 9+4(|T|-1)        (w=6, |T|>=1), (3.1)

since at most one direction can have p=3. If there is no such direction, the right side still dominates 4|T|.

For a set T of three directions, the needed bounds are therefore

| w | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---:|---:|---:|---:|---:|---:|
| e_T(w) | 1 | 3 | 12 | 12 | 17 | 27 |

For these bounds,

    e_T(w)-1 <= (11/2)(w-2)              for every 2<=w<=7.   (3.2)

## 4. The one-low-fibre obstruction

We will use two elementary observations, valid for N>=4.

If z=1 and |K|<3N-2, (2.3) gives B<=1. Thus every outer fibre has at most three points. Let d be the sole low residue. The central edge {0,d} contributes zero, while each of the N/2-1 other residue edges contributes at most one to (2.1). This is impossible.

If z=1 and |K|=3N-2, then B<=2. Again, all outer fibres of size at most three cannot cover the direction d. The only other possibility is one four-point outer fibre, at residue h, with every other non-low outer fibre having exactly two points. In this case equality in the cardinality budget also forces A_d empty.

For direction d, the only residue edge capable of contributing more than one is the edge containing h. Its contribution is at most two; every other noncentral edge contributes at most one. Since there are N/2-1 noncentral edges, reaching N/2 forces the h-edge to contribute two and every other noncentral edge to contribute one. Hence every two-point outer fibre has pair difference d.

Choose any residue e of one of these two-point fibres; such a residue exists because N-3>=1. We have e!=0,d. Its pair difference is d, so the central edge {0,e} contributes zero in direction e. No two-point outer fibre has an e-pair, and the single four-point fibre cannot make a noncentral active edge by itself. Thus no lifted direction above e can be covered. This is again impossible.

## 5. Proof of Theorem A

Assume |K|<3N-2. Then z>=1, since otherwise every outer fibre has at least two points. The case z=1 was excluded in Section 4, so z>=2.

For 3<=w<=6, the table in Section 3 gives

    e(w)-1 <= 8(w-2).

Moreover, whenever w-2 is odd, the stronger bound

    e(w)-1 <= 8(w-2)-6

holds: the gaps are six for w=3 and nine for w=5.

The total excess B is at most 2z-1. If B is odd, at least one odd-cost term occurs, and therefore

    sum(e(w_a)-1) <=8B-6 <=16z-14.

If B is even, B<=2z-2, and the same sum is at most 16z-16. In either case it is at most 16z-14. Inequality (2.4) now gives

    Nz <= N-1-z+16z-14 = N+15z-15,
    (z-1)N <=15(z-1).

As z>=2, this forces N<=15, contrary to n>=4. The lower bound follows.

## 6. Proof of Theorem B: lower bound

Assume |K|<3N-2. Again z>=1 and Section 4 excludes z=1.

If z=2, then B<=3, so every outer fibre has size at most five. The energy table gives

    e(w)-1 <=(11/2)(w-2)  (2<=w<=5).

Thus (2.4) yields

    2N <= N-3+(11/2)*3 = N+27/2,

which is impossible for N>=32.

If z>=3, use the uniform bound

    e(w)-1 <=(62/5)(w-2)  (2<=w<=7).

Then

    (z-1)N <= (119z-67)/5,
    N <=119/5 + 52/[5(z-1)] <=29.

This also contradicts N>=32.

## 7. Proof of Theorem B: equality rigidity

Suppose |K|=3N-2.

If z>=4, the same coefficient 62/5, now with B<=2z, gives

    N <=119/5 +114/[5(z-1)] <=157/5 <32,

which is impossible.

If z=3, use the restricted-direction energy bounds (3.2) on T=L. We have B<=6, so

    3N <=N-4+(11/2)*6 =N+29,
    N<=29/2,

again impossible.

If z=2, then B<=4, so every outer fibre has size at most six. The coefficient eight from Section 5 gives

    2N <=N-3+8*4=N+29,

which is impossible for N>=32.

Section 4 excludes z=1. Therefore z=0. The cardinality budget forces every outer fibre to have exactly two points. If its own pair were absent at any residue d, all N/2-1 noncentral edges would contribute at most one in direction d, contradicting coverage. Thus every outer pair has difference equal to its residue label. This is exactly a generalized star.

Conversely, in a generalized star, A_0 supplies all N/2 tangent pair labels in every direction d, while A_d supplies one d-pair. The central residue edge therefore covers all lifted directions above d, over either ring, and the total size is N+2(N-1)=3N-2.

## 8. General reusable form

Let m be an outer-fibre cap, and let C_m satisfy

    E(A)-1 <= C_m (|A|-2)       for 3<=|A|<=m.

For any Kakeya set with a full hub and |K|<=3N-2-delta, if z>=2, (2.3)-(2.4) imply

    N <= (2C_m-1) + [2C_m-2-C_m*delta]/(z-1).                (8.1)

In particular, delta>=1 gives

    N <=(2C_m-1)+(C_m-2)/(z-1).

The point is not just a scalar total-energy bound: only directions with missing central edges are charged, and the allowable extra points are paid for by missing or singleton fibres. Restricted-direction energies, parity, and exact own-direction budgets can all strengthen this inequality.

## 9. Status and limits

Theorems A and B are newly established analytic conditional results in this continuation. No M19 profile cuts or M11 support-class cuts are credited to these two full-hub theorems; the separate round-2 ledgers record the reductions of those frontiers. The maximum-fibre ranges 12 through 18 also remain open. In n=5, the full-hub case was already among earlier exclusions of maximum fibre at least 20; the new content is a dimension-uniform proof and equality rigidity under the stated outer-fibre cap.

No statement here assumes that ordinary fibre compression preserves Kakeya coverage. It does not.
