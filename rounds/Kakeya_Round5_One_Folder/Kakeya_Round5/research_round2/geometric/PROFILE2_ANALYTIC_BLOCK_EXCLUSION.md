# A short geometric exclusion of support11 parent profile2

The profile has a19-point hub and ten other own-positive fibres with weights

    2, 3, 3, 8, 8, 8, 8, 8, 8, 18.

Its total weight is93. Every own-positive fibre contains a pair in the direction toward the hub. The pair-active residue support has11 points, so the21 directions outside that support require total quotient-lift capacity at least21*16=336.

Use the paired blocks {d,d+a} at each nonhub residue a. Every outside-support active edge uses a different block at that vertex.

**A weight8 fibre has a sharp geometric alternative.** If it is an affine3-flat, its seven maximal pair directions are the nonzero directions of that flat. Its own-positive direction a lies in this3-dimensional direction subspace, leaving exactly three paired blocks with nonzero maxima, each4. If it is not an affine3-flat, it has at most one maximal pair direction. Indeed maximal pair count4 means translation invariance. Those directions together with0 form the stabilizer H. If |H|>=4, then an8-point set is either one coset of an8-point subgroup or two cosets of a4-point subgroup. The union of two such cosets over F2 is itself an affine3-flat. Thus a nonflat has |H|<=2. Consequently it has at most one block maximum4, with all remaining block maxima at most3.

Call the six weight8 fibres and the weight18 fibre heavy. There are21 heavy pairs, each with quotient capacity at most16, for nominal total336. Fix a weight8 heavy vertex. It has five weight8 neighbors of cap4 and one weight18 neighbor of cap9.

If the fibre is a flat, its three nonzero paired blocks give incident capacity at most3*16=48. If it is not a flat, placing its possible block maximum4 against a cap4 neighbor gives at most

    16 + 4*12 + 16 = 80.

Placing that block against the cap9 neighbor gives at most16+5*12=76. If there is no block maximum4, the same upper bound80 still holds. Thus the incident total is always at most80, a loss of at least16 from the nominal six-edge total96.

There are six weight8 vertices. Their incident losses sum to at least96. Each edge deficit is counted at most twice, so the actual heavy-heavy capacity is at most336-48=288.

The own-positive weight2 fibre has its only pair in the own direction and contributes no outside-support edge. Each own-positive weight3 fibre has exactly two other pair directions, which lie in the same paired block, so it contributes to at most one outside-support edge. That edge has capacity at most9, the largest other fibre cap. Counting both weight3 fibres therefore adds at most18, including any possible edge between them safely as an overcount.

Altogether

    C_out <= 288 + 18 = 306 < 336.

This contradiction excludes the whole profile, uniformly over all support arrangements and tangent fibre shapes, for both rings. No full-spectrum or affine-orbit enumeration is required for this hand proof. The stronger exact block-census optimization happens to give294, but306 already proves the exclusion.
