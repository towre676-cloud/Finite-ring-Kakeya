KAKEYA ROUND 8 — START HERE
===========================

ONE DOWNLOAD, ONE EXTRACTION FOLDER
----------------------------------
This is one ordinary ZIP. It extracts into one top-level folder named
Kakeya_Round8. All earlier packaged research is preserved inside that
folder, together with the new proofs and current account.

READ FIRST
----------
The readable current account is exactly1500 words, including its title:

    research_round8/Round8_Monograph_1500.pdf

Its editable Markdown source is next to it. The PDF has three visually
checked pages and its extracted body text exactly matches the source.

The short public-facing announcement is:

    research_round8/Round8_Public_Post.txt

The precise branch theorem and trust boundary are in:

    research_round8/SUPPORT13_MAXIMUM11_THEOREM.txt

The complete current ledger is:

    Kakeya_Research_Frontier_Round8.json

MAIN RESULT
-----------
The exact-maximum-eleven, support-thirteen branch is closed in dimension
five for both Z/4Z and F2[epsilon]/(epsilon^2), under the inherited
reductions and reviewed necessary-condition encoder. The four remaining
marked roles all have checked refutations against their exact formulas.
They close affine classes109,110,111 and reduce the maximum-eleven
ledger from45 open affine classes to42:

    support14: 9 classes
    support15: 16 classes
    support16: 17 classes

The full94-point lower bound remains OPEN. Combined direct exact-eleven
coverage is39 of55 marked support-thirteen cases; the complete branch
closure also uses the inherited class reductions. A marked role and an
entire affine support class are different accounting units.

NEW MIDDLE-PROFILE EXCLUSIONS
---------------------------
The incidence and price theorems exclude 950 whole weight profiles in
every placement and in both rings. The matching threshold excludes 745;
the three-direction price bound excludes 488, of which 205 are new.
The overlap is 283, so the combined total is 950, with no duplicate credit.

    maximum:      12   13   14   15   16   17   18
    exclusions:  129   68  191  108  250   94  110

The middle-maxima ledger changes 183476 to 182526. Remaining profiles:

    support 13: 84946
    support 14: 74039
    support 15: 19362
    support 16:  3793
    support 17:   386

All 950 have exactly nine heavy fibres. Of the original 2187 nine-heavy
profiles, 1237 remain. The earlier cumulative stages 16, 128, 175 and 745
are preserved as history; they are included in 950, not added to it.
Every final source line has an explicit integer certificate. Direct and
staged regeneration produce byte-identical surviving profiles.

    research_round8/incidence/THREE_DIRECTION_PROFILE_EXCLUSIONS.json
    research_round8/incidence/after_three_direction_survivors.txt
    research_round8/incidence/THREE_DIRECTION_PRICE_LEMMA.md
    research_round8/geometry/MATCHING_THRESHOLD_LEMMA.md

REUSABLE MATHEMATICS
-------------------
* S13/max<=11 needs at least10 fibres of size>=4 and a full heavy-residue
  difference cover, without a total-weight or census premise.
* Under total<=93 it needs at least11 such fibres. An elementary price
  argument gives748<768. Its only finite classification premise checks
 14950 normalized ten-point supports; no fibre/sumset census is needed.
* An independent enumeration of85184 actual fibres gives the stronger
  price bound689<768 and corroborates separate integer calculations.
* For at least9 heavy residues, r*|M|<=n2+2*n3, where M is the missing
  heavy-difference set and r=ceil(16/floor(maximum/2)). This applies to
  the next S13/max12–13 and S14/max11 encoded cases. A separate analytic
  extension proves the ten-heavy requirement through maximum 15 on S13.
* Missing-direction edges use distinct heavy partners. Sorting their
  pair ceilings gives the exact partner threshold used in 745 exclusions.
* With at least9 heavy residues, three missing directions are independent.
  For a price lambda,
  their capacity is at most lambda*(n2+2*n3) plus each heavy fibre's largest
  surplus E_k(w)-lambda*k, for k=0..3. A value below48 is impossible.
  The E tables are checked from only276 subsets of cubes of size<=8,
  followed by exact coset convolution. This adds205 exclusions.
* The all-edge tetrahedron14 bound, optional hyperplane crossing-pair
  constraints, and optional Q211 paired-space constraints are included
  with their own soundness notes and finite controls.

WHAT THE FOUR REFUTATIONS USED
-----------------------------
All four accepted searches used the unchanged initial Round8 mode:
ten-heavy/full-heavy-cover plus all-edge tetrahedral capacities. Each
finished within its120-second search budget. Proof checking took extra
time. Later eleven-heavy, incidence, hyperplane and Q211 results were
not retrofitted into those accepted formulas.

The proof pipeline reconstructs LRAT with pinned DRAT-trim and checks it
with the pinned CakeML checker against the original strengthened CNF.
Compact replacement proofs have separately passed the same original-CNF
check. The portable replayer regenerates every exact formula.

    research_round8/strengthened/CERTIFICATE_MANIFEST.json
    research_round8/strengthened/compact/COMPACT_CERTIFICATE_MANIFEST.json
    research_round8/strengthened/compact/COMPACT_CERTIFICATE_REPLAY.json

REPLAY
------
From the extracted Kakeya_Round8 folder, run:

    python3 VERIFY_ROUND8.py

This checks all new finite results and all four compact certificates,
then rebuilds the exact ledger. It performs no SAT search and requires
no network access. Use ordinary Python3 with assertions enabled and a
C compiler/C++ compiler for the bundled proof-checker sources. Do not
run Python with -O. The inherited Round7 payloads are hash-bound to their
completed checkpoint; they are not all re-certified by the Round8 driver.
Their original sources and replay scripts remain in the package.

For a quick integration pass after a complete new proof replay already
exists, the explicit receipt-binding mode is:

    python3 VERIFY_ROUND8.py --reuse-checked-certificates

That mode is labelled as reuse in its receipt; it does not claim fresh
proof checking. The default command checks all four new proofs afresh.

NEXT PREPARED ATTACK
-------------------
    research_round8/NEXT_ATTACK_QUEUE.json
    research_round8/incidence/encode_next_frontier.py

The queue contains54 pending marked cases:27 each at exact maxima12 and13
on support13. Their sources, scope and new incidence cuts are prepared.
No checked exclusion is claimed merely because a case is queued.
The next maximum-eleven branch has9 support14 affine classes; these are
not automatically9 marked solver cases.

CURRENT LIMITS
--------------
The Python encoders and entire Kakeya reduction are not formalized in a
proof assistant. Mathematical soundness, census completeness and correct
encoding remain obligations alongside the checked propositional proofs.
Model-agent reviews are not independent human refereeing.

The established exact minima in dimensions2 and3 remain10 and22. The
dimension4 target46 and dimension5 target94 remain open. Historical
session snippets were reconciled without promoting unseen or incomplete
proof archives. No claim is made that a remote background sweep is live.

ARCHIVE CONTENTS
----------------
The sealed Round7 payload is preserved byte for byte, including all
earlier packaged work. Only the four new large untrimmed Round8 DRAT
streams are replaced in this ZIP by freshly checked compact versions.
Every original CNF, original proof hash, scope record, receipt, source
and compact proof needed for replay is retained. Compiled binaries,
caches and temporary reconstructed LRAT streams are unnecessary.

The latest status is in the Round8 files. Earlier reports and monographs
are historical checkpoints and retain their original dates and counts.
