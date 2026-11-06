# Dense-fibre encoder: completed bounded tests

**The two local models are implemented and pass exhaustive constructive validation. No new support exclusion or search-speed benefit was obtained from the dense-only trials.**

| Marked support | Mode | Limit | Solve time | Status | DRAT bytes |
|---:|---|---:|---:|---|---:|
| 1022358 | baseline | 60 s | 60.073 s | Timeout; uncertified | 124,734,531 |
| 1022358 | dense | 60 s | 60.075 s | Timeout; uncertified | 162,242,157 |
| 37848950 | baseline | 30 s | 3.806 s | CakeML accepted | 19,246,275 |
| 37848950 | dense | 30 s | 6.608 s | CakeML accepted | 45,219,591 |
| 75737494 | dense | 30 s | 30.243 s | Timeout; uncertified | 97,898,036 |

The baseline and dense proofs for T37848950 cover the same already-certified mathematical case. They add zero new marked-case exclusions. The stronger formula was slower and produced a larger proof in this smoke test. Both formulas timed out on T1022358. T75737494 also timed out with the dense rows; its separate baseline survey had timed out at the same thirty-second limit. Single runs shared the environment and are not controlled general performance measurements.

All completed refutations passed the pinned DRAT-trim-to-LRAT-to-CakeML chain against their exact formula. Unfinished traces were hashed for provenance and discarded; none is an exclusion. Exact formula bytes, completed proofs, checker logs and production receipts are in ../variant_cases. The generic variant replay binds their formulas and semantic source hashes.

The local replay checked all 6,188 four-/five-point complements in a four-flat, every 5,208 labelled weight-eleven circuit profile and 3,255 weight-twelve J,u profile, all 8,463 explicit clause assignments, 64 arbitrary inactive-gate assignments, six incorrect witnesses and 21,625 input-plus-auxiliary truth-table assignments across 22 small Boolean primitive instances. Disabling the new rows reproduces the frozen baseline byte-for-byte. These are mathematical/code and finite checks, not proof-assistant formalization.

Recommendation: preserve these exact local models for targeted branches and for a fuller geometric encoder. The present evidence does not justify enabling them globally as a speed optimization.
