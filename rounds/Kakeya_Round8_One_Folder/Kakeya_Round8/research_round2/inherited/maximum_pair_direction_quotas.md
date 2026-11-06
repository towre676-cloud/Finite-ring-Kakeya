# Maximum-pair direction quotas and their use in the off-hub bound

Internal analytic proof note, 28 October 2026. Everything through the allocation inequalities is uniform in the ambient binary dimension. The numerical demand specialization is for a nineteen-point hub in F_2^5. No finite search is used in these proofs.

## 1. Definitions

Let V=F_2^n, N=|V|, and let A subset V have w points, with 1<=w<=N. For d!=0 let p_A(d) be the number of unordered pairs {a,a+d} contained in A. Define for all d in V

    D_A(d)=|A\(A+d)|=w-|A cap (A+d)|
          =(1/2)|A symmetric_difference (A+d)|.

For d!=0,

    D_A(d)=w-2p_A(d).                                      (1.1)

In particular D_A(d) has the parity of w. Translation invariance of symmetric difference and its triangle inequality give

    D_A(d+e)<=D_A(d)+D_A(e).                               (1.2)

The elementary directional cap is c=floor(w/2).

## 2. Odd cardinalities: the maximal-pair directions form a subspace

Suppose w is odd. Define

    H={0} union {d!=0:p_A(d)=(w-1)/2}
     ={0} union {d!=0:D_A(d)=1}.

**Theorem.** H is a linear subspace. If h=|H|>=2, all but one H-coset are either full or empty in A, and the remaining coset has either one point or h-1 points. Consequently h divides w-1 or w+1.

Proof of closure. If d,e are distinct nonzero elements of H, then d+e!=0 and (1.2) gives D_A(d+e)<=2. Equation (1.1) says this is a positive odd integer, so it equals one. The cases involving zero or d=e are immediate. Thus H is an additive subgroup and hence an F_2-linear subspace.

For the structure statement, let k_C=|A cap C| for each H-coset C. Counting ordered pairs (a,b) with a in A, b outside A, and a+b in H\{0}, gives the exact identity

    sum_{d in H\{0}} D_A(d)
      =sum_{H-cosets C} k_C(h-k_C)=h-1.                   (2.1)

For every proper nonempty occupancy 1<=k<=h-1,

    k(h-k)-(h-1)=(k-1)(h-k-1)>=0.

Equality holds exactly at k=1 or k=h-1. Because h>=2 is even and w is odd, at least one coset is partially occupied. Identity (2.1) forces exactly one such coset, with occupancy one or h-1. Hence w is congruent to 1 or -1 modulo h. QED.

The h=1 case is separate: there are no nonzero maximal-pair directions and no partial-coset assertion is needed. Divisibility by one is automatic.

Geometrically, when h>=2, toggling one exceptional point makes A a union of H-cosets. This is a precise near-periodicity statement, not an assumption about generic high additive energy.

## 3. Even cardinalities: the maximal-pair directions are periods

Suppose w>0 is even. By (1.1), p_A(d)=w/2 exactly when D_A(d)=0, or equivalently A+d=A. Therefore

    H={d:A+d=A}

is the usual translation stabilizer, and its nonzero elements are exactly the maximal-pair directions. Since A is a union of full H-cosets, h=|H| divides w. Again h is a power of two.

## 4. Universal quotas

For w>=2, define

    r(w)=2^{v_2(w)}-1,                                  if w is even;

    r(w)=max(2^{v_2(w-1)},2^{v_2(w+1)})-1,              if w is odd.

Here v_2 is the exponent of the largest power of two dividing its positive argument. Then

    #{d!=0:p_A(d)=floor(w/2)} <= r(w).                    (4.1)

For w=1 the cap is zero and every nonzero direction attains it, so use r(1)=N-1; the displayed odd formula is not used because v_2(0) is undefined. Empty fibres can simply be omitted from the active-fibre allocation problem.

Relevant examples:

| w | cap floor(w/2) | quota r(w) |
|---|---:|---:|
| 2 | 1 | 1 |
| 3 | 1 | 3 |
| 4 | 2 | 3 |
| 5 | 2 | 3 |
| 6 | 3 | 1 |
| 7 | 3 | 7 |
| 8 | 4 | 7 |
| 9 | 4 | 7 |
| 10 | 5 | 1 |
| 11 | 5 | 3 |
| 12 | 6 | 3 |
| 13 | 6 | 3 |
| 14 | 7 | 1 |
| 15 | 7 | 15 |
| 16 | 8 | 15 |
| 17 | 8 | 15 |
| 18 | 9 | 1 |
| 19 | 9 | 3 |

The number of maximal-pair directions in the entire space is h-1 for a subspace H. For w=19, h divides18 or20, so h is1,2,or4 and the global count is0,1,or3. However, a selected subset of directions can contain two of the three maximal directions. An allocation restricted to selected neighbours must enforce only the inequality in (4.1), not a prohibition of selected count two.

## 5. Stronger demand for a nineteen-point hub

