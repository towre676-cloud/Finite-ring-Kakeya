# Round 4 method: exact support-orbit tests with checked refutation proofs

## Scope

This round attacks the dimension-five problem for both rings
R = Z/4Z and R = F2[e]/(e^2): show that every Kakeya set K in R^5 has at least 94 points.
A counterexample would have at most 93 points. The round-3 strata are indexed by the largest
residue-fibre size m. This method decides one pair (m, S) at a time, where S is a pair-active
residue support up to linear equivalence. It works for every residue placement and fibre shape
simultaneously.

Each exclusion here is a statement that a finite system of necessary conditions has no
solution. The refutation proof for that system is checked by a separately written DRAT
checker. This is computer-assisted mathematics: the conclusions rely on (i) the mathematical
lemmas below, (ii) correctness of the CNF encoder, and (iii) correctness of the proof checker.
The solver itself need not be trusted. Nothing here is a proof-assistant formalization.

## 1. Set-up and normalization

Write V = F2^5 and u = 2 (for Z/4Z) or u = e. Every point of R^5 is r~ + u t, where r in V is its
residue, r~ the 0/1 lift, and t in V its tangent coordinate. The fibre over r is
A_r = {t : r~ + u t in K}.

A primitive direction D = d~ + u e has nonzero residue d. Its four-point line through a = r~ + u t
meets the fibre over r in the pair {t, t+d}. It meets the fibre over r+d in a d-pair whose class in
V/<d> equals t + e + c(r,d). Here the carry c(r,d) is r AND d for Z/4Z and 0 for F2[e]/(e^2).
Unit multiples identify e with e + d, so each nonzero d has 16 lifted directions, labelled by
V/<d>; there are 496 directions in all.

For a fibre A and d != 0 let P_A(d) be the set of classes in V/<d> of d-pairs inside A, and
p_A(d) = |P_A(d)|. The edge {r, r+d} covers exactly the label set
P_{A_r}(d) + P_{A_{r+d}}(d) + c(r,d). Hence a Kakeya set satisfies, for every d != 0,

    sum over edges {r, r+d} of |P_{A_r}(d) + P_{A_{r+d}}(d)|  >=  16.            (C)

Normalizations, each preserving the Kakeya property and not increasing |K|:

* Fibres with one point lie on no line and are deleted. The pair-active support S is the set of
  residues whose fibre has at least two points.
* Translation by a lift of a residue puts a largest fibre, of size m, over residue 0.
* GL_5(F2) lifts to GL_5(R) and fixes residue 0, so S may be replaced by any GL_5(F2)-image.
  Fibre shapes change by affine maps, which permute pair spectra.

Condition (C) forces S + S = V ("covering"), so S spans V.

## 2. Complete orbit list of supports

`src/orbits_all.cpp` enumerates all spanning sets T of nonzero vectors (T = S \ {0}) up to
GL_5(F2). It grows sets one point at a time from the unique 5-element basis orbit; every spanning
(k+1)-set contains a spanning k-subset. Its canonical form is the least image bitmask over ordered
bases chosen from T, restricted at each step by a GL-invariant vertex invariant. The explored basis
set is equivariant, so the form is a canonical orbit label.

Completeness check: for every k from 5 to 31,

    sum over orbits of |GL_5(F2)| / |Stab(T)|  =  number of spanning k-subsets of V \ {0},

where |Stab(T)| is the number of explored bases attaining the minimum. The right side is computed
independently by Mobius inversion over the subspace lattice. All 27 sizes agree exactly. A split
orbit would make the left side too large, and canonical forms are images of T, so two inequivalent
sets cannot merge. Restricting to covering sets leaves 1,113 support orbits, of sizes 10 to 32
including 0. For support sizes 11 and 12, `src/orbcheck.cpp` brute-forces all 65,780 normalized
sets of size 11. It reproduces round 3's 7,676 covering sets and the same 13 orbits.

## 3. The necessary conditions encoded for one pair (m, S)

Unknowns: for each v in S, a fibre size w_v and a pair spectrum; for each v and each incident
direction d in D_v = {v + b : b in S, b != v}, the integer p_v(d); and for each edge, a capacity.

(A) Realizable spectra. The histogram of (p_A(d))_{d != 0} must be one of the spectra in the
    complete census `data/spec32.csv` (all weights 1 to 32). The values on the incident directions
    D_v must form a sub-multiset of that histogram. Hub size w_0 = m; outer sizes lie in [2, m];
    the outer sizes sum to at most 93 - m. The census is recomputed by `src/spectra32.cpp`. For
    weights up to 19 it agrees exactly with round 2's independent census.

(B) Edge capacity. |X + Y| <= Mtab[|X|][|Y|] for X, Y in V/<d> (about F2^4). `data/Mtable.txt` is
    the exact maximum, computed exhaustively by `src/msum.cpp`. It is min(16, pq) except
    (3,5) -> 13, (3,6) -> 14, (3,7) -> 15, as in round 2.

(C) Coverage: the 16-label demand of every nonzero direction.

(D) Affine-rank direction space. If p_A(d) > 0 then d is a difference of A, so d lies in the
    linear direction space H of the affine hull of A, and dim H equals the affine rank. The census
    records the possible ranks of each spectrum; only one weight-6 spectrum occurs with two ranks
    (4 and 5). If a spectrum has exactly 2^r - 1 positive directions at rank r, the positive set
    is exactly H \ {0}.

(E) Maximal-pair subspace. With c = floor(w/2), the directions with p_A(d) = c, together with 0,
    form a linear subspace whose size is one more than the histogram count at c. For even w it is
    the translation stabilizer of A. For odd w it is round 2's quota theorem: D(d) = w - 2p(d) is
    subadditive and odd, so two maximal directions sum to a maximal one.

The subspaces in (D) and (E) are chosen once per fibre and used at every incident direction. This
couples the direction labels on the actual support, which round 3's label-free relaxations did
not.

All five conditions hold for both rings, because the carry only translates a sumset. A pair (m, S)
for which this system is unsatisfiable has no Kakeya set of at most 93 points with maximum fibre
m over residue 0 and pair-active support in the orbit of S.

## 4. Encoding, proofs and checking

`src/encode_cnf2.py` writes the conditions as CNF:

* one-hot spectrum, value and subspace variables;
* sequential at-most-one constraints;
* full totalizers for cardinalities and the weight sum;
* unary edge capacities with ordering clauses.

CaDiCaL 1.9.5, through PySAT, solves each instance with proof logging. `src/dratcheck.cpp` is a
forward checker that verifies every lemma by RUP, with RAT on the pivot as a fallback.
`src/dratback.cpp` is a backward, core-first RUP checker. Neither shares code with the solver.

Both checkers accept valid pigeonhole proofs and reject fabricated proofs. They also passed a
soundness fuzz: 317 valid refutations were replayed against weakened, satisfiable formulas, and
neither checker accepted any of them.

Encoder soundness test (`src/soundness.py`, `src/soundness2.py`): actual Kakeya sets in both
rings are converted to fibre data. The CNF must be satisfiable when their true spectra and
directional pair counts are fixed. The test sets were:

* the 94-point generalized star (full hub);
* ten greedy-minimal random Kakeya sets of 276 to 294 points;
* two SAT-constructed Kakeya sets of 150 points with a hub of 19 on a 12-point support.

All of these pass.

## 5. What survives

A satisfiable instance is not a Kakeya set. It only shows that conditions (A) to (E) do not
exclude that support. Survivors are recorded with a witness of their weights.
