# Kakeya Round 4 handoff: support-orbit certificates

Date: 2026-10-28. Input: `Kakeya_Complete_Round3.zip`
(SHA-256 `191e32c619ddca37ff08c08a23715c4be9fab2ff68a42b96a035e2d725f1eb82`).

**Git status.** None of the session's repositories (singularity, PerfectJet, nonlinearhamiltonian,
perfectpower) contains Kakeya work. This package has therefore **not been committed or pushed
anywhere**. It is a self-contained checkpoint, ready to be placed wherever you choose.

## 1. Bottom line

| Item | Status |
|---|---|
| Round 3 archive replay (`VERIFY_ROUND3.py`, fresh extraction) | **PASS**, all 15 stages, 232 s (`results/ROUND3_REPLAY_RECEIPT.json`) |
| New method: exact per-support test with checked DRAT refutations | Implemented, validated (Section 4) |
| **Maximum fibre 19, pair-active support 11 or 12** | **All 38 support orbits excluded**; every refutation DRAT-verified |
| Consequence for the round-3 M19 frontier (3,798 profiles) | All are excluded, *given* round 3's inherited lemma that M19 support is 11 or 12 |
| M19, other support sizes (independent of that lemma) | Exploratory solving in progress: 120/1,113 orbits, 0 survivors, no proofs yet |
| Maxima 11 to 18, all supports | Exploratory solving in progress: 478/8,904 cases (supports 10 to 13 done), 0 survivors, no proofs yet |
| Unrestricted dimension-5 bound 94 | **OPEN** |

"Exploratory" means CaDiCaL returned UNSAT without proof logging. Those results are **not credited**
as exclusions until they are rerun with proofs and checked.

## 2. What the last push did, in one paragraph

Round 3 excluded profiles using label-free resource bounds: each fibre's pair counts were
optimized direction by direction, ignoring which actual residue edges share a fibre. Round 4
does the opposite. It fixes the actual pair-active residue support S, enumerating every
possibility up to GL_5(F2). It then asks one finite question per (m, S): can the fibres be
assigned realizable pair spectra, so that every edge's exact sumset capacity covers all 16 lifts
of every direction? The question also imposes two consistent subspace structures per fibre, its
affine direction space and its maximal-pair subspace. That question is a SAT instance. When it is
UNSAT, the solver's DRAT proof is checked by a checker written for this project. For m = 19 every
support of size 11 or 12 is UNSAT, so no counterexample of that type exists in either ring.

## 3. The mathematics (full write-up: `docs/SUPPORT_ORBIT_METHOD.md`)

Necessary conditions encoded for one (m, S), valid for both rings because the Z/4Z carry only
translates a quotient sumset:

* **(A) Spectra.** Each fibre's 31-direction pair histogram is one of the census spectra
  (`data/spec32.csv`, weights 1 to 32), and its values on the incident support directions form a
  sub-multiset of it. Hub = m, outer sizes in [2, m], outer total <= 93 - m.
* **(B) Capacity.** An edge in direction d covers at most Mtab[p][q] lifts (exact maximum sumset
  size in F2^4).
* **(C) Coverage.** Each of the 31 residue directions needs 16 covered lifts.
* **(D) Affine rank.** Positive-count directions lie in the direction space H of the affine hull,
  dim H = rank. When the spectrum has 2^r - 1 positive directions, they are exactly H minus 0.
* **(E) Maximal pairs.** Directions with p = floor(w/2), together with 0, form a subspace of the
  matching size: the stabilizer for even w, round 2's quota theorem for odd w.

The subspaces in (D) and (E) are shared by all edges at the same fibre. This is the "one common
shape per fibre" coupling that round 3 named as the next frontier, in a solver-checkable form.

Normalizations used:

* delete singleton fibres;
* translate a largest fibre to residue 0;
* apply GL_5(F2), which lifts to GL_5(R).

## 4. Validation evidence

* **Orbit list complete.** For every set size k = 5..31, the sum of |GL|/|Stab| over orbits
  equals the Möbius count of spanning k-sets. `VERIFY_ROUND4.py` re-checks this. Support size 11
  was also brute-forced over all 65,780 normalized sets: 7,676 covering sets and 13 orbits, the
  same counts as round 3 (`results/orbcheck_support11.txt`). There are 1,113 covering support
  orbits in total.
* **Census and table.** The spectrum census and sumset table were independently recomputed. For
  weights up to 19 they match round 2's files byte-for-byte after sorting.
