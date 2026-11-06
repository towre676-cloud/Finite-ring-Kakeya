# Compact certificates for the 38 joint maximum cases

**All 38 certificates have been converted to standard DRAT and accepted again through DRAT-trim followed by the mandatory CakeML checker.** This changes the distributed representation of existing certificates. It adds no exclusions and changes no mathematical scope.

The cases cover the same 13 marked support-eleven cases and 25 marked support-twelve cases as `joint_maxima/JOINT_CERTIFICATE_MANIFEST.json`, with maximum fibre size in `[2, 18]` and total size at most 93. The formulas encode common necessary conditions for both rings. The mathematical justification of those conditions and the encoder's faithfulness remain separate from propositional proof checking.

## Size and provenance

| Representation of the same 38 cases | Bytes |
| --- | ---: |
| Original solver LRAT streams | 11,925,732,987 |
| Previously accepted LRAT cores | 7,604,741,883 |
| Those cores compressed with ordinary XZ | 481,732,272 |
| Complete compact DRAT streams | 953,890,333 |
| Complete compact DRAT streams compressed with ordinary XZ | **109,808,024** |

The compact proof payload is about 104.72 MiB. It saves 371,924,248 bytes, or 77.2%, relative to the compressed LRAT cores. These figures exclude the exact CNFs, source code, manifests and logs. The original proofs and original CNFs were preserved during conversion.

LRAT explicitly records clause identifiers and propagation hints. Standard DRAT records clause additions and deletions without those hints. `lrat_to_drat.cpp` reconstructs every emitted deletion from the active indexed clause database and preserves addition literal order, including each RAT pivot. It rejects output paths that alias either original input. The converter is an **untrusted producer**: its output is accepted only after the fresh proof-checking route succeeds against the unchanged original CNF.

The full production receipt is `COMPACT_BATCH_RECEIPT.json`. It records 38 accepted cases and 858.43 seconds of elapsed batch time. Two disjoint helper groups completed and joined before the final manifest was published; the main producer incorporated their results through its exact-hash resume checks. Each case folder contains its accepted compressed DRAT, production receipt and checker logs.

## Portable replay

From the project root:

```bash
python3 research_round6/compact_certificates/verify_compact_certificates.py --jobs 2
```

For a short installation check:

```bash
python3 research_round6/compact_certificates/verify_compact_certificates.py --jobs 1 --quick
```

The quick mode checks one small case from each support size. **It is not a full replay of the 38 certificates.** The root `VERIFY_ROUND6.py` includes the complete compact replay in its full mode.

Portable replay requires the exact CNFs, these compact DRAT files, the retained source code and pinned checker sources. It does not require the old dense LRAT streams or the old compressed LRAT cores. The reusable `proof_core/verify_cores.py` module is a code dependency; its old proof payloads are not replay inputs. The producer script, by contrast, needs the old accepted cores if one wants to reproduce the conversion itself.

For every case the portable verifier:

1. Checks the complete case inventory, marked-support transport witnesses, authoritative joint manifest hash and semantic source hashes.
2. Regenerates the CNF from the pinned encoder and data and requires its byte hash to match the authoritative original formula.
3. Checks the compressed DRAT hash and the decoded DRAT hash and size.
4. Runs pinned DRAT-trim to reconstruct a fresh LRAT proof in a private temporary directory, then requires fresh CakeML acceptance against that exact CNF.
5. Rechecks the persisted proof and CNF hashes after checking and writes a new replay receipt.

The verifier resets its receipt before preflight. A missing manifest, changed source, invalid resource limit, failed checker or timeout cannot leave an earlier PASS as the current result. The converter and DRAT-trim do not become trusted mathematical authorities: the reconstructed proof must pass the mandatory checker. This does not constitute formal verification of the Kakeya reduction or the CNF encoder.

## Controls and integrity

`verify_conversion_controls.py` exercises nine controls, all recorded as passed in `COMPACT_CONTROL_REPLAY.json`: three preflight stale-receipt controls; conversion and acceptance of a genuine RAT example containing negative hints; rejection of a bogus proof for a satisfiable formula; and four direct-path or hardlink protections for original CNF and LRAT inputs.

`COMPACT_CERTIFICATE_MANIFEST.json` is published only after the full production inventory is complete. It binds each proof to its original CNF, source-core provenance, production receipt and the original joint manifest. Recorded acceptance is not substituted for fresh checking by the portable replay command.
