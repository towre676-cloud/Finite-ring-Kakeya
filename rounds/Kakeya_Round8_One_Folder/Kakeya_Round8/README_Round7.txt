KAKEYA RESEARCH — ROUND 7 CHECKPOINT
===================================

Start here. This is one ordinary ZIP, extracting into one Kakeya_Round7
folder. The complete earlier Round 6 payload is preserved byte for byte,
including the supplied Claude Round 4 handoff, earlier work, sources and
proof dependencies. Round 7 adds the theorem, exclusions and tools below.

MAIN RESULT
-----------
For both R = Z/4Z and R = F2[epsilon]/(epsilon^2), the minimum size of a
primitive-direction Kakeya set in R^3 is exactly 22.

There are two complete routes. The elementary proof uses small fibre
geometry and a charging argument; it has no SAT, spectrum-census, or
support-orbit enumeration premise. Separately, the exact actual-point
encoder covers all five marked support classes in each ring, and all ten
refutations have been regenerated and checked by pinned CakeML through
DRAT/LRAT. The 22-point star construction supplies the matching upper bound.
The independent elementary dimension 2 proof gives 10, also corroborated
by four refutations and two actual ten-point witnesses.

These are results established in this project. We make no claim here
about priority in the literature. Neither the general proposed formula
3*2^n-2 nor the dimension 5 target 94 is proved by this checkpoint.

READING ORDER
-------------
1. research_round7/Kakeya_Round7_Monograph.pdf
   A readable, exactly 1,500-word account, with bold emphasis. Its complete
   source is Kakeya_Round7_Monograph.txt in the same directory.
2. research_round7/dimension3/DIMENSION3_ELEMENTARY_PROOF.md
   The complete mathematical proof of the 22-point theorem.
3. Kakeya_Research_Frontier_Round7.json
   The reconciled machine-readable ledger, with explicit dependencies.
4. research_round7/NEXT_ATTACK.txt
   Which remaining questions the new methods address, and which tests
   failed to produce exclusions.
5. research_round7/PUBLIC_UPDATE.txt
   An unsent public-facing research update. Nothing has been posted.

DIMENSION5: WHAT REALLY CHANGED
------------------------------
The previous checkpoint already excluded pair-active supports of size
at most 12 under its recorded reductions. Maximum fibre 19 stays closed
using the inherited support11/12 restriction; no outer-weight14 cap is
used by its checked refutations. This package does not replace that
restriction with an all-support maximum 19 theorem.

A new integer charging inequality excludes 3,006 entire weight profiles
for maxima 12 through 18, in every placement and in both rings. The complete
middle-maxima list therefore shrinks from 186,482 to 183,476:

    support     before       removed       remaining
       13       85,802           462          85,340
       14       75,766         1,393          74,373
       15       20,438           924          19,514
       16        4,051           198           3,853
       17          425            29             396

The new verifier recomputes the required sumset coefficients from three
elementary formulas. It does not need the old sumset census as a mathematical
premise. The complete fibre-spectrum census remains an explicit dependency.
Each excluded profile has its own integer certificate, heavy positions,
strict gap and source-line binding. No floating-point optimization result
is accepted as an exclusion.

The complete support 13 catalogue has 55 marked cases, which distinguish
the location of a largest fibre. The delivered certificate inventory has
48 rows:47 new refutations and one inherited refutation. Several formulas
cover the same marked support or only a maximum interval, so 48 is not a
count of 48 different support geometries.

    maximum interval       marked cases covered /55
          2..18                         28
          exact11                       35
          exact17                       31
          exact18                       39

The maximum 11 inherited affine-class frontier improves from 46 to 45:
class 105 is now completely covered in every possible largest-fibre role.
The remaining support 13 portion has classes 109,110,111, with only four
uncovered marked roles:377850134,411136406,671697334,2185856310.
The other support 14..16 maximum 11 classes remain as listed in the ledger.

None of the 55-case maximum cells is completely closed by the new support 13
inventory. Partial support coverage is not subtracted from whole weight
profiles. The 3,006 profile exclusions come from the separate universal
charging certificates.

NEW SHORT GEOMETRIC RESULTS
---------------------------
* A support 13 Kakeya configuration with every fibre of size at most 18
  needs at least eight fibres of size at least 4. This proof needs no
  total 93 assumption, census, or SAT result.
* Eight residue points in F2^5 determine at most 25 distinct nonzero
  differences; nine points determine at most 28. Both have short symbolic
  proofs, with complete small finite corroborations.
