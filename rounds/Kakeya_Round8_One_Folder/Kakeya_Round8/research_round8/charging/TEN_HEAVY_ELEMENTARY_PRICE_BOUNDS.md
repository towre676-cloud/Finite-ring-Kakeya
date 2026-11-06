# Ten heavy fibres are impossible below ninety-four points

## Result and dependency boundary

For either ring, suppose a dimension-five Kakeya set has thirteen
pair-active residue fibres, each of weight at most eleven, and total
weight at most ninety-three. Then **at least eleven fibres have weight
at least four**.

The earlier `HEAVY_DIFFERENCE_COVER_THEOREM.md` proves, without a census,
that there are at least ten heavy fibres and that their residues cover
all thirty-one nonzero differences. It remains to exclude exactly ten.

We use the complete ten-point difference-cover classification in
`research_round8/geometry/TEN_HEAVY_RANK_CONSEQUENCES.md`, checked by
`verify_ten_heavy_ranks.py`. Its normalization covers all
$\binom{26}{4}=14,950$ ten-sets containing an affine basis; all eighty
normalized difference covers have the stated structure. **That small
support classification is the only finite census required by the proof
below. No fibre-spectrum or quotient-sumset census is a premise.**

## Geometry of ten heavy residues

After a common affine change of residue coordinates, the heavy set is

$$
H=(W\setminus\{0\})\cup(U\setminus\{0\}),\qquad
\dim W=3,\quad\dim U=2,\quad W\cap U=\{0\}.
$$

There are three light residues. In any direction, edges with a light
endpoint supply at most $3\cdot5=15$ lifted labels. Thus every direction
needs an active heavy-heavy edge.

The twenty-four directions outside $W$ have exactly one heavy-heavy
edge each: twenty-one between the seven $W$-vertices and three
$U$-vertices, and three between the $U$-vertices. Every such edge must
be active. Their forced positive directions imply:

- Every $U$-fibre has affine rank five and lies on nine of these edges.
- Every $W$-fibre has rank at least three and lies on three of these edges.
- At most two $W$-fibres have rank three.

For completeness, the three cross directions at $w\in W\setminus\{0\}$
span $U+\langle w\rangle$. If its fibre has rank three, this is its
whole direction space; it contains none of that vertex's internal
$W$-edge directions. Therefore all seven internal $W$-directions must be
covered by edges between $W$-vertices of rank at least four. Four vertices
have only six pairs, so at least five of the seven vertices must have
rank at least four. The full rank argument is recorded in the cited
geometry note.

## An elementary price for a pair count

For $0\le p\le5$, set

$$
\phi(p)=(0,1,4,9,16,17)_p.
$$

If $P,Q\subseteq\mathbb F_2^4$ have sizes $p,q\le5$, then

$$
2|P+Q|\le\phi(p)+\phi(q).
\tag{1}
$$

Product and ambient-size bounds suffice for every pair except $\{p,q\}
=\{3,5\}$. A three-point set lies in an affine two-plane. Partition
the five-point set among the four cosets of that plane. A nonempty
part of size $r$ contributes at most $r+2$ sums, giving
$|P+Q|\le5+8=13$. Thus the remaining case obeys
$2|P+Q|\le26=9+17$. There is no sumset-table assumption in (1).

For a fibre $A$ of weight $w$, let $R_k(A)$ be the sum of the largest
$k$ values among $\phi(p_A(d))$, $d\ne0$. Put

$$
R_U=R_9(A),\qquad R_W=R_3(A),\qquad
R_L=10\binom w2
$$

for the respective vertex roles. Summing capacity over the twenty-four
unique-heavy-edge directions gives

$$
768=2\cdot16\cdot24
\le \sum_U R_U+\sum_W R_W+\sum_L R_L=:R.
\tag{2}
$$

Indeed, (1) pays for each heavy-heavy edge from its two endpoint
directional resources. An edge with a light endpoint costs at most five
times that endpoint's pair count, hence ten after doubling. Charge such
an edge to one light endpoint. A vertex has at most one edge in each
direction, so no resource is charged twice. Using the full light pair
budget and the largest available heavy prices can only increase the
upper bound.

## Two elementary rank observations

If an even-sized fibre has $p_A(d)=w/2$, then $A+d=A$. Two distinct
such directions generate a four-element period group. Therefore a
six-set has at most one three-pair direction. A six-set with even one
three-pair direction is the union of three cosets of a one-space, so
its affine rank is at most three. An eight-set with two four-pair
directions is the union of two cosets of a two-space, again of rank
at most three. The analogous four-set observation gives rank at most
two for a two-pair direction.

