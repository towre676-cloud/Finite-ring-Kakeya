Kakeya Complete Round5
=====================

START HERE

The principal new theorem is an unrestricted support exclusion:
in either four-element target ring, every dimension-five Kakeya set
with at most93 points has at least11 pair-active residue fibres.
The whole support10 branch is closed, without a largest-fibre cap.

Read research_round5/support10_roles/SUPPORT10_UNRESTRICTED_PROOF.md.
It uses a complete finite support classification and a short analytic
weight argument. It does not require the weight-profile census, the
old middle screens, or Claude's unavailable SAT encoder/proofs.

The unrestricted lower bound94 and the general formula3*2^n-2 remain open.

CURRENT STATE

- Maximum19: reported closed by the user's Claude session on the38
  inherited open support cases. Actual new CNFs/DRAT files were not
  available here, so this package does not claim to have checked them.
- Exact case universe independently established:13 marked support11
  classes and25 marked support12 classes. Complete coverage verified
  from296,010 normalized supports, with102,324 explicit transport witnesses.
- Maxima12..18:4,976 additional whole weight profiles excluded from the
  Round4 residual.270,779 necessary-condition weight profiles remain in
  48 nonempty support/maximum cells. Supports now begin at11.
- Maximum11:46 inherited affine support classes remain open.
- Fifteen new Lean coordinate/carry/line-to-pair theorems compiled.
- The mandatory proof-checking path uses the upstream verified CakeML
  artifact. Four archived Kakeya examples and acceptance controls pass.

IMPORTANT FILES

Kakeya_Research_Frontier_Round5.json
    Current machine-readable state and exact trust boundaries.
research_round5/Kakeya_Round5_Monograph.txt
    Updated1500-word explanation.
research_round5/CLAUDE_NEXT_STEP_HANDOFF.txt
    Concrete unsent handoff, including the new theorem and proof acceptance.
research_round5/support10_roles/SUPPORT10_UNRESTRICTED_PROOF.md
    Main new theorem, with all fibre weights allowed.
research_round5/encoding_bridge/ENCODING_AND_SYMMETRY_BRIDGE.md
    Exact ring semantics, affine normalization, marked-support contract.
research_round5/proof_audit/README_PROOF_AUDIT.md
    Ready-to-run proof gate, manifest schema, upstream provenance and limits.
research_round5/ROUND5_MERGED_REPLAY.json
    Exact disjoint exclusions and support/maximum counts.
research_round5/after_round5_survivors.txt
    Complete remaining normalized middle weight-profile list.

REPLAY

On Linux x86_64 with Python3 and a C compiler:

    python3 VERIFY_ROUND5.py

The default replay uses no network, SAT solver, optimizer, or Lean download.
The CakeML assembly is for x86_64; see its upstream distribution for ARM.
Python assertions are part of the checks: do not run with -O.

To also recompile the15 Lean theorems, provide the pinned local installations:

    python3 VERIFY_ROUND5.py --mathlib /path/to/mathlib --lean-bin /path/to/lean/bin

The exact Lean4.24.0 and Mathlib commit are recorded in the bridge receipt.
The completed Lean receipt is supplied even when the portable run skips Lean.
The whole new theorem is not Lean-formalized.

SOURCE AND PROOF PRESERVATION

Every entry of Kakeya_Complete_Round4.zip is preserved byte-for-byte inside
this archive. Older frontiers are historical; the Round5 frontier governs
the current counts. MANIFEST_ROUND5.json records all payload hashes and
the preserved prior-archive identity. Verify hashes before replay, since
replay intentionally rewrites elapsed-time receipts and generated ledgers.

The full upstream HOL4/CakeML proof development was not rebuilt here.
The published checker assembly hash was checked and the artifact built
locally. A stale upstream C-wrapper checksum is documented transparently.
The ordinary C LRAT utility is diagnostic only after a reproduced false
acceptance; the CakeML acceptance gate rejects the same bogus proof.

Multiple model agents and separately implemented checkers support
reproducibility. They are not independent human reviewers. Weight-profile
counts, affine support classes and Claude's8904 SAT cases are different
inventories; do not add or subtract them from each other.