* Two nonplanar four-point sets in F2^4 have at most 14 sums, rather than
  the product upper bound 16. This gives a new cross-edge geometric cut.
* All feasible weight/three-direction pair-count tuples in a binary plane
  have an exact local characterization. Shared direction-space containment
  also bounds edge capacities. The dense 11- and 12-point types have explicit
  circuit/subspace direction models.

The cheap four-pair wrapper was tested on the two single-gap maximum 11
classes. Both 45-second trials timed out; one support had no unique edge
to which that particular wrapper applied. These outcomes earn no exclusion
credit. The code and valid lemmas are retained for stronger later encodings.

DIMENSION4
----------
The support inventory is complete:28 covering marked support classes,
giving 56 exact ring-specific cases. All 32,768 support transports and a
separate Burnside count are checked. Fourteen cases are UNSAT with checked
proofs;42 timed out. No counterexample was found. Both rings now exclude
all marked supports of sizes 6..8 and two of the six size 9 classes.
The proposed exact minimum 46 remains open. A46-point star is verified.

HOW TO REPLAY
-------------
From the extracted folder, using Python3, gcc/g++ and Linuxx86_64:

    python3 VERIFY_ROUND7.py --quick

This runs the finite checks, exact small-dimension certificates and a
sample of the larger new proof collections. The receipt explicitly says
that the new proof replay is a sample.

    python3 VERIFY_ROUND7.py

This freshly regenerates and rechecks ALL delivered Round 7 proof cases,
with explicit no-exclusion handling of timeout formulas. It samples the
older Round 6 proof collections; their earlier full replay is preserved.
No SAT solver or network access is needed for these replay commands.

    python3 VERIFY_ROUND7.py --inherited-full

This additionally rechecks the complete older proof collections. --jobs 1
reduces concurrency. Run without Python -O: some inherited finite routines
use assertions. The two proof-checking workers may need several gigabytes
of temporary disk space and memory. Exact runtime depends on the machine.

The assembly run uses --reuse-checked-certificates after each new collection
has completed its own full portable replay. That mode hashes and binds the
full receipts and their inputs; it is explicitly not another fresh checker
execution. The default command above executes the checkers afresh.

For fresh Lean compilation, supply the separately installed Lean 4.24.0
binaries and mathlib at commit f 897ebcf 72cd 16f 89ab 4577d 0c 826cd 14afaafc 7:

    python3 VERIFY_ROUND7.py --mathlib /path/to/mathlib --lean-bin /path/to/lean/bin

The package includes source, logs and axiom-audited compilation receipts.
Lean itself and the mathlib checkout are not embedded in this ZIP.

WHAT THE PROOFS TRUST
--------------------
The elementary dimension 3 theorem is a written mathematical proof. Small
enumerations corroborate its steps but are not assumptions of that proof.

A checked CNF refutation proves the exact formula unsatisfiable. Its Kakeya
interpretation still depends on the written one-way encoder argument and
complete support reduction. The exact ring model uses actual points and
the correct coordinate carry; its symmetry is one common affine tangent
shear, not independent translations of every fibre.

Lean checks that common shear and the abstract charging algebra/summation
core,14 new statements/equivalences in all. It does not yet formalize the
whole Kakeya theorem, Python encoder, finite spectrum census, or geometric
incidence-to-charge construction.

The pinned CakeML checker is the acceptance authority. An ordinary C LRAT
utility is retained only as a diagnostic; its recorded negative-control
failure is documented in the inherited proof-audit material. Multiple
model agents add reproducibility and review, not independent human refereeing.

ARCHIVE REPRESENTATION
----------------------
The original Round 6 payload remains byte-identical. New large S13 and
dimension 4 refutations are delivered as smaller, separately checked DRAT
cores against the SAME original CNFs. The original untrimmed Round 7 DRAT
streams are omitted from this portable archive; their hashes and provenance
are retained. No original untrimmed stream is required by the compact replay.
Standard XZ stores proof/CNF bytes inside the ordinary ZIP.

Exact-ring n2/n3 proofs retain their original complete refutations. The
accepted S13 and n 4 original formulas remain stored, independently regenerated
and hashed. Exploratory unfinished proof traces are not certificates and
are not delivered as if they were.

MANIFEST_ROUND7.json binds every delivered file. To check the extracted
archive before running scripts:

    python3 research_round7/verify_archive_manifest.py

All searches in this checkpoint are stopped. Results reflect the supplied
external snapshot and accessible earlier archives, not unseen live sessions.
