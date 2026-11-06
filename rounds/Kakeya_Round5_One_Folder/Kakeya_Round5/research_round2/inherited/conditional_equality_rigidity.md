# Equality rigidity for the two-image Kakeya theorem

Internal proof note, 28 October 2026. This is an analytic refinement of the supplied all-dimension two-image proof. Its only external additive-combinatorial input is Kneser's stabilizer theorem, stated explicitly below. The proof is not a proof-assistant formalization.

## 1. Statement and normalization

Let R be Z/4Z or F_2[epsilon]/(epsilon^2), put pi=2 or epsilon respectively, let n>=2, and put N=2^n. Write V=F_2^n. For f:R^n -> R^n, define

    K_f = union_{r in R} (f+r Id)(R^n).

Suppose two parameter images have size N and their parameters differ by a unit.

**Theorem.** After translating the set, exactly one of the following holds:

1. K_f consists of the full residue-zero fibre pi R^n, together with a tangent pair {b_y,b_y+y} in each nonzero residue fibre y in V. Its cardinality is 3N-2.
2. |K_f| >= 3N-1.

The pairs in alternative 1 may be chosen independently. Thus equality in the two-image lower bound is equivalent to being a generalized star. In fact, if equality holds, one of the two selected normalized images is a full residue fibre and the other is a residue transversal.

The n=1 set at equality is the whole four-element ring, but the assertion about which selected image is a full fibre need not hold. We therefore state the rigidity theorem for n>=2.

If the selected parameters are r,s with u=s-r a unit, set

    g(w)=f(u^{-1}w)+r u^{-1}w.

The selected images of g occur at 0,1 and K_g=K_f. Write A=g(R^n), B=(g+Id)(R^n). The map

    w -> (g(w),g(w)+w)

is injective. Both its domain and A x B have N^2 elements, so it is bijective. Every element of R^n has a unique expression b-a. In particular A cap B is a singleton; translate it to zero.

Define the other images

    C = {(1-pi)a+pi b : a in A,b in B},
    D = {-pi a+(1+pi)b : a in A,b in B}.

These are exactly the parameter images at pi and 1+pi because every pair (a,b) occurs. Their union with A,B is K_f. Interchanging A and B preserves this union: it is the change of parameter r -> 1-r, and 1-pi=1+pi in both rings.

## 2. Residue data and exact identities

Use the coordinatewise 0/1 section sigma:V -> R^n. Write

    A = union_{x in S} (sigma(x)+pi A_x),
    B = union_{y in T} (sigma(y)+pi B_y),

where the nonempty tangent fibres A_x,B_y are subsets of V. Put

    s=|S|, t=|T|, q=|S cap T|>=1,
    alpha_x=|A_x|, beta_y=|B_y|,
    a=max alpha_x, b=max beta_y.

Exact difference counting gives

    sum_x alpha_x = sum_y beta_y = N,
    sum_{x+y=z} alpha_x beta_y = N       for each z in V.       (2.1)

Consequently

    S+T=V, st>=N, sum_{x in S cap T} alpha_x beta_x=N,
    ab<=N, a<=t, b<=s, as>=N, bt>=N.                          (2.2)

For a<=t, for example, every beta_y<=N/a, so N=sum beta_y<=tN/a. The other inequalities follow directly.

Multiplication by pi kills tangent coordinates and converts subtraction to binary addition. Thus, in BOTH rings, the remaining tangent fibres are exactly

    C_x=A_x+x+T,       D_y=B_y+y+S.                           (2.3)

The carry in sigma(y)-sigma(x) disappears after multiplication by pi; no assertion that the two rings have identical additive laws is being made.

Define

    Delta = sum_{x in S cap T} (alpha_x-1)(beta_x-1) >=0.

Using alpha+beta=alpha beta+1-(alpha-1)(beta-1), (2.1) gives

    sum_common (alpha_x+beta_x)=N+q-Delta.

Therefore the original mass on the two EXCLUSIVE residue regions is exactly

    sum_{S\T} alpha_x + sum_{T\S} beta_y = N-q+Delta.          (2.4)

