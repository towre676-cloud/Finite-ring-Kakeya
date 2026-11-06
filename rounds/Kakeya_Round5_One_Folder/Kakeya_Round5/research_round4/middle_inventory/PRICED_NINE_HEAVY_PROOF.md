# A complete one-heavy incidence-price family

## Result and relation to the baseline inventory

This is a separately recorded stage after the frozen276,267-profile middle
inventory. It applies one proved resource/LP family to every residual profile,
excludes **512** additional whole weight multisets, and leaves **275,755**.

The sole remaining support17/maximum18 profile is excluded. Consequently:

> For either target ring in dimension five, a Kakeya set of size at most93
> with exact maximum fibre size18 has pair-active support at most16.

This conclusion combines the complete support17 weight inventory with the
previous exclusions of support18 and every larger support. The other55
support/maximum cells in the middle inventory remain nonempty.

## The resource bound with one distinguished heavy vertex

Select the nine largest fibres as heavy, and distinguish one largest heavy
vertex h0. Let F be the set of directions absent from the nine-heavy residue
support, and let r=|F|. The inherited nine-point difference theorem gives
r>=3; the missing set F is sum-free.

For a light fibre of weight w, put c=floor(w/2), let ell be the largest light
pair cap, and set

    B=floor(w^2/4),    q_F=(q(w)+1)/2.

Here q(w) is the proved maximum-direction quota. Sum-freeness gives the
restricted pair budget B and the restricted maximum-count quota q_F.
The nine potential heavy-neighbor pair counts x0,...,x8 satisfy

    0<=xj<=c,    sum xj<=B,    #{j:xj=c}<=q_F.

These are necessary constraints, not a complete shape characterization.
Let cj be the pair cap of heavy vertex j. Define two exact local resource
maxima over this relaxation:

    a_i = ell*B + max_{x0=0} sum_j [2M(xj,cj)-ell*xj],
    b_i = ell*B + max_{x0>=1} sum_j [2M(xj,cj)-ell*xj].

For any nonnegative price t charged when the incidence at h0 is positive,
the corresponding local row is exactly

    R_i(t)=max(a_i,b_i-t).

At h0 there is at mostone neighboring residue in each direction in F, so
at most r light incidences there can be positive. The heavy/light resource
inequality therefore bounds doubled total capacity in F by

    U_r(t)=sum_i max(a_i,b_i-t)+r*t.                       (1)

Coverage requires at least32r in doubled units. If0<=t<=32 and

    U_3(t)<96,                                           (2)

then, for every r>=3,

    U_r(t)=U_3(t)+(r-3)t <96+32(r-3)=32r.

Thus(2) excludes the profile for every possible nine-heavy residue placement.
No assumption that exactlythree directions are missing is made.

## Exact optimization: this is a small LP dual

Write d_i=b_i-a_i. Then

    U_3(t)=sum_i a_i + sum_i(d_i-t)_+ +3t.

The minimum over all t>=0 is

    sum_i a_i + the sum of the three largest positive d_i,             (3)

using fewer terms when fewer thanthree gains are positive. To see this,
any fixed three positive gains satisfy sum_i(d_i-t)_++3t>=their sum.
Equality is attained by taking t to be the third-largest positive gain,
or by t=0 when there are fewer thanthree positive gains.

This is the dual of the cardinality LP maximizing sum_i d_i*z_i under
0<=z_i<=1 and sum_i z_i<=3. The LP selects the three largest positive gains.
The variables describe use of the distinguished heavy vertex in the local
relaxation; no claim of full fibre-type realizability is made.

Every gain satisfies

    d_i<=max_{x>=1}[2M(x,c0)-ell*x]<=32-ell<=31.

Indeed, allocating positive x0 leaves no more mass and no more maximum-count
quota for the other eight slots than in the inactive problem. Their remaining
score cannot exceed the inactive optimum. Therefore an integer price in
0..31 always attains(3), and the implemented bank0..32 is complete for this
one-distinguished-heavy price family, even allowing arbitrary real prices.

This is an exact automatic dual optimization, with no floating-point solver.
It still uses a deliberately relaxed local state space and one distinguished
heavy vertex; it is not the entire type-coupled optimization proposed by the
user.

## The newly closed boundary cell

The frozen inventory contains exactlyone support17/maximum18 profile:

    (18,8^5,7,6^2,2^8).

The nine heavy caps are(9,4^5,3^3), and the eight light fibres each have
weight two. Each light fibre has a_i=8 and b_i=18. Price t=10 gives

    U_3(10)=8*max(8,18-10)+3*10=64+30=94<96.

There is also a direct undoubled proof. The eight light fibres supply at
mosteight pair units across the missing directions. All non-h0 edges
contribute at mostfour per light pair unit. At most r edges reach h0, and
each such edge can add at mostfive beyond that baseline. Thus

    capacity(F)<=4*8+5r=32+5r<16r       for every r>=3.

This hand argument verifies the final boundary exclusion without using any
energy-table value or optimizer. The complete weight inventory is what
establishes that there are no other profiles in the cell.

## Complete additional accounting

| Support | Baseline profiles | New price cuts | Final profiles |
|---|---:|---:|---:|
| 10 | 3,220 | 0 | 3,220 |
| 11 | 24,708 | 0 | 24,708 |
| 12 | 61,048 | 0 | 61,048 |
| 13 | 86,075 | 162 | 85,913 |
| 14 | 76,019 | 154 | 75,865 |
| 15 | 20,584 | 93 | 20,491 |
| 16 | 4,150 | 74 | 4,076 |
| 17 | 463 | 29 | 434 |
| **Total** | **276,267** | **512** | **275,755** |

The absence of new cuts at supports10..12 is expected: with at mostthree
light vertices, the distinguished heavy's three-incidence constraint adds
nothing to the unpriced local rows.

## Exact replay and audit

The producer uses forward resource dynamic programming and scans the integer
price bank. The verifier independently reconstructs active/inactive maxima
with backward recursion. It checks every supplied light row, price, strict
bound, and weight profile. It compares the price-bank optimum with the exact
three-largest-gain formula for every cut, and verifies every residual profile
has optimized value at least96. Exact set subtraction checks that no profile
is removed without a certificate.

The LP/geometry reviewer accepted the resource formula, the r>=3 slope
argument, and the94<96 boundary calculation before the scan was credited.
As elsewhere in this project, this is model-agent mathematical cross-checking
and independent implementation, not external human review or proof-assistant
formalization.

Run after verifying the frozen baseline inventory:

    python3 research_round4/middle_inventory/verify_priced_nine.py

The authoritative receipt is PRICED_NINE_INDEPENDENT_REPLAY.json. The final
full list is after_priced_nine_survivors.txt. The preceding276,267-profile
list and its receipt remain unchanged as a distinct verified stage.
