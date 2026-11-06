# Optional structural derivation through the nine-point equality theorem

This is an alternative proof of the canonical ten-point support shape.
It does **not** remove all finite-census dependencies. It replaces the
direct14,950-candidate ten-point check by the independently verified
2,930-candidate nine-point missing-neighbor census, followed by an
analytic equality theorem. The direct80-support census remains the
primary structural certificate in the Round5 proof.

## Dependencies

1. The complete seven-row nine-point geometry table, independently
   reproduced in `research_round5/nine_geometry/verify_nine_geometry.py`
   and `research_round5/middle_duals/verify_nine_degree_types.py`.
   This table is a finite census, not an analytic classification.
2. The analytic theorem in
   `research_round3/m11/NINE_POINT_DIFFERENCE_RIGIDITY.md`: a nine-set
   with28 nonzero differences has the displayed normal form below.
   Its proof does not use an affine-orbit census.

## Step1: a ten-point difference cover has a degree-three unique-edge vertex

Let S have ten points and cover all31 nonzero differences. For x in S,
put T=S minus {x}, and let F be the directions missing from T+T.
Every missing direction must be supplied by an edge from x to T, so

    F is a subset of x+T.

Consequently x has exactly |F| neighbors in T through the missing
directions. The seven-row table permits this only when |F|=3 or9:

| Missing count | Maximum outside missing-direction degree |
|---:|---:|
| 3 | 3 |
| 4 | 3 |
| 6 | 4 |
| 8 | 6 |
| 9 | 9 |
| 10 | 9 |
| 16 | 9 |

Deleting x loses exactly the directions of those edges incident to x
that were unique in S. Hence every vertex of S has unique-edge degree
either3 or9. They cannot all have degree9: the sum of these degrees
would be90, whereas there are at most31 unique directions and hence
at most62 unique-edge endpoints. Therefore some vertex has degree3.
Deleting it gives a nine-point set with exactly28 differences.

## Step2: analytic equality normal form and unique extension

The inherited analytic equality theorem gives, after an affine change
of coordinates,

    T = (V minus {0,d}) union (W minus {0}),

where dim V=3, dim W=2, V and W are complementary, and d is a nonzero
element of V. Its missing directions are

    F = d + (W minus {0}).

The only point a outside T satisfying a+F subset T is a=d. Here is a
direct check without any neighbor census. Write a=v+w0 with v in V
and w0 in W. If v is neither0 nor d, then a+F has a fixed nonzero
V-coordinate v+d; membership in T would force all three of its
W-coordinates to be0, impossible. If v=0, the V-coordinate is d,
which does not occur in T. If v=d, the V-coordinate is0, and

    w0 + (W minus {0}) is a subset of W minus {0}

holds precisely when w0=0. Thus a=d, proving

    S = (V minus {0}) union (W minus {0}).

This is the canonical ten-point support used by the unrestricted
weight argument.

## Audit of the inherited equality proof

The archived proof is genuinely analytic. Its key steps are valid:

- A nine-set with a direction having four pairs has at most21
  differences, so this cannot happen in the28-difference case.
- If n_j counts directions with j pairs, then n_2+2n_3=8, while
  n_2+3n_3 is divisible by3 by counting affine planes. Thus n_3=1 or4.
- The n_3=4 case has n_2=0. The translation symmetric-difference
  metric forces these four directions together with0 to be closed
  under addition, an impossible subgroup of order5.
- For the unique three-pair direction d, its three full two-point
  cosets are a three-flat with one d-coset removed. Their internal
  spectrum accounts for all repeated directions.
- The three remaining points occupy the three other cosets of that
  three-flat. Their XOR lies in the omitted d-coset; translation by
  that XOR puts them into a two-dimensional complementary subspace.

The only finite-classification dependency of this optional route is
Step1. It should not be described as a fully census-free hand proof.
No new exclusions or frontier counts are claimed by this note.
