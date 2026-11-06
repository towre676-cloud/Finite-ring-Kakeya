Kakeya Round6: complete support-eleven and support-twelve exclusions
================================================================

MAIN RESULT

For R = Z/4Z and R = F2[epsilon]/(epsilon^2), no Kakeya set in R^5
of at most 93 points has pair-active residue support 11 or 12 and maximum
fibre size at most 19.

This is established by two complete collections on the same 38 marked
support classes (13 of size 11, 25 of size 12):

  * 38 freshly generated formulas at maximum 19, using the exact supplied
   encoder, accepted through DRAT-trim, LRAT, and the pinned CakeML checker;
  * 38 new formulas permitting EVERY maximum from 2 through 18 jointly,
   with direct LRAT proofs accepted by the same CakeML checker.

With the inherited exclusion of maxima >= 20 and Round5's exclusion of
supports <= 10, every remaining at-most93-point counterexample has at
least 13 pair-active residue fibres. The unrestricted lower bound 94,
and the general formula 3*2^n-2, remain OPEN.

EXACT FRONTIER

The middle-maxima inventory loses 84,297 whole weight profiles:
270,779 becomes 186,482; 48 nonempty support/maximum cells become 34.

Support       Previous profiles       Remaining profiles
11                  23,474                     0
12                  60,823                     0
13                  85,802                85,802
14                  75,766                75,766
15                  20,438                20,438
16                   4,051                 4,051
17                     425                   425

Maximum 11 separately retains 46 affine support classes. An additional
support 13 marked class is excluded for maxima 2..18, but that alone does
not remove any whole weight profile. The two proofs of that marked case
are counted as one mathematical exclusion.

START READING

  research_round6/Kakeya_Round6_Monograph.pdf
      Formatted reading copy, with bold emphasis and the same monograph.
  research_round6/Kakeya_Round6_Monograph.txt
      Editable source: exactly 1,500 whitespace-separated words.
  Kakeya_Research_Frontier_Round6.json
      Machine-readable current ledger, scope and dependencies.
  research_round6/CLAUDE_NEXT_STEP_HANDOFF.txt
      Concrete draft handoff for the other session; not sent.
  research_round6/PUBLIC_UPDATE_DRAFT.txt
      Concise public-facing draft; not posted.

ANALYTIC PROOFS

  research_round6/structural_progress/
    SUPPORT11_COMPLEMENTARY_SUBSPACES_PROOF.md
      The support V union W, with complementary dimensions 3 and 2,
      forces at least 94 points without a maximum-fibre hypothesis.
      This proof uses local graph bounds, a 92-point baseline and
      forced affine four-flats. No spectrum census or SAT dependency.
    ADDITIONAL_LOCAL_GRAPH_CUTS.md
      Partial restrictions for the other support 11 geometries.

  research_round6/encoder_audit/
    ONE_WAY_SOUNDNESS_AUDIT.md
      Every hypothetical Kakeya counterexample extends to a satisfying
      assignment of the relevant CNF, including every auxiliary family.
    MAXIMAL_SUBSPACE_COSET_LEMMA.md
      Pair counts are constant on cosets of the maximal-pair subspace.
      For odd weight and a nontrivial such subspace, the fibre differs
      by one point from a periodic set. The optional stronger encoder
      is proved sound; small diagnostics did not show a speed advantage.

  research_round6/next_frontier/
    DENSE_FIBRE_COMPLEMENT_LEMMAS.md
      Further hand proofs describe all pair-direction patterns for
      eleven- and twelve-point fibres in affine four-flats. They give
      targeted necessary clauses even when the maximal-pair subspace
      is trivial. All 6,188 small complements are checked by the companion
      verifier. These additional lemmas change no exclusion counts.
    DENSE_TYPE_ENCODING_DESIGN.txt
      Exact structured direction models for the two dense types with
      trivial maximal-pair subspace, with constructive converse proofs.
      These are designs for the next encoder, not implemented benchmarks.
    SUPPORT13_CASE_QUEUE.json
      The complete next 55 marked cases, with one already certified and
      54 still requiring a complete joint certificate. Proposed splits
      are explicit and unrun branches receive no credit.

REPLAY

Requirements: Python 3.10 or later, C and C++ compilers, Linux x86_64,
and several GB of temporary disk space for reconstructed LRAT proofs.
Use --jobs 1 to reduce concurrent memory and disk use. The complete
replay uses the published x86_64 CakeML artifact. No network, PySAT,
new SAT search, or solver installation is required.

From the single extracted Kakeya_Round6 folder:

    python3 VERIFY_ROUND6.py

This rechecks the inherited Round5 finite components, new finite data
and mathematical checks (including the dense-complement lemmas),
all 38 maximum-19 certificates, all 38 joint
certificates, the support13 diagnostic certificates, and the ledger.
Exact CNF regeneration binds certificate bytes to declared supports,
parameters, and the actual encoder sources.

    python3 VERIFY_ROUND6.py --quick

Quick mode checks a sample of the two main proof collections. Its result
is explicitly labelled QUICK and does not claim a complete 76-proof replay.

    python3 research_round6/verify_archive_manifest.py

The manifest command checks the bytes as distributed. Run it before
procedural replays, which may rewrite timing receipts and diagnostic logs.

PROOF STORAGE AND TRUST

The portable edition contains exact input formulas and complete DRAT
refutations for all 76 main cases, with ordinary XZ compression. The two
support-13 diagnostic formulas retain their accepted LRAT certificates.
On replay of a main case, pinned DRAT-trim
reconstructs LRAT certificates and the pinned CakeML checker must accept
every one. Decoding verifies the declared uncompressed SHA256 before
proof checking; every regenerated formula must match its recorded hash.

For the joint collection, the original LRAT proofs were trimmed to checked
dependency cores before conversion to the smaller DRAT representation.
The resulting DRAT proofs were converted back to LRAT and accepted by
CakeML on the exact unchanged formulas. None of these representation
conversions changes the mathematical statement or adds an exclusion.
The untrusted solver, converter and core trimmer are not final authorities.

Larger intermediate LRAT streams are represented by their provenance and
hashes; complete replayable refutations are included. Historical producer
and replay scripts are retained for provenance. Use the root replay above
for the certificate representation actually included in this edition.

The checker proves exact Boolean-formula unsatisfiability. The separate
one-way mathematical/code review supplies the Kakeya interpretation.
The complete spectrum census is a finite computational dependency.
The encoder and full Kakeya exclusion are not proof-assistant formalized.
Earlier Lean formalizations cover specified semantic components only.
Reviews by separate model agents are not independent human review.

PROVENANCE

The uploaded Claude Round4 archive is preserved, its 26 payload files are
imported unchanged, and the complete earlier Round5 archive payload is
preserved byte-for-byte. The upload contained the current encoder and
historical records, but no historical CNFs or proof files. Round6 therefore
certifies the supplied encoder directly and does not assume equivalence
to its unavailable earlier revision. Both rings share the same necessary-
condition formulas because the carry translates quotient sumsets without
changing their cardinalities.

One generated DRAT file failed a final integrity check. Deterministic
regeneration restored exactly its recorded bytes; both checkers accepted
again and a subsequent full compressed replay passed. No mismatch was
waived. The cause is undetermined and the incident record is included.

No result from an exploratory timeout is counted as an exclusion. External
sweep counts are dated snapshots from the attached handoff, not live status.
