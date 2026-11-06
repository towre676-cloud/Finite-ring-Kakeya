# The unrestricted support-10 exclusion

## Theorem

**For either R = Z/4Z or R = F2[epsilon]/(epsilon^2), a Kakeya set
K in R^5 with at most 93 points cannot have exactly ten pair-active
residue fibres. There is no hypothesis on the largest fibre.**

A pair-active fibre has at least two points. Singleton fibres cannot
contribute to a primitive four-point line. The complete nine-point
difference calculation in this package also excludes supports of
size nine; smaller supports have at most C(8,2)=28 differences.
Consequently any such hypothetical K has **at least eleven pair-active
residues**.

The proof uses the complete, separately checked finite classification
of ten-point difference covers, followed by the analytic argument below.
The weight-profile census, earlier middle screens, energy maxima,
Claude's SAT results, and a maximum-fibre restriction are unnecessary
for this theorem. The support classification remains a finite-computation
component; this is not a claim of full proof-assistant formalization.

## 1. Geometry of the support

Every nonzero residue direction must occur on a pair-active support
edge. The ten-point support is therefore a difference cover of F2^5.
The complete classification gives, after an affine transformation,

    S = (V minus {0}) union (W minus {0}),
    dim V = 3, dim W = 2, and V direct-sum W = F2^5.

Call the three points of W minus zero centres and the seven points of
V minus zero ordinary vertices. All edges incident to a centre are
unique in their direction: 24 unique edges altogether. The remaining
seven directions have three ordinary-ordinary edges each.

Every difference cover has affine rank five, so normalize an affine
basis to 0,1,2,4,8,16. There are C(26,4)=14,950 extensions by four points.
Exactly 80 cover all nonzero differences. The producer and separate
bitset verifier check the complementary-subspace form on all 80.
No inherited orbit catalogue is used. An alternative analytic support
classification, if supplied separately, can replace this finite step.

The affine normalization lifts to an invertible affine map over either
ring. Over Z/4Z the associated fibre translations include the carry;
the full argument is in ENCODING_AND_SYMMETRY_BRIDGE.md.

## 2. Pair demands and graph bounds

Let p_A(d) count unordered pairs of a fibre A in direction d. A unique
support edge must cover the entire 16-point quotient F2^5/<d>. Its two
quotient pair sets therefore have full sumset, up to a fixed carry
translation. If their sizes are p,q, then pq is at least 16.

If one summand has three points, translate it into its four-point
linear span H. To cover all four H-cosets, the other summand needs at
least two points in each coset. Its size must therefore be at least
eight. This elementary three-point lemma strengthens product counting.

In particular, a neighbor of weight at most 7 forces at least eight
local pairs; a neighbor of weight at most 15 forces at least four.
A neighbor of weight at most 31 forces at least two. A weight-32
neighbor may permit one, and is treated separately below.

For any support vertex, its incident unique directions form a sum-free
set. The corresponding difference graph on a weight-t fibre is
triangle-free, so its edge count is at most floor(t^2/4).

At an ordinary vertex v, the three unique directions are v+w for
w in W minus zero. They are independent: they are distinct, nonzero,
and their sum is v, not zero. Their Cayley graph is four disjoint
copies of Q3. Four selected vertices give at most four edges; five
give at most five. For the latter statement, a triangle-free five-vertex
graph with six edges would be K2,3, but two distinct vertices in these
cube components have at most two common neighbors.

## 3. Every centre has weight at least twelve

Write the three central weights as a <= b <= c. The sum of these
weights and the seven ordinary weights is at most 93. Every fibre
has size at most 32 simply because its ambient space is F2^5.

If a <= 7, each of its seven ordinary neighbors needs at least eight
pairs in that unique direction, hence at least 16 points. Their
combined weight is already at least 112. Thus a >= 8.

Suppose 8 <= a <= 11. Every ordinary neighbor needs at least four
pairs, so every ordinary weight is at least eight. The other two
central weights are also at least eight. The largest of the nine
neighbors of the a-centre is at most

    93 - a - 8*8 = 29 - a <= 21.

At most one of these neighbors can have weight at least 16: two would
force total weight at least a + 9*8 + 2*8 = a+88 >= 96. The other
eight neighbors each force at least four central pairs; the possible
larger neighbor still forces at least two. Thus the centre requires
at least 34 pairs in its nine unique directions. Its triangle-free
budget is at most floor(11^2/4)=30. Contradiction. Hence **a >= 12**.

## 4. A centre between twelve and fifteen is impossible

If a <= 15, every ordinary weight is at least eight. The three central
weights therefore sum to at most 37. Since each is at least twelve,
a=12 and every centre has weight at most 13. Every ordinary weight
is at most nine: the other six ordinary weights contribute at least
48 and the centres contribute at least 36.