Dropping Delta and bounding exclusive masses by their maxima yields

    N <= (s-q)a+(t-q)b+q <= 2st-q(s+t-1).                    (2.5)

Also, (a-alpha_x)(b-beta_x)>=0 at each common label, so

    alpha_x beta_x >= b alpha_x+a beta_x-ab.

Summing, and bounding omitted alpha and beta masses by (s-q)a and (t-q)b, gives

    ab(s+t-q)>=N(a+b-1).

Put

    F=N(a+b-1)/(ab);         q<=s+t-F.                       (2.6)

At an exclusive S-label, A union C has fibre

    A_x + ({0} union (x+T)),

whose second summand has t+1 elements. The analogous exclusive T-fibre has a summand of size s+1. A common fibre has at least max(s,t) points. Hence

    |K_f| >= 2st+s+t-q(min(s,t)+2).                          (2.7)

Finally, if st<2N, some residue z has just one representation x+y=z by support labels. Its product alpha_x beta_y equals N, forcing ab=N. In that situation a,b are powers of two:

    st<2N  =>  ab=N.                                        (2.8)

## 3. Binary sumset threshold and two counting estimates

Kneser's stabilizer theorem says that, for nonempty finite sets X,Y in an abelian group and H={h:(X+Y)+h=X+Y},

    |X+Y| >= |X+H|+|Y+H|-|H|.

It implies the following threshold in V. If d is a power of two, 1<=|X|<=d, and |Y|>=d+1, then

    |X+Y| >= |X|+d.                                        (3.1)

Proof: write h=|H|. If h>d, then h>=2d, and X+Y, being a nonempty union of H-cosets, has size at least 2d>=|X|+d. Otherwise h divides d, so |Y+H|, a multiple of h exceeding d, is at least d+h. Kneser now proves (3.1).

Suppose each exclusive S-fibre gains at least delta_A beyond alpha_x, and each exclusive T-fibre gains at least delta_B beyond beta_y. Set

    E=(s-q)delta_A+(t-q)delta_B.

Since |A union B|=2N-1 and the additional points are in exclusive fibres,

    |K_f|>=2N-1+E.                                         (3.2)

Alternatively retain the exact exclusive original mass (2.4) and at least t points at each common label:

    |K_f|>=N+q(t-1)+E+Delta.                               (3.3)

The Delta term is the new refinement. Dropping it recovers the supplied proof's inequality.

## 4. First cap regime

Round a,b up to powers of two. If the product of these caps is at most N, enlarge a cap to obtain powers P>=a, Q>=b with PQ=N. Interchange factors so P>=Q. If P=Q, also arrange the definitions below so u<=v. Write

    s=Q+u, t=P+v, u,v>=0.

The function F=N(1/a+1/b-1/(ab)) is nonincreasing in each positive argument. Therefore

    F>=P+Q-1,       q<=u+v+1.                              (4.1)

Apply (3.1) to the exclusive fibres using summands of sizes t+1 and s+1. The increments P,Q are valid. Thus

    E=P(s-q)+Q(t-q)=2N+Pu+Qv-q(P+Q).

Equation (3.3) becomes

    |K_f| >= 3N+Pu+Qv+q(v-Q-1)+Delta.                      (4.2)

If v>=Q+1, this is at least 3N. Otherwise using (4.1) with the nonpositive q-coefficient gives

    |K_f|-(3N-2)
      >=u(P-Q-1+v)+v^2-Q+1+Delta.                         (4.3)

### 4.1. The cases u=0, valid for both equal and unequal caps

All Q alpha masses then equal P.

If v=0 as well, all P beta masses equal Q, st=N, and (2.1) forces q=1. Equation (3.2) gives

    |K_f| >= 4N-P-Q-1
            =3N-2+(P-1)(Q-1).                             (4.4)

If Q>=2, this is at least 3N-1. If Q=1, then P=N, s=1, t=N; A is a full residue fibre and B is a transversal. This is precisely the star case classified in Section 6.

If u=0 and v>0, each C-fibre has at least 2P points by (3.1), so |C|>=2N. The common-product identity gives sum_common beta=Q. The exclusive T-fibres contribute at least

    N-Q+Q(t-q)>=N,

