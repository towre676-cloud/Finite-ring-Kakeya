# Small heavy supports and the directions they miss

All spaces in this note are binary. These lemmas supply the geometric final
steps in the middle-maxima support theorem. The proofs are analytic, with no
affine support-orbit census as a dependency.

## 1. Eight-point difference sets

For T subset F2^5 with |T|=8, the number of its nonzero pair differences is
at most25.

Proof. The augmented point matrix, with columns(1,x), has rank at most6.
Its kernel has dimension at least2. Every nonzero kernel vector has positive
even weight at least4, because the columns are distinct. If no four-subset
has sum zero, every nonzero vector has weight6 or8. Two distinct weight-six
vectors in length8 have symmetric difference of size at most4; a weight-eight
and weight-six vector have difference of size2. These facts preclude a
subspace of dimension2 with all nonzero weights6 or8. Therefore T contains
an affine plane. Its six pairs yield three repeated directions, so the28
pairs of T determine at most28-3=25 distinct nonzero differences.

## 2. The equality geometry for eight points

If T has exactly25 nonzero differences, its missing set F of six nonzero
directions is an affine three-flat with an affine line removed. In particular
F lies in a character halfspace and is triangle-free.

Proof. If n_j counts directions with j unordered pairs, then
sum(j-1)n_j=28-25=3. One affine plane already creates three directions
with multiplicity at least2. Thus those three have multiplicity exactly2,
all other represented directions have multiplicity1, and T contains exactly
one affine plane. Translate that plane to a linear two-space U.

The four remaining points x_1,...,x_4 lie in four distinct nonzero U-cosets:
two in one coset would create a second affine plane using two points of U.
Their four quotient classes in F2^5/U=F2^3 contain no triangle, because three
classes summing to zero would make three extras plus a point of U into a
second affine plane. Four distinct nonzero triangle-free points in F2^3
are an affine hyperplane not containing zero: choose any three, which must
be independent; the fourth must be their sum. Consequently

    sigma=x_1+x_2+x_3+x_4 belongs to U and sigma!=0.

The inequality follows because otherwise the extras would themselves be a
second affine plane. Let y_1=x_1+x_2, y_2=x_1+x_3, y_3=x_1+x_4. Their
quotient classes are the three nonzero elements of a two-space, and

    y_1+y_2+y_3=sigma.

In each of those three quotient cosets the represented directions are
exactly y_i+<sigma>. Choose a in U\<sigma>, and let
L=span(sigma,y_1,y_2). The quotient classes of y_1,y_2 are independent,
so L has dimension3 and L intersect U=<sigma>. The missing directions are

    F=(a+L) \ (a+<sigma>).

Because a is outside L, this is contained in an affine hyperplane not
through zero. In particular no three distinct members of F sum to zero.

## 3. Nine-point difference sets

For T subset F2^5 with |T|=9, there are at most28 nonzero pair differences.

Proof. First, if one direction h has four pairs, T consists of four full
<h>-cosets plus one point. Its directions consist of at most one within-pair
direction, at most2*binom(4,2)=12 directions between full cosets, and at
most8 directions from the singleton to the paired points. Hence it has at
most21 nonzero differences. We may therefore assume all pair counts<=3.

The augmented point matrix has binary kernel dimension at least3. Take any
three-dimensional subspace C of that kernel. Its seven nonzero words have
even weights at least4. The sum of all their weights is4 times the number
of active coordinate positions, hence at most36. If at most two had weight4,
the sum would be at least2*4+5*6=38. Thus T contains at least three affine
planes.

Let n_j count directions having j pairs, j=1,2,3. Then

    n_1+2n_2+3n_3=36,
    n_2+3n_3=3*(number of affine planes)>=9.

If T had at least29 differences, then n_2+2n_3<=7. Since n_2+3n_3 is a
multiple of3, the only possibilities are(n_2,n_3)=(3,2) or(0,3).

For distinct directions d,e with three pairs, the translation-defect
triangle inequality gives p_T(d+e)>=2: the defects are9-2*3=3, their sum
is6, and a nonzero defect has odd parity. Put U=<d,e>.

