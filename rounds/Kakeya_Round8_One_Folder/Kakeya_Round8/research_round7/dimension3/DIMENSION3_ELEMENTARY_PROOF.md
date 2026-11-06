# An elementary exact theorem in dimension three

## Theorem

For either ring

$$
R=\mathbb Z/4\mathbb Z\quad\text{or}\quad
R=\mathbb F_2[\epsilon]/(\epsilon^2),
$$

the minimum size of a Kakeya subset of $R^3$ is

$$
\boxed{k_R(3)=22=3\cdot2^3-2.}
$$

Here Kakeya means that the set contains a full line in every primitive
direction. The proof below is independent of SAT, a spectrum census,
support-orbit enumeration, and the earlier dimension-five reductions.
The accompanying finite replay corroborates its small local facts but is
not needed for the mathematical argument.

## 1. Fibres and the two basic counting bounds

Write $u=2$ or $u=\epsilon$, and put $V=\mathbb F_2^3$. Reduction
modulo $u$ partitions a set $K\subseteq R^3$ into binary fibres

$$
A_a=\{t\in V:\widetilde a+ut\in K\}\qquad(a\in V).
$$

A primitive line meets each of its two residue fibres in a pair with the
same nonzero binary difference. A singleton fibre therefore lies on no
such line and can be deleted. Write $S\subseteq V$ for the remaining
pair-active support, $w_a=|A_a|\ge2$, and $s=|S|$.

For $d\ne0$, let $P_a(d)\subseteq V/\langle d\rangle$ be the set of
classes of $d$-pairs in $A_a$, and let $p_a(d)=|P_a(d)|$. The quotient
has four elements. The residue edge $\{a,a+d\}$ covers a translate of
$P_a(d)+P_{a+d}(d)$, so every Kakeya set satisfies

$$
\sum_{\{a,b\}\subseteq S:\ a+b=d}|P_a(d)+P_b(d)|\ge4
\qquad(d\ne0).
\tag{1}
$$

The carry in the first ring only translates these sumsets; all bounds
used below therefore hold for both rings. We use their actual cardinality
when needed, and otherwise the elementary upper bound

$$
|P_a(d)+P_b(d)|\le p_a(d)p_b(d).
\tag{2}
$$

There are seven nonzero residue directions. A support of at most four
points has at most six edges and cannot represent all seven directions.
Thus $s\ge5$.

Define $Q(A)=\sum_{d\ne0}p_A(d)^2$. Summing (1), applying (2) and
$2xy\le x^2+y^2$, and observing that a vertex has at most one edge in
each direction, gives

$$
28\le\sum_{\{a,b\}\subseteq S}p_a(a+b)p_b(a+b)
\le\frac12\sum_{a\in S}Q(A_a).
$$

Consequently

$$
\sum_{a\in S}Q(A_a)\ge56.
\tag{3}
$$

Also, for every fibre,

$$
\sum_{d\ne0}p_A(d)=\binom{|A|}{2}.
\tag{4}
$$

## 2. The complete local information needed

The following energy bounds and pair-count facts are elementary:

| Weight $w$ | Maximum $Q(A)$ | Additional fact |
|---:|---:|---|
| 2 | 1 | One positive direction, with one pair |
| 3 | 3 | Three positive directions, each with one pair |
| 4 | 12 | An affine plane has two pairs in its three direction-space directions; every other four-set has one pair in six directions |
| 5 | 16 | Two pairs in the three nonzero directions of one two-space, and one pair elsewhere |
| 6 | 33 | Three pairs in exactly one direction, and two pairs in every other direction |
| 7 | 63 | Three pairs in every nonzero direction |
| 8 | 112 | Four pairs in every nonzero direction |

The first two rows follow by counting pairs. A four-set has a repeated
pair difference precisely when it is an affine plane, giving the third
row. For the remaining rows, let $B=V\setminus A$. For every $d\ne0$,
the four $d$-pairs partition $V$, and counting which pairs meet the
complement gives

$$
p_A(d)=|A|-4+p_B(d).
\tag{5}
$$

Apply this identity to complements of sizes three, two, one, and zero.

We will also use this elementary consequence of the first four rows:

$$
Q(A)-1\le\frac{11}{2}(|A|-2)
\qquad(2\le|A|\le5).
\tag{6}
$$

If two four-point fibres are affine planes with the same direction space
$L$, then for $0\ne d\in L$ their quotient pair sets are affine cosets
of the same one-dimensional space $L/\langle d\rangle$. Their sumset
has **two** elements, not four:

$$
|P_A(d)+P_B(d)|=2.
\tag{7}
$$

Assume from now on, for a contradiction, that $|K|\le21$. We consider
the four possible support sizes.

## 3. Five support points

