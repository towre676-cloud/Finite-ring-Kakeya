# Kakeya spectral and carry extension — v0.2

Open **Kakeya_Spectral_Carry_v0.2.html** for the complete offline monograph,
including the interactive four-frequency theorem. No server or internet
connection is needed. The Markdown source is `MONOGRAPH.md`.

## Main results

- An exact signed-Walsh realization criterion in every binary dimension.
- A complete dimension-four local classification: 5,227 square-spectral
  candidates, 1,260 explicitly characterized phase obstructions, and exactly
  3,967 realizable fibre types.
- A shared-period correction to the directional product bound, together with
  an explicit 128-member family of 24-point Kakeya sets without a full fibre,
  valid in both four-element rings.
- The uniform bound `(h-1)^2 >= 2^n-1` for the number of fibres larger than two
  in a configuration without a full fibre, and the sharp all-dimensional law
  when at most two fibres are larger than two.
- Complete standard-library finite proofs of the dimension-three minimum 22
  and unique extremal size profile. Each ring has 131,072 minimum sets.
- Exact carry-transfer equations, an all-dimensional gauge obstruction, and
  a proof characterizing all 64 mixed-only Kakeya subsets of the digit plane.
- Explicit length-three traces, an all-length carry recursion, the sharp first
  nonaffine trace at each prime, and an exact odd-prime length-three affine
  incidence census in every dimension.

## Verification

Python 3.10 or later is sufficient for the default and full verification.
No third-party package is required.

```bash
python verify_release.py
python verify_release.py --full
```

The default checks exact local spectra, subspace budgets, period capacities,
all 128 new constructed sets, the plane census, carry-transfer certificates,
stored SAT refutations, and a quick independent trace profile. It stages a
temporary copy so that the delivered receipts remain intact. Its logs and
summary are written under `verification_results/`.

The full mode also replays the standard higher-length arithmetic census and
the finite dimension-three lower-bound and equality-profile proofs. The
original runs of those two finite searches took about two and three minutes,
respectively. Search limits are explicit; reaching a limit is not a proof.

## Research programs

| Directory | Purpose |
|---|---|
| `extension/theory/` | General proofs, exact local classification, complete type table |
| `extension/gauge/` | Carry-transfer certificates, plane classification, concrete transfer |
| `extension/trace/` | All-length arithmetic, affine-trace classification and censuses |
| `extension/solver/` | Improved global models, finite proofs, SAT proof checker, constructions |
| `extension/baseline/` | Fresh replay of the uploaded notation checks |
| `kakeya_sharp/` | Original v0.1 source, preserved unchanged |
| `kakeya_tilt_notation/` | Original notation overlay, preserved unchanged |

For optional new optimization runs:

```bash
python -m pip install -r requirements-optional.txt
python extension/solver/spectral_relaxation.py 3 --mode EP --smax 7 --seconds 30
python extension/solver/certified_sat.py Z4 2 9 --prefix run_Z4_n2 --verify
```

The models are `T` (triangle defects), `S` (square spectra), `S4` (the exact
dimension-four phase condition), `E` (complete local subset types), and `EP`
(complete local types plus shared-period capacity). Every exported feasible
assignment is checked independently against its declared conditions.

## Scope and source reconciliation

The two source packages have different scopes. The notation overlay reports
the dimension-four value 46 by reference to an older 80-cube proof campaign;
its CNFs, refutation proofs and full checker are not present in these uploads.
This release preserves that attribution. It independently reconstructs the
local type foundation and the upper construction, while its own bounded
dimension-four global searches remain undecided.

The unrestricted dimension-five value and the all-dimensional sharp law
are not resolved here. The complete local classification does not by itself prove the
global Kakeya lower bound. The higher-length trace separation is a statement
about fixed Teichmüller digit geometry, not a claim that the Kakeya minima of
the two rings differ.

`INPUTS.json` records the uploaded archive identities by filename, size and
SHA-256. `MANIFEST.sha256` records the delivered files. The original inputs
were not modified; the additions are contained in `extension/` and the
top-level release files.
