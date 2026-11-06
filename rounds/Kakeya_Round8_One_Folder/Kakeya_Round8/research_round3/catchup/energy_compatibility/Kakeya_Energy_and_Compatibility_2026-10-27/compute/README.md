# Exact translation completion for fixed Kakeya fibre shapes

This package supplies a small exact second stage after fibre shapes have been
chosen. It also supplies a cheap, translation-invariant overlap bound that can
reject a shape family before the second stage is solved.

**Scope:** the results concern the recorded fixed labelled shapes, their
independent internal translations, and the explicitly listed residue
directions. They do not close the unrestricted dimension-five theorem, an
entire maximum-fibre stratum, or the all-dimension lower bound. No actual
weight-at-most-93 family satisfying every local coverage condition was supplied
to this stage. The 94-point star is a positive control.

## Verify the saved results without installing a solver

From this directory, run:

```sh
python verify_completion_results.py
```

The verifier uses only the Python standard library. It reconstructs every
saved CNF, checks hashes and strict DIMACS syntax, checks decoded SAT witnesses
using separate coordinate arithmetic in the actual four-element rings, and
independently checks the short UNSAT proofs by forward RUP. It also recomputes
the complete two-dimensional classification by translations and exhaustively
checks the tree-overlap inequality on all three-set systems in `F2^2`.

The saved result is `STANDARD_LIBRARY_VERIFICATION.json`. The current receipt
records:

* ten reconstructed CNFs, with six SAT witnesses and four UNSAT proofs;
* 4,802 two-dimensional shape-family/ring combinations;
* 12,578 affine-gauged offset assignments in the original encoder audit;
* 500 additional three-dimensional pinned-offset fixtures in that audit;
* 65,536 three-set/relative-translation checks of the tree-overlap bound.

The three-dimensional fixtures are finite implementation checks. The proof
of the encoder's semantics is the exact quotient identity below.

`rupcheck2.c` is an unchanged copy of the independently developed forward RUP
checker from the recovered continuation package; `CHECKER_PROVENANCE.json`
records its source and hash. It can also replay the proofs:

```sh
cc -O2 rupcheck2.c -o rupcheck2
./rupcheck2 n5_four12_block_dual/input.cnf n5_four12_block_dual/proof.drat
```

The C log counts nonempty added lemmas; the Python receipt counts the terminal
empty clause as well. Thus the same four-lemma refutation appears as five
checked proof clauses in the Python receipt.

## What the solver encodes

The input gives a subset `A_x` of `F2^n` at each active residue label `x`.
The unknowns are offsets `t_x` in `F2^n`. The actual fibre is `A_x + t_x`.
No independent rotations are allowed.

For each nonzero required residue direction `d`, form the quotient
`Q_d = F2^n / <d>` and the set of full internal pairs

\[
P_x(d)=\{u+\langle d\rangle:\{u,u+d\}\subseteq A_x\}.
\]

The edge joining `x` and `x+d` covers exactly

\[
P_x(d)+P_{x+d}(d)+q_d(t_x+t_{x+d}+c_R(x,d)),
\]

where `c_R=0` for the dual numbers and `c_R=x & d` for `Z/4Z` with the binary
section. The union over all such base edges must equal `Q_d`.

The encoder uses Boolean translation bits, exact XOR gates for their quotient
differences, exact selectors for each possible quotient shift, and one
coverage clause for each quotient class. A common set of offset bits is used
for every direction; their phases cannot be selected independently.

An affine shear of high coordinates sends offsets to `t_x + Lx + c` and
only relabels lifted directions by the common shift `Ld`. It therefore
preserves the required coverage. This permits fixing `t_x=0` at an affine
basis of the active base support. The code does **not** fix the remaining
offsets independently.

## Tree-overlap precheck

Let `S_1,...,S_m` be the nonempty edge output sets for a residue direction,
and let `T=sum |S_i|`. For each pair calculate exactly

\[
\mu_{ij}=\min_h |S_i\cap(S_j+h)|.
\]

