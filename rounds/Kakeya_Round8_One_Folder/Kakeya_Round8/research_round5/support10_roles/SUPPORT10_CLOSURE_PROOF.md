# Support ten is impossible below 94 when all fibres have size at most 18

## Theorem and exact scope

Let R be either Z/4Z or F2[epsilon]/(epsilon^2). A Kakeya set in R^5
with at most 93 points and all residue fibres of size at most 18 cannot
have exactly ten pair-active residue fibres. Here a pair-active fibre
has at least two points; singleton fibres cannot contribute to a
primitive four-point line.

Together with the nine-residue difference bound, this gives at least
eleven pair-active residues under these hypotheses. In the existing
dimension-five middle ledger, it closes all seven support-10 cells for
exact maxima 12 through 18. This is not the unrestricted lower bound 94.

The proof below has a complete finite support classification and a
complete finite weight-role reduction, followed by elementary rigidity.
Neither finite reduction uses the earlier middle survivor screens,
Claude's CNF encoding, a SAT solver, or the twelve-point energy census.
The finite computations have separate implementations. This theorem
has not been formalized in a proof assistant.

## 1. Normalize the support and the total weight

Discard singleton fibres, which removes no primitive line. Add points
within the ten existing active fibres until their total is 93, keeping
each fibre of size at most 18. This is possible because their available
capacity is 180. Adding points preserves the Kakeya property and does
not change the active support. It therefore suffices to consider ten
weights between 2 and 18, of total 93.

For every nonzero residue direction d, some active support edge must
have difference d. Thus the support is a ten-point difference cover
of F2^5 and has affine rank five.

The complete support classification gives, after an affine change,

    S = (V minus {0}) union (W minus {0}),
    dim V = 3, dim W = 2, and V direct-sum W = F2^5.

The seven points of V minus zero are ordinary vertices; the three
points of W minus zero are centres. Every edge incident to a centre
is the unique support edge in its direction. There are 24 such edges.
The seven other directions each occur on three ordinary-ordinary edges.

Completeness is checked without an inherited orbit catalogue: every
support has an affine basis that can be sent to 0,1,2,4,8,16. Enumerating
the remaining four points gives C(26,4)=14,950 normalized candidates.
Exactly 80 cover every nonzero direction. Two programs verify the
displayed complementary-subspace form on all 80.

The affine residue normalization lifts to an invertible affine map
over either ring. The residue-dependent fibre translations needed
over Z/4Z are retained in ENCODING_AND_SYMMETRY_BRIDGE.md.

## 2. Unique edges force local pair resources

Write p_A(d) for the number of unordered d-pairs in a fibre A.
It is at most floor(|A|/2). For a unique support edge in direction d,
the two quotient pair sets must sum to all 16 points of F2^5/<d>,
up to the ring's fixed carry translation. If their sizes are p and q,
then pq is at least 16.

There is one useful improvement. If a summand has three points, its
affine span is a four-point plane. To cover each of the four cosets of
that plane, the other summand must contribute at least two points per
coset. It therefore has at least eight points. Consequently a neighbor
pair cap c forces the local pair count to be at least

| Neighbor cap c | Forced local pair count |
|---|---:|
| 1 | 16 |
| 2 or 3 | 8 |
| 4 through 7 | 4 |
| 8 or 9 | 2 |

At every support vertex, the set of incident unique directions is
sum-free. The corresponding difference graph on a weight-w fibre is
triangle-free. Mantel's theorem gives a total pair budget floor(w^2/4).
Each role assignment must satisfy this budget and every individual
pair cap simultaneously.

For an ordinary vertex, its three incident unique directions are
linearly independent. Their Cayley graph is four disjoint copies of
the three-cube Q3. The exact induced-edge maxima on one cube at weights
0 through 8 are

    0, 0, 1, 2, 4, 5, 7, 9, 12.

Both programs enumerate all cube subsets and optimize their sums over
four cosets. In particular, five points can supply at most five pairs
in those three directions, while unique-edge coverage requires at
least two per direction. An ordinary weight-five fibre is impossible.

## 3. Complete weight-role reduction

There are exactly 102,842 nonincreasing ten-part partitions of 93
with parts between 2 and 18. Of these, 102,620 have maximum 12 through
18; the other 222 have maximum 10 or 11. The producer generates all
partitions recursively and tests all choices of central weights.

The separate verifier first counts partitions by generating functions.
It then chooses the central triple first and enumerates all eligible
seven-part ordinary multisets, imposing every centre's mass budget.
It imports no producer and reads no earlier survivor screen to derive
its result. The elementary role budgets leave 174 profiles; the cube
resource leaves exactly the following eleven. Each has the indicated
unique allowed central weight multiset.

