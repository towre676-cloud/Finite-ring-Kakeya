# Additional support-eleven restrictions

These are local necessary conditions for two more of the four support-eleven affine geometries. **They do not constitute complete exclusions of those geometries.** The complete analytic exclusion established in this directory is the separate complementary-subspaces theorem.

## 1. A support whose unique edges form a ten-leaf star

The two marked representatives with masks 360808726 and 377585942 have ten unique edges, all incident to one centre. Their ten direction vectors form a set $F$ with the following properties:

* $F$ is sum-free.
* There is a nonzero period $h$ such that $F+h=F$.
* For every nonzero $z\ne h$, $|F\cap(F+z)|\le4$.

One canonical example is

\[
F=\{1,2,4,8,15\}+\{0,16\}
\]

in binary coordinates. The quotient five-set consists of four independent vectors and their sum. Its ten unordered pair sums are distinct and avoid the five-set, proving the displayed properties without an exhaustive census.

**Claim.** A thirteen-point induced subgraph of the Cayley graph with direction set $F$ has at most 39 edges.

The graph is triangle-free. Suppose first the selected graph is not bipartite, and choose its shortest odd cycle of length $2r+1$, where $2\le r\le6$. The cycle has no chords. Every outside vertex has at most $r$ neighbours on it, since consecutive cycle vertices cannot both be neighbours. Mantel bounds the graph on the remaining vertices. The resulting upper bounds on the total edges, for odd cycle lengths $5,7,9,11,13$, are

\[
37,\ 34,\ 29,\ 22,\ 13.
\]

Now suppose the selected graph is bipartite and has at least forty edges. Its sides must have sizes $5+8$ or $6+7$. The $5+8$ case is complete. The $6+7$ case misses at most two cross-edges. In either case, choose two vertices on the smaller side whose difference is not $h$: this is possible because the $h$-pairs have size two and the side has at least five vertices. They have at least five common neighbours, contradicting $|F\cap(F+z)|\le4$ for their difference $z\ne h$. This proves the claim.

**Consequently the star centre must have weight at least sixteen in any at-most-93-point counterexample.** A centre of weight at most seven forces ten neighbours of weight at least sixteen. A centre of weight $8\le c\le15$ forces all ten neighbours to have weight at least eight. The budget then forces $c\le13$, and leaves at most five extra points above those ten baseline weights. Thus every neighbour has weight at most thirteen, forcing at least four central pairs in each of the ten unique directions. That requires forty edges on at most thirteen points, contradicting the preceding claim.

This restriction has no hypothesis on the maximum fibre elsewhere in the support. It excludes this geometry whenever the global maximum is at most fifteen, and constrains it otherwise.

For exploration only, the complete ternary occupancy enumeration in **clebsch_blowup_budget.cpp** gives the stronger exact bound 32 at weight thirteen. It checks $3^{16}=43,046,721$ vectors for the two-fold independent blowup of the Clebsch graph. That stronger enumerated bound is unnecessary for the argument above.

## 2. A support obtained by adding one point to the ten-point geometry

Take

\[
S=(V\setminus\{0\})\cup(W\setminus\{0\})\cup\{u+w\},
\]

where $\dim V=3$, $\dim W=2$, $V\cap W=\{0\}$, and $0\ne u\in V$, $0\ne w\in W$. Its unique-edge graph is $K_{2,7}$ together with a pendant edge at one of the seven common neighbours, and one isolated vertex.

The two degree-seven vertices have local direction graphs isomorphic to

\[
\operatorname{blowup}_2(K_{4,4}\text{ minus a matching})\ \mathbin{\Box}\ K_2.
\]

Here every vertex in the first graph is replaced by two independent vertices, with every edge replaced by all four cross-edges. This is a 32-vertex graph of degree seven.

**degree7_pair_budget.py** computes its exact induced-edge budget by an integer dynamic program with at most 6,561 states. In each of four paired blocks, the selected counts on the two sides and two layers are $(a_0,a_1,b_0,b_1)\in\{0,1,2\}^4$. Given aggregate side counts $(A_0,A_1,B_0,B_1)$, the number of edges is bounded sharply by

\[
A_0B_0+A_1B_1+
\sum_{\text{blocks}}\bigl[-a_0b_0-a_1b_1+
\min(a_0,a_1)+\min(b_0,b_1)\bigr].
\]

The minimum terms can be simultaneously attained by aligning selected positions in the layer matchings. The other terms depend only on block counts. This proves that the dynamic program's maxima are exact.

For weights zero through sixteen, the resulting budgets are

\[
0,0,1,2,4,6,9,12,16,18,21,24,28,32,37,42,48.
\]

In particular a centre of weight at most eleven supplies at most 24 pairs in its seven unique directions.

**Both degree-seven centres must have weight at least twelve in an at-most-93-point counterexample.** Let $a$ be their smaller weight. If $a\le7$, the seven common neighbours have weight at least sixteen. Otherwise, if $8\le a\le11$, all seven neighbours have weight at least eight and the other two vertices have weight at least two. No common neighbour can have weight thirty-two. For $a=8$ at most two common neighbours can have weight at least sixteen; the required central pair mass is at least $5\cdot4+2\cdot2=24$, exceeding Mantel's bound 16. For $9\le a\le11$ at most one can have weight at least sixteen, because two would require at least $2a+76\ge94$ points. The pair demand is then at least 26, exceeding the exact local budget 24.

There is a further short reduction if either of those centres has weight at most fifteen. Write $C$ for the common neighbour carrying the pendant edge, $D$ for its pendant neighbour, and $E$ for the isolated vertex. All seven common neighbours have weight at least eight. If $C\ge16$ and $C\le31$, then $D\ge4$, giving at least $24+6\cdot8+16+4+2=94$ points; if $C=32$, the budget fails even with $D=2$. Thus $C\le15$ and $D\ge8$.

The resulting baseline is

\[
(12,12,\underbrace{8,\ldots,8}_{8\text{ vertices}},2),
\qquad\text{total }90.
\]

There are at most three extra points. Both degree-seven centres are therefore at most fifteen, all seven common neighbours and $D$ are at most eleven, and $E\le5$. This leaves a small, explicitly bounded low-centre branch; **its exclusion is not proved by these local bounds**.

## Verification scope

**verify_additional_local_cuts.py** checks the star intersection property, its thirteen-vertex extremal arithmetic, the canonical degree-seven graph identification, the integer DP replay, and the budget reductions. These local cuts are mathematically separate from any solver results. No numerical optimizer or floating-point bound is used.
