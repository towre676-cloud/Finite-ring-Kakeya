# An elementary nine-point difference bound in binary dimension five

For a finite set $A\subseteq\mathbb F_2^5$, write

$$
D(A)=\{a+b:a,b\in A,\ a\ne b\}.
$$

**Theorem.** If $|A|=9$, then $|D(A)|\le28$.

The proof below is symbolic. It does not use the normalized nine-set
enumeration, the fibre-spectrum census, a SAT solver, or a sumset table.
The independent finite calculation in `DIFFERENCE9_REPLAY.json` agrees
with the bound and exhibits a set attaining twenty-eight.

## Every eight-point set contains an affine plane

Let $B\subseteq\mathbb F_2^5$ have eight points. Form the augmented
relation code

$$
\mathcal C_B=\left\{(c_b)_{b\in B}\in\mathbb F_2^B:
\sum_b c_b=0,\quad\sum_b c_b b=0\right\}.
$$

The defining linear map has target dimension six, so
$\dim\mathcal C_B\ge2$. All its words have even weight. A nonzero word
cannot have weight two because the points of $B$ are distinct. A word
of weight four gives four distinct points summing to zero, hence an
affine plane.

Suppose there is no affine plane. Every nonzero codeword then has weight
six or eight. Choose two distinct nonzero codewords $u,v$. If both have
weight six, their supports intersect in at least four positions, so
$0<\operatorname{wt}(u+v)\le4$. If one has weight eight, their difference
has weight two; two distinct weight-eight words are impossible. In
either case this contradicts the permitted nonzero weights. Thus every
eight-point set contains an affine plane.

One immediate consequence is $|D(B)|\le25$: each of the three directions
of a contained affine plane occurs for two distinct unordered pairs,
so at least three repetitions occur among the twenty-eight pairs.

## Nine points containing at most two affine planes

Let $|A|=9$. Every deletion of one point leaves an eight-point set and
therefore leaves an affine plane. Consequently $A$ cannot have zero or
one affine plane. If it has exactly two, the planes are disjoint:
deleting a common point otherwise destroys both.

Write these disjoint planes as $P=a+U$ and $Q=b+V$, where $U,V$ are
two-dimensional vector spaces, and write $x$ for the ninth point.
If $P\cup Q$ has affine rank at most four, its differences have at most
fifteen possible nonzero values. Adding $x$ creates at most eight new
differences, giving $|D(A)|\le23$.

It remains to consider affine rank five. Translate so that
$P=U$ and $Q=c+V$. The equality
$\dim\langle U,V,c\rangle=5$ forces

$$
W=U+V,\qquad\dim W=4,\qquad U\cap V=\{0\},\qquad c\notin W.
$$

The cross-plane differences are exactly the sixteen points of $c+W$.
The internal differences contribute six further points, namely
$(U\setminus\{0\})\cup(V\setminus\{0\})$. The ambient space has
only the two cosets $W$ and $c+W$. If $x\in W$, all four differences
between $x$ and $Q$ already lie in the cross-plane difference set.
If $x\in c+W$, the same holds for its four differences with $P$.
Thus the ninth point adds at most four differences, and

$$
|D(A)|\le16+6+4=26.
$$

## Nine points containing at least three affine planes

Choose three distinct affine planes $P_1,P_2,P_3\subseteq A$.
Construct a graph whose vertices are the thirty-six unordered pairs
of distinct points of $A$. Each plane contributes three graph edges:
for each of its three directions, join its two parallel unordered pairs.

These are **nine distinct graph edges**. Indeed, their two pair-vertices
determine the four points of the plane, so the same graph edge cannot
come from two different planes. Every graph edge joins pairs with the
same difference. For any one difference, there are at most three graph
edges, one supplied by each chosen plane. Therefore the only possible
cycle is a triangle, and any triangle uses all three planes.

There can be at most one such triangle. If triangles occurred in two
different directions, any fixed pair of planes among $P_1,P_2,P_3$
would share an unordered pair of points in each of those directions.
These two pairs are distinct and their union contains at least three
points. Two distinct affine planes over $\mathbb F_2$ cannot share
three points: three distinct points are affinely independent and
determine their affine plane. This is a contradiction. There cannot be
two triangles in one direction either, since that direction has at most
three graph edges.

The graph therefore has cycle rank at most one. Its nine edges enforce
at least eight independent equalities among unordered-pair differences.
More explicitly, its graphic rank is at least $9-1=8$. Since every
connected component lies inside one same-difference class, that rank is
at most

$$
\sum_{d\in D(A)}\bigl(\#\{\{a,b\}:a+b=d\}-1\bigr)
=\binom92-|D(A)|=36-|D(A)|.
$$

It follows that $8\le36-|D(A)|$, proving $|D(A)|\le28$.

## Use in the heavy/light inequality

The universal bounds for sets of zero through nine heavy residues are

$$
0,0,1,3,6,10,15,21,25,28.
$$

Thus nine heavy residues leave at least three binary directions outside
their difference set. The nine-heavy version of the existing integer
dual may use a left side of $32(31-28)=96$. Its actual profile sweep
found the same 3,006 exclusions as the earlier optional-heavy sweep;
this new geometric proof does not supply any additional counted
profile exclusion.

This argument was proposed by the root agent and checked separately by
the dense-encoder agent. That is an additional model-agent review, not
an independent human review or a proof-assistant formalization.
