# Extending the integer dual to nine heavy vertices

The heavy/light charging theorem and the eight-point analytic difference
bound are unchanged. This extension adds one exact finite geometric fact:

    For nine distinct points H in F₂⁵, |D(H)|<=28.

Here D(H) is the set of nonzero pair differences. If H has affine rank at
most four, all its differences lie in a vector space with at most sixteen
points, giving at most fifteen nonzero differences.

Otherwise choose an affine basis consisting of six of its points. Translate
one to zero and apply an invertible linear map taking the five independent
basis differences to e1,...,e5. The normalized set contains
{0,1,2,4,8,16}; its other three points are distinct choices among the
remaining twenty-six vectors. This covers every rank-five nine-point set
up to affine equivalence. Duplicate normalized presentations cause no
problem for an upper bound.

`difference9_bound.py` exhausts all C(26,3)=2,600 choices and computes each
set of pair differences directly. The complete list of extras and counts
is delivered in `DIFFERENCE9_REPLAY.json`. The maximum is twenty-eight,
attained by {0,1,2,3,4,5,8,16,30}. The distribution is:

| Distinct differences | Normalized choices |
|---:|---:|
| 21 | 60 |
| 22 | 60 |
| 23 | 810 |
| 25 | 660 |
| 27 | 750 |
| 28 | 260 |

Thus the complete upper-bound vector for zero through nine selected heavy
vertices is

    0,0,1,3,6,10,15,21,25,28.

For h=9 the integer dual consequently has left side at least
32(31-28)=96. The previous binomial estimate gave no positive bound for
nine heavy vertices and could not test that case.

This is a finite geometric proof with a complete affine-basis reduction;
it is not asserted to be a purely symbolic derivation of the value
twenty-eight. Its replay is small and independent of the fibre-spectrum
census. The subsequent weight-profile exclusions still use that census
and the reproduced quotient-sumset capacity table as stated in
`HEAVY_LIGHT_DUAL_LEMMA.md`.

The newly named screen and receipt preserve the earlier diagnostic files.
Each certificate identifies its exact heavy positions, price and light
ceiling and is checked again with Python integers. No existing ledger is
changed by discovery. No attempt with ten heavy vertices is needed for
this universal counting method: a ten-point difference cover of F₂⁵
exists, so its worst-case missing-direction lower bound is zero.