because q<=s=Q and t-q>=P+v-Q>=v>=1. These fibres are disjoint from C, so |K_f|>=3N. This argument includes P=Q and, in particular, the small equal-cap case m=2,u=0,v=1.

### 4.2. Unequal caps and u>=1

Here P>=2Q. If Q=1, then P=N and t<=N forces v=0. The non-Delta expression in (4.3) equals u(N-2)>0 because n>=2.

Now let Q>=2. The non-Delta expression in (4.3) is at least v^2+v. It is positive if v>=1. If v=0, it is

    u(P-Q-1)-Q+1.

This can vanish only when P=2Q and u=1. In that exception, (4.1) gives q<=2. If q<=1, the stronger (4.2) is already strictly above 3N-2. If q=2, then t=P and every beta mass equals Q. The common-product identity gives sum_common alpha=P. Consequently

    Delta=(Q-1)(P-2)>0.

Equation (4.3) again gives |K_f|>=3N-1. Thus no unequal-cap case with u>=1 permits equality.

### 4.3. Equal caps

Put P=Q=m; N=m^2 and m is an even power of two. Cases with u=0 were already handled. We may therefore assume 1<=u<=v.

If u+v<=m-2, (3.2) and (4.1) give

    |K_f|>=4N-1-m(u+v+2)>=3N-1.

Otherwise u+v>=m-1, hence v>=m/2. When m>=4, the non-Delta expression in (4.3) satisfies

    u(v-1)+v^2-m+1
       >= m^2/4-m+1=(m/2-1)^2>=1.

For m=2, v>=2 is also strict. The only remaining possibility is u=v=1, so N=4,s=t=3. The q=3 value needed to approach equality is impossible: (2.5) would give 4<=3. Thus q<=2, and (4.2) gives |K_f|>=12. This completes the first regime.

## 5. Second cap regime

Let P,Q be the least powers of two at least a,b. Since a>P/2, b>Q/2, and ab<=N, their product is strictly less than 4N. The first regime leaves only PQ=2N.

Neither maximum equals its cap: a=P would give ab>PQ/2=N, and similarly for b=Q. Thus

    P/2<a<P, Q/2<b<Q, P,Q>=4.                              (5.1)

Equation (2.8) forces st>=2N=PQ.

### 5.1. Both supports reach their opposite caps

Suppose s>=Q,t>=P. If t>P, (3.1) applied to C gives |C|>=N+Ps>=3N. If s>Q, use D symmetrically. Only s=Q,t=P remains.

The exclusive increments P,Q in (3.2) give

    |K_f|>=6N-1-q(P+Q).

If the caps are unequal, q<=min(P,Q) and the larger is at least twice the smaller, yielding q(P+Q)<=3N. If P=Q=m, equation (2.5) gives

    q <= floor(3m^2/[2(2m-1)]) = 3m/4.

Here m>=4 is divisible by four; the displayed fraction exceeds 3m/4 by 3m/(8m-4), which lies strictly between zero and one. Again q(P+Q)<=3N. Hence this entire boundary has |K_f|>=3N-1.

### 5.2. One support is below its opposite cap

Both supports cannot be below their opposite caps because st>=PQ. Interchange factors to leave

    s<Q, t>P.

Put xi=P-a>0, eta=Q-b>0. Every exclusive T-fibre gains at least eta beyond its beta mass. Indeed s>=b>Q/2. If beta<=Q/2, use (3.1) at Q/2 to gain at least Q/2>=eta. If beta>Q/2, choose a Q/2-point subset and apply (3.1), obtaining at least Q>=beta+eta points. This reasoning applies to each fibre separately.

Meanwhile |C|>=N+Ps. From (2.4), dropping Delta and bounding exclusive alpha mass by a(s-q), the exclusive beta mass is at least N-q-a(s-q). Adding exclusive T-fibres therefore yields

    |K_f|>=2N+xi s+eta t+q(a-1-eta).                        (5.2)

