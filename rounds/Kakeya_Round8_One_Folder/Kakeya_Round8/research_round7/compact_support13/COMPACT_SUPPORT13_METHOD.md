# Compact support-thirteen proof delivery

## What this collection certifies

This directory contains smaller proof payloads for exactly the accepted
support-thirteen cases listed in the frozen original certificate
manifest. It changes the delivery representation of those certificates.
It does not add a support, maximum interval, weight profile, or theorem
case to their mathematical scope.

Each new proof is checked against the **exact original CNF**. Original
formulae, accepted production receipts, semantic sources, catalogue
bindings, affine transports, and inherited ledger dependencies remain
part of the checkpoint. The original new Round7 DRAT payloads can be
omitted from the delivered archive after complete compact replay. The
one inherited Round6 LRAT remains in the base checkpoint unchanged.

## Producing a smaller certificate

For each original new DRAT certificate, the producer first regenerates
the formula from its pinned semantic sources and requires its SHA-256 to
equal the original CNF hash. It verifies the original compressed and
decoded CNF and DRAT hashes. It then runs the pinned DRAT-trim command

```text
drat-trim original.cnf original.drat -l core.drat
```

The resulting core is an untrusted candidate proof. The producer makes
a **fresh** call of the existing proof-audit pipeline on
`original.cnf` and `core.drat`. That pipeline converts the proof to LRAT
and requires acceptance by the pinned upstream CakeML checker. The
original CNF is used directly; no learned units or other added axioms are
introduced at this stage. Any preprocessing prefix in the original
search proof remains part of its provenance, but need not remain in the
core if the core is independently accepted against the original CNF.

Only an accepted core is compressed and published. The producer checks
the persisted compressed and decoded core hashes, binds its receipt to
the full immutable original case row, and checks that the original
compressed inputs have not changed. Incomplete proof output does not
enter the compact inventory. One pre-existing pilot core can be imported
only after checking its original-input hashes, core hashes, and recorded
original-CNF CakeML acceptance. The final portable replay checks that
core again along with all the others.

Two workers may produce cores concurrently using an explicitly frozen,
disjoint partition of case identifiers. Each worker has separate progress
files and private temporary storage. Both use the same frozen per-case
producer and acceptance rule. A three-gibibyte temporary-disk guard is
checked before each new production. Earlier completed cores are validated
and reused on restart, never silently overwritten.

## Final inventory and portable replay

The original support-thirteen manifest may grow while additional searches
finish. Per-case cores are produced against immutable accepted rows during
that period. Final publication occurs only after the source inventory has
stopped changing and every new DRAT case has a checked core.

`COMPACT_SUPPORT13_MANIFEST.json` then records an exact byte copy of the
original manifest, all original case rows in their original order, every
replacement proof and receipt hash, the original coverage calculation,
and all semantic and replay source hashes. The replayer requires complete
coverage of that exact inventory. A quick sample is explicitly labelled
as a sample and cannot stand in for the full replay.

From the checkpoint root, run:

```bash
python3 research_round7/compact_support13/verify_compact_support13.py --jobs 2
```

One worker is available with `--jobs 1`. The complete replay builds the
pinned checkers, regenerates every exact CNF, checks every compact DRAT
against its original CNF through the DRAT-to-LRAT-to-CakeML pipeline, and
checks the inherited LRAT with CakeML. It then repeats the final source
and coverage bindings. The explicit successful status is

```text
PASS_ALL_ORIGINAL_SUPPORT13_CASES_VIA_COMPACT_CAKEML_PROOFS
```

The portable replayer **does not open or require the original new Round7
DRAT files**. It needs their small original receipts and hash declarations
as provenance, together with the original CNFs, replacement core files,
semantic sources, catalogues, checker sources, and inherited Round6 data.
The old full replay script still expects the original large proof payloads;
the compact replay command above is the intended replay entry point for
the compact archive.

## Trust and scope

The core-trimming algorithm is not trusted for acceptance: its output
must pass the fresh CakeML check against the exact original formula.
The ordinary C LRAT checker is diagnostic only. The package verifies and
builds the pinned upstream CakeML assembly artifact; it does not rerun
the HOL4 proof development. The compiler, linker, runtime and supplied
wrapper remain part of the execution environment.

Most importantly, verified propositional unsatisfiability is distinct
from the mathematical claim that every relevant Kakeya configuration
maps to a satisfying assignment of the formula. The original encoding
soundness lemmas, orbit completeness, affine transports, and inherited
reductions retain their documented status. Proof compaction neither
formalizes nor weakens those separate obligations.

The original workspace proofs remain unchanged as provenance. The final
archive may omit only the explicit original new DRAT paths covered by
accepted replacements; original formulae, receipts and required sources
are retained. A complete compact inventory and its full successful replay
are required before this omission is authorized.