If(n_2,n_3)=(3,2), the pair counts on U\0 are3,3,2. If k_C are the
populations of the U-cosets, then sum_C binom(k_C,2)=8 and sum_C k_C=9.
The only partition with entries at most4 satisfying these equations is
(4,2,2,1). A full four-point coset and either two-point coset yield at least
two pairs in each of the four directions of their difference coset outside
U. Together with the three directions in U this gives at least seven
directions of multiplicity>=2, contradicting n_2+n_3=5.

If(n_2,n_3)=(0,3), the three multiplicity-three directions are U\0.
Now sum_C binom(k_C,2)=9, so the populations are either(4,3,1,1) or
(3,3,3). In the first case the full coset and three-point coset give at
least three pairs in four outside-U directions. In the second, two
three-point subsets of four-point cosets intersect in at least two points
after every relative translation, again giving four outside-U directions
of multiplicity>=2. Either contradicts the specified spectrum.

All possibilities with29 or more differences are excluded.

## 4. Missing heavy directions spend light pairs

Partition the residue fibres into a heavy set T and light fibres of sizes
at most3. Let F=V\({0} union(T+T)) be the directions with no heavy-heavy
edge. At a light fibre, each pair count is0 or1, and the total number of
available pair incidences is binom(w,2).

Let c_1>=c_2>=... be the heavy pair-count caps. Suppose t<=|T| and
c_1+...+c_(t-1)<16. Then every direction in F requires at least t light
pair incidences. Indeed, with at most t-1 such incidences, light-heavy edges
use distinct heavy endpoints and cover at most that sum. Replacing a
light-light edge by its two endpoint incidences in unused heavy slots can
only increase this upper bound; heavy caps here are at least2.

Consequently

    t*|F| <= sum_light binom(w,2).                         (L1)

Use |F|>=6 for eight heavy bases and |F|>=3 for nine heavy bases.

## 5. A unique cap-six hub bonus

Suppose the heavy set consists of one fibre of pair cap6 and others of cap
at most4, and every light fibre has pair cap at most3. Let r=|F|. Let b count
light fibres of size at least4, and B=sum_light binom(w,2). Then

    B >=4r-b.                                            (L2)

For a direction in F, let q be its total light pair mass and p the light
pair count on the edge to the cap-six hub (zero if absent). Every other
light-heavy edge covers at most4 times its light pair count. Every
light-light edge obeys pq<=4(p+q), since its two counts are at most3.
Thus coverage in that direction is at most4q+2p.

If q<=2 then p<=q and4q+2p<=12<16. If q=3, reaching16 requires p>=2.
Therefore the direction costs at least4 light pairs unless its hub partner
has size at least4, in which case it still costs at least3. Each fixed light
residue can meet the hub in exactly one direction. Hence at most b directions
receive this one-pair saving. Summing proves(L2).

## 6. Two final boundary profiles

### Profile A

Weights are(12,8^6,6^2,3,2^9). Take the nine fibres of weights>=6 as heavy.
There are at least three missing heavy directions, and each needs at least
four light pair incidences because the three largest heavy caps sum to
6+4+4=14<16. The light budget is3+9=12. Therefore there must be exactly
three missing directions and all light pair mass must occur there.

Those three missing directions cannot be the nonzero elements of a
2-dimensional subspace: the nine heavy residues would then meet every coset
of that subspace in at most one point, but there are only eight cosets.
The three missing directions are thus linearly independent. The three pair
differences of a three-point fibre sum to zero, so at most two can belong
to this missing set. The actual restricted light budget is at most2+9=11,
contradicting the required12.

### Profile B

Weights are(12,8^6,6,5,4,2^9). Take the eight fibres of weights>=6 as heavy.
The light total pair mass is10+6+9=25 and b=2. If r>=7 then(L2) requires
at least4*7-2=26 pairs, impossible. Thus r=6. Section2 says the missing set
lies in a character halfspace. For a w-point light fibre the number of pairs
whose difference is in that halfspace is at most floor(w^2/4), by splitting
its points between the two character values. The total available restricted
light pair mass is therefore at most

    floor(5^2/4)+floor(4^2/4)+9=6+4+9=19.

But(L2), applied to those same missing directions, requires at least
4*6-2=22. Contradiction.

Both exclusions use only the common necessary lift capacities and therefore
apply to both target rings, without dropping or choosing any carry phases.