Choose a weight-12 centre w. Every one of its nine neighbors has
weight at most 13, so every unique direction forces at least four
central pairs. The corresponding graph has at least 36 edges and,
by Mantel, at most 36. Equality would force K6,6.

But the centre direction set

    F_w = (w + (V minus {0})) union (W minus {0,w})

does not permit that graph. Any six-subset of F_w has at most two
common neighbors. Indeed, for nonzero z in V,

    F_w intersection (F_w + z) = w + (V minus {0,z}),

and for z outside V the intersection has at most two points. Thus a
nonzero common neighbor of a six-subset determines that six-subset
uniquely and is itself unique; zero is the only other possible common
neighbor. Translating a vertex of K6,6 to zero contradicts this bound.

The overlap argument is analytic. The separate check also enumerates
all 84 six-subsets: 77 have one common neighbor and seven have two.
This excludes the low-centre branch, including the possible total-92
profile (12^3,8^7); no padding to total 93 is needed.

## 5. The high-centre branch has only three units of slack

It remains that a,b,c are all at least sixteen. First exclude a full
32-point centre. There cannot be two: their weights plus the third
centre and seven pair-active ordinary fibres total at least

    32 + 32 + 16 + 7*2 = 94.

If exactly one centre has weight 32, the other two have weight at most
31. Each ordinary fibre then needs at least two pairs towards each
of those two centres and at least one towards the full centre, for
a total of at least five pairs in its three independent directions.
Weights at most three cannot supply the required two-pair incidences;
weight four has at most four cube edges. Every ordinary weight is
therefore at least five. The total is at least

    32 + 16 + 16 + 7*5 = 99,

another contradiction. Thus every centre has weight at most 31.

Every ordinary fibre now needs at least two pairs in each of its three
unique directions. Its weight is at least five by the individual cap
and triangle-free budget, and weight five is impossible by the cube
bound. Every ordinary weight is at least six.

The baseline total is therefore 3*16+7*6=90. There are **at most three
additional points**.

## 6. A weight-16 centre forces a four-flat

If some centre has weight sixteen, at least four ordinary neighbors
have weight exactly six: raising four ordinary weights above six
would use at least four additional points. Along these four unique
directions the ordinary pair counts are at most three. Full quotient
coverage forces eight central pairs, by the three-point lemma.

Eight disjoint pairs exhaust the 16-set, so all four directions are
periods. Four distinct nonzero periods span at least a three-space H.
The fibre is two H-cosets, hence an affine four-flat. Every positive
pair direction must lie in its four-dimensional direction space.

The centre's nine unique directions F_w span all five dimensions and
all require positive pair counts. Contradiction.

## 7. Without a weight-16 centre, everything is forced

If no centre has weight sixteen, all three have weight at least
seventeen. The total lower bound becomes 3*17+7*6=93, so equality is
forced: the central weights are (17,17,17), and all seven ordinary
weights are six.

Choose one central 17-set A at w. It has eight pairs in every direction
of F7 = w + (V minus {0}), for a total of 56 edges. Let
L=V+span(w). The F7 graph on each of the two L-cosets is the 7-regular
bipartite graph K8,8 with a perfect matching removed.

A t-point induced subgraph has at most

    e(t) = min(floor(t^2/4), floor(7t/2))

edges. If both coset intersections have at least two points, their
sizes are k and 17-k, with the smaller k between 2 and 8. The bounds
e(k)+e(17-k) are 53,51,46,42,39,37,36, all below 56. Thus the split
is 16+1: a full L-coset and one point outside it.

Such a set has exactly one pair in every direction outside L. The
two central-central unique-edge directions lie outside L, and their
opposite fibres have pair cap eight. Those edges cover at most eight
quotient labels, contradicting the required sixteen.

All cases are exhausted. The argument applies to both rings because
the carry translates each unique-edge sumset without changing whether
it is the whole quotient.

## Verification and limits

The included independent support classification is the only exhaustive
mathematical classification required by this proof. The 102,842-profile
weight census and its eleven rigidity applications are additional
reproducibility checks for the bounded-weight subcase, not premises of
this unrestricted argument. The complete 2,930-case nine-point degree
census supplies the stated lower-support corollary.

The main replay also checks the three centre direction sets, the cube
edge bounds, all 84 common-neighbor cases for each centre, and the
seventeen-point arithmetic. Analytic model reviews are recorded in
FIRST_FIVE_RIGIDITY_AUDIT.md, ADDITIONAL_RIGIDITY_AUDIT.md, and the
unrestricted analytic-role audit. These are separate model-agent checks
in one session, not independent human peer review.

**The unrestricted Kakeya lower bound 94 remains open on larger
supports. This theorem closes the complete support-10 branch.**
