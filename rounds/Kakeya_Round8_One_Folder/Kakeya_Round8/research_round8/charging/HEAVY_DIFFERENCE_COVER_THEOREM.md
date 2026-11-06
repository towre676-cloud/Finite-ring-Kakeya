# Thirteen residue fibres of maximum size eleven require a heavy difference cover

Let $R$ be either $\mathbb Z/4\mathbb Z$ or
$\mathbb F_2[\epsilon]/(\epsilon^2)$. Consider a primitive-direction
Kakeya set in $R^5$ whose pair-active residue support $S\subseteq
\mathbb F_2^5$ has thirteen points. Write $A_a\subseteq\mathbb F_2^5$
for its fibre at $a\in S$ and assume

$$
2\le |A_a|\le11\qquad(a\in S).
$$

Define the heavy residue set and its differences by

$$
H=\{a\in S:|A_a|\ge4\},\qquad
D(H)=\{a+b:a,b\in H,\ a\ne b\}.
$$

**Theorem.** The heavy set satisfies

$$
\boxed{|H|\ge10\quad\hbox{and}\quad D(H)=\mathbb F_2^5\setminus\{0\}.}
$$

No total-size assumption, fibre-spectrum census, support-orbit catalogue,
or SAT computation is used. The theorem holds for every maximum at most
eleven, not merely exact maximum eleven.

## Pair resources and two small geometric bounds

For $d\ne0$, let $p_a(d)$ be the number of disjoint $d$-pairs in $A_a$.
Every unordered fibre pair has exactly one difference, so

$$
\sum_{d\ne0}p_a(d)=\binom{|A_a|}{2}.
$$

All fibres have $p_a(d)\le5$. A light fibre, of size two or three, has
$p_a(d)\in\{0,1\}$ and total pair resource at most three. A three-point
fibre has exactly three positive directions, which are the three nonzero
elements of a two-dimensional binary vector space.

For a fixed residue direction $d$, the residue edges $\{a,a+d\}$ form a
matching. Their quotient sumsets must together cover sixteen lifted
directions. Each edge has capacity at most $p_a(d)p_{a+d}(d)$.
The ring carry only translates a quotient sumset, so this estimate applies
to both rings.

We use the elementary binary-space facts

$$
|B|=8\implies |D(B)|\le25,
\qquad
|B|=9\implies |D(B)|\le28.
\tag{1}
$$

Their symbolic proofs are supplied in the immutable Round7 file at the
checkpoint-root path
`research_round7/dense_encoder/NINE_POINT_DIFFERENCE_ANALYTIC_PROOF.md`.
The eight-point fact follows by finding an affine plane through the
augmented relation code. The nine-point proof uses either two disjoint
planes or nine pair-equality relations from three planes, which have
cycle rank at most one. The accompanying Round8 finite verifier also
checks the complete affine-basis normalizations as corroboration.

## At least nine heavy fibres

Put $h=|H|$ and $L=S\setminus H$. If $d\notin D(H)$, every residue
edge in direction $d$ has a light endpoint. Charge its capacity to one
such endpoint. Each charged pair count costs at most five, and an
endpoint is incident to at most one edge in any given direction. Hence

$$
16(31-|D(H)|)\le5\sum_{a\in L}\binom{|A_a|}{2}
\le15(13-h).
\tag{2}
$$

For $0\le h\le7$, use $|D(H)|\le\binom h2$. The left side of (2)
minus the final right side is at least

$$
301+23h-8h^2.
$$

This concave quadratic is positive at both endpoints of $[0,7]$, where
it equals $301$ and $70$. Thus $h\le7$ is impossible. If $h=8$, (1)
makes the required capacity at least $16\cdot6=96$, whereas five light
fibres contribute at most $15\cdot5=75$. Therefore $h\ge9$.

## Nine heavy fibres are impossible

Suppose $h=9$. There are exactly four light residues. Write

$$
\Lambda=(\mathbb F_2^5\setminus\{0\})\setminus D(H).
$$

By (1), $|\Lambda|\ge3$. Fix $d\in\Lambda$. There is no heavy-heavy
edge in this direction. A heavy-light edge contributes at most five,
and a light-light edge contributes at most one.

**All four light vertices must belong to active heavy-light edges in
direction $d$.** If there is a light-light edge, it uses two of the four
light vertices, leaving at most two heavy-light edges; the capacity is
at most $1+2\cdot5=11$. Two light-light edges supply even less. If there
is no light-light edge but some light vertex is unmatched or its pair
count is zero, at most three heavy-light edges contribute, with total
at most fifteen. Both cases fall short of sixteen.

It follows that every light fibre has a positive pair count in every
direction of $\Lambda$. A light fibre has at most three positive
directions. Consequently $|\Lambda|=3$, every light fibre has size
three, and

$$
\Lambda=\{d_1,d_2,d_1+d_2\}
$$

for distinct nonzero $d_1,d_2$. Choose any light residue $a$. The active
heavy-light edges just proved put both $a+d_1$ and $a+d_2$ in $H$.
Their difference is $d_1+d_2$, so $d_1+d_2\in D(H)$, contradicting its
membership in $\Lambda$. Thus $h\ne9$, and $h\ge10$.

## Every direction has a heavy-heavy edge

There are now at most three light residues. If some direction lay outside
$D(H)$, charging its matching edges to light endpoints would give total
capacity at most $3\cdot5=15$. The required capacity is sixteen. This
contradiction proves $D(H)=\mathbb F_2^5\setminus\{0\}$.

## Exact Boolean consequence

Let $b_a$ mean that fibre $a$ has weight at least four. Introduce, for
each residue edge, $e_{ab}\leftrightarrow(b_a\wedge b_b)$. One may add

$$
\sum_{a\in S}b_a\ge10,
\qquad
\bigvee_{\substack{\{a,b\}\subseteq S\\a+b=d}}e_{ab}
\quad(d\ne0).
$$

The implementation defines every reused heavy indicator from the spectrum
selectors by equivalence, checks that all fibre domains have weights in
$[2,11]$, and appends exact AND gates and a bidirectional unary counter.
It therefore adds only necessary conditions for actual Kakeya sets.
The result does not by itself exclude any whole marked support.

For the four remaining marked supports, residue zero is a distinguished
largest fibre of exact weight eleven and is therefore heavy. Under that
hub convention the surviving heavy-set counts, for sizes $10,11,12,13$,
are respectively $(4,21,11,1)$, $(6,31,12,1)$, $(1,24,12,1)$, and
$(2,24,12,1)$ in the order of masks
$377850134,411136406,671697334,2185856310$.
