# Exact halfspace pair energy through eighteen points

## Theorem

Let V be any finite binary vector space, let ell be a nonzero linear functional,
and let A be a subset of V. For nonzero d write p_A(d)=|A intersect(A+d)|/2.
If |A|=w<=18, then

    sum_{ell(d)=1} p_A(d)^2 <= h(w),

where h(0)=h(1)=0 and

| w | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| h(w) | 1 | 2 | 8 | 10 | 21 | 36 | 64 | 68 | 89 | 118 | 168 | **222** | **301** | **392** | **512** | **520** | **561** |

All entries are attained in dimension at least five. Entries through sixteen
are already attainable in dimension four. The bounds hold in every dimension
where the given set exists. The new contribution is the last six entries;
the earlier proof through twelve is retained as a dependency.

## Mixed energy and elementary facts

Split A into its two ell-halfspaces and identify both halves with W=ker(ell).
Call the resulting subsets P,Q, with sizes p<=q. For each x in W let
r(x)=#{(a,b) in P times Q:a+b=x}. Then the halfspace energy is

    E(P,Q)=sum_x r(x)^2=sum_d c_P(d)c_Q(d),
    c_P(d)=|P intersect(P+d)|.

Consequently E(P,Q)<=p^2 q and E(P,Q)^2<=E(P,P)E(Q,Q).
Also E(P,Q)=pq+4 sum_{d!=0}p_P(d)p_Q(d), so E(P,Q) is congruent
to pq modulo four.

For a set T of size t, let Z4(T) count its four-element subsets with xor zero.
Every such subset is an affine two-flat and yields three pair partitions, giving

    sum_{d!=0}p_T(d)^2=binom(t,2)+6 Z4(T),
    E(T,T)=t^2+4 binom(t,2)+24 Z4(T).

The following estimates suffice; no census of fibre shapes is used.

### Six points

A zero-sum four-subset is the complement in T of a pair whose sum equals
sigma=xor(T). If sigma=0 there are no such pairs. Otherwise pairs of sum sigma
are disjoint, so there are at most three. Thus E(T,T)<=168 for |T|=6.

### Seven points

Every nonzero pair count is at most three, and their sum is21. Hence
E(T,T)<=49+4*3*21=301 for |T|=7.

### Eight points: a stability gap

An eight-point affine three-flat has additive energy512. If an eight-point
set is not such a flat, its affine rank is at least four. Its augmented point
matrix has columns (1,x) and rank at least five, so its binary kernel has
dimension at most three. Each zero-sum four-subset supplies a distinct nonzero
kernel vector. There are at most seven such vectors. Therefore

    E(T,T)<=64+4*28+24*7=344

for every eight-point set which is not an affine three-flat.
This argument is valid in arbitrary ambient dimension.

### Nine points: the exact maximum and a stability gap

For a nine-point set T, let H consist of zero and the directions with pair
count four. Define D(d)=9-2p_T(d)=|T triangle(T+d)|/2 for d!=0.
The triangle inequality gives D(d+e)<=D(d)+D(e). For distinct nonzero d,e
with D=1, the left side is positive and odd, so it equals one. Thus H is a
subspace.

If H has order at least four, choose an order-four subspace L of H. If k_C
are the populations of T in the L-cosets, counting the symmetric differences
in the three nonzero L-directions gives

    3=sum_C k_C(4-k_C).

Thus there is exactly one partial coset, of size one or three. Since |T|=9
is congruent to one modulo four, it has size one; the other occupied cosets
are exactly two full L-cosets. The union of two distinct L-cosets is an affine
three-flat. Consequently T is an eight-point affine three-flat plus a point
outside it.

Such a set has seven nonzero pair counts four and eight pair counts one, so
E(T,T)=81+4*(7*16+8)=561. Every other nine-point set has at most one pair
count four; using total pair mass36 and remaining counts at most three gives

    sum p_T(d)^2<=16+3*(36-4)=112,
    E(T,T)<=529<561.

Therefore E(T,T)<=561 for every nine-point set, and equality forces and is
attained by an affine three-flat plus an outside point. The upper529 in the
other case is adequate here; it is not advertised as sharp.

### Ten points: a sufficient bound

A direction has pair count five precisely when it is a nonzero translation
period. The period group has order dividing ten, so there is at most one
such direction. Other counts are at most four; their total mass is45. Hence

    E(T,T)<=100+4*(25+4*(45-5))=840.

This is only a convenient upper bound, not an assertion that840 is sharp.

## The six new halfspace maxima

For w=13 the only potentially maximal split is p=6,q=7. Cauchy--Schwarz gives
E(P,Q)^2<=168*301=50568<225^2. Since E(P,Q) is an integer congruent to42
modulo four, E(P,Q)<=222. Splits with p<=5 have p^2q<=200.

For w=14 the split7+7 gives at most301; all smaller p have p^2q<=288.
For w=15 the split7+8 gives at most392; all smaller p have p^2q<=324.
For w=16 the split8+8 gives at most512; all smaller p have p^2q<=441.

For w=17 consider8+9. If P is an affine three-flat of direction U, then

    E(P,Q)=8 sum_{U-cosets C}|Q intersect C|^2
           <=8*(8^2+1^2)=520.

If P is not such a flat, E(P,Q)^2<=344*561<520^2. All smaller p give
p^2q<=490. Thus h(17)<=520.

For w=18, the split9+9 has energy at most561. For the split8+10, an affine
three-flat P gives at most8*(8^2+2^2)=544. A nonflat P gives
E(P,Q)^2<=344*840<544^2. All p<=7 give p^2q<=539. Thus h(18)<=561.

## Attainment

Use a fixed binary coordinate system on W, let P={0,...,p-1} and
Q={0,...,q-1}, and put P and Q in distinct ell-halfspaces. The splits

    (p,q)=(6,7),(7,7),(7,8),(8,8),(8,9),(9,9)

give respectively222,301,392,512,520,561. The last two constructions fit
in V=F2^5; the others fit in F2^4.

## Relevance and scope

The theorem sharpens any necessary Kakeya inequality that sums pair-square
energy over a character halfspace, including the earlier empty-flat and
singleton-flat restrictions. It is a dimension-free local theorem. It does
not alone exclude any unrestricted maximum-fibre stratum12–18.

The companion halfspace_energy_controls.py checks the identities on every
subset of F2^4, verifies the two stability classifications in that space,
and recomputes the six attainment constructions by direct point membership.
The analytic arguments above supply the arbitrary-dimensional justification.
