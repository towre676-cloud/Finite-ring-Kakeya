# Full pair-spectrum compatibility and resource certificates

## Scope

This layer applies to the two rings Z/4Z and F2[e]/(e^2), in dimension five. A residue fibre is a subset A of V=F2^5. For d!=0 let p_A(d) count unordered pairs {x,x+d} contained in A. A weight-w fibre has a **single common pair spectrum**, the multiset of its 31 values p_A(d). Choosing each directional value independently, even subject to its total and maximum-value quota, discards this compatibility.

The M19 input is exactly the 69,205 previously surviving selected weight/own-direction profiles: support11 has51,173, support12 has18,032. These are the previous after-bank lists with the complete quota exclusions removed. This stage does not assert that these lists exhaust every actual Kakeya set, or that a surviving numerical profile is geometrically realizable.

## Complete spectrum census

An affine-rank-r subset of V can be translated and linearly transformed to contain the affine basis 0,e1,...,er and lie in its r-dimensional coordinate subspace. Affine transformations permute nonzero directional pair counts. Therefore it suffices to enumerate every subset of F2^r containing this basis, for r=0,...,5.

For weights at most16, this means at most10 additional points from26 available positions when r=5. The exact numbers of visited normalized sets for r=0,...,5 are

    1, 1, 2, 16, 2048, 10970272.

The enumeration visits every admissible cardinality at every rank; no orbit-canonicalization assumption is used. Duplicate spectra are simply removed. Weights17,...,19 follow by complementation, using

    p_{V\A}(d) = 16 - |A| + p_A(d).

The distinct spectrum counts for weights1,...,19 are

    1,1,1,2,2,3,5,7,9,14,16,21,24,27,30,32,30,27,24.

The census includes an actual 32-bit representative set for every spectrum. Root independently recomputed all unordered differences at each normalized leaf (as opposed to the producer's incremental packed histogram), and checked every representative. See ../root/ROOT_VERIFIED_PAIR_SPECTRUM_CENSUS.json.

## Local assignment upper bound

Let A have weight w. There are distinct selected directions d1,...,dk, and a distinct reserved own direction a. Its own flag f is0 if p_A(a)=0 and1 if p_A(a)>0. Put T=C(w,2), and let q1,...,qk be upper bounds for partner fibre pair counts in these directions. Define the valid quotient sumset upper bound

    M(p,q)=min(16,pq),

except that unordered pairs(3,5),(3,6),(3,7) have bounds13,14,15 respectively.

For an integer ell>=0 consider

    ell*(T-p_A(a)) + sum_j [2*M(p_A(dj),qj)-ell*p_A(dj)].      (1)

For each realizable spectrum h, expand its31 entries p_1,...,p_31. Assign the k selected directions and the one own direction to distinct entries. Selected slot j receives score 2*M(p,qj)-ell*p; the own slot receives -ell*p and is permitted only when p=0 (f=0) or p>=1 (f=1). Maximize the assignment score and then add ell*T. Finally maximize over all realizable spectra. Call the result B(w,f,q,ell).

The actual directional values form one of these assignments, so (1)<=B. Labels and addition relations among directions are relaxed, not imposed. The upper bound is therefore valid uniformly over all residue support arrangements and fibre shapes.

The no-own-direction version omits the reserved slot and uses f=-1. It bounds ell*T+sum_j[2*M(p_A(dj),qj)-ell*p_A(dj)] and is used for the sibling middle-maximum analysis.

## Exact integer matching certificates

Each local bound is accompanied by an integer dual certificate for every eligible spectrum. For selected/own slots i and spectrum entries j, let s_ij be the allowed score. The certificate supplies lambda_i and mu_j satisfying

    mu_j>=0;  lambda_i+mu_j>=s_ij for every allowed assignment.

Any injective assignment therefore has score at most sum_i lambda_i + sum_j mu_j, because its used entries are distinct and all unused mu_j are nonnegative. Taking the maximum of these certified bounds over all spectra, then adding ell*T, proves B. No floating point arithmetic, optimizer tolerance, or claim of numerical optimality is needed for exclusion.

The producer computes these witnesses with rectangular integer assignment, but the verifier only checks the displayed inequalities. It does not call or trust that algorithm.

## From local bounds to global capacity

Remove the19-point hub at residue0. Other pair-active fibres have weights w_i, caps c_i=floor(w_i/2), and own flags f_i. Let H={i:c_i>ell}, L the remaining indices, and q_H the multiset of heavy caps.

For an edge between two light vertices, with actual pair counts p<=ell and q<=ell,

    2*M(p,q)<=2*p*q<=ell*(p+q).

For a fixed light fibre, the sum of all its pair counts outside its own direction is exactly C(w_i,2)-p_i(own). Its selected heavy-neighbour directions are distinct and different from own. Replacing light-light incidences by the preceding linear bound and using (1) gives

    2*C_off <= 2*C0 + sum_{i in L} B(w_i,f_i,q_H,ell),

where C0=sum_{i<j in H}M(c_i,c_j).

For heavy i, let

    base_i=sum_{j in H\{i}}M(c_i,c_j),
    loss_i=base_i-B(w_i,f_i,q_{H\{i}},0)/2.

Each actual heavy-heavy edge capacity is bounded by M(c_i,c_j), and each heavy incident total is bounded by the local assignment result. Hence total heavy-heavy loss is at least

    max(max_i loss_i, ceil(sum_i loss_i/2)).

Subtract twice this quantity from the previous doubled upper bound. This step remains an upper bound because heavy directions leading to light fibres were not charged against the heavy endpoint optimization.

Finally, if z is the number of own-zero directions and u is the number of own-positive fibres of weight2 or3, the previously proved off-hub demand is

    D = 16*z + 7*u + max(0,u-3).

All current inputs have u<=3. An upper bound strictly below2*D excludes the complete weight/own-direction profile for both rings.

## New M19 counts

Support11:17,398 exclusions from51,173 inputs, leaving33,775.
Support12:5,297 exclusions from18,032 inputs, leaving12,735.
Total:22,695 new exclusions, leaving46,510 tracked profiles.

Every new ID lies outside all earlier plain, heavy, rational-price, and maximum-quota exclusion batches. Verification of integer matching duals and all profile arithmetic is recorded separately. These counts must not be merged with later screens unless their inputs are filtered by these exact IDs.

## A small conceptual example

A four-point fibre has only two possible spectra: either six1s (an affine-independent tetrahedron), or three2s (an affine plane), with all remaining counts zero. A six-point fibre has only three possibilities:

    fifteen1s;
    nine1s and three2s;
    six2s and one3.

Thus a six-point fibre possessing a direction with three pairs cannot independently allocate pair-count1 to other directions: all its other nonzero counts are2. The former total/maximum-quota relaxation allowed such combinations. The full-spectrum bound removes precisely this kind of incompatible local resource allocation.