Here is the odd-sized version needed below. Let $d,e$ be distinct
nonzero directions. Partition a fibre into cosets of
$K=\langle d,e\rangle$. In a coset containing $r$ points, the number
of induced $d$- and $e$-edges is at most

$$
\begin{array}{c|ccccc}
r&0&1&2&3&4\\\hline
\text{edges}&0&0&1&2&4.
\end{array}
$$

Every partially occupied coset therefore has a deficit of at least one
between its point count and its edge count. If a seven-set has
$p_A(d)=p_A(e)=3$, the total deficit is exactly one. There is exactly
one partial coset, of size three, and one full coset. Its rank is at
most three. Similarly, an eleven-set with two five-pair directions has
coset sizes $4,4,3$ and rank at most four. Consequently a rank-at-least-four
seven-set has at most one three-pair direction, and a rank-five
eleven-set has at most one five-pair direction.

## Elementary resource bounds

The following are upper bounds, not asserted exact maxima:

| Fibre role | Weight | Upper bound for its resource |
|---|---|---|
| $U$, rank five, $R_9$ | $6,7,8,9,10,11$ | $15,27,46,78,126,145$ |
| $W$, rank three, $R_3$ | $4,5,6,7,8$ | $3,12,17,27,48$ |
| $W$, rank at least four, $R_3$ | $5,6,7,8,9,10,11$ | $3,12,17,34,48,51,51$ |
| Light, $10\binom w2$ | $2,3$ | $10,30$ |

Here are the details behind the only nontrivial entries. The pair-energy
identity is

$$
Q(A)=\sum_{d\ne0}p_A(d)^2=\binom w2+6Z_4(A),
\tag{3}
$$

where $Z_4(A)$ counts affine planes in $A$. Each plane gives two parallel
pairs in each of its three directions, which proves (3).

For an affine-rank-five fibre, the augmented relation code has dimension
$w-6$. Every affine plane is a distinct nonzero weight-four codeword.
Thus

$$
Z_4(A)\le2^{w-6}-1.
$$

For $w=6,7,8,9$, (3) bounds $Q(A)$ by $15,27,46,78$ respectively;
$R_9(A)\le Q(A)$ because $\phi(p)\le p^2$.

For $w=10$, (3) gives $Q(A)\le135$. Select the nine largest pair counts,
and let $t$ of them equal five. Their sum is at most $36+t$, whereas
all thirty-one counts sum to $45$. The omitted counts therefore
contribute at least $9-t$ to the energy. Since
$\phi(5)=5^2-8$ and $\phi(p)=p^2$ for $p\le4$,

$$
R_9(A)\le135-(9-t)-8t=126-7t\le126.
$$

For $w=11$ and rank five, the odd-coset observation allows at most one
five-pair direction, so $R_9(A)\le17+8\cdot16=145$.

For the $W$ rows, a rank-three four-set and a rank-four five-set are
affinely independent, hence have no repeated pair difference; their
top-three resource is at most three. The period observations give the
entries seventeen for rank-three weight six, twelve for higher-rank
weight six, and seventeen for higher-rank weight seven. A higher-rank
eight-set has at most one four-pair direction, giving
$16+9+9=34$. All other displayed entries follow directly from
$p\le\lfloor w/2\rfloor$ and $\max_{p\le5}\phi(p)=17$.

## A short integer certificate

Every entry in the elementary table satisfies

$$
\begin{aligned}
4R_U&\le45w+85,\\
4R_W&\le45w-213+45[\operatorname{rank}(A)=3],\\
4R_L&\le45w-15.
\end{aligned}
\tag{4}
$$

There are three $U$-vertices, seven $W$-vertices, three light vertices,
at most two rank-three $W$-fibres, and at most ninety-three total points.
Summing (4) therefore gives

$$
4R\le45\cdot93+3\cdot85-7\cdot213+2\cdot45-3\cdot15
=2994<3072=4\cdot768.
$$

This contradicts (2). Exactly ten heavy fibres are impossible.

The standalone integer replay checks the price inequalities, the
four-cycle deficit table, every elementary row inequality, and the final
strict gap. It also computes the exact maximum of these deliberately
weaker resource bounds under the budget: $744$ without fixing a hub,
$729$ with a weight-eleven hub in $W$, and $744$ with such a hub in $U$.
These dynamic-program values are corroboration; the short certificate
(4) already proves the contradiction.

The stronger root-audit certificate and its exact values $663$ and $685$
remain separately pinned in `research_round8/root_audit/`. They use finer
resource tables. The geometry agent's direct finite fibre normalization
can independently verify those tables. Neither is required for the
weaker elementary local proof given here.
