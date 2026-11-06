# Exact paired-direction block compatibility

## Outside-support directions use distinct blocks

Let S be the pair-active residue support, including the19-point hub at0. Fix a nonzero a in S and its fibre A_a. A direction d outside S can contribute at this vertex only if a+d lies in S. Its paired direction d+a cannot also be outside S, because it equals that partner residue. Hence all active outside-support directions at a select at most one member of each pair

    {d,d+a},  d not in {0,a}.

There are15 such blocks. For a fibre A define

    h_A,a({d,d+a})=max(p_A(d),p_A(d+a)).

Every actual outside-support pair count is at most the maximum of its block, and different active outside-support edges at the vertex use different blocks. This gives the finite common-fibre constraint used here.

## The exact block census

The inherited, independently audited affine shape census has382 representatives of all subsets of F2^5. The frozen source is

    research_sources/extracted/Kakeya_Reconciled_Proofs_2026-10-27/halfspace_extension/M11_BOUNDED_GEOMETRIC_REDUCTION.json

For every representative of weight2 through19, evaluate every nonzero own direction a. Record the histogram of the15 block maxima, together with whether p_A(a)=0 or p_A(a)>0. Affine transformations preserve weight, permute directions, and send paired blocks to paired blocks. This produces the complete candidate census.

The local independent replay computes translated intersections for each direction, reconstructs every distinguished-direction histogram, compares all output classes, and checks every stored witness. Root additionally verified completeness without the382-orbit dependency: normalize an own pair to0,e1 and extend it to an affine basis for every positive-own case; enumerate all zero-pair own directions of every normalized set for negative-own cases; use complementation for weights17 through19. This direct normalized-subset enumeration reproduced every histogram. See ../root/ROOT_VERIFIED_BLOCK_CENSUS.json. There are at most138 histograms in any weight/own-flag class. Exact histograms and representative masks/directions appear in PAIRED_BLOCK_MAXIMUM_CENSUS.json.

## Why block maxima suffice

All capacities M(p,q) are monotone in both arguments. Replacing an actual pair count by its block maximum only enlarges capacity. For light fibres of cap at most ell, block maxima also are at most ell, so an outside-support light-light edge obeys

    2*M(p,q)<=2*M(h,k)<=ell*(h+k).

A heavy neighbor whose residue edge is not in an outside-support direction contributes zero. Therefore a local selected-heavy slot uses score

    max(0, 2*M(h,q)-ell*h),                                  (1)

and all such slots are matched to distinct blocks. The zero alternative is necessary: one cannot impose a negative charge for an absent edge. In the M19 profiles there are at most10 other nonhub vertices, fewer than15 blocks, so every inactive slot can be padded by an unused block and receive its zero score.

For a fixed block spectrum h_1,...,h_15, the local light bound is

    ell*sum_b h_b + max_injective_assignment sum_j (1).

Maximize this expression over the complete weight/own-flag block census. This jointly constrains the block budget and its distribution. It is stronger than merely bounding sum h by C(w-1,2) when the own flag is positive.

For a heavy endpoint, take ell=0 and the other heavy caps as slots. The result bounds twice the actual outside-support heavy incident capacity. Absent edges are harmless because all scores then are nonnegative.

## Global upper bound and exact certificates

Use the same heavy/light partition and shared-heavy-deficit argument as in FULL_PAIR_SPECTRUM_RESOURCE_PROOF.md, with the preceding block-local bounds. The nominal heavy graph may include edges absent from the outside-support graph. Such absent edges have actual capacity zero and simply contribute their full deficit; the endpoint deficit argument remains valid.

Every outside-support direction requires16 covered quotient lifts. There are32-|S| such directions, so

    C_out >= 16*(32-|S|).

A computed doubled upper bound strictly below32*(32-|S|) excludes the entire profile for both rings.

Each local optimization has exact integer assignment duals for all eligible block spectra: lambda_i+mu_j is at least the score (1), with every mu_j nonnegative. Their sum bounds any injective selection. Adding ell*sum h and maximizing over all spectra is an upper bound without relying on numerical optimizer correctness. The verifier checks these inequalities directly.

## Stage accounting

Inputs are the full-spectrum survivors after the root outside-support-budget stage:

    support11: 33,775 - 1,437 = 32,338;
    support12: 12,735 - 22 = 12,713.

This block stage excludes5,918 support11 profiles and1,254 support12 profiles, a total of7,172. It leaves26,420 and11,459 respectively, for37,879 tracked profiles. This accounting is disjoint from the spectrum and outside-budget stages by explicit input filtering. The root outside-budget candidates must be independently accepted before this three-stage combined frontier is asserted.
