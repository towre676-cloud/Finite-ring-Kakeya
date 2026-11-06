# Ten-point support structure and 641 additional exclusions

## Structural theorem

Every ten-point subset S of F2^5 whose differences cover all31 nonzero
directions is affinely equivalent to

S = (V minus {0}) union (W minus {0}),

where V and W are complementary linear subspaces of dimensions3 and2.
Thus the support has seven ordinary vertices and three central vertices.
Every central-central or central-ordinary edge is the unique support edge
in its direction. The seven remaining directions each have three
ordinary-ordinary edges. The graph of unique edges is the join of K3 and
an independent seven-set: central degrees9, ordinary degrees3.

This finite structural theorem is established by two exhaustive programs
with different representations. Difference coverage forces affine rank5.
Translate an affine basis point to0 and map five independent differences
to1,2,4,8,16. Every support then occurs among the14,950 four-element
extensions of this fixed six-set. Exactly80 extensions cover all31
directions. Both programs verify the claimed structure on every one.
The first finds the missing origin by XORing the seven ordinary points;
the second tests all32 possible origins, obtaining exactly one. Both
check closure, dimensions, and complementary subspaces explicitly.

For each support vertex x, the directions of its incident unique edges
are sum-free. This follows either from the canonical form or directly
from both complete checks. For ordinary x in V minus {0}, these are
x + (W minus {0}). For central x in W minus {0}, these are
x + (V minus {0}), together with the two nonzero elements of W other
than x. Sums of two different directions in either displayed set do
not belong to that set.

## Pair resource bound

For a fibre A of weight w, let p_A(d) count its unordered pairs in
direction d. The graph on A whose edges have directions in a sum-free
set is triangle-free: the three directions of a triangle sum to0.
Mantel's theorem therefore gives

sum over incident unique directions d of p_A(d) <= floor(w²/4).

Also p_A(d) <= floor(w/2), since each direction is a matching.

## Unique-edge demand and the three-point lemma

When a support edge is unique in direction d, its two quotient pair
sets must sum to the whole16-point quotient F2^4 (up to a ring-dependent
translation). Thus their cardinalities p,q satisfy pq >=16.

If one quotient pair set has size3, its affine span is a plane of size4.
Each of the four cosets of that plane requires at least two points of
the other set: a single point covers at most three of its four points.
Consequently the other set must have size at least8. This argument is
unchanged by the ring carry, which only translates the required sumset.

For neighbor pair cap c <=9, every unique edge therefore forces the
local pair count to be at least

- 2 if 8 <= c <=9;
- 4 if 4 <= c <=7;
- 8 if 2 <= c <=3;
- 16 if c =1.

A local demand exceeding floor(w/2) is already impossible. Otherwise,
if the sum of the demands at a vertex exceeds floor(w²/4), its role
assignment is impossible.

## Exhaustive role assignment and result

Input: the648 support10 profiles in the independently replayed Round5
nine-heavy geometry residual; total weight93, maximum12 through18.
For each profile, every choice of three weights for the central roles
is tested. Ordinary roles are interchangeable for this test. To exclude
a whole profile, every central weight triple must fail at a vertex.

The producer records a failed vertex and its demands for every distinct
central weight triple. The separate verifier uses all120 choices of
three indexed positions, and the explicit threshold table above,
rather than importing the producer's capacity function. It verifies
77,760 indexed role assignments and the exact residual subtraction.

Result: **641 new whole-profile exclusions, seven residual profiles**.
No Qmax census, maximal-direction quota, LP, SAT, or fibre-shape census
is used. No assumptions are made about fibre shape or placement beyond
the proved support structure. The exclusions apply to both rings.

The seven residual profiles and their unique allowed central triples
are saved separately. These are survivors of necessary conditions,
not Kakeya constructions. Any subsequent rigidity exclusions belong
to a separate stage, so this641-profile result remains fixed.

The checks are separately implemented finite verifications. They are
not proof-assistant formalization or independent human review.