In dimension five each nonzero residue direction has16 lifted projective directions. Let z be the number of residue directions with no active hub edge, and let u be the number of own-positive non-hub fibres of weight two or three.

Each of these u fibres has exactly one own-direction pair, so its hub edge covers at most p_H(d) lifted directions, where H now denotes the nineteen-point hub set. At most three distinct d have p_H(d)=9; all others have p_H(d)<=8. The u small own-positive fibres have distinct residue labels, so their total hub coverage is at most

    9 min(u,3)+8 max(u-3,0)=9u-max(u-3,0).

Their off-hub deficit is therefore at least7u+max(0,u-3). The z hub-inactive directions are distinct from them and each contributes demand16. Thus

    OFF-HUB DEMAND >= 16z+7u+max(0,u-3).                  (5.1)

If the actual maximal-direction subgroup order h is known, one can replace3 by h-1. Formula (5.1) uses the universally safe maximum h=4 and needs no structural classification of the hub beyond its weight.

More generally, for an odd hub of weight w, a small own-positive partner has cap one and the maximal hub pair count is c=(w-1)/2. If its maximal-direction subgroup has size h, the same reasoning gives

    demand >= (N/2)z+(N/2-c)u+max(0,u-(h-1)).

The ring does not affect this count: a fixed endpoint pair translates the opposite pair-coset set in V/<d>.

## 6. Quotas in light-to-heavy allocation

Translate the hub's residue label to zero. For any other fibre i of weight w_i and own-positive flag f_i in{0,1}, put

    c_i=floor(w_i/2),
    m_i=binom(w_i,2)-f_i.

This is an upper bound on its off-own pair budget. An off-hub edge from residue a_i to a_j uses direction a_i+a_j. For a fixed i these directions are distinct as j varies, and none equals a_i because a_j!=0. Therefore the actual selected edge pair counts t_j satisfy

    0<=t_j<=c_i,
    sum_j t_j<=m_i,
    #{j:t_j=c_i}<=r(w_i).                                (6.1)

The quota in (6.1) does not subtract a possible maximal own-direction pair. Omitting that subtraction only enlarges the feasible set and is conservative.

Let ell be a cutoff, with light fibres having c_i<=ell and heavy caps h>ell. Let M be any valid monotone symmetric upper bound for pair-coset sumset sizes, with M(p,q)<=pq. For actual light-light counts a,b<=ell,

    2M(a,b)<=2ab<=ell(a+b).

Charging the remaining pair budget to light-light edges as before gives the valid doubled contribution bound for a light fibre:

    ell m_i + max sum_h [2M(t_h,h)-ell t_h],

where the maximum now includes ALL three constraints in (6.1). Every actual configuration is feasible for this maximum, so adding the quota cannot create a false exclusion.

## 7. Quotas in the heavy-heavy endpoint-loss bound

Let the baseline heavy-heavy cap sum be

    C_0=sum_{unordered heavy pairs {i,j}} M(c_i,c_j).

All heavy fibres here are non-hub fibres. Empty sums and empty nonnegative maxima are interpreted as zero, so the formulas also cover zero or one heavy fibre.

For each heavy endpoint i define

    B_i=sum_{j heavy,j!=i} M(c_i,c_j),

    R_i=max sum_{j heavy,j!=i} M(x_j,c_j),

where 0<=x_j<=c_i, sum_j x_j<=m_i, and #{j:x_j=c_i}<=r(w_i). Put L_i=B_i-R_i>=0.

Let E_ij be the actual integer number of lifted directions covered by edge {i,j}, and put

    delta_ij=M(c_i,c_j)-E_ij>=0.

The actual pair counts at endpoint i satisfy the endpoint constraints. Monotonicity of M in the other endpoint gives

    sum_j E_ij <= sum_j M(p_i(a_i+a_j),c_j) <= R_i.

Consequently

    sum_j delta_ij >= L_i.                               (7.1)

Write S=sum_{unordered heavy pairs} delta_ij. Nonnegativity and (7.1) imply

    S>=max_i L_i,
    2S>=sum_i L_i.

Since S is an integer,

    S>=max(max_i L_i, ceil((sum_i L_i)/2)).

Hence

    DOUBLED HH CAPACITY
      <=2C_0-2 max(max_i L_i,ceil((sum_i L_i)/2)).          (7.2)

The heavy endpoint constraints ignore pair budget used on light-heavy edges. This enlarges each R_i and weakens, rather than invalidates, the upper bound. Thus (7.2) may be added to the independent quota-constrained light contribution bound of Section6.

This proves the precise no-double-counting step: each heavy-heavy edge loss is charged to two endpoint sums, which is why the total endpoint loss is divided by two, with an additional valid maximum-single-endpoint bound.

## 8. Scope of the resulting finite cuts

All these inequalities use only necessary constraints for actual fibres. They hold for every residue-support arrangement and in both four-element rings, because tangent differences live in V and the Z4 carry only translates the relevant pair-coset sumsets. The number and identity of profiles excluded by an implementation still require separate source and code verification; no profile-count claim is made by this analytic note.
