KAKEYA ROUND-2 PROOFS AND EXACT EXCLUSIONS

The unrestricted conjecture k(R,n)=3*2^n-2 remains OPEN for both
R=Z/4Z and R=F2[epsilon]/(epsilon^2). The dimension-five target is94.

Read Kakeya_Research_Round2_Report.txt for the mathematical narrative and
Kakeya_Research_Frontier_Round2.json for the precise frozen ledger.

This package contains the new analytic proofs, complete census data, exact
integer certificates, source code, survivor lists, and frozen prior inputs
required to replay the new work. The old full checkpoint remains the source
for inherited theorems and older profile-census provenance; its identity and
SHA256 appear in the report and frontier.

REPLAY

1. Extract this archive into a fresh writable directory.
2. Install/use Python3 and a C++17 compiler available as g++.
3. Run: python3 VERIFY_ALL.py

No third-party Python package, optimizer, OpenSSL, network connection, or
previous workspace directory is needed by this default verification path.
Some optional producer sources use OpenSSL; they are not called by this path.
Do not run Python with -O: the exact checkers use assertions.

The runner first checks every payload SHA256 and byte count against
MANIFEST.json. It then compiles the independent census checkers and replays
all15 verification/accounting steps. Logs appear in verification_logs/ and
the final result in VERIFICATION_RECEIPT.json.

Some checkers regenerate receipts, including timings. For another pristine
hash-checked replay, extract the archive again. A second run in a modified
copy may correctly fail the initial hash check.

SCOPE

The new M11 support reduction closes73 of the previous130 affine-support
classes, leaving57. The earlier59-class stage is contained in these73.
The middle support theorem excludes every support19 through32 profile for
maxima12 through18. The new M19 stages exclude38,734 tracked profiles, leaving
30,471. Counts use different mathematical objects and must not be summed.

The file ROOT_ANALYTIC_PROOF_REVIEW.txt records proof review. The replay
checks finite enumerations, integer inequalities, source identities and
accounting; it does not substitute for reading the analytic proofs and is
not a formal proof-assistant certification. Numerical survivors are necessary
data, not constructed Kakeya sets.