| Weights, with exponents denoting repetitions | Central weights | Obstruction |
|---|---|---|
| (18,17,16,6^7) | (18,17,16) | Four periods |
| (18,16,16,7,6^6) | (18,16,16) | Four periods |
| (17,17,17,6^7) | (17,17,17) | Seventeen-point split |
| (17,17,16,7,6^6) | (17,17,16) | Four periods |
| (17,16,16,8,6^6) | (17,16,16) | Four periods |
| (17,16,16,7^2,6^5) | (17,16,16) | Four periods |
| (16^3,9,6^6) | (16,16,16) | Four periods |
| (16^3,8,7,6^5) | (16,16,16) | Four periods |
| (16^3,7^3,6^4) | (16,16,16) | Four periods |
| (13,12,12,8^7) | (13,12,12) | Mantel equality |
| (12^3,9,8^6) | (12,12,12) | Mantel equality |

The three obstructions below eliminate all eleven for every placement
of the ordinary weights. No realizability of a surviving relaxation
is assumed.

## 4. Four periods force the wrong affine dimension

In eight rows, choose a weight-16 centre with at least four ordinary
neighbors of weight at most six. The neighbor pair counts are at most
three. Full quotient coverage and the three-point lemma force the
central pair count to be eight along each corresponding direction.

Eight disjoint pairs exhaust a 16-set A. Thus each of these four
distinct directions is a period of A. Four distinct nonzero periods
span at least three dimensions. Choose a three-dimensional period
subspace H. Then A is exactly two H-cosets, and the union of two
distinct cosets of a subspace is an affine subspace of one higher
dimension. Hence A is an affine four-flat.

All directions in which A has a positive pair count lie in that
four-flat's direction space. But at a centre w the nine required
unique directions are

    F_w = (w + (V minus {0})) union (W minus {0,w}).

These span all five dimensions. Every one requires a positive central
pair count, giving a contradiction.

## 5. The seventeen-point split

For (17,17,17,6^7), select any centre w. Its seven ordinary neighbors
all have weight six, so again the central pair count must be eight
in every direction of F7 = w + (V minus {0}). There are therefore
56 edges in the F7-difference graph on the 17-set A.

Let L = V + span(w), a four-space. The F7 graph consists of two
L-coset components. Each is a 7-regular bipartite graph K8,8 with a
perfect matching removed. A t-point induced subgraph has at most

    e(t) = min(floor(t^2/4), floor(7t/2))

edges. If A meets the two cosets in k and 17-k points, and both
intersections have at least two points, choose the smaller k in
2 through 8. The bounds e(k)+e(17-k) are respectively

    53, 51, 46, 42, 39, 37, 36,

all less than 56. Thus the only possible split is 16+1: a full L-coset
plus one point in the other coset. In every direction outside L,
such a set has exactly one pair. The other two central edge directions
lie outside L, and the opposite central pair cap is eight. They can
cover at most eight quotient labels, instead of the required sixteen.
This is the final contradiction for this row.

## 6. Mantel equality is impossible in the centre graph

In the last two rows choose a weight-12 centre. Every neighbor has
weight at most 13 and pair cap at most six. Full coverage forces at
least four central pairs in each of the nine unique directions:
counts at most two fail the product bound, and count three fails the
three-point lemma. The centre's difference graph therefore has at
least 36 edges. Mantel bounds it by 36, so equality would force K6,6.

That equality cannot occur in the Cayley graph with direction set F_w.
For nonzero z in V,

    F_w intersection (F_w + z) = w + (V minus {0,z}),

which has six points. For z outside V, the intersection has at most
two points: in the four-point quotient by V the occupied cosets of
F_w have sizes 7,1,1.

It follows that any six-subset Y of F_w has at most two common
neighbors. Zero is one; if a nonzero z is another, Y must equal the
displayed six-set, which determines z uniquely. A K6,6, translated
so that one vertex is zero, would give six common neighbors of its
opposite six-vertex class. Contradiction. In fact every 12-set has
at most 35 edges in this centre graph.

The separate finite check examines all 84 six-subsets of F_w. Exactly
77 have one common neighbor and seven have two. The root rigidity
replay checks all three choices of centre and every surviving role
assignment.

## Conclusion and replay

Every complete weight-role branch is excluded. Both rings satisfy
the theorem because the carry translates a unique edge's quotient
sumset without changing whether it fills the quotient.

From the archive root, the core finite checks are:

    python3 research_round5/support10_roles/verify_support10_roles.py
    python3 research_round5/support10_roles/FULL_S10_verify.py
    python3 research_round5/support10_roles/verify_support10_mantel_obstruction.py
    python3 research_round5/support10_roles/verify_support10_rigidity.py

The first also replays the historical 641-cut intermediate stage.
Its support-classification check is the part needed by the standalone
proof. The full weight reduction itself is independent of that stage's
648-profile input. The argument establishes a genuine support exclusion,
not a proof of the unrestricted Kakeya formula or closure of the middle
maximum strata.
