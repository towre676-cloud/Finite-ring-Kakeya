# Dimension-four checkpoint with compact, checked proofs

**The dimension-four lower bound of forty-six is still open in this
checkpoint.** The complete bounded search produced fourteen checked
refutations and forty-two timeouts. No satisfiable instance or actual
counterexample was found.

The fourteen refutations exclude every pair-active support of size six,
seven or eight in both rings, and two of the six marked support classes
of size nine in both rings. Thus any Kakeya set of at most forty-five
points must have at least nine pair-active residue fibres. Four marked
size-nine classes and all larger support classes remain unresolved.

## What is exhaustive

`../dimension4/catalogue_dimension4.py` enumerates every one of the
$2^{15}=32,768$ binary supports containing the marked largest-fibre
residue zero. Twelve elementary transvections generate all 20,160
elements of $\mathrm{GL}(4,2)$. Breadth-first orbit enumeration gives
forty-six marked subset classes, twenty-eight of which cover all fifteen
nonzero binary directions. The archive contains explicit linear
transports for all 32,768 supports. An independent Burnside count from
the complete group's cycle polynomials reproduces the orbit counts by
support size.

The covering classes, and the resulting exact two-ring case inventory,
are:

| Support size | Marked classes | Ring cases | Checked UNSAT | Timeouts |
|---:|---:|---:|---:|---:|
| 6 | 1 | 2 | 2 | 0 |
| 7 | 2 | 4 | 4 | 0 |
| 8 | 2 | 4 | 4 | 0 |
| 9 | 6 | 12 | 4 | 8 |
| 10 | 5 | 10 | 0 | 10 |
| 11 | 4 | 8 | 0 | 8 |
| 12 | 3 | 6 | 0 | 6 |
| 13 | 2 | 4 | 0 | 4 |
| 14 | 1 | 2 | 0 | 2 |
| 15 | 1 | 2 | 0 | 2 |
| 16 | 1 | 2 | 0 | 2 |
| **Total** | **28** | **56** | **14** | **42** |

Supports of size at most five have at most ten edges and cannot cover
the fifteen nonzero residue directions. The two rings are
$\mathbb Z/4\mathbb Z$ and
$\mathbb F_2[\epsilon]/(\epsilon^2)$.

## Exact formula and validation

Each formula uses actual membership variables for the sixteen possible
points in every residue fibre. Pair indicators and lifted-direction
coverage are exact. The carry is included explicitly for
$\mathbb Z/4\mathbb Z$. The formula enforces total size at most
forty-five and chooses residue zero as a largest fibre of size between
two and sixteen. It uses the common affine tangent shear to put zero
in the five affine-basis anchor fibres; it does not independently
translate every fibre. This is the frozen exact-ring encoder used in
the dimension-two and dimension-three certifications, with no
fibre-spectrum census dependency.

All fifty-six cases received a twenty-second solver limit, using one
solver process. The original accepted proofs were checked by a pinned
DRAT-to-LRAT-to-CakeML chain. Timeout traces were hashed and discarded;
they provide no exclusion. The explicit forty-six-point star was
checked directly against literal ring lines and against all clauses in
the corresponding formula, in both rings.

## Why compact proofs preserve the result

The files in `cases/` replace only proof payloads. For every one of the
fourteen accepted cases, the producer regenerated the original CNF
byte for byte, trimmed the old DRAT, then ran a fresh mandatory
DRAT-to-LRAT-to-CakeML check of the compact proof against that same
original CNF. No clauses or mathematical assumptions were added.
Original artifacts were kept unchanged during production.

The frozen compact manifest binds the complete original case inventory,
source hashes, exact CNF and proof hashes, individual production
receipts, and unchanged scope. The portable replay requires the compact
proofs and the original compressed CNFs and receipts. It does not open
or require the original dimension-four DRAT payloads.

From the archive root, run:

```bash
python3 research_round7/dimension4_compact/compact_dimension4.py --replay
```

This rebuilds the pinned checkers, reproduces the full support catalogue
and the forty-six-point star, regenerates all fifty-six CNFs, and checks
all fourteen compact proofs. The forty-two timeout cases receive only
a formula-regeneration receipt and explicitly no exclusion credit.
`COMPACT_DIMENSION4_REPLAY.json` records the result. A `--quick` replay
is only a smoke check and does not establish the full inventory.

The formula's equivalence to the actual Kakeya problem is supported by
the written exact-ring proof and finite validations. The Python encoder
is not a proof-assistant formalization. The CakeML checker certifies
the refutations of the exact CNF bytes supplied to it.
