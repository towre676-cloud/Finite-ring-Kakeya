# Bounded review of the separate nine-heavy degree screen

I read the complete C++ producer and NINE_GEOMETRY_PROOF.md supplied by the
root agent. The following is a model-agent mathematical/code cross-check
within this session, not an external human review.

The geometric table was independently recomputed by direct Python set
differences and neighbour counts over all2930 affine-basis-normalized
nine-point sets. It has exactly the seven stated rows, with normalized
multiplicities260,750,660,810,60,60,330 for missing counts3,4,6,8,9,10,16.
Each row has23 outside positions and total degree9r. The code and receipt
for this separate corroboration are verify_nine_degree_types.py and
NINE_DEGREE_TABLE_CROSSCHECK.json.

The resource and assignment steps are sound:

* The accepted M(p,c) is nondecreasing in c for all relevant integer caps,
  including the special three-point values. Therefore any actual set of
  k heavy-neighbour caps is bounded by the k largest heavy caps, after
  assigning its pair counts to the corresponding sorted caps.
* Each local DP keeps the pair-mass budget and maximal-direction quota
  jointly. Permitting unrealizable allocations and unused mass is a safe
  upper relaxation.
* R(w,k) is nondecreasing in k because each new slot may take pair count0.
* Any L distinct outside positions have sorted degrees coordinatewise
  bounded by the largest L degrees in that geometry row. Replacing them
  by those slots and maximizing over a bijective light-weight assignment
  therefore bounds every actual placement, without reusing a rare role.
* The C++ assignment subset DP performs exactly this maximum. The
  missing-direction count and degree histogram remain coupled, and every
  one of the seven rows must be strictly below its own demand32r.

The odd-weight maximal-direction subspace proof explicitly handles the
trivial N=1 case before asserting exactly one partial coset. I checked the
corrected wording. For N>1, the identity
sum_cosets k(N-k)=N-1 proves the required single partial coset and the
congruence w=+1 or-1 modulo N. The closure argument for maximal directions
is valid: a partial two-point coset would contribute two unmatched points
in at least one of the two directions, contradicting the permitted zero
or one. The even-weight period-subspace case is also valid.

This review checks the formula, hypotheses, complete small geometry table,
and producer logic. It does not independently recompute each of the4088
resource-profile certificates; the root agent's separate backward-DP and
degree-multiplicity assignment checker performs that full replay.

The saved geometry cutset and the240 multi-price cuts were compared as
sets of complete weight tuples. Their overlap is zero. Their union has
4328 profiles, leaving271427 from the common275755-profile baseline,
subject to successful completion of the separate geometry replay.
