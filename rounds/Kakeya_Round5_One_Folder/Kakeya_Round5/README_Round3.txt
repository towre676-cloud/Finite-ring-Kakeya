KAKEYA RESEARCH ROUND 3 — VERIFIED CHECKPOINT

Read Kakeya_Research_Round3_Report.txt for the requested1500-word account
(whitespace-delimited count, including headings and the displayed formula).
Read Kakeya_Research_Frontier_Round3.json for the exact current status.

Accepted new frontier, both rings in dimension five, hypothetical size<=93:
  Maximum11: pair-active support<=16;46 remaining affine support classes.
  Maximum12..18: pair-active support<=17; all support18 partitions excluded.
  Maximum19:3798 tracked profiles remain,896 at support11 and2902 at12.
The unrestricted94 lower bound remains OPEN.

New conditional all-dimension result:
  For n>=6, a full residue fibre and all outer fibres of size<=12 force
  |K|>=3*2^n-2, with equality exactly for generalized stars.

The principal new analytic tools are the cube-direction/residual-energy
inequality, shared own periods, rooted affine-rank capacity bounds,
forced-period eight-point energy rigidity, and actual-support Hall roles.

REPLAY

Unpack into a new writable directory and run ordinary Python3 without -O:

    python3 VERIFY_ROUND3.py

The replay requires Python's standard library and a C++17 g++ compiler for
the inherited independent census enumerators. It requires no optimization
solver or third-party Python package. Optional producer scripts are supplied
for transparency and may have additional dependencies; they are not called
by the verification entry point.

The entry point verifies every archived payload hash, reruns the included
round2 verification chain, checks the caught-up compatibility archive,
replays every credited new exclusion stage, and regenerates the frontier.
The scripts write receipts and logs in the extracted copy. The initial
payload manifest describes the files before those timing-bearing receipts
are regenerated. Use another fresh extraction for a repeat integrity check.

An archive-wide manifest and per-stage hashes record provenance. The archive
contains the unchanged round2 payload and all needed new proof/certificate
inputs. Earlier unrestricted strata exclusions and small-dimensional minima
remain inherited from the older checkpoint identified in the round2 ledger.

The catch-up compatibility package's STATUS.json is historical. Current
counts are exclusively those in Kakeya_Research_Frontier_Round3.json.
Uncredited pilot screens and exploratory cube-joint data are omitted.

Proof documents are mathematical arguments reviewed independently within
this research session; arithmetic replays are exact finite checks. This is
not a proof-assistant formalization or external peer review. Surviving
necessary-condition profiles are not Kakeya constructions.

MAIN PROOF PATHS

research_round3/m11/M11_SUPPORT_SEVENTEEN_EXCLUSION.md
research_round3/m11/s16/M11_SIX_SUPPORT16_CLASS_EXCLUSIONS.md
research_round3/middle/MIDDLE_SUPPORT_AT_MOST_SEVENTEEN.md
research_round3/middle/CUBE_ENERGY_SUPPORT18_EXCLUSIONS.md
research_round3/m19/M19_ROUND3_FINAL_MANIFEST.json
research_round3/m19/UNIQUE_EDGE_ROLE_PROOF.md
research_round3/root/SHARED_PERIOD_AND_ROOTED_RANK_THEOREMS.txt
research_round3/root/FULL_HUB_OUTER_TWELVE_THEOREM.txt
research_round3/root/ROOT_ANALYTIC_REVIEW_ROUND3.txt

REMAINING CASES

M11 class IDs: Kakeya_Research_Frontier_Round3.json.
M11 support16 weights: research_round3/m11/s16/S16_INDEPENDENT_REPLAY.json.
M19 profiles: research_round3/m19/s11_final_round3_survivors.txt and
research_round3/m19/s12_final_round3_survivors.txt.
Middle supports17 and below remain open, subject to earlier selected cuts.
