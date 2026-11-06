ROUND 6: FRESH CERTIFICATES FOR THE EXACT IMPORTED MAXIMUM 19 ENCODER
=================================================================

Read M19_COMPLETE_CERTIFICATION_RECEIPT.json and M19_FRESH_REPLAY.json for
completion status and measured timings. A file or status marked RUNNING is
not a completed exclusion. The mathematical interpretation is reviewed
separately in research_round6/encoder_audit.

Why this work was necessary
--------------------------
The uploaded Kakeya_Round4_Handoff.zip contained the current encoder, data,
and historical certification receipts. It contained neither the original
38 CNFs nor their DRAT proofs, and did not include the earlier encoder
revision that produced those recorded CNF hashes. The historical receipts
therefore could not be independently replayed from the uploaded files.

This work regenerates each CNF from the exact supplied encode_cnf2.py,
solves it afresh, and preserves the complete refutation. It does not assume
that the unavailable earlier encoder is equivalent to the supplied one.
No original historical proof is claimed to have been checked here.

Exact scope
-----------
Maximum fibre 19, total size at most 93, and pair-active support size 11 or 12.
The hub is distinguished and placed at residue zero. Tied maximum fibres
are permitted. Outer fibre weights range from 2 through 19. No outer-weight-14 cap
is imposed. There are 13 marked support-11 classes and 25 marked support-12
classes. Explicit invertible transports bind every imported representative
to the complete independently enumerated Round 5 contract.

The common necessary-condition relaxation applies to both Z/4Z and the
dual numbers F2[e]/(e^2), subject to the separate mathematical and encoding
soundness argument. An exact CNF refutation proves the encoded necessary
conditions inconsistent; it does not by itself prove their correctness as
conditions on Kakeya sets.

Authority and trust
-------------------
The untrusted solver used here is the installed CaDiCaL 2.1.2 executable.
It writes original ASCII DRAT proofs directly to disk. Pinned upstream
DRAT-trim converts each proof to LRAT. The pinned upstream CakeML checker
artifact must then accept that LRAT against the SAME ORIGINAL CNF.
The required output is exactly "s VERIFIED UNSAT", with zero exit status
and empty stderr. All input, converted-proof, and log hashes are retained.

The ordinary C LRAT checker is not an acceptance authority. No custom
Claude checker is needed for these fresh certifications. Details and pinned
upstream sources are in research_round5/proof_audit. The upstream HOL4 and
CakeML proof development was not rebuilt in this session.

Contents
--------
CASE_UNIVERSE.json: complete 38 imported-to-contract mappings and old logs.
BUILD_RECEIPT.json: exact solver binary and checker source/build provenance.
cases/CASE_ID/input.cnf[.xz]: exact original CNF, retained losslessly.
cases/CASE_ID/proof.drat[.xz]: original fresh DRAT refutation.
cases/CASE_ID/audit/converted.lrat[.xz]: checked LRAT refutation.
cases/CASE_ID/CASE_RECEIPT.json: hashes, timings, and checker outcomes.
M19_CERTIFICATE_MANIFEST.json: exact 38-case inventory and semantic-source hashes.
M19_COMPLETE_CERTIFICATION_RECEIPT.json: aggregation of the checked evidence.
M19_FRESH_REPLAY.json: fresh full proof replay plus exact CNF regeneration.

Replay without SAT search
-------------------------
From the complete package root:

  python3 research_round6/certification/verify_m19_certificates.py

Requirements: Python 3, gcc or compatible C compiler, Linux x86_64. No PySAT,
network access, or SAT solver is needed. The script checks all input hashes,
the exact 38-case support contract, and all semantic-source hashes. It regenerates
every precise CNF from the declared support and maximum and requires byte
identity. It then rebuilds and runs CakeML against every preserved CNF/LRAT.
Compressed .xz siblings supply the same logical bytes whenever the raw file
is absent. Every original uncompressed SHA256 is checked. At most one case
is decompressed at a time. Use --compressed-only to require .xz input even
when raw copies are present. The delivered package may contain only .xz
copies of large certificates; no proof content is omitted by compression.

To also repeat the DRAT-to-LRAT conversion:

  python3 research_round6/certification/verify_m19_certificates.py --convert-drat

That optional route writes fresh LRAT copies beneath fresh_replay; it needs
additional disk space. The default route already independently establishes
UNSAT against the original formula from its preserved LRAT refutation.

To regenerate all search proofs with a specified installed solver:

  python3 research_round6/certification/regenerate_and_check.py --solver /path/to/cadical --jobs 2
  python3 research_round6/certification/finalize_certificates.py

The generation driver resumes only after checking the original CNF/DRAT
and converted LRAT hashes of completed cases. Its default solver path is
specific to the producing environment; supply --solver on another machine.
The finalization script aggregates completed per-case checks and validates
the full mapping. It does not substitute for fresh proof replay.

Limits
------
These 38 cases alone do not exclude maximum 19 on other support sizes. The
profile-level consequence for all 3,798 inherited maximum 19 profiles also
uses the inherited support-11/12 reduction. No unrestricted dimension-5
lower bound 94 or all-dimension formula is claimed by this certificate set.

Integrity incident during production
------------------------------------
The final hash gate detected one stored DRAT file truncated after its earlier
acceptance. Its CNF and already checked LRAT still matched their hashes. The
cause is undetermined. The case was solved again with the same encoder and
solver, restoring exactly the original DRAT SHA256 and byte length; both
DRAT-trim and CakeML accepted again. All 38 final bindings then passed.
An incident record is retained in integrity_incident/INTEGRITY_INCIDENT.json.
No hash mismatch was waived. Compressed files are round-trip verified and
published atomically only after the writer closes. The final compressed
replay checks actual decompressed bytes and reruns the required checker.

Optional LRAT-only distribution
-------------------------------
If a distribution contains exact CNFs and checked LRATs but omits redundant
original DRAT search traces, run:

  python3 research_round6/certification/verify_m19_certificates.py --lrat-only

The same exact 38-case inventory, semantic-source hashes, byte-identical CNF
regeneration, CNF/LRAT hashes, and mandatory CakeML checks remain in force.
Only the original DRAT file is optional in this mode. Its recorded hash is
retained as provenance, and the fresh receipt explicitly says those search
trace bytes were not checked in that replay. The preserved LRAT itself is
a complete, separately checkable UNSAT proof for the original CNF; the
solver's discarded search history is unnecessary for that conclusion.
--lrat-only cannot be combined with --convert-drat. See the complete package
README for which distribution scope was selected.