* **Checkers.**
  * Both checkers verify CaDiCaL proofs of pigeonhole formulas.
  * They reject fabricated proofs.
  * Fuzz test: 317 valid proofs were replayed against weakened, satisfiable formulas, and neither
    checker accepted any of them.
  * On the real instances, `dratcheck` (forward, all lemmas) and `dratback` (backward, core
    lemmas) agree.
* **Encoder soundness.** Real Kakeya sets must satisfy the CNF with their true spectra and pair
  counts fixed, and all of these did:
  * the 94-point generalized star in both rings;
  * ten greedy-minimal random Kakeya sets of 276 to 294 points;
  * two SAT-constructed 150-point Kakeya sets with a hub of 19 on support-12 orbits.

## 5. Trust boundary: what a reader must accept

1. The five lemmas (A) to (E), which are short and stated in the method document.
2. That `src/encode_cnf2.py` encodes them faithfully. This rests on code review and the soundness
   tests; the encoder is **not** formally verified.
3. That `src/dratback.cpp` / `src/dratcheck.cpp` are correct. They are about 200 lines each,
   tested as above. Running a standard checker such as drat-trim as well would be a cheap, strong
   extra check. Building it was not permitted in this session.

The solver and the round-3 resource arguments are **not** trusted dependencies of the M19
exclusion. The inherited lemma "M19 support is 11 or 12" is a dependency of the profile-level
statement, until the all-support M19 sweep is certified.

## 6. Files

```
HANDOFF.md                      this file
VERIFY_ROUND4.py                replay: build, regenerate data, completeness check, re-certify
docs/SUPPORT_ORBIT_METHOD.md    method, lemmas, encodings, validation
src/orbits_all.cpp              support-orbit enumerator (canonical forms + stabilizers)
src/orbcheck.cpp                brute-force cross-check for a fixed support size
src/spectra32.cpp               pair-spectrum census with affine ranks, weights 1..32
src/msum.cpp                    exact max sumset table in F2^4
src/encode_cnf2.py              CNF encoder for conditions (A)-(E)
src/run_cert2.py, batch2.py     solve-with-proof + check pipeline (development driver)
src/explore.py                  proof-free exploration driver
src/dratcheck.cpp, dratback.cpp DRAT checkers written for this project
src/soundness*.py, fuzz.py      encoder soundness and checker fuzz tests
data/orbits_all.txt             size, canonical mask, stabilizer order, covering flag (all orbits)
data/spec32.csv, Mtable.txt     census and sumset table
results/m19_s11_12.jsonl        38 certified M19 exclusions (CNF + proof SHA-256, checker output)
results/explore_*.jsonl         uncredited exploration snapshots
results/ROUND3_REPLAY_RECEIPT.json, orbit_counts.txt, orbcheck_support11.txt
```

The 38 recorded certifications used an earlier encoder revision, `encode_cnf.py`. That revision
differs only in loading a census truncated at weight 19 and value range 0 to 9, which is equivalent
for m = 19. `VERIFY_ROUND4.py` re-certifies with the current encoder, so CNF hashes in a fresh
receipt differ from those in `results/m19_s11_12.jsonl`.

## 7. Replay

```
pip install python-sat          # CaDiCaL 1.9.5 via PySAT
python3 VERIFY_ROUND4.py --quick --both    # ~3 min: one orbit per size, both checkers
python3 VERIFY_ROUND4.py --jobs 4          # all 38 orbits, roughly 1-2 h
```

Quick mode was run on this checkpoint and passes. The full certification ran as the development
batch: 38/38 verified, longest case 20 min including the forward check.

## 8. Next steps, in order

1. **Certify the M19 all-support sweep.** That removes the dependence on the inherited support
   lemma and closes M19 independently.
2. **Maxima 11 to 18.** Supports 10 to 13 are explored with no survivors. Solve time grows with
   support size: about 15 to 45 s per case at size 13. A sample at supports 16 and above produced
   no answer within an hour, so the large-support cases may need more structure before they are
   tractable:
   * symmetry breaking by Stab(S);
   * a redundant doubled-energy cut;
   * splitting by hub spectrum.
3. **Re-certify with a standard checker.** Run drat-trim, or have CaDiCaL emit LRAT and use
   cake_lpr, in an environment where it can be built.
4. **Extend to maxima 2 to 10 and 20 to 32.** The census and encoder already support every m. The
   dimension-five theorem would then not depend on any earlier checkpoint.

Counting caution, unchanged from round 3: support orbits, weight multisets and profiles are
different objects and are not summed.
