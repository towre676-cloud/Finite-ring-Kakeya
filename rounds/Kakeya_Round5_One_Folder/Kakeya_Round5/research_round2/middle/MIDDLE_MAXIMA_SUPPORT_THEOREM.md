# A complete support reduction for all open middle maximum-fibre strata

## Theorem

Let R be Z/4Z or F2[epsilon]/(epsilon^2), and suppose K subset R^5 is Kakeya
with |K|<=93. If its exact maximum tangent-fibre size m lies in12..18,
then its pair-active residue support has at most18 points.

Thus every one of the seven remaining middle maxima has the same new
necessary support bound:

    12<=m<=18  implies  s<=18.

The theorem is uniform over all residue arrangements and actual tangent
fibre shapes. It is a support reduction, not a proof that any complete
maximum-fibre stratum is empty. The unrestricted94-point lower bound remains
open on the outstanding smaller supports.

## Complete arithmetic accounting

Delete singleton fibres, which cannot occur in a primitive four-point line.
The remaining support is a difference basis, hence has at least9 points.
Since9*12>93, one can pad within the existing support, preserving maximum m,
to total93. It suffices to consider all nonincreasing partitions of93 into
s integers between2 and18, with largest part12..18 and19<=s<=32.

The independent completion replay regenerates all747,922 such partitions.
Their disjoint exclusion stages are:

| Method | Entire weight multisets excluded |
|---|---:|
| Global pair budgets and maximal-direction quotas | 747,867 |
| Exact local pair-spectrum assignment | 19 |
| Missing heavy directions and light-pair resources | 31 |
| Unique cap-six hub savings | 3 |
| Three missing directions: triangle obstruction | 1 |
| Six missing directions: halfspace obstruction | 1 |
| **Total** | **747,922** |
| **Remaining** | **0** |

The first stage leaves exactly three profiles at support20 and52 at support19.
All other supports in the theorem have already closed. The19 spectrum cuts
are all at support19. The other36 profiles are excluded by short analytic
geometric lemmas. No affine support-orbit census is used for those lemmas.

## The proof ingredients

GLOBAL_SUPPORT_REDUCTION_PROOF.md develops the global resource inequality.
For actual fibre pair counts, all31 residue directions demand16 lifted
classes each. Therefore the sum of edge capacities is at least496. Shared
pair budgets, maximal-direction quotas and a heavy/light split give a
certified doubled upper bound B. A partition is excluded when B<992.
The producer and independent replay use different local optimization
recurrences, and all inequalities are integer inequalities.

The exact-spectrum stage replaces the local budget relaxation by an
assignment of neighbor directions to distinct entries of a genuine fibre's
complete pair-count spectrum. The complete spectrum census is in
../geometric/PAIR_SPECTRUM_CENSUS.json. The assignment producer outputs integer
dual certificates. The verifier checks their inequalities directly and does
not run or trust a matching optimizer. Its proof is the no-own-direction
version of ../geometric/FULL_PAIR_SPECTRUM_RESOURCE_PROOF.md.

DIFFERENCE_AND_LIGHT_RESOURCE_LEMMAS.md proves the geometric completion:

* Eight residues have at most25 nonzero pair differences.
* Nine residues have at most28 nonzero pair differences.
* If eight residues attain25 differences, their six missing directions
  form an affine three-flat with a line removed and lie in a character
  halfspace.
* Directions missing from a heavy support must spend enough pair mass
  from light fibres; a unique larger hub can save only in the one direction
  connecting it to a particular light residue.

The two final profiles are

    A=(12,8^6,6^2,3,2^9),
    B=(12,8^6,6,5,4,2^9).

For A, nine heavy bases leave at least three missing directions and the
light budget forces exactly three. Those missing directions cannot form
a triangle, whereas the three differences of the three-point light fibre
do; only11 light pairs are available where12 are required.

For B, eight heavy bases must attain their maximum25 differences. Their
missing six directions lie in a character halfspace. The two larger light
fibres, of sizes5 and4, contribute at most6 and4 pairs in that halfspace;
the nine two-point fibres contribute at most9. The resulting upper19
contradicts the required22.

These arguments only use necessary cardinalities of actual lifted coverage,
so both ring carries are automatically respected.

## Independent verification and deliverables

Run the following in order:

    python verify_global_spectrum_cuts.py
    python verify_middle_high_support_completion.py

The first verifies233,525 matching duals, checking92,294,719 exact integer
inequalities, and then verifies23,400 whole-weight-multiset exclusions.
Of those,19 are used above at support19. The other23,381 are additional
selected exclusions at supports15..18; they do not constitute support
closures there and are accounted for separately.

The second independently regenerates all747,922 partitions and composes
the finite and analytic stages. Its receipt is
MIDDLE_MAXIMA_SUPPORT_COMPLETION.json. It checks that the basic survivor
list is exactly the55-profile boundary and that no profile remains.

GLOBAL_SPECTRUM_INDEPENDENT_REPLAY.json records the exact dual and candidate
hashes. GLOBAL_SPECTRUM_CANDIDATES.jsonl preserves every newly certified
weight multiset and its numerical bound. GLOBAL_SPECTRUM_DUAL_CERTIFICATES.jsonl
contains the integer certificates; the checker needs no solver dependency.

The earlier GLOBAL_SUPPORT_INDEPENDENT_REPLAY.json remains a valid, weaker
560,918-partition verification. The complete747,922-partition theorem in
this note supersedes its preliminary per-maximum support thresholds.

## Additional local theorems from this continuation

HALFSPACE_ENERGY_THROUGH_EIGHTEEN.md proves the exact halfspace pair-square
energy values for weights13..18:

    222,301,392,512,520,561.

STABILITY_AND_HALFSPACE_ENERGY_THROUGH_TWENTY.md sharpens the nine-point
stability gap and extends the exact table to weights19 and20, with values
618 and712. These analytic local theorems are independent of the finite
middle-support reduction and do not contribute extra exclusion counts.
