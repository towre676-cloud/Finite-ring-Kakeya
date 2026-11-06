# Independent review of the full-hub outer-cap-twelve theorem

Reviewed root proof: `research_round3/root/FULL_HUB_OUTER_TWELVE_THEOREM.txt`.

**Verdict: PASS.** The proof establishes, for both rings and every n>=6, the sharp bound3*2^n-2 and generalized-star equality classification under the stated full-hub and outer-cap12 hypotheses. It does not imply an unrestricted Kakeya theorem.

The rank extension of the small-fibre energy table is correct. A set of size w and affine rank at least6 has augmented relation-code dimension at most w-7. Its affine planes inject into nonzero relation vectors. The identity E_pair=binom(w,2)+6*(number of affine planes) gives upper bounds21,34,54,87,145,252 for weights7..12, all below the independently complete F_2^5 maxima. Thus the table is dimension-independent, with the stated census dependency.

The restricted-direction bound R_z(w) correctly uses at most q(w) maximum pair counts and count at most floor(w/2)-1 elsewhere, capped by total energy. The low-residue defect inequality and point-excess budget are exact. Dropping the number-of-fibres restriction in the knapsack only enlarges its feasible set.

The verifier's recurrence was additionally checked by explicitly enumerating every nondecreasing integer partition of each budget0..2z with part sizes1..10, for z=2..12. This enumeration reproduces all eleven maxima14,47,74,157,193,239,343,409,564,609,630. Every value is strictly below64(z-1)+z+1.

The large-z coefficient299/10 is valid for every weight3..12. Its resulting bound at z=13 is3817/60, strictly less than64, and decreases for larger z.

The one-low-residue equality argument is valid: its sole potentially exceptional configuration has one four-point fibre, one empty fibre, and all other outer fibres of size two. Covering the empty residue's direction forces every two-point fibre's difference to equal that direction; then another residue direction has no possible contributing edge. With no low residue, the total size forces all outer fibres to have size two, and their own pair directions are necessary, giving precisely generalized stars.

Exact review controls and the reviewed proof/source hashes are recorded in `FULL_HUB_TWELVE_INDEPENDENT_REVIEW.json`.
