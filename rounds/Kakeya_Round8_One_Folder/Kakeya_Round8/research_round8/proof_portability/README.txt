Completed fresh-extraction proof replay
======================================

This directory preserves the successful full replay of all four new
compact refutation proofs after extracting an earlier Round8 package
into an empty temporary directory. Every exact CNF was regenerated;
DRAT-trim reconstructed LRAT and the pinned CakeML checker accepted it.

The later incidence and price extensions changed the middle-profile
ledger, not those four CNFs, compact proofs, encoders or mathematical
scopes. The final archive checker explicitly verifies that these proof
files and all semantic source hashes agree with this completed replay.

The profile counts in this historical replay precede the later stages.
The current count is 950 cumulative exclusions and 182526 survivors,
as recorded in the main Round8 ledger and final profile certificate.

The ordinary command python3 VERIFY_ROUND8.py freshly checks all four
proofs and all current finite results. Its optional explicit reuse mode
binds the completed proof receipts and reruns the current finite results.
The receipt records which mode was used and which stages completed.
