# Further small-set stability and exact halfspace energies at nineteen and twenty

This addendum strengthens two auxiliary bounds in HALFSPACE_ENERGY_THROUGH_EIGHTEEN.md
and extends its exact halfspace energy table by

    h(19)=618,     h(20)=712.

The statements hold in arbitrary binary dimension; attainment is possible
in dimension five. They are local energy theorems, not complete maximum-fibre
Kakeya exclusions.

## 1. Relation-code and complement formulas

For a finite set T of size t and affine rank r, the kernel of its augmented
point matrix has dimension t-r-1. If P(T) counts its zero-sum four-subsets,
then P(T)<=2^(t-r-1)-1, and

    E(T,T)=t^2+4*binom(t,2)+24*P(T).

If A is a subset of a binary space H of order16 and B=H\A, then for d!=0

    p_A(d)=|A|-8+p_B(d).

This follows by counting the complement of B union(B+d) inside H.

## 2. Nine-point sets

Every nine-point set A has affine rank at least4. If its rank is at least5,
its relation code has dimension at most3, so

    E(A,A)<=81+4*36+24*7=393.

If its rank is4, take its sixteen-point affine hull and its seven-point
complement B. Then

    E(A,A)=309+4*sum_{d!=0}p_B(d)^2.

If B lies in an affine three-flat, it is that flat minus one point. Its
complement A is the other parallel eight-point flat plus that one point;
its energy is561. Otherwise B has affine rank4, so its relation code has
dimension2 and at most three zero-sum four-subsets. Thus

    sum p_B(d)^2<=21+6*3=39,
    E(A,A)<=309+4*39=465.

Consequently the exact maximum is561, and every set not consisting of an
eight-point affine three-flat plus an outside point has energy at most465.

## 3. Ten-point sets

A ten-point set also has affine rank at least4. Rank at least5 gives relation
code dimension at most4 and

    E(A,A)<=100+4*45+24*15=640.

At rank4, complement it inside its sixteen-point affine hull to a six-point
set B. The exact six-point bound sum p_B(d)^2<=33 gives

    sum p_A(d)^2=15*4+4*15+sum p_B(d)^2<=153,
    E(A,A)<=100+4*153=712.

Thus E(A,A)<=712 in every dimension, attained by the binary initial segment
{0,...,9}.

## 4. Sufficient eleven- and twelve-point bounds

For eleven points, at most three directions can have the maximal pair count5
by the proved odd nearperiod subspace theorem. All other counts are at most4,
and their total mass is55. Hence

    E(A,A)<=121+4*(4*55+3*5)=1061.

No sharpness claim is made for1061.

For twelve points, if any nonzero translation period exists, quotient by its
two-element subgroup. A becomes the full preimage of a six-point set B, and
E(A,A)=8E(B,B)<=8*168=1344. If no period exists, every nonzero pair count is
at most5; their total is66. Thus

    E(A,A)<=144+4*5*66=1464.

The upper1464 suffices here and is not advertised as sharp.

## 5. Mixed energy against an eight-flat plus one point

Suppose P=U union{r}, with U a three-dimensional subspace and r outside U.
Let Q have q<=11 points, and group its points into cosets of H=U+<r>.
Within each H-coset let x,y be its populations in the two U-cosets.
Then0<=x,y<=8, sum(x+y)=q, and direct correlation counting gives

    E(P,Q)=q+sum_Hcosets [8(x^2+y^2)+4xy].

For n=x+y the maximum bracket is

    g(n)=8n^2                           for0<=n<=8,
    g(n)=8n^2-96n+768                    for8<=n<=11.

This follows by minimizing xy at fixed n, because the bracket is8n^2-12xy.
The function g is superadditive whenever a,b>=0 and a+b<=11. If a+b<=8,
the difference is16ab. If both a,b<=8 but a+b>=8, then ab>=8(a+b-8),
so the difference16ab-96(a+b)+768 is at least32(a+b-8)>=0. If a>=8,
the difference is16b(a-6)>=0. Thus

    E(P,Q)<=q+g(q),

in particular E(P,Q)<=618 at q=10, and E(P,Q)<=691 at q=11.

## 6. Exact halfspace energy for nineteen points

Split the set between the two character halfspaces into sizes p<=q, p+q=19.
For p=9,q=10, a nine-point P of the structured form in Section5 gives618;
every other P gives E(P,Q)^2<=465*712<618^2.

For p=8,q=11, an affine-three-flat P gives at most8*(8^2+3^2)=584.
A nonflat P has energy at most344, so E(P,Q)^2<=344*1061<618^2.
All p<=7 have E(P,Q)<=p^2q<=7^2*12=588.
Therefore h(19)<=618. Binary initial segments of sizes9 and10 in opposite
halfspaces attain618.

## 7. Exact halfspace energy for twenty points

For p=q=10, Cauchy--Schwarz and Section3 give E(P,Q)<=712.
For p=9,q=11, the structured form gives at most691, while other nine-point
sets give E(P,Q)^2<=465*1061<712^2.
For p=8,q=12, an affine three-flat gives at most8*(8^2+4^2)=640, and a
nonflat gives E(P,Q)^2<=344*1464=503616<712^2=506944.
All p<=7 give E(P,Q)<=7^2*13=637.
Thus h(20)<=712, with equality from two opposite copies of{0,...,9}.

## Verification

All inequalities above are exact integers. The extended controls in
stability_halfspace20_controls.py check the rank and complement statements
against every nine- and ten-point subset of F2^4, the superadditivity
inequalities for every a+b<=11, every displayed squared comparison, and
the two new attainment constructions directly.
