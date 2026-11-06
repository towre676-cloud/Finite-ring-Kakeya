# Twelve-point pair energy: an analytic maximum and equality classification

## Result

Let `A` be a twelve-point subset of any binary affine space. For nonzero
direction `d`, write `p_A(d)=|A intersect(A+d)|/2`, and put

    Q(A)=sum_{d!=0} p_A(d)^2.

Then **Q(A)<=300**, with equality exactly when `A` is an affine four-flat
with one affine plane removed. More precisely, the affine-rank strata obey:

| Affine rank of A | Bound |
|---|---:|
| at most3 | impossible for twelve points |
| 4 | exactly294 or300 |
| 5 | at most222, attained |
| at least6 | at most252 |

The proof below is analytic. It reads no census and uses no classification
of affine subset orbits. The accompanying independently written enumeration
corroborates the rank4 and rank5 claims but is no longer a dependency of the
energy bound used by the Round3 support-eighteen proof.

## 1. The pair-energy identity

Let `Z_4(A)` be the number of affine planes contained in `A`. Then

    Q(A)=binom(|A|,2)+6 Z_4(A).                            (1)

Indeed, `sum_d p_A(d)=binom(|A|,2)`. Two different unordered pairs of the
same nonzero difference are disjoint and form an affine plane. Each plane
has three nonzero directions, so `sum_d binom(p_A(d),2)=3 Z_4(A)`.
Expanding `p^2=p+2 binom(p,2)` gives(1).

For a set of size `w` and affine rank `r`, its augmented point matrix has
rank `r+1`, hence its binary relation code has dimension `w-r-1`. Every
affine plane gives a distinct nonzero relation vector. Therefore

    Z_4(A)<=2^(w-r-1)-1.                                  (2)

These facts immediately give the following small-set bounds:

* Four points have energy12 if they form a plane and6 otherwise.
* Five points have energy at most16. Two different affine planes cannot
  fit into five points: their intersection would contain three points,
  which already determine a binary affine plane.
* Six points of affine rank3 are the complement of two points in an
  eight-point three-flat and have energy33. At rank at least4, (2) gives
  at most one affine plane and hence energy at most21. Thus `Q_max(6)=33`.
* Seven points of affine rank3 are a three-flat minus one point and have
  energy63. At rank at least4, (2) gives at most three planes and energy
  at most39. Thus `Q_max(7)=63`.
* Eight points that form a three-flat have energy112. Every other
  eight-point set has affine rank at least4, so (2) gives at most seven
  planes and energy at most70.

All displayed maxima are attained. The statements are dimension-independent.

## 2. Complements in a four-flat

Let `H` be a sixteen-point affine four-flat. If `D subset H` has size `t`
and `B=H\D`, then, for every nonzero tangent direction `d` of `H`,

    p_B(d)=8-t+p_D(d).                                    (3)

This is direct inclusion-exclusion of the two translated complements.
There are fifteen nonzero tangent directions, so

    Q(B)=15(8-t)^2+2(8-t)binom(t,2)+Q(D).                 (4)

For `|B|=9,10,11`, the small-set bounds above give respectively

    Q(B)<=120,153,211.                                    (5)

For a twelve-point set of affine rank4, its affine hull is such an `H`,
and its complement has four points. Equation(4) becomes

    Q(A)=288+Q(H\A).

Hence `Q(A)` is294 or300. It is300 precisely when the complement is an
affine plane. This proves the stated equality description within rank4.

## 3. Every twelve-set in a five-flat has a hyperplane containing eight points

There are62 affine hyperplanes in a binary five-flat. Every point belongs
to31 of them and every distinct pair belongs to15 of them. For a fixed
twelve-set, let `k_J=|A intersect J|`. Double counting gives

    sum_J k_J=372,
    sum_J binom(k_J,2)=990,
    sum_J (k_J-6)^2=120.                                  (6)

If no hyperplane contained eight points, each would contain at most seven.
Its complementary hyperplane also contains at most seven, so every `k_J`
would lie between five and seven. The last sum in(6) would then be at most
62, a contradiction.

If `A` has affine rank5, no hyperplane contains all twelve points. Choose
one containing `b>=8` points, translate it to a linear four-space `H`, and
write

    A=B union(v+C),  B,C subset H,  v not in H,
    b=|B| in{8,9,10,11},  c=|C|=12-b.

## 4. An exact energy identity for a hyperplane split

Set `T=sum_{d in H\{0}} p_B(d)p_C(d)`. The within-hyperplane counts are
`p_B(d)+p_C(d)`. The cross-hyperplane counts are the correlations
`r(h)=|B intersect(C+h)|`, and

    sum_h r(h)^2=bc+4T.

The diagonal choices contribute `bc`; nonidentical ordered pairs with
common difference `d` contribute `(2p_B(d))(2p_C(d))`. Consequently

    Q(A)=Q(B)+Q(C)+bc+6T.                                 (7)

For `b=9,10,11`, use(5), the energies of a three-, two-, or one-point set,
and `T<=floor(b/2)binom(c,2)`. This yields:

| b,c | Q(B) bound | Q(C) | bc | T bound | Q(A) bound |
|---|---:|---:|---:|---:|---:|
| 9,3 |120|3|27|12|222|
| 10,2 |153|1|20|5|204|
| 11,1 |211|0|11|0|222|

It remains to treat `b=8,c=4`.

## 5. The eight-plus-four split

### B is not a cube; C is a plane

