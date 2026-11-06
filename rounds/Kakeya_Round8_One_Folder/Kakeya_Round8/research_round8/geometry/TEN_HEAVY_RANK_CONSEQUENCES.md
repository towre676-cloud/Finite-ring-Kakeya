# Ten heavy fibres force eight large affine ranks

## Analytic statement

Suppose a Kakeya configuration over either ring, in dimension five, has
thirteen pair-active residue fibres, all of weight at most eleven. Suppose
exactly ten fibres have weight at least four. Let $H$ denote their residue
set. The other three fibres have weight two or three.

Assume the following affine decomposition of the heavy residues:

$$
H=t+\bigl((W\setminus\{0\})\cup(U\setminus\{0\})\bigr),
\qquad \dim W=3,\quad \dim U=2,\quad W\cap U=\{0\}.
\tag{1}
$$

Then:

1. The three fibres at $t+(U\setminus\{0\})$ have affine rank **five**.
2. At a vertex $t+w$, $0\ne w\in W$, the fibre's direction space contains
   $U+\langle w\rangle$ and hence has rank at least **three**.
3. At least **five of these seven** $W$-vertex fibres have rank at least
   **four**. Thus at most two can have rank three.

These conclusions use no fibre-spectrum census, total-weight budget or
SAT result. They hold for every decomposition (1). The finite calculation
below verifies that every ten-point heavy difference cover in binary
dimension five has such a decomposition; its completeness argument is
separate from this analytic lemma.

## Every direction requires an active heavy–heavy edge

For a nonzero direction $d$, write $p_v(d)$ for the number of $d$-pairs in
the fibre at residue $v$. Every fibre has $p_v(d)\le5$. A light fibre,
of size two or three, has $p_v(d)\le1$.

Charge each edge with a light endpoint to one such endpoint. A vertex has
at most one incident edge of a fixed direction. The combined capacity of
all edges with a light endpoint is therefore at most $3\cdot5=15$.
Covering all sixteen lifted labels requires an **active heavy–heavy
edge in every direction**: both endpoint pair counts must be positive.
In particular $D(H)$ is the complete set of thirty-one nonzero directions.

## The twenty-four unique heavy edges

Translation by $t$ does not change differences. Under (1), directions in
$W\setminus\{0\}$ have three heavy–heavy edges, all internal to the
seven $W$-vertices. Each of the twenty-four directions outside $W$ has
exactly one heavy–heavy edge: the twenty-one $W$–$U$ edges and the three
edges among the $U$-vertices.

All twenty-four of these unique edges must therefore be active at both
endpoints.

Fix a nonzero $u\in U$. Its seven directions $w+u$, $0\ne w\in W$,
span $W+\langle u\rangle$. One of its directions to another nonzero
$U$-vertex lies outside this four-space. Thus its nine forced positive
directions span all of $\mathbb F_2^5$. A fibre's positive pair
directions lie in its affine direction space, proving the first claim.

Now fix $0\ne w\in W$. Its three directions to the $U$-vertices are
$w+u$ for $u\in U\setminus\{0\}$. Their pairwise sums generate
$U$, and the sum of all three equals $w$. They span precisely the
three-space $U+\langle w\rangle$, proving the second claim.

## At least five higher-rank vertices in the seven-point component

If the fibre at $t+w$ has rank exactly three, its direction space equals
$U+\langle w\rangle$. This space meets $W$ in $\{0,w\}$. Every
internal edge from $t+w$ to another $t+w'$, $0\ne w'\ne w$, has
direction $w+w'\in W\setminus\{0,w\}$. That direction is outside
the fibre's span, so its pair count is zero.

Consequently every active internal edge in a $W$-direction must join two
$W$-vertices whose fibres have rank at least four. Let $B$ be those
vertices, translated back into $W\setminus\{0\}$. Every nonzero
direction of $W$ still requires an active heavy–heavy edge, and there
are no other heavy–heavy edges in those directions. Therefore

$$
D(B)=W\setminus\{0\}.
$$

Four vertices have at most six unordered pairs, fewer than the seven
required directions. Thus $|B|\ge5$, proving the third claim.

## Complete finite classification used to apply the lemma

Any ten-point difference cover $H\subseteq\mathbb F_2^5$ has affine
rank five. Choose an affine basis of six points and map it to
$\{0,e_1,e_2,e_3,e_4,e_5\}$. The remaining four points are a subset
of the other twenty-six points. Thus checking all

$$
\binom{26}{4}=14{,}950
$$

normalized sets is complete; uniqueness of the normalization is not
required. The accompanying independent replay finds eighty normalized
difference covers. Every one has pair histogram twenty-four single-pair
directions and seven triple-pair directions. The latter, together with
zero, form a three-space $W$.

The cosets of $W$ meet $H$ in sizes $7,1,1,1$. Let $t$ be the missing
point in the seven-point coset. After translating by $t$, the three
singleton representatives, together with zero, form a two-space $U$
complementary to $W$. This supplies (1) in every enumerated case.

The replay also checks the thirteen surviving ten-heavy placements
inside the four specified marked support-thirteen cases. It records the
actual residue labels of the three forced rank-five vertices and the
seven vertices requiring at least five further rank-four-or-five
fibres. It does not move or choose the distinguished largest-fibre
vertex arbitrarily; the original marked vertex remains identifiable.

This classification is a small complete finite computation, not an
analytic classification theorem or a SAT exclusion. A subsequent
capacity certificate can use the proved rank consequences together with
the explicitly checked decomposition. This note alone does not exclude
every ten-heavy weight assignment.
