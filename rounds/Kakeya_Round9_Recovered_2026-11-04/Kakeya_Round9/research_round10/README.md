# Round 10 review: exact dimension-five Kakeya exclusions

Base repository commit: `de29e4473bfe4c46a90ccb85a33ad44b7a203caa`. Prepared November 8, 2026.

**25 newly excluded marked cases; 0 remain from the original 25-case queue.**
New exclusions at exact maximum 12: 14. At maximum 13: 11.
Remaining at exact maximum 12: 0. At maximum 13: 0.

## Scope and correction

Every result concerns the common necessary relaxation for both rings, binary dimension five, pair-active support 13, total at most 93, and hub 0 of exact maximum 12 or 13; largest-fibre ties are permitted.
The four proposed cuts were already present in every recovered CNF. The queue's nested pending/new-cut fields were historical metadata. All 25 old formulas were regenerated with matching hashes. No recovered Round9 file was changed.

## Mathematical and code changes

See `SOUNDNESS.md` for the proofs and precise CNF clauses. The heavy threshold is four. The established consequences are h>=10, 3|M|<=L2+2L3, and h>=11 implies full difference coverage. The tetrahedral capacity-14 bound is conditional on the audited nonplanar type flags, not every four-pair endpoint.

`encode_projected.py` appends 27–241 clauses per case, with no new variables. Its disabled mode reproduces the recovered CNF byte for byte. These projections expose existing incidence/capacity consequences; they are not new geometric theorems.
For the requested target, 23 minimal light-set clauses and 80 pair-count clauses expose 34 surviving heavy/light patterns from 299 hypothetical patterns satisfying the heavy-count/hub premise. The other 265 are already ruled out mathematically; this is not a count of newly excluded SAT cases.

`campaign.py` retains exact scopes, hashes, compressed inputs and complete accepted proofs. `replay.py` independently regenerates formulas and reconstructs/checks LRAT without a SAT solver. `resume_campaign.py` corrects the runtime disk guard to inspect the actual work filesystem, leaving the historical supervisor frozen.

## Target and controls

| Mask | Maximum | Variant | Result | Search wall seconds |
|---:|---:|---|---|---:|
| 411136406 | 13 | baseline | CERTIFIED_EXCLUSION | 91.994 |
| 411136406 | 12 | baseline | CERTIFIED_EXCLUSION | 101.961 |
| 2185856310 | 12 | baseline | CERTIFIED_EXCLUSION | 70.730 |
| 1101613334 | 12 | baseline | CERTIFIED_EXCLUSION | 33.262 |
| 1101613334 | 12 | projected | CERTIFIED_EXCLUSION | 35.060 |

The target is independently refuted on its unchanged original formula as well as on the projected formula. A single paired trial did not show a speedup. The baseline control for mask 2185856310/max12 succeeded after its projected trial timed out. These are bounded trials on a shared host, not a controlled solver-performance benchmark.

Target original SHA-256: `e32ef48ad3630327a4feb64ab8ea4e37414c445c8c1266953e81b776aac9e795`.
Target projected SHA-256: `80e22b8fdfb03db63efdb626f10391c906e192a58fed33752f9dbc310cbb1242`.

## Complete case ledger

| Mask | Affine class | Exact maximum | Credited exclusion | Final projected search |
|---:|---:|---:|---|---|
| 1101613334 | 114 | 12 | Yes | CERTIFIED_EXCLUSION |
| 308384030 | 109 | 13 | Yes | CERTIFIED_EXCLUSION |
| 10069398 | 109 | 12 | Yes | CERTIFIED_EXCLUSION |
| 411136406 | 111 | 12 | Yes | UNKNOWN_RESOURCE_LIMIT |
| 671697334 | 110 | 12 | Yes | CERTIFIED_EXCLUSION |
| 2185856310 | 110 | 12 | Yes | UNKNOWN_RESOURCE_LIMIT |
| 1101613334 | 114 | 13 | Yes | CERTIFIED_EXCLUSION |
| 308384030 | 109 | 12 | Yes | CERTIFIED_EXCLUSION |
| 377850134 | 109 | 12 | Yes | CERTIFIED_EXCLUSION |
| 1022358 | 111 | 12 | Yes | CERTIFIED_EXCLUSION |
| 675359134 | 109 | 12 | Yes | CERTIFIED_EXCLUSION |
| 2185856310 | 110 | 13 | Yes | CERTIFIED_EXCLUSION |
| 10069398 | 109 | 13 | Yes | CERTIFIED_EXCLUSION |
| 1611227990 | 110 | 12 | Yes | CERTIFIED_EXCLUSION |
| 377850134 | 109 | 13 | Yes | CERTIFIED_EXCLUSION |
| 814057878 | 114 | 12 | Yes | CERTIFIED_EXCLUSION |
| 1116316054 | 112 | 12 | Yes | CERTIFIED_EXCLUSION |
| 411136406 | 111 | 13 | Yes | UNKNOWN_RESOURCE_LIMIT |
| 1022358 | 111 | 13 | Yes | CERTIFIED_EXCLUSION |
| 671697334 | 110 | 13 | Yes | CERTIFIED_EXCLUSION |
| 814057878 | 114 | 13 | Yes | CERTIFIED_EXCLUSION |
| 360808918 | 109 | 12 | Yes | CERTIFIED_EXCLUSION |
| 675891606 | 106 | 12 | Yes | CERTIFIED_EXCLUSION |
| 675359134 | 109 | 13 | Yes | CERTIFIED_EXCLUSION |
| 1611227990 | 110 | 13 | Yes | CERTIFIED_EXCLUSION |

