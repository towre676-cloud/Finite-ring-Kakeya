# Whole-profile exclusions from the weighted light-incidence bound

## The criterion

Let $H$ consist of the residue fibres of weight at least four, and put $h=|H|$. Let $L_2,L_3$ count fibres of weights two and three. For maximum fibre weight $m$, put

$$
P=\lfloor m/2\rfloor,\qquad
r=\left\lceil\frac{16}{P}\right\rceil.
$$

The general theorem in `MISSING_DIRECTION_INCIDENCE.md` states that, whenever $h\ge9$,

$$
r\bigl|(\mathbb F_2^5\setminus\{0\})\setminus D(H)\bigr|
\le L_2+2L_3.
\tag{1}
$$

It applies to arbitrary support sizes. Its proof uses the following facts. A missing heavy direction needs at least $r$ active light endpoints to cover its sixteen lifts. The missing-direction set cannot contain all three nonzero points of a binary two-space, since then nine heavy residues could not fit into its eight cosets. Therefore each light fibre of weight two contributes at most one incidence, and each light fibre of weight three contributes at most two, over the entire missing-direction set.

The analytic nine-point direction bound gives $|D(H)|\le28$ when $h=9$. Thus a whole weight profile is excluded whenever

$$
\boxed{h=9\quad\text{and}\quad
3\left\lceil\frac{16}{\lfloor m/2\rfloor}\right\rceil>L_2+2L_3.}
\tag{2}
$$

This criterion holds for every placement of the profile's weights and every actual fibre shape, in both rings. It does not assert that all larger supports must have ten heavy fibres: the exact light weights on the right side matter. No total-weight assumption is needed by (1) or (2).

The proof is analytic. Neither a fibre-spectrum census, a quotient-sumset table, nor a SAT computation is a premise of the new exclusions. The inherited frontier is only the finite list to which the criterion is applied.

## Exhaustive application to the pinned frontier

The original Round7 survivor file has $183{,}476$ profiles. All already have at least nine heavy fibres. Exactly $2{,}187$ have $h=9$, and (2) excludes exactly **175** of them. The other $2{,}012$ nine-heavy profiles pass this necessary condition; that does not establish their realizability. Profiles with $h\ge10$ receive no exclusion from the cardinality-only missing-direction lower bounds used in this replay.

The replay also evaluates the weaker universal incidence screen for every profile with $h\le8$, using

$$
r|M|\le L_2+3L_3,
$$

the pair bound for $h\le7$, and $|D(H)|\le25$ for $h=8$. The pinned input contains **no profiles in these heavy-count ranges**, so this screen supplies zero additional exclusions here.

The cumulative exclusions are:

| Support size | Maximum 12 | Maximum 13 | Maximum 14 | Maximum 15 | Total |
|---|---:|---:|---:|---:|---:|
| 13 | 10 | 6 | 69 | 43 | 128 |
| 14 | 2 | 1 | 23 | 10 | 36 |
| 15 | 0 | 0 | 7 | 2 | 9 |
| 16 | 0 | 0 | 2 | 0 | 2 |
| **Total** | **12** | **7** | **101** | **55** | **175** |

The first 128 were recorded in the frozen maximum-fifteen support-thirteen extension. This final general-weight application adds **47** profiles. Their light-weight patterns are:

| Support size | Number of new profiles | Light weights | $L_2+2L_3$ |
|---|---:|---|---:|
| 14 | 36 | $2,2,3,3,3$ | 8 |
| 15 | 9 | $2,2,2,2,3,3$ | 8 |
| 16 | 2 | $2,2,2,2,2,2,3$ | 8 |

All new profiles have $r=3$, so each yields $9>8$. In the cumulative family, 174 profiles give $9>8$ and the exceptional original source line 146219 gives $9>7$.

## Exact accounting and replay

The final weight-profile frontier is

$$
\boxed{183{,}476-175=183{,}301.}
$$

| Support size | Original profiles | Cumulative exclusions | Remaining profiles |
|---|---:|---:|---:|
| 13 | 85,340 | 128 | 85,212 |
| 14 | 74,373 | 36 | 74,337 |
| 15 | 19,514 | 9 | 19,505 |
| 16 | 3,853 | 2 | 3,851 |
| 17 | 396 | 0 | 396 |
| **Total** | **183,476** | **175** | **183,301** |

These are whole-profile exclusions. They do not add or duplicate any support-orbit SAT-role credit. The remaining profile list is an inherited frontier, not a complete list of all unresolved cases of the dimension-five problem.

Run:

```bash
python3 research_round8/incidence/verify_general_incidence_profiles.py
```

The replay scans every original source profile and computes its exact integer criterion. It regenerates all 175 certificates and checks that every retained source line is preserved byte-for-byte and in order. It separately verifies that removing exactly the 47 new profiles from the frozen 128-exclusion frontier gives identical final bytes. Both earlier stages' source, certificate, and survivor files are hash-pinned and remain unchanged.

The geometric arguments are given by the pinned hand proofs. The Python implementation checks exact finite arithmetic and complete ledger coverage; it is not a proof-assistant formalization.