If a-1-eta>=0, use q>=1, s>=b, and t-1>=P:

    xi s+eta t+q(a-1-eta)
      >=xi b+eta P+a-1
      =PQ-ab+a-1>=N+a-1.

This is strictly sufficient. It always covers P>=Q because a>P/2 and eta<Q/2.

Thus only Q>P and a-1-eta<0 remain.

If Q=2P, then N=P^2 and s,t>=P+1. Use q<=min(s,t) in (5.2). If s<=t, the extra term is at least

    s(P-1)+eta(t-s)>=N-1.

If t<=s, it is at least

    t(P-1)+xi(s-t)>=N-1.

Thus |K_f|>=3N-1.

Finally suppose Q>=4P, set D=Q/2, and note N=PD, D>=2P, s>=b>D. If t>D, (3.1) at D gives

    |C|>=N+Ds>N+D^2>=3N.

Otherwise P<t<=D<s. Because N/b>=a and a>1,

    F=N/a+(N/b)(1-1/a)>=N/a+a-1
      =P+D-1+delta,
    delta=(P-a)(D-a)/a>0.                                 (5.3)

The STRICT inequality is essential: a<P<D by (5.1), so delta is positive. Here min(s,t)=t. Combining (2.6),(2.7),(5.3) gives

    |K_f|>=(t-1)s-t^2-t+(P+D-1)(t+2)+delta(t+2).

Both t-1 and t+2 are positive. Substitute s>=2PD/t from st>=2N, then factor:

    |K_f|-(3N-2)
      >=(t-P)(D-t)(1+2/t)+delta(t+2)>0.

The first term is nonnegative and the second strictly positive, including at the endpoint t=D. Integrality yields |K_f|>=3N-1. This completes the second regime and the proof of the alternative.

## 6. Exact star geometry and converse

The only equality branch has Q=1,P=N,s=1,t=N. Since 0 is in both A and B, the unique residue label of A is zero. Thus A=pi R^n and B is a transversal:

    B={sigma(y)+pi b_y : y in V},    b_0=0.

Formula (2.3) gives C=A and

    D_y={b_y+y}.

At y=0 the full fibre is already present. At each nonzero y, B and D supply the distinct points with tangent labels b_y and b_y+y. Their union has N+2(N-1)=3N-2 points.

Conversely take any full central fibre and, in each other residue fibre y, any tangent pair of difference y. Translate a point of the full fibre to zero. Let A be the full fibre and let B select one point from each pair, together with zero. Because B is a transversal and A is the full kernel of reduction, b-a represents every ambient vector uniquely. Define g(v)=a for that unique pair. Equations (2.3) recover exactly the prescribed set. Hence every generalized star is Kakeya and satisfies the two-image hypothesis.

For n>=2 the full fibre is unique. There are exactly N(N/2)^(N-1) labeled generalized stars: choose its residue label, then choose one of N/2 tangent pairs in every other fibre.

## 7. An 11-point example showing the gap is sharp

In n=2, for either ring, put

    A={0,1} x {0,pi},       B={0,pi} x {0,1}.

Coordinatewise, {0,1} and {0,pi} are unique difference factors of R, so A,B are unique difference factors of R^2. The remaining images are exactly

    C={0,1+pi} x {0,pi},
    D={0,pi} x {0,1+pi}.

For Z4, 1-pi=1+pi=3; for dual numbers, 1-pi=1+pi as well. The central residue fibre in the union is {(0,0),(pi,0),(0,pi)}, of size three. Residues (1,0) and (0,1) each have four points, and residue (1,1) has none. Thus

    |A union B union C union D|=3+4+4=11=3N-1.

This example proves sharpness of the general integer gap. It does not assert sharpness of 3N-1 as the second-smallest value in every higher dimension.

## 8. Quantifier boundary

The theorem classifies equality only under the two-image hypothesis. It neither proves that every minimizing Kakeya set admits such a representation nor proves the unrestricted lower bound. It shows that an every-minimizer representation theorem would imply an every-minimizer generalized-star theorem. A nonstar sharp minimizer would refute the former, but would not refute the numerical lower bound or a representation theorem restricted to hypothetical strictly subthreshold sets.
