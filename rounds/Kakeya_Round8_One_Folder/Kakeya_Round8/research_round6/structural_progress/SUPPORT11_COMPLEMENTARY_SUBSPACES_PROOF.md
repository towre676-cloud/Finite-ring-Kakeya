# A support-eleven exclusion with no maximum-fibre hypothesis

## Theorem

Let $R$ be either $\mathbb Z/4\mathbb Z$ or $\mathbb F_2[\epsilon]/(\epsilon^2)$. Suppose the pair-active residue support of a Kakeya set $K\subset R^5$ is affinely equivalent to

\[
S=V\cup W,\qquad \dim V=3,\quad\dim W=2,\quad V\cap W=\{0\}.
\]

**Then $|K|\ge94$. There is no hypothesis on the largest fibre.**

This is one of the four unmarked affine support-eleven geometries. It accounts for three of the thirteen hub-marked support-eleven classes in the supplied catalogue. The theorem itself needs no completeness claim about that catalogue: its hypothesis is the displayed geometric form.

Write $W\setminus\{0\}=\{w_1,w_2,w_3\}$, where $w_1+w_2+w_3=0$. Call these three points the centres; call the seven points of $V\setminus\{0\}$ ordinary vertices. The remaining support vertex is the origin. Its fibre has at least two points, just as every pair-active fibre does.

## 1. The support and its unique directions

Every centre-ordinary edge has a unique residue direction. These are the 21 directions $w_i+v$, with $v\in V\setminus\{0\}$. Their graph on the support is $K_{3,7}$, together with an isolated origin. Each nonzero direction $w_i\in W$ instead occurs on exactly two edges:

\[
\{0,w_i\},\qquad \{w_j,w_k\},\qquad \{i,j,k\}=\{1,2,3\}.
\]

For a unique edge, the two quotient pair sets must sum to the entire sixteen-point quotient. The carry term for ℤ/4ℤ only translates that sumset. Thus all the following pair demands hold in both rings.

If one endpoint has weight at most seven, the other needs at least eight pairs in that direction and therefore at least sixteen points. If one endpoint has weight at most fifteen, the other needs at least four pairs and therefore at least eight points. If one endpoint has weight at most thirty-one, the other needs at least two pairs.

The only improvement over product counting used here is the elementary three-point lemma: a three-point subset of 𝔽₂⁴ lies in an affine plane, and a second summand covering all four plane cosets must have at least two points in each coset. Thus three plus at most seven cannot sum to all sixteen points.

## 2. Two local graph facts

At a centre $w_i$, the seven unique directions are

\[
F_i=w_i+(V\setminus\{0\}).
\]

Their Cayley graph is a disjoint union of two copies of $K_{8,8}$ with a perfect matching removed. Each component is a coset of $L_i=V+\langle w_i\rangle$, with its two bipartite parts the two $V$-cosets. For $t\le16$, an induced $t$-point subgraph of one component has at most

\[
g(t)=\lfloor t^2/4\rfloor-\max(0,t-8)
\]

edges. Indeed, if its two sides have sizes $x,y$, at least $\max(0,x+y-8)$ of the removed matching pairs meet both sides. Maximizing $xy$ gives the displayed upper bound. For eleven selected vertices distributed between the two components, the bounds for splits $0+11,1+10,\ldots,5+6$ are

\[
27,23,20,18,16,15.
\]

**Any fibre of weight at most eleven therefore supplies at most twenty-seven pairs in these seven directions.** The graph is triangle-free, so Mantel also gives the simpler bound $\lfloor t^2/4\rfloor$, useful at weights at most nine.

At an ordinary vertex $v\ne0$, the three unique directions $v+w_1,v+w_2,v+w_3$ are linearly independent: their sum is $v\ne0$, and they are distinct and nonzero. Their Cayley graph is four disjoint three-dimensional cubes. Four selected points have at most four edges, and five have at most five. For the latter, a triangle-free graph with five vertices and six edges would be $K_{2,3}$, whereas two cube vertices have at most two common neighbours. A disconnected choice cannot improve this bound.

## 3. Every centre must have weight at least sixteen