A case is counted once even if two variants are certified. When a baseline control certifies a projected timeout, the case is credited and both outcomes remain visible. `RESULTS.json` lists the accepted variant and exact input hash.

## Validation and certificate boundary

- Regenerated all 25 historical CNF hashes; disabled-mode byte identity and unchanged original clause/variable prefix verified in all 25 cases.
- Checked 7,475 heavy/light assignments and 4,887 exact pair-count triples; four invalid scopes rejected.
- Replayed inherited incidence mathematics/Boolean controls and tetrahedral capacity/type controls. Their tested semantic sources match the recovered encoder sources.
- All credited streams passed DRAT-trim-to-LRAT reconstruction followed by the pinned CakeML checker with exact `s VERIFIED UNSAT` output. Input and proof hashes, source pins, compiler/binary hashes, and checking logs are retained.
- The original target certificate also passed a separate fresh invocation of the new replay program. Other accepted streams were independently checked during production; a second full campaign replay is not claimed.
- The ordinary C LRAT checker is not used for acceptance. Solver preprocessing is untrusted and its RUP unit prefix is included in every accepted proof.
- Initial solver-API and disk-guard failures are preserved under `attempts/`; no exclusion is credited from them. Disk-stopped trials were rerun with the guard on the actual memory-backed working filesystem. Time limits are explicit in each receipt.

## Composed frontier and remaining theorem gap

The recovered 54-case campaign now has 54 accepted cases when these new certificates are combined with its 29 historical certificates.
Coverage of the 55 marked roles per maximum, including the 28 inherited roles per maximum: {'12': 55, '13': 55}.
Complete affine classes under that composition: {'12': [97, 98, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 114], '13': [97, 98, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 114]}.
All 169 largest-fibre transports were checked afresh in the composition. The inherited and earlier 29 proof streams were not all rechecked in this turn; the combined closure explicitly depends on their historical certificates.
The unrestricted dimension-five lower bound 94 remains OPEN, as does the all-dimensional law. This update does not resolve other support/maximum strata. The separately tracked 182,526 middle-maximum profiles and 42 maximum-11 affine classes are unchanged; these are different ledgers and must not be added together.

## Replay

Obtain the reviewed certificate archive from the repository maintainer. The archive filename and SHA-256 appear in EVIDENCE_MANIFEST.json. GitHub contains the source, result ledger, per-run receipts and hashes. The archive contains the exact CNF and proof bytes and the full logs. Access to the archive is required for certificate replay. On Linux x86_64 with Python 3 and gcc (including suitable WSL2):

```bash
python3 restore_evidence.py
python3 rounds/Kakeya_Round9_Recovered_2026-11-04/Kakeya_Round9/research_round10/restore_round10.py /path/to/Finite_Ring_Kakeya_Round10_Review.zip
python3 rounds/Kakeya_Round9_Recovered_2026-11-04/Kakeya_Round9/research_round10/replay.py
```

Replay needs no SAT solver or network after evidence restoration. Do not use Python `-O`. For fresh search and projection tests, use `python-sat==1.9.dev19`; commands are `campaign.py --variant projected --limit 90 --jobs 2`, `verify_projection.py`, and `verify_inherited.py` in the same directory. The search producer skips already completed receipts; preserve them before starting a distinct trial.
The visible-file proof-size guard monitors `.drat` export files; it does not bound the native solver anonymous temporary trace. Search time and actual work-filesystem free-space guards remain separate. The interrupted session and disk-stopped trials confer no credit.
The bundled proof checker is a verified upstream artifact, but this work does not jointly formalize the mathematical normalization, census, encoding, compiler/runtime and support coverage in a proof assistant.
