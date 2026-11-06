Maximum-19 compact replay: exact CNFs and original DRAT proofs
=============================================================

This is a smaller representation of the same 38 accepted formulas. No new
mathematical exclusion or encoder change is introduced by this packaging.
Here "original DRAT" means the fresh solver output from the exact-encoder
recertification in this session. The unavailable historical Claude proof
bytes are not claimed to have been recovered or checked.

The payload consists of the original exact CNFs and original DRAT proofs,
stored losslessly as .xz files beneath research_round6/certification/cases.
Their combined compressed size is 156,822,792 bytes. Original LRAT payloads
are unnecessary: the replay reconstructs LRAT from each supplied DRAT, then
requires acceptance by the pinned upstream CakeML checker against the SAME
ORIGINAL CNF. The reconstructed LRAT exists only in a private temporary
directory, so replay does not accumulate a second large proof collection.

Run from the package root:

  python3 research_round6/compact_m19/verify_compact_m19.py --jobs 2

A diagnostic two-case run is available:

  python3 research_round6/compact_m19/verify_compact_m19.py --jobs 1 --quick

Quick mode explicitly certifies only two cases and cannot produce the full
38-case success status. The default without --quick checks every case.
Requirements are Python 3, a C compiler, and Linux x86_64. No SAT solver,
PySAT installation, or network access is required. Checker sources and
licenses are inherited from the complete Round 5 proof-audit package.

What the full replay checks
---------------------------

* The compact manifest is bound to the exact original manifest hash.
* Its inventory is exactly all 13 marked support-11 classes and all
  25 marked support-12 classes, with explicit invertible affine transports.
* The original encoder, data tables, and mathematical method source have
  their declared hashes. The exact original encoder is used directly.
* Each declared support and maximum regenerate a byte-identical CNF.
* Each original CNF and DRAT has its declared uncompressed SHA256, even
  when only the lossless .xz representation is supplied.
* Pinned DRAT-trim must validate the original DRAT and reconstruct LRAT.
* Pinned CakeML must accept that reconstructed LRAT against the same CNF.
  Its exact success output, exit code, and empty stderr are required.
* Persisted CNF and DRAT hashes are checked again after proof acceptance.
* The final successful full receipt requires all 38 exact case identifiers.

Only checker transcripts, hashes, and case receipts leave the private
working directories. No original certificate is edited or deleted.
The converter and solver are not acceptance authorities. This script never
opens an original LRAT payload; the old LRAT hash is retained only as
provenance. The new reconstructed LRAT's actual hash is recorded separately.

Key records
-----------
COMPACT_M19_MANIFEST.json: exact input, support, and provenance bindings.
COMPACT_M19_REPLAY.json: full replay status, case results, and checker pins.
COMPACT_M19_QUICK_REPLAY.json: separate two-case diagnostic receipt.
replay_logs/CASE_ID/: fresh checker transcripts and case receipts.

The final status for a completed full run is:

  PASS_ALL_38_EXACT_CNF_DRAT_CAKEML_CERTIFICATES

A timeout, source/hash mismatch, missing case, missing success marker, or
checker failure cannot produce that status. A new run first replaces its
receipt with RUNNING; failures replace it with FAIL. An old successful
receipt cannot stand in for the current invocation.

Mathematical scope
------------------
Maximum fibre exactly 19, at most 93 total points, and pair-active support
11 or 12. Tied maximum fibres are allowed, and no outer-weight-14 cap is
imposed. The common necessary-condition encoding applies to both rings,
subject to the separately documented mathematical and encoding soundness
argument. This replay does not formally prove that argument. The overall
maximum-19 closure continues to use the inherited reduction to supports
11 and 12. The unrestricted lower bound of 94 remains open.

Completed production replay
---------------------------
The initial full compact replay passed all 38 cases on the final guarded
code in 488.065809 seconds using one worker. It read no original LRAT
payloads. The same run also reproduced all 38 previously accepted LRAT
SHA256 hashes. COMPACT_M19_SUMMARY.json records these measured results.
The representation saves 158,893,244 compressed bytes compared with keeping
the original CNF and LRAT payloads, with no change to the encoded formulas.