Any five-point subset of $V$ is an affine plane $P$ together with one
point $c\notin P$. Indeed its three-point complement lies in a unique
four-point affine plane, whose fourth point is $c$; the other coset is
$P$. The four edges from $c$ to $P$ have unique directions. Each must
cover all four quotient labels by itself.

Let $w=|A_c|$. If $w=2$ or $3$, the central fibre has fewer than four
positive pair directions. The same is true of a four-point affine plane.
If $w=4$ and the fibre is not a plane, its pair counts are at most one;
all four neighbouring fibres would need four pairs and hence eight
points each. These cases are impossible.

If $w=5$, its three two-pair directions form a two-space minus zero.
The four spoke directions form an affine plane not containing zero. Its
intersection with any linear two-space has at most two points. At least
two spokes therefore have central pair count one, forcing their two
neighbours to have eight points each. The total is at least
$5+8+8+2+2=25$, again impossible.

If $w=6$ or $7$, every central pair count is at most three. Each
neighbour needs at least two pairs on its unique spoke, so each has at
least four points. The total is at least $6+4\cdot4=22$.

It remains to consider $w=8$. The four fibres on $P$ have total weight
at most thirteen. Each of the three nonzero directions of $P$'s
direction space occurs on two edges of $P$, a perfect matching of its
four vertices. Call a fibre large if its weight is at least four. There
are at most two large fibres on $P$.

With no large fibre, each matching supplies at most two labels. With one
large fibre, each matching has a large–small edge and a small–small edge.
The latter contributes at most one. Since the large fibre has weight at
most seven, equality with the required four demands a contribution of
three from the first edge and one from the second. The large fibre must
have weight at least six, and all three small fibres must have positive
pair counts in all three plane directions. Each small fibre therefore
has weight at least three. Their total is at least $6+3+3+3=15$.

With two large fibres, the budget thirteen forces each to have weight at
most five. The two matchings that pair large with small must each obtain
two labels from both edges. Both small fibres have positive pair counts
in two distinct directions, so both have weight at least three. The
total is at least $4+4+3+3=14$.

All possibilities contradict the budget thirteen. Hence support five
requires at least twenty-two points.

## 4. Six support points

Translate a largest fibre to residue zero, and write the two missing
residues as $a,b\ne0$. Put

$$
L=\langle a,b\rangle=\{0,a,b,a+b\}.
$$

The support consists of the affine plane $C=V\setminus L$ and the two
points $0,a+b$. Each missing-hub direction $a,b$ occurs on exactly two
edges, namely one perfect matching on $C$.

### Largest fibre eight

The five outer fibres have total weight at most thirteen. At most one
has weight at least four, and none has weight above five. In either
missing-hub direction, at most one of the two edges has capacity above
one, and that capacity is at most two. Their sum is at most three,
contradicting (1).

### Largest fibre seven

The five outer fibres have total weight at most fourteen. To cover a
missing-hub direction, at least one outer fibre has weight at least four.
If there is only one such fibre and it has weight at most five, the same
capacity bound three applies. If it has weight six, the outer profile is
exactly $6,2,2,2,2$. Reaching four in either matching requires three
pairs at the six-point fibre in that direction. A six-point fibre has
only one three-pair direction, so it cannot cover both $a$ and $b$.

The only remaining possibility is outer profile $4,4,2,2,2$. Both
four-point fibres must be on $C$, since otherwise a missing-direction
matching has at most one large endpoint. If the edge joining these two
large vertices has neither direction $a$ nor $b$, both missing
directions pair large with small. Each of the two small fibres on $C$
would need positive pair counts in both directions, impossible for a
two-point fibre.

Thus the large–large edge has, say, direction $a$. Direction $b$
pairs large with small and requires both capacities to be two. Both
four-point fibres therefore have two $b$-pairs and are affine planes;
both small fibres have their sole positive direction equal to $b$.
In direction $a$, the small–small edge consequently contributes zero.
The large–large edge must supply four, so both planes have positive
pair count in direction $a$. Their direction spaces contain $a,b$
and hence both equal $L$. By (7), this edge has capacity two. This is
the final contradiction for largest weight seven.

### Largest fibre at most six

If all fibres have weight at most five, (6) gives

$$
\sum Q(A_v)\le6+\frac{11}{2}(21-12)=55.5<56,
$$

contradicting (3). Therefore some fibre has weight six.

Let $H\subseteq S$ be the set of vertices of weight at least four,
let $h=|H|$, let $n_6$ count six-point fibres, and put

$$
C_0=\sum_{v\in S\setminus H}\binom{w_v}{2},\qquad
D(H)=\{x+y:x,y\in H, x\ne y\}.
$$

