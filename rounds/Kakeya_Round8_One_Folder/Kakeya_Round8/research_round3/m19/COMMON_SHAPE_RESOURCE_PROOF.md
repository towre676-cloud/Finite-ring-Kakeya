# One common affine-rank mode across all fibre incidences

## Scope

The inputs are exactly the frozen round2 M19 survivors:21,356 selected support11 weight/own-direction profiles and9,115 support12 profiles, each of total weight93. The19-point hub is at residue0. Every exclusion in this stage is uniform over all residue placements and all tangent-fibre shapes, for both rings. The output is not an exhaustive count of actual Kakeya sets, and surviving profiles are not constructions.

## 1. Actual edge capacities between positive low-rank fibres

Let A_a and A_b be distinct nonhub fibres, each with positive own pair count. Let their affine direction spaces H_a,H_b have dimension at most3. Own positivity gives a in H_a and b in H_b. If their edge in direction d=a+b is active, d belongs to both direction spaces, so both a and b belong to H_a intersect H_b. Since a,b are distinct nonzero vectors over F2, their span has dimension2.

The actual quotient pair-label sumset is contained in a coset of

    (H_a+H_b)/<d>.

Its dimension is at most3+3-2-1=3. Therefore its cardinality is at most8. This bounds the actual quotient sumset, not the coarse scalar M(p,q). For inactive edges the capacity is zero. Consequently the valid local cap for two such positive low-rank fibres is

    C(p,q)=min(M(p,q),8).

All other edge types retain M(p,q). Both rings satisfy the same bound because the carry is only a translation of the quotient sumset.

## 2. A stronger bound on their outside-support subgraph

For r selected positive low-rank fibres, restrict to residue edges whose directions lie outside pair-active support S. Every actual edge capacity is at most8. A positive triangle at residues a,b,c has linearly independent residue vectors: a dependence would be a+b=c, putting that edge direction inside S. Own positivity and the active triangle place span(a,b,c) in all three direction spaces. They all therefore equal this three-space, and every actual quotient-sumset capacity on the triangle is at most4.

Normalize capacities by4. Every edge weight lies in[0,2], and any edge of weight greater than1 has no common positive neighbor. If such an edge uv exists in an r-vertex graph, each other vertex contributes at most2 to the edges incident with u or v. Removing u and v therefore removes total weight at most2r-2. Induction gives total weight at most floor(r^2/2). If no edge has weight greater than1, total weight is at most C(r,2), which is no larger. Thus

    total actual outside-support capacity within the group
        <= 4*floor(r^2/2).

This argument works for mixed six-, seven-, and eight-point fibres of affine rank3, as well as for cubes.

## 3. Complete low-rank/high-rank mode split

For positive-own fibres of weights6,7,8, branch according to whether their affine rank is3 (mode1) or greater than3 (mode2). Other fibre types remain unbranched (mode0).

The full pair spectrum of an affine-rank3 fibre is uniquely determined:

    w6: six pair counts2 and one pair count3;
    w7: seven pair counts3;
    w8: seven pair counts4;

with all other directional counts zero. These spectra also force affine rank3. For w6, a maximal3-pair direction is a period and the fibre is the union of three cosets of a line, which lies in an affine three-space. For w7, its seven maximal directions form the near-period three-space, and the fibre is that coset minus one point. For w8, its seven period directions form its three-dimensional stabilizer, and the fibre is a coset of that stabilizer. Conversely these spectra follow directly by taking complements of two, one, or zero points in an eight-point affine space.

The positive-own paired-block catalogue is split by the same affine-rank mode. It is independently complete by enumerating normalized sets containing0,e1,...,er for ranks3,4,5 and weights6,7,8, then every positive own direction. Only594 normalized sets are needed. The distinct block-histogram counts are

    weight6: low2, high4;
    weight7: low1, high9;
    weight8: low1, high16.

The normalization preserves affine rank and direction labels up to linear permutation. The full frozen round2 spectra and block catalogues remain in use for unbranched types.

## 4. Exhaustive common-mode branches

For each weight w in{6,7,8}, let n_w be the number of positive-own outer fibres of that weight. Enumerate every choice0<=k_w<=n_w for the number assigned the low-rank mode. A branch fixes one common mode for every fibre. The fibres of identical weight and own flag are interchangeable in the ensuing label-free resource bounds, so count branches cover every possible actual mode assignment.

Importantly, all incidences involving a given fibre use the same mode in a branch. A low-rank fibre cannot use a high-rank spectrum to improve one endpoint bound, or vice versa. Low-low pair caps use the8-bound simultaneously on all those edges.

## 5. Two valid resource channels per branch

### Full graph including the hub

Use the round2 hub-inclusive heavy/light resource bound, now with the mode-restricted full spectra and the cap C(p,q) on low-low pairs. The own slot still has score2*M(p,9)-ell*p, with the recorded own flag. Every selected nonhub-heavy slot has score2*C(p,q)-ell*p, where C=M unless both modes are low.

All31 residue directions require16 quotient lifts, so doubled total demand is992. The cutoff runs from0 through8, keeping the hub heavy. The same shared heavy-endpoint deficit proof applies.

### Outside-support graph

Use the round2 paired-block matching bound with mode-restricted block spectra and the same pair-specific cap C. A selected slot has score

    max(0,2*C(h,q)-ell*h),

and the baseline is ell times the sum of the15 block maxima. The zero alternative permits absent outside-support edges. There are at most10 other outer vertices, so inactive slots can be padded by unused blocks. Doubled outside demand is32*(32-|S|).

## 6. Combining the subgroup deficit without double counting

Let C0 be the nominal total heavy-edge capacity using the valid pair caps. Let L_i be the certified deficit at heavy vertex i, and let G be the group of low-rank heavy vertices. All nominal edges within G have cap8, because their weights are6,7,8. Section2 gives a group deficit

    D_G = 8*C(|G|,2) - 4*floor(|G|^2/2).

The usual total heavy deficit lower bound is

    max(max_i L_i, ceil(sum_i L_i/2)).

Edges internal to G do not meet vertices outside G. Hence, in addition to D_G, the deficit on the remaining heavy edges is at least

    max(max_{i outside G} L_i, ceil(sum_{i outside G} L_i/2)).

Taking the maximum of these two justified lower bounds combines them without counting the same deficit twice. Twice the resulting loss is subtracted from the doubled heavy/light capacity upper bound. This subgroup correction is used only for the outside-support channel.

## 7. Exact certificates and whole-profile conclusion

Every local matching bound supplies integer dual potentials for every eligible spectrum in that mode. Selected-slot potentials lambda and nonnegative spectrum-entry potentials mu satisfy lambda_i+mu_j>=score_ij on every allowed assignment. Their sum bounds every injective assignment. The fixed baseline is added, and the maximum is taken over every allowed spectrum.

The independent verifier checks every dual inequality, every local mode catalogue, all heavy/light arithmetic, the subgroup-deficit combination, and the complete Cartesian set of count branches. A profile is excluded only if every count branch has a strict contradiction in at least one of the two channels. Different branches may use different valid cutoffs and channels; no branch is omitted.

The producer found17,604 candidate whole-profile exclusions:11,527 on support11 and6,077 on support12. After independent verification these leave9,829 and3,038 profiles respectively, for12,867. These numbers are provisional until the companion exact verifier and root audit both pass.