Assume for contradiction that the total weight is at most 93. Let the central weights be $a\le b\le c$.

If $a\le7$, all seven ordinary fibres have weight at least sixteen, already exceeding the total budget. Hence $a\ge8$.

Suppose $8\le a\le11$. Every ordinary fibre then has weight at least eight. The three centres contribute at least $3a$, and the origin contributes at least two. There can be at most one ordinary fibre of weight at least sixteen, since two would force a total of at least

\[
3a+7\cdot8+2\cdot8+2=3a+74\ge98.
\]

No ordinary fibre can have weight thirty-two, since that would instead force at least $3a+82\ge106$ points.

If $a\le9$, the six ordinary neighbours of weight at most fifteen force at least four pairs each at the $a$-centre. The possibly heavier seventh still forces two. This requires at least 26 pairs, exceeding Mantel's upper bound $\lfloor9^2/4\rfloor=20$.

If $a=10$ or $11$, even one ordinary neighbour of weight at least sixteen would force at least $3a+66\ge96$ total points. All seven therefore have weight at most fifteen, forcing 28 pairs at the $a$-centre. Section 2 bounds that quantity by 27. Both cases are impossible, so $a\ge12$.

If $12\le a\le15$, all seven ordinary fibres still have weight at least eight, giving

\[
|K|\ge3\cdot12+7\cdot8+2=94.
\]

This contradiction proves that **all three central weights are at least sixteen**.

## 4. Only one point of slack remains

There cannot be two central fibres of weight thirty-two, because

\[
32+32+16+7\cdot2+2=96.
\]

If exactly one central fibre has weight thirty-two, each ordinary fibre needs at least one pair towards it and at least two towards each of the other centres. These five required cube edges cannot fit on four points. All seven ordinary fibres have weight at least five, yielding

\[
32+16+16+7\cdot5+2=101.
\]

Thus every central weight is at most thirty-one. Each ordinary fibre needs at least two pairs in each of its three independent unique directions. The six required cube edges cannot fit on five points, so every ordinary fibre has weight at least six.

We now have the lower baseline

\[
3\cdot16+7\cdot6+2=92.
\]

There is at most one further point. Consequently at least two centres have weight exactly sixteen, at least six ordinary fibres have weight exactly six, every central weight is at most seventeen, and the origin has weight at most three.

## 5. The sixteen-point fibres force a contradiction

Choose a centre $w_i$ of weight sixteen. Every adjacent ordinary fibre of weight six has at most three pairs in the unique edge direction, so the three-point lemma forces eight pairs at the centre. Eight pairs exhaust its sixteen points: each such direction is a translation period of its fibre.

There are at least six such directions in $F_i$. Any five distinct elements of $F_i$ span $L_i$. To see this, a linear subspace of dimension at most three intersects the affine coset $w_i+V$ in at most four points. Its intersection is either empty or a coset of its intersection with $V$; a nonempty intersection with $w_i+V$ precludes being contained in $V$.

The sixteen-point fibre is therefore invariant under the sixteen-element space $L_i$, hence is one affine coset of $L_i$. Its pair count is zero in every direction outside $L_i$, including both directions from $w_i$ to the other centres.

At least two centres have weight sixteen. Every edge joining two centres therefore has capacity zero. For each nonzero $w_i\in W$, the only remaining support edge in direction $w_i$ is $\{0,w_i\}$. The origin fibre has weight at most three and hence at most one pair; the central fibre has weight at most seventeen and hence at most eight pairs. This edge covers at most eight quotient labels, strictly fewer than the required sixteen.

The contradiction completes the proof.

## Scope and replay

This proves an unrestricted exclusion for the displayed support geometry, with no spectrum census, maximum-energy value, SAT refutation, or inherited maximum-fibre screen. It does not exclude the other three affine support-eleven geometries by itself.

`verify_support11_subspaces.py` checks the explicit local graphs, the eleven-point edge bounds, cube bounds, period spans and integer-budget deductions. It also identifies the three corresponding marked supports in the imported support catalogue by explicit translated complementary subspaces. This replay is a finite verification aid, not a proof-assistant formalization and not a replacement for the written argument.