Every direction outside $D(H)$ has only edges with a light endpoint,
whose weight is two or three and whose pair counts are at most one.
Charge each such edge to one light endpoint. Normally its capacity is
at most twice that endpoint's pair count. The only exception is an edge
to a six-point fibre in its unique three-pair direction, costing at most
one additional label. Each six-point fibre has at most one such edge.
Using (4), summing the charges gives the useful inequality

$$
4(7-|D(H)|)\le2C_0+n_6.
\tag{8}
$$

There are at most three heavy vertices: a six-point fibre, three further
fibres of weight at least four, and two further pair-active fibres would already cost
$6+3\cdot4+2\cdot2=22$. If $h=1$, (3) fails because the total energy
is at most $33+5\cdot3=48$.

If $h=2$, the four light fibres have total weight at most eleven. For
weights two or three, $\binom w2=2w-3$, so $C_0\le10$. Also $n_6\le2$
and $|D(H)|=1$. Inequality (8) would require

$$
24\le2C_0+n_6\le22,
$$

a contradiction.

If $h=3$, the three light fibres have total weight at most seven, so
$C_0\le5$. There can be only one six-point fibre, because two sixes,
a four, and three twos already total twenty-two. Since $|D(H)|\le3$,
(8) now requires

$$
16\le2C_0+n_6\le11,
$$

again impossible. This completes support six without a profile census.

## 5. Seven support points

Again place a largest fibre at zero, and let $a\ne0$ be the missing
residue. Direction $a$ has exactly three outer edges.

With largest weight eight, the six outer fibres have total weight at
most thirteen. All have weight at most three and pair counts at most
one, so these three edges supply at most three labels.

With largest weight seven, the outer budget is fourteen. Unless the
outer profile is $4,2,2,2,2,2$, all outer pair counts are at most one
and the same obstruction applies. In the exceptional profile, attaining
four labels in direction $a$ requires capacity two on the edge
incident with the four-point fibre and capacity one on both other edges.
All five two-point fibres must therefore have their sole positive
direction equal to $a$. Outside direction $a$, the only potentially
active edge is the one joining the seven-point and four-point fibres.
It has just one direction, so the other five directions receive no
coverage at all.

Finally suppose the largest weight is at most six. Two six-point fibres
would cost at least $6+6+5\cdot2=22$, so there is at most one. With no
six-point fibre, (6) bounds the total energy by
$7+\tfrac{11}{2}(21-14)=45.5<56$. With exactly one, the other six fibres
have total weight at most fifteen, and the energy is at most

$$
33+6+\frac{11}{2}(15-12)=55.5<56.
$$

Both contradict (3), completing support seven.

## 6. Eight support points

A fibre of weight eight would force total weight at least
$8+7\cdot2=22$. If the maximum is seven, the entire profile is
$7,2,2,2,2,2,2,2$. Let $x$ count active edges joining the seven-point
fibre to a two-point fibre, and let $y$ count active edges joining two
two-point fibres. Each small fibre has one available pair direction, so

$$
x+2y\le7.
$$

The first type of edge has capacity at most three, and the second at
most one. Total capacity is therefore at most $3x+y\le21$, whereas
(1) requires at least $7\cdot4=28$.

If the maximum is at most six, at most one six-point fibre is possible.
Without one, (6) gives total energy at most
$8+\tfrac{11}{2}(21-16)=35.5<56$. With one, the other seven fibres have
total weight at most fifteen, giving at most

$$
33+7+\frac{11}{2}(15-14)=45.5<56.
$$

Thus support eight is also impossible at total weight twenty-one.

We have excluded every possible pair-active support size. Hence
$|K|\ge22$.

## 7. The matching construction

Take the full eight-point zero residue fibre $uV$, and for each
$d\in V\setminus\{0\}$ take the two points

$$
\widetilde d,\qquad \widetilde d+ud.
$$

This set has $8+2\cdot7=22$ points. For every primitive direction
$D=\widetilde d+ue$, the line $ue+RD$ consists of the four points

$$
ue,\quad u(e+d),\quad \widetilde d,\quad \widetilde d+ud,
$$

all belonging to the construction. This works in both rings and proves
the upper bound. Together with the preceding lower bound it establishes
$k_R(3)=22$.

## Reproducibility and proof status

`verify_dimension3_hand_proof.py` independently enumerates all 256 binary
three-space subsets, checks the local pair-count table, the shared-plane
capacity fact, and every support geometry used above. It also enumerates
the small weight partitions as a corroborating check; the proof itself
does not rely on that enumeration. In particular its six surviving
energy-only support-six profiles are all covered by the coarse argument
in Section 4.

The separate exact-ring SAT certificates give a second reproducible
computer-assisted route. They are not premises of this elementary proof.
This document is a mathematical proof, not a complete proof-assistant
formalization. The dimension-five lower bound of ninety-four and the
general formula remain separate open targets in this project.
