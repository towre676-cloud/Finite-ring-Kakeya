# Independent review of the new halfspace-energy bounds

Reviewed file: `research_round2/middle/HALFSPACE_ENERGY_THROUGH_EIGHTEEN.md`.

The six new values

    h(13),...,h(18) = 222,301,392,512,520,561

pass an independent analytic review. This review concerns the new extension; the pre-existing proof through twelve remains its stated dependency.

1. For an eight-point nonflat set, affine dimension at least four makes the augmented point matrix have rank at least five and kernel dimension at most three. Its distinct zero-sum four-subsets inject into the at most seven nonzero kernel vectors. The resulting self-energy upper bound 344 is correct in every ambient dimension.

2. For a nine-point set, the directions with four pairs close under binary addition, by the symmetric-difference triangle inequality and odd parity. If this subspace contains a four-point subgroup L, the exact occupancy identity `3=sum k(4-k)` permits precisely one partial L-coset; cardinality nine forces occupancy one, leaving two full L-cosets. Their union is an affine three-flat, and the remaining point lies outside it. Its pair spectrum is seven counts four and eight counts one, giving self-energy 561. Otherwise at most one pair count is four, and the stated upper bound 529 follows.

3. The six-point energy bound 168 follows from at most three zero-sum quadruples; complementary pairs with the fixed total xor are disjoint. The seven-point bound 301 and ten-point bound 840 follow from the stated pair-count caps and period count. The ten-point bound is only used as an upper bound, with no false exactness claim.

4. In the 6+7 split, the self-energy product is 50,568, less than 225 squared. Mixed energy is integral and congruent to 42 modulo four, so the next admissible value above 222 is 226; hence 222 is the correct bound. All smaller splits have the stated elementary upper bounds.

5. In the 8+9 and 8+10 splits, a flat eight-point side gives `8 sum k_C^2`; distributing nine or ten points among cosets of capacity eight gives 520 or 544. The nonflat alternatives are bounded respectively by the square roots of `344*561` and `344*840`, strictly below the advertised thresholds.

6. The attainment constructions can also be checked without enumeration. Their pair-spectrum dot products give mixed energies:

    6+7: 42 +4*45  =222,
    7+7: 49 +4*63  =301,
    7+8: 56 +4*84  =392,
    8+8: 64 +4*112 =512,
    8+9: 72 +4*112 =520,
    9+9: 81 +4*120 =561.

No defect, hidden dimension assumption, or unsupported equality assertion was found in the six new bounds.

## Subsequent extension to nineteen and twenty

The later addendum `research_round2/middle/STABILITY_AND_HALFSPACE_ENERGY_THROUGH_TWENTY.md` also passes independent analytic review. In particular:

- The relation-code and sixteen-point complement formulas correctly give the non-cube nine-point stability bound465 and the dimension-independent ten-point maximum712.
- For an eight-flat plus one outside point, the exact mixed-correlation formula is `q+sum[8(x^2+y^2)+4xy]`. The stated piecewise function g is correct, and all three cases of its superadditivity proof hold.
- At q=10 the structured mixed maximum is618; at q=11 the sufficient structured upper bound is691.
- The split comparisons proving `h(19)=618` and `h(20)=712` are valid, including the close comparison `344*1464=503616 <712^2=506944`.
- Initial segments of sizes9 and10 give mixed energy `10+8*(64+4)+4*16=618`. Two ten-point initial segments have pair spectrum one count5, six counts4, and eight counts2, giving self-energy `100+4*(25+96+32)=712`.

The sufficient eleven- and twelve-point bounds are used only as upper bounds, not incorrectly advertised as sharp maxima.

## Separate audit: outside-support selector budget

The root's new proposed budget was independently checked as follows. Fix a nonzero residue a, and decompose a fibre A into t full a-cosets and s singleton a-cosets, so w=2t+s. A pair of full cosets contributes `(2,2)` to a direction block `{d,d+a}`, a full/singleton coset pair contributes `(1,1)`, and a pair of singleton cosets contributes either `(1,0)` or `(0,1)`. If at most one direction from every block is selected, then

    sum_selected p_A(d)
       <=2 binom(t,2)+ts+binom(s,2)
        =binom(w,2)-t(w-t).

The inequality remains valid when several coset pairs contribute to the same direction block, because the maximum of their sums is at most the sum of their individual maxima. For t>=1, this is at most `binom(w-1,2)`.

If S is the pair-active residue support and a is in S, a direction d outside S can serve an active edge from a only when a+d is in S. Its paired direction d+a then has partner d outside S, and so cannot also serve an active edge. Therefore the selector hypothesis is satisfied. This argument is valid with either full occupied support or pair-active support, provided the latter is used consistently. Ring carries have no role in the pair-count budget.
