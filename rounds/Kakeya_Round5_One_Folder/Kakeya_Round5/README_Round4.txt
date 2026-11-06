KAKEYA RESEARCH — ROUND 4
28 October 2026

The unrestricted dimension-five lower bound94 and the general formula
3*2^n-2 remain OPEN for this project. This archive contains partial theorems,
explicit exclusions, and exact replay material, with their scopes stated.

START HERE

1. Kakeya_Research_Round4_Report.txt gives the substantive audit response and
   the mathematical direction of the continuation.
2. research_round4/Kakeya_Round4_Monograph.txt is the updated exactly1500-word
   account for mathematically curious outsiders, with selective emphasis.
3. Kakeya_Research_Frontier_Round4.json is the current authoritative ledger.
   Older reports and ledgers are preserved as historical checkpoints.

WHAT CHANGED

* Q(A)<=300 for every twelve-point binary set now has an analytic proof.
  Equality is exactly an affine four-flat minus an affine plane. A separate
  implementation checks230560 normalized sets, including rank5 maximum222.
* All2163945 normalized middle weight profiles on supports10..17 and maxima
  12..18 are inventoried. The final certified residual is275755 profiles.
* The exact maximum18 branch now has support at most16. The other55 middle
  support/maximum cells still have relaxation survivors.
* A common embedded-type IP/LP model and exact rational certificate checker
  are implemented and tested on complete dimension-two domains. The global
  dimension-five type model has NOT been solved or exhaustively instantiated.
* Thirteen finite-incidence and algebraic statements compile in pinned Lean.
  Geometric bridges, the energy theorem, and the complete Kakeya reduction
  are explicitly outside that formalization.

FINAL MIDDLE FILES

  research_round4/middle_inventory/after_priced_nine_survivors.txt
  research_round4/middle_inventory/MIDDLE_FINAL_FRONTIER_AFTER_PRICING.json

The276267-profile after_cube list and MIDDLE_COMPLETE_INVENTORY.json are a
frozen preceding stage. The priced stage removes another512 profiles. The
older file named final_weight_survivors.txt is earlier still, before the
joint-cube stage; it is not the final Round4 ledger.

REPLAY

With Python3 and a C++17 g++ compiler, from the extracted archive root:

  python3 VERIFY_ROUND4.py

This verifies initial payload hashes, recomputes the relevant finite input
census and all new finite stages, checks exact stage accounting, and records
a replay receipt. It needs no floating-point optimizer or network access.
The prior complete Round3 replay is available separately:

  python3 VERIFY_ROUND4.py --with-round3

The Lean project is in research_round4/lean. See README_LEAN.md there for
pinned installation and reproduction. The default portable finite replay
does not silently install Lean or claim to have rerun it. Its actual compiled
receipt and source are included with the explicit formal scope.

VERIFICATION LANGUAGE

Separate implementations and model-agent cross-checks support reproducibility.
They are not independent human review or external peer review. The analytic
proofs are supplied in full for mathematical review; the entire research
program is not formalized in a proof assistant.

The archive preserves every entry of the earlier Round3 proof archive
byte-for-byte. That includes the earlier caught-up research records and
compatibility package. It does not claim access to every unseen conversation.
MANIFEST_ROUND4.json hashes the complete delivered payload, excluding itself.

PRIMARY PROOF AND CODE MAP

  research_round4/energy12/ENERGY12_ANALYTIC_PROOF.md
  research_round4/middle_inventory/MIDDLE_INVENTORY_PROOF.md
  research_round4/middle_inventory/PRICED_NINE_HEAVY_PROOF.md
  research_round4/optimization/M18_SUPPORT17_BOUNDARY_PROOF.md
  research_round4/optimization/TYPE_MODEL_AND_CERTIFICATES.md
  research_round4/lean/CubeMaster.lean
  research_round4/lean/README_LEAN.md

The support maximum11 branch remains46 affine support classes; maximum19
remains3798 tracked weight/own-direction profiles. These count different
objects from the middle weight inventory and must not be added together as
a measure of how much of the conjecture is complete.
