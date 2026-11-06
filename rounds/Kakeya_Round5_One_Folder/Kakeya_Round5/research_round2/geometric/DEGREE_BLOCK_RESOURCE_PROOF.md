# Coupling paired blocks to actual residue-support degrees

Let S be the pair-active residue support containing the hub0, and let s=|S|. Necessarily S+S=F2^5, since each nonzero residue direction must have some pair of pair-active residue fibres. On S\{0}, define the outside-support graph by joining a and b precisely when a+b is outside S.

## Complete degree patterns

The frozen382 affine representatives yield44 hub-marked difference-covering supports of size11 and96 of size12. They give12 and18 different outside-degree multisets respectively. All hub choices are included, then translated to0. OUTSIDE_SUPPORT_DEGREE_PATTERNS.json records every case and graph.

There is a small independent completeness check: a hub-marked rank5 support can be affinely normalized to contain0,e1,...,e5, with the hub fixed0. Rank5 is necessary for S+S=F2^5. Enumerate65,780 normalized size11 sets and230,230 size12 sets; retain those whose sumset is all32 points and compute their outside-degree multisets. This independently recovers the same12 and18 patterns, without depending on the old affine-orbit classification.

## A mandatory restriction at maximum-degree vertices

At a vertex a, the other s-2 nonhub residue points b are paired by b<->b+a. If both belong to S, they contribute an offhub residue edge in the own direction a and neither is an outside-support neighbor of a. If exactly one belongs to S, it contributes one outside-support neighbor. Therefore

    d_out(a) = s-2 - 2*r_a,

where r_a is the number of offhub residue edges in direction a.

If d_out(a)=s-2, then r_a=0. The sole residue edge in direction a is the hub edge, which must cover all16 quotient lifts. Its capacity is at most9*p_Aa(a). Thus an own-zero fibre or a fibre of weight2 or3 cannot occupy a maximum-degree vertex. This necessary restriction is imposed in the degree assignment.

## Exact local incident bound at degree d

For a given outer fibre type (w,f), consider all its15 paired-block maxima from the exact distinguished-direction census. Its actual outside-support edges use exactly d distinct residue-neighbor slots and distinct blocks. The other nonhub fibre caps are known as a multiset q1,...,qk, where k=s-2, although their placement in the graph is relaxed.

For a fixed block spectrum, maximize the sum M(h,q) over all matchings of exactly d neighbor slots to distinct blocks. Maximize again over all block spectra compatible with (w,f). The result F_i(d) is a valid upper bound on the actual outside-support incident capacity at that vertex.

To certify the cardinality-d matching, append k-d dummy block columns, each giving score1000, and assign all k neighbor rows to distinct columns. Every true cardinality-d matching extends to such an assignment using every dummy. Hence any integer matching dual bound minus1000*(k-d) is an upper bound on the desired incident capacity. Exact dual witnesses are supplied for every spectrum. All real scores are at most16; the large dummy value also makes the producer's optimal solution use all dummies, although this optimization fact is not needed by the checker.

## Assigning fibre types to support degrees

For each complete support-degree pattern d1,...,d_{s-1}, assign the known fibre types to its slots. Row i and degree slot j receive upper-bound score F_i(dj). Forbid the maximum-degree assignments identified above. If the pattern has fewer nonmaximum slots than forbidden fibre types, it is impossible immediately. Otherwise an exact integer assignment dual bounds the sum of incident capacities over every possible placement of the types.

Every actual outside-support edge is counted twice, so C_out is at most half this sum. Take the maximum bound over every possible degree pattern. If this maximum is less than32*(32-s), the whole profile is excluded, since C_out>=16*(32-s).

## New disjoint stage

Input is exactly the30,496 profiles surviving the hub-inclusive spectrum stage. This degree/block layer excludes25 additional support11 profiles and no support12 profiles. It leaves21,356 support11 and9,115 support12 profiles, total30,471. All25 exclusions are uniform over all residue supports and fibre shapes. The modest gain indicates that further progress requires more of the support adjacency and own-direction coverage constraints than degree alone.
