# Joint hub and outer-fibre spectrum resource bound

## Purpose and scope

This stage includes the19-point hub in the capacity graph. The full-spectrum off-hub screen previously bounded nonhub capacity and subtracted a coarse contribution for hub edges. The present bound forces each outer fibre's actual own pair count to share the same spectrum as its other directions, while also imposing the hub's own19-point spectrum in its endpoint bound.

All31 nonzero residue directions require16 quotient lifts. Thus total edge capacity satisfies C_total>=496. The upper bound applies to each complete weight/own-direction profile, uniformly over residue arrangements and fibre shapes, for both rings.

## Local outer-fibre bound

Fix a cutoff ell in{0,...,8}, so the hub of cap9 is heavy. All other heavy caps are q1,...,qk. For an outer fibre A of weight w, reserve the own direction toward the hub and impose its recorded flag: p_own=0 if flag0, p_own>=1 if flag1. The k heavy-neighbor directions are distinct and different from own.

For each realizable full pair spectrum, injectively assign these k+1 directions to spectrum entries. A nonhub selected slot j receives score

    2*M(p,qj)-ell*p.

The own slot receives score

    2*M(p,9)-ell*p,

subject to its flag restriction. Add ell*C(w,2), and maximize over all allowed assignments and all realizable spectra. Call this H(w,f,q,ell). The actual fibre's total incident heavy contribution plus its light-edge linear budget is bounded by H, by exactly the usual heavy/light resource argument. The own slot is included once and consumes one spectrum entry.

For a heavy outer endpoint, ell=0 and only the other heavy outer caps are selected. The own slot includes its hub edge. H/2 bounds its total heavy incident capacity.

## Hub endpoint

An own-zero outer fibre has no edge capacity to the hub. Omit these zero-capacity hub slots. Match the cap of every own-positive heavy outer fibre to distinct entries of one realizable19-point hub spectrum; there is no reserved own direction for the hub. At ell=0 the resulting matching bounds twice the hub's heavy incident capacity.

## Global heavy baseline and deficit

The nominal heavy graph contains all outer-heavy pairs with cap M(ci,cj). A hub edge has cap M(9,ci) when the outer own flag is1 and zero when its flag is0. Let C0 be the sum of these caps.

For each heavy vertex, including the hub, subtract its certified incident upper bound from its nominal incident sum, obtaining loss_i>=0. Any actual heavy-heavy configuration then has total capacity at most

    C0 - max(max_i loss_i, ceil(sum_i loss_i/2)).

Combining this bound with H for all light fibres yields the doubled total upper bound. A value strictly below992 excludes the full profile. The computation takes the best bound among ell=0,...,8; it does not claim that these are the only possible resource bounds.

## Exact verification

Every matching upper bound has integer dual certificates for each eligible full pair spectrum. Selected/own slot potentials lambda and nonnegative spectrum-entry potentials mu obey lambda_i+mu_j>=score_ij for all allowed assignments. Their sum gives an upper bound on every injective assignment. The independent checker validates these inequalities and all profile arithmetic, rather than trusting an assignment solver or floating point output.

## Disjoint stage accounting

Inputs are the previously surviving profiles after the full-spectrum, outside-support-budget, and paired-block stages:

    support11:26,420;
    support12:11,459.

This stage excludes5,039 and2,344 respectively, a total of7,383. The remaining tracked lists have21,381 and9,115 profiles, a total of30,496. All exclusions are disjoint by explicit input filtering. Prior outside-budget and paired-block stages must also pass their independent checks before using the combined counts.