For every tree on the edge channels, successive union addition yields

\[
\left|\bigcup_i(S_i+h_i)\right|
\le T-\sum_{ij\text{ in tree}}\mu_{ij}.
\]

The maximum spanning tree gives the strongest bound of this form. A bound
below `|Q_d|` excludes every choice of the fibre offsets. The CNF still
encodes the original exact coverage clauses; no tree-bound axiom is inserted
into the saved refutations. Thus the SAT proofs provide a separate check of
the excluded fixtures.

## Saved fixtures and what they establish

| Case | Required directions | Result | Interpretation |
| --- | --- | --- | --- |
| Four three-point fibres, `n=2`, dual numbers | All 3 | UNSAT | Every local sumset-size bound passes, but shared translations are inconsistent. |
| Same shapes, `n=2`, `Z/4Z` | All 3 | SAT, 12 points | The carry changes the compatibility equations. |
| Four twelve-point fibres, `n=5`, dual numbers | `1,2,3` | UNSAT | A local three-direction obstruction; 4 RUP lemmas. |
| Same shapes, `n=5`, `Z/4Z` | `1,2,3` | SAT for those directions | 48 projective directions checked; this four-fibre set is not a full Kakeya set. |
| Fibre weights `2,16,2,16`, `n=5`, both rings | `16` | UNSAT | Two eight-class edge outputs always overlap in at least two classes, so their union has at most 14; 6 RUP lemmas in each ring. |
| Full hub star, `n=5`, both rings | All 31 | SAT, 94 points | Full positive control, 496 projective directions checked per ring. |
| Larger product-shaped controls, `n=5`, both rings | All 31 | SAT, 264 points | Nontrivial offset-solving positive controls with 2,800 variables and 15,342 clauses. |

For the two-dimensional four-three-point case, write each fibre as
`F2^2 \ {h_x}` and put `H = xor_x h_x`. Direct enumeration of all 256 hole
assignments finds none for the dual ring and exactly 64 for `Z/4Z`. In the
latter ring the necessary and sufficient condition is `H=3`. One witness has
holes `[0,0,0,3]`. The complete enumeration of two-dimensional translation
classes finds 135 completable families for the dual ring and 136 for `Z/4Z`.

The five-dimensional four-twelve-point block uses bases `0,1,2,3`, low-plane
triangle `{1,2,3}`, and the four high-coordinate planes

```text
H0 = {0,8,16,24}
H1 = {0,4,16,20}
H2 = {0,12,16,28}
H3 = {0,4,8,12}
```

Its fibres are `{1,2,3} + Hx`. Every two distinct listed planes span the
three-dimensional high space, and their union covers that space. Each of
the three tested directions has two eight-class outputs. The dual-ring
translation compatibility equations contradict one another even though
every individual direction can be completed. The result extends to a larger
family only when no additional base edge supplies any of those three residue
directions. The surrounding untested directions remain outside this local
certificate.

## Solve a new fixed-shape input

Only new solving requires PySAT. The tested version is pinned in
`requirements-solver.txt`:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements-solver.txt
.venv/bin/python translation_completion.py input.json output_directory --seconds 30
```

On Windows, use the virtual environment's `Scripts/python.exe` executable.
An input has the form:

```json
{
  "n": 2,
  "ring": "dual",
  "fibres": {"0": [1,2,3], "1": [1,2,3], "2": [1,2,3], "3": [1,2,3]}
}
```

The ring values are `dual` and `z4`. Optional
`"required_residue_directions": [1,2,3]` limits the obligation to the listed
directions. Omitting it requires every nonzero residue direction. Every saved
result explicitly states this scope. `UNKNOWN` is a time limit, not an
exclusion. A new `UNSAT` must have its saved proof independently replayed
before it is accepted as a certificate.

Run `validate_translation_completion.py` with the solver interpreter to
repeat the exhaustive encoder-versus-coordinate-enumerator audit. This is
separate from the default standard-library verification of the saved results.
