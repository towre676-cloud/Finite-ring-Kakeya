# Independent review of the M19 actual-role/Hall exclusion

**Review result: PASS.** The analytic argument and the completeness
normalization are valid for the stated inputs. The stage excludes 8,837
support-eleven weight/own-flag profiles, leaving 896 there and 2,902 on
support twelve. The frozen support-eighteen middle-maxima files were not
changed during this review.

## Mathematical checks

1. A unique edge in a direction outside the support has two nonhub endpoints.
   Every outer weight is at most fourteen, as checked for all input profiles.
   If one endpoint had weight at most seven, its pair-label set would have
   size at most three and the other at most seven. Three points lie in an
   affine two-plane. Covering all four cosets of its direction space requires
   at least two points of the other summand in each coset, hence at least
   eight points. Thus full sixteen-label coverage is impossible. Smaller
   summands are excluded by the product bound. The forced weight-eight
   attribute is justified over both rings.

2. For a nonzero support vertex a with q_S(a)=1, the unique edge is exactly
   the hub edge {0,a}. Its outer fibre must be own-positive. Weight at most
   three gives at most one own pair against the hub's at most nine pairs,
   so cannot cover sixteen labels. The forced own-positive, weight-at-least-
   four attribute is justified.

3. S+S=V implies S spans V. With the hub translated to zero, a basis can
   be selected from S and mapped to the coordinate basis by a linear
   automorphism fixing zero. Therefore enumeration of every support
   containing {0,1,2,4,8,16} is exhaustive, with repetitions harmless.
   The C++ recursion and Python combinations loop both enumerate precisely
   the required binomial family. No inherited orbit-class list is needed.

4. The four Hall inequalities are sufficient as well as necessary for the
   two-attribute assignment relaxation. Allocate the r3 vertices needing both
   attributes to a3 eligible fibres. After this, the remaining deficits for
   the L-only and P-only roles are

       max(0,r1-a1),  max(0,r2-a2).

   The other three inequalities ensure their sum is at most a3-r3: if both
   deficits are positive use the nonfree inequality; if exactly one is
   positive use its corresponding L or P inequality. Fill those deficits
   with the remaining both-attribute fibres, then place all leftovers in
   unrestricted roles. The total numbers of roles and fibres agree.
   Therefore no missing Hall subset can change this relaxation's decision.
   Satisfying the relaxation is not claimed to produce a Kakeya configuration.

## Bounded independent replay

The review did not rerun the exhaustive normalized-support census. It read
the proof, its C++ producer, and its independent Python verifier, and checked
the saved census hash against the completed verification receipt.

A separate 0.3-second check reconstructed all twenty-five saved role witnesses
directly from unordered pairs, independently parsed every input profile, and
verified all 88,370 Hall witnesses. It also enumerated all seven nonempty
subsets of constrained role types for every encountered role/attribute pair
and confirmed equivalence with the stated four inequalities. Exact survivor
subtraction agrees with the saved outputs. No M19 data files were modified.

The audit script is review_m19_role_certificates.py. Its receipt is
MIDDLE_AGENT_M19_ROLE_REVIEW.json, including dependency hashes and the explicit
statement that the expensive census was not rerun.