Here `Q(B)<=70`, `Q(C)=12`, and the three nonzero directions of the
plane's two-space `U` have `p_C(d)=2`. Thus

    T=2 sum_{U-cosets J} binom(|B intersect J|,2).

There are four `U`-cosets in `H`, each with at most four points. For eight
points the maximum within-coset pair count is12, attained only by the
occupancy pattern `(4,4,0,0)`. That pattern would make `B` an affine cube,
which is excluded in this case. Every other pattern has at most nine
pairs, with extremal pattern `(4,3,1,0)`. Hence `T<=18`, and(7) gives

    Q(A)<=70+12+32+6*18=222.

### B is not a cube; C is not a plane

Translate `C` to `{0,x,y,z}` with independent `x,y,z`. Its six difference
directions are all the nonzero vectors of `U=span(x,y,z)` except
`s=x+y+z`. In each `U`-coset, the graph of these six directions is the
complete graph on eight vertices with a perfect matching removed.

There are two `U`-cosets in `H`. Let their occupancies in `B` be `k,8-k`.
The values0 and8 would make `B` a cube, so `1<=k<=7`. Among `k` points,
at least `max(0,k-4)` pairs of the removed perfect matching are present.
Therefore

    T <= binom(k,2)-max(0,k-4)
         +binom(8-k,2)-max(0,4-k)
       <=18.

Here `Q(C)=6`, so(7) gives `Q(A)<=70+6+32+108=216`.

### B is a cube

Translate its affine three-flat to a linear three-space `U subset H`.
Its pair counts are four on `U\{0}` and zero elsewhere. If all four
points of `C` lay in one `U`-coset, `A` would lie in an affine four-flat,
contrary to its rank5. Thus the two `U`-coset occupancies of `C` are
`1,3`, `2,2`, or `3,1`.

For occupancies1,3 or3,1, `C` cannot be a plane: a plane projects to
either one coset or two equally populated cosets. Thus `Q(C)=6` and
`T=4 binom(3,2)=12`, giving

    Q(A)=112+6+32+72=222.

For occupancies2,2, `T=4(1+1)=8` and `Q(C)<=12`, giving `Q(A)<=204`.

This proves `Q(A)<=222` throughout rank5. Equality is attained by
`A={0,1,2,...,10,16}` in the usual integer encoding of `F2^5`.

## 6. Higher ranks and the final equality statement

For rank at least6, the relation code of twelve points has dimension at
most five. Equations(1) and(2) give

    Q(A)<=66+6(2^5-1)=252<300.

Combining all ranks proves the dimension-independent maximum300. Only
rank4 can attain it, and Section2 shows that equality means exactly an
affine four-flat with an affine plane removed. For example `{0,...,11}`
is a maximizer, as the complement `{12,13,14,15}` in `{0,...,15}` is a plane.

### The two rank4 types and their periods

There are exactly two affine types of twelve-point sets of rank4: take
their four-point complements in the affine hull. Four points form either
an affine plane or an affine tetrahedron, and affine transformations are
transitive on each of these two possibilities.

Equation(3) gives the complete directional spectra in `F2^5`:

| Removed four-point set | Energy | Directional pair counts | Period subgroup |
|---|---:|---|---|
| affine plane of tangent two-space U |300|6 on3 directions,4 on12 directions,0 on16 directions|exactly U, of order4|
| affine tetrahedron |294|5 on6 directions,4 on9 directions,0 on16 directions|trivial|

For the plane complement, the three count-six directions are precisely
`U\{0}`. For the tetrahedron complement, its six distinct differences
produce count five, and no direction has count six. A direction is a period
of a twelve-set exactly when its pair count is six. Directions outside the
four-flat's tangent space have no pairs. Thus the stated period subgroups
follow directly, without imposing any additional shape assumptions.

For a type-based optimization, these are two actual affine shape types;
orientation still matters when their spectra are assigned to residue-edge
directions. The separate rank5 branch has energy at most222. These shape
facts do not by themselves exclude any additional Kakeya weight profile.

## 7. Independent implementation and its exact scope

`verify_energy12.cpp` was written for this audit without importing or
consulting the earlier census or producer implementation. It reads no input
files. Every twelve-point set has affine rank4 or5 in `F2^5`. Translate one
of its points to zero, choose an affine basis from its points, and map that
basis to the coordinate basis of its affine hull. Thus it suffices to check:

* Rank4: every set containing `{0,1,2,4,8}` in `F2^4`, namely
  `binom(11,7)=330` normalized sets.
* Rank5: every set containing `{0,1,2,4,8,16}` in `F2^5`, namely
  `binom(26,6)=230230` normalized sets.

These representatives can repeat affine classes; completeness does not
require uniqueness. Every normalized set has the claimed rank because it
contains the coordinate affine basis.

For each set the program independently computes unordered-pair differences
and affine planes by triple completion: three points determine the fourth
by XOR, and the plane is counted only when that fourth point is largest.
It checks(1) on all230560 normalized sets. The observed maxima are300 at
rank4 and222 at rank5. The full energy histograms and witness sets are in
`ENERGY12_ENUMERATION.json`. `replay_energy12.py` compiles and reruns this
program in a fresh temporary directory and checks the witness energies by
translated intersections and four-subset XOR tests.

This is a separately written implementation and an analytic replacement for
the old census dependency. It is not epistemically independent human review
or a Lean formalization. No lower-support Kakeya profiles are excluded by
this energy audit alone.
