ROUND 8: THE FOUR REMAINING SUPPORT-13 MAXIMUM-11 ROLES

This directory owns isolated common-ring strengthened formulas, bounded
search receipts, and portable certificate replay. Every Round7 source,
formula, proof and manifest is a read-only dependency.

Declared marked roles, in trial order:
377850134, 411136406, 671697334, 2185856310.
The distinguished maximum fibre is at residue0, exact maximum11, with
total size at most93. The first two fill the single remaining roles in
inherited affine classes109 and111; both of the last two are needed to
close class110. Those class conclusions require the inherited Round7
ledger and are reconciled by the parent project, not assumed here.

CUT FAMILIES

1. Heavy cardinality: at least9 fibres have weight>=4 when all weights
   are<=13; the general support13 threshold is8 when all are<=18.

2. Heavy difference cover: the new elementary theorem for maximum<=11
   strengthens this to at least10 heavy fibres, and every nonzero residue
   direction is a difference of two heavy residues. This is implemented
   by exact ANDs for heavy-heavy edges and one disjunction per direction.
   The module and its complete Boolean controls are in ../charging.

3. All-edge tetrahedral capacities: two nonplanar quotient four-sets
   have at most14 sums. Safe fibre-spectrum flags activate this bound.
   A second explicit capacity calculation handles every edge, including
   directions with multiple edges. It never infers the location or meaning
   of hidden baseline auxiliary variables.

encode_strengthened.py exposes f.r8_heavy, f.r8_tetra_type,
f.r8_edge_capacity[(a,b)] and f.r8_direction_edges[d]. The audited baseline
with strengthen=False also exposes f.h_selectors and f.k_selectors while
retaining byte identity with the original joint-maxima encoder.

Explicit trial modes are baseline, heavy, tetrahedral, heavy_tetrahedral,
heavy_cover, and heavy_cover_tetrahedral. The first bounded four-case
trial uses heavy_cover_tetrahedral with a120-second search limit per case.
No performance attribution to any individual cut is claimed.

VALIDATION AND SOURCE FREEZE

STRENGTHENED_FINITE_REPLAY.json records complete heavy-flag truth tables,
conditional edge-capacity truth tables, a genuine multiple-edge14+2
coverage witness, negative controls, and disabled byte identity for all
four actual target formulas. COMPOSITION_CONTROLS.json binds the initial
combined formulas and their explicit interfaces. Heavy-cover controls are
recorded independently in ../charging/HEAVY_COVER_REPLAY.json.

FROZEN_SOURCES.json pins the semantic inputs and the producer/replayer
sources. Changing one of these files invalidates further use of this
frozen trial family. Later mathematical variants require their own source
version and exact formula binding; accepted proof files are not relabelled.

SEARCH AND ACCEPTANCE

The inherited safe supervisor owns an entire process group, kills/reaps
descendants, monitors every live DRAT stream, and confirms the group is
gone before publication. The trial family uses an aggregate768MiB live
DRAT limit and keeps at least2GiB free temporary disk.

The RUP-unit wrapper is untrusted search preprocessing. Every accepted
prefixed DRAT is checked against the exact unaugmented strengthened CNF
through pinned DRAT-trim -> LRAT -> CakeML. A solver's UNSAT line alone
does not earn an exclusion. Unaccepted partial proof streams are not
delivered as certificates. A SAT assignment to the relaxation is not an
actual Kakeya counterexample.

REPLAY

For the delivered compact proof collection, the primary command is:

    python3 research_round8/strengthened/compact/compact_certificates.py --replay

It regenerates the unchanged original CNFs and freshly checks the compact
DRATs with CakeML. The original large Round8 DRAT streams are not required.
The compact manifest preserves the entire original outcome inventory and
binds every replacement proof to its original formula and immutable receipt.

Finite controls, without a solver:

    python3 research_round8/strengthened/verify_strengthened.py
    python3 research_round8/charging/verify_heavy_cover.py

In the full production workspace, including original large DRAT payloads,
inventory and freshly check every original outcome with:

    python3 research_round8/strengthened/verify_certificates.py --freeze

Subsequent original-payload replay of that inventory:

    python3 research_round8/strengthened/verify_certificates.py

Replay regenerates each formula byte-identically. Accepted proofs must
again pass CakeML; timeout formulas are regenerated with explicit zero
exclusion credit. No SAT solver is needed for these replay commands.

The encoder is not proof-assistant formalized. Its Kakeya interpretation
uses the written one-way argument, complete inherited spectrum/support
data, and the stated geometric lemmas. The precise trial outcomes and
proof hashes live in immutable per-case CASE_RECEIPT.json files; a completed
full replay is recorded separately in CERTIFICATE_REPLAY.json.
