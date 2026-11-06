# Independent full support10 weight universe

This stage leaves the original641-profile stage unchanged. It starts
from every nonincreasing ten-part partition of93 with weights between2
and18, with no input from an earlier survivor screen.

There are102,842 such profiles:102,620 have maximum12 through18, and222
have maximum10 or11. The producer recursively generates every partition;
the verifier independently counts them by coefficient extraction from
the product over w=2,...,18 of (1-z t^w)^(-1), retaining coefficient
z^10 t^93. Counts are also checked separately for each exact maximum.

The original role inequalities leave174 profiles. Every one has exactly
one allowed central weight multiset. An additional local resource bound
reduces this to11, as follows.

## Three independent ordinary directions

In the canonical support (V minus0) union (W minus0), an ordinary vertex
v in V minus0 has unique directions v+w for the three nonzero w in W.
These three directions are linearly independent: they are distinct and
nonzero, and their sum is v, which is nonzero. Their Cayley graph on
F2^5 is therefore a disjoint union of four copies of the three-cube Q3.

The maximum induced edge counts in one Q3, for weights0 through8, are

0,0,1,2,4,5,7,9,12.

Both programs check this tiny table by complete enumeration, using
different representations. The bound for a weight-w fibre in all of
F2^5 is the maximum of the sum of four table entries whose indices sum
to w. The producer uses forward convolution; the verifier enumerates
all9^4 index quadruples.

In particular, a weight5 ordinary fibre can supply at most5 pairs in
its three unique directions. Those three edges each require at least2
pairs when every fibre weight is at most18, so weight5 is impossible.
The complete cube resource gives exactly this additional improvement
on the174 bare-role survivors:163 are excluded, leaving11.

## Complete independent role enumeration

The producer tests every distinct choice of three central weights in
every partition. The verifier instead first chooses every nondecreasing
central triple in2,...,18. It derives the eligible ordinary weights
from the pair cap, cube edge resource, and the central pair-count caps.
It then enumerates every seven-part ordinary multiset of the required
remaining total, imposing the central mass budgets. Thus the verifier
does not share the producer's partition order or profile-wise search.

Both obtain exactly the same174 bare survivors and11 cube survivors,
including all allowed central triples. The11 consist of the original
seven profiles, plus

- (18,17,16,6^7), central (18,17,16);
- (18,16,16,7,6^6), central (18,16,16);
- (17,17,17,6^7), central (17,17,17);
- (17,17,16,7,6^6), central (17,17,16).

These11 profiles must be discharged by the separate rigidity stage.
The present programs do not claim that role inequalities alone close
support10. For maximum at most11, each central vertex needs at least4
pairs in each of9 unique directions, so it needs36 while its sum-free
budget is at most floor(11²/4)=30. That whole low-maximum range is also
excluded directly, independently of the222-profile finite check.

No Qmax census, LP, SAT, or earlier profile-screen input is used here.
The proof still uses the separately verified ten-point support
classification and the elementary unique-edge sumset lemma. It applies
to both rings because the ring carry only translates the required
quotient sumset. Code verification is not proof-assistant formalization.
