# Kakeya Round 9 — recovery completed

All 27 previously reported successful cases have been regenerated and independently rechecked. All 54 prepared cases were rerun and their exact CNFs regenerated. The recovery produced two additional accepted cases: masks 110453014 and 360808918, each at exact maximum 13.

| Exact maximum | New checked marked exclusions | Covered marked cases, including 28 inherited | Remaining roles | Complete affine classes |
|---|---:|---:|---:|---|
| 12 | 13 | 41 / 55 | 14 | 97, 98, 103, 104, 105, 107, 108 |
| 13 | 16 | 44 / 55 | 11 | 97, 98, 103, 104, 105, 106, 107, 108, 112 |

The formulas are common necessary conditions for both Z/4Z and F2[epsilon]/(epsilon^2), in dimension five, total size at most 93, pair-active support 13. Ties for the largest fibre are permitted. Whole affine-class closures combine new checked certificates with inherited certificates after checking all 169 largest-fibre transports. Inherited proof streams remain in the saved Round 8 archive and are not freshly rechecked in this continuation.

## What was recovered and what was regenerated

The 47 required original source/data/checker dependencies match the saved Round 8 archive byte for byte. The original truncated integrity-test CNF and its complete version were reconstructed and match both hashes recorded before the loss. Historical producer, resume, worker, replay and packaging source programs were reconstructed from the tool-input text retained in this conversation. No old source-file hash list survives to independently prove their byte identity.

The 54 case formulas, 29 proof streams, execution logs and receipts are newly generated replacements. All 27 original successful cases are included. Original experimental timing logs and proof-file byte identity cannot be recovered or claimed. New timing logs are retained. This package restores the mathematical results with reproducible evidence; it does not pretend every deleted temporary byte was undeleted.

RECOVERY_ORIGIN.txt is the earlier loss-time record. Its statement that no Round 9 certificate package existed is superseded by this recovered release and the completed VERIFIED_FRONTIER.json.

## Verification

On Linux x86_64 with Python 3 and gcc (Windows users can use an appropriate WSL2 Linux environment):

```bash
python3 research_round9/recover.py replay --jobs 2
```

This requires no SAT solver installation or network. It decompresses and hashes every exact input, regenerates every CNF, reconstructs LRAT from every accepted DRAT proof and requires acceptance by the pinned CakeML checker. It verifies all 54 case scopes and all 169 hub transports. Run without -O.

The completed recovery used research_round9/verify_reconstruction.py. Its source hash, all semantic source hashes, exact counts and composed frontier are in research_round9/VERIFIED_FRONTIER.json. Production and fresh checker build receipts are retained. The ordinary C LRAT utility is diagnostic only.

## Files

- research_round9/cases/: all 54 exact CNFs, 29 complete refutations, search logs and checked receipts.
- research_round9/fresh_replay/: fresh independent checking receipts for accepted proofs.
- research_round9/REMAINING_CASES.json: all 25 timeouts, with exact scope and formula hashes.
- research_round9/historical_source_reconstruction/: source recovered from conversation tool inputs.
- research_round9/historical_integrity_incident/: hash-matched integrity-test bytes.
- SOURCE_RESTORATION.json: original dependency comparisons.
- RECOVERY_COMPLETENESS.json: precise recovery inventory and limitations.
- PAYLOAD_SHA256.json: archive payload hashes.

## Mathematical boundary

The unrestricted n=5 lower bound 94 and the all-dimensional formula remain OPEN. No whole weight profiles were subtracted: the tracked 182526 middle-maximum profiles and 42 maximum-11 affine classes remain unchanged. The entire normalization, census and Python encoder are not jointly formalized in a proof assistant. The reviewed one-way soundness argument supplies the interpretation of the checked CNF refutations.
