# Compact certificates with unchanged mathematical scope

The joint-maximum solver proofs originally totalled approximately 11.93 GB of ASCII LRAT. They contain many derived clauses that are never used in the final contradiction. This directory constructs smaller **proofs of the same exact CNFs**, accepts each new proof with the pinned upstream CakeML checker, and stores the accepted ASCII proof in ordinary XZ compression.

The core producer is untrusted. Its output has no status until the mandatory checker accepts it. The original solver proofs, original CNFs, and their historical receipts are not modified by this work.

## Completed production result

All **38 joint-maximum cases** passed the mandatory fresh CakeML core check. The full production batch took approximately 449 seconds with two workers.

| Representation | Total bytes |
|---|---:|
| Original joint LRAT search traces | 11,925,732,987 |
| Accepted ASCII LRAT cores | 7,604,741,883 |
| Complete accepted cores in standard XZ | 481,732,272 |

The dependency closure retained 3,353,150 of 10,824,719 derived clauses. All retained hints in these 38 particular cores are positive RUP hints; the separate genuine-RAT control checks the producer's handling of negative references. The largest expanded core is 2,255,284,752 bytes. Two-worker replay can temporarily materialize that core alongside the second largest core of 1,425,557,091 bytes.

## The production pipeline

1. Check the exact original CNF and LRAT hashes against their accepted receipt.
2. Read the original ASCII LRAT in three passes. Starting from the final empty clause, retain every derived clause recursively referenced by its hints. Negative RAT clause references are included.
3. Preserve the original order of retained additions and their exact bytes. Preserve deletion chronology, retaining deletion targets that are original CNF clauses or retained derived clauses. Gaps in clause IDs remain.
4. Run the pinned CakeML checker on the **new core and unchanged original CNF**. Require the exact success line, an accepted return status, and empty stderr. Recheck hashes after checking.
5. Compress the accepted core with standard XZ. Decompress and hash the stored artifact, requiring exact identity with the accepted ASCII proof.
6. Publish the closed compressed file, checker logs, and receipt. Temporary raw candidates are removed.

Every acceptance therefore rests on the final checker and exact CNF bytes. Trust in the solver or the core producer is unnecessary for the CNF's unsatisfiability. Correctness of the mathematical CNF encoding remains a separate obligation.

## Files and replay

Each case has a directory beneath **cases/** containing:

* **core.lrat.xz**: the complete accepted LRAT proof, using standard XZ compression.
* **CORE_RECEIPT.json**: original and core hashes, exact CNF location, marked-support metadata, maximum interval, checker outcome, and compression identity.
* **cake_lpr.stdout.txt** and **cake_lpr.stderr.txt**: checker output.
* Trimmer statistics and logs.

**CORE_BATCH_RECEIPT.json** records the complete declared inventory. The replay script checks all 38 marked-support classes, their affine transport witnesses and maximum interval. It binds every case to the original authoritative certificate manifest and all pinned encoder/data source hashes, then regenerates each exact CNF from its support and maximum interval. Only byte-identical regeneration passes. It also checks compressed proof hashes, decompressed proof hashes and sizes, and fresh CakeML acceptance, and rechecks the stored artifacts after acceptance.

Original CNFs may be present as plain files or as their standard **.cnf.xz** siblings. The shared certificate-storage helper materializes and hashes them before use. The old large LRAT search traces are referenced only by provenance hashes and are unnecessary for this portable replay.

From the package root:

    python3 research_round6/proof_core/verify_cores.py --jobs 2

A smaller integration check, clearly labelled incomplete:

    python3 research_round6/proof_core/verify_cores.py --quick

Replay needs Python 3, a C compiler, Linux x86_64, and temporary disk space for one or two expanded proofs. It needs no network access, SAT solver, original long solver proofs, C++ compiler, or core producer. The pinned checker assembly, C wrapper and provenance are supplied in the preserved Round5 checker package.

To regenerate all joint cores from the original full proofs, which are retained in the working checkpoint:

    python3 research_round6/proof_core/trim_and_check.py --scope joint --jobs 2

This production command additionally requires a C++17 compiler. The helper also supports **--scope m19** or **--scope both**, and explicitly selected cases. A selected-case receipt cannot stand in for a complete-scope replay.

## Focused controls

**verify_core_controls.py** confirms that a genuine RAT proof remains accepted after trimming, including its three negative RAT references. A fabricated empty-clause proof for a satisfiable CNF remains rejected by CakeML. Direct and hardlink aliases of either original input are rejected as output paths without changing the inputs. These are implementation checks, not a formal proof of the trimmer.

The first large pilot shrank from 760,336,747 bytes to 484,564,216 bytes and was accepted by CakeML in approximately 22.7 seconds. Its backward dependency closure retains 208,344 of 508,975 derived clauses. Standard XZ reduces this core to approximately 35 MB.

## Experiments that are not used in production

**lrat_hint_core.cpp** additionally simulates positive RUP hint sequences and retains the reverse reason cone of their conflict. On the large pilot all 64,603,230 retained hints were already in those cones, so this produced no further reduction. Negative RAT lines are left unchanged. The production pipeline does not invoke this optional experiment.

**lrat_pack.cpp** is an experimental lossless integer-delta storage codec. Its complete pilot roundtrip reproduced the accepted ASCII SHA256, but improved compressed size by only about six percent. It is also unused. All delivered production certificates use ordinary **.lrat.xz**, and the portable replay does not invoke either experimental program.
