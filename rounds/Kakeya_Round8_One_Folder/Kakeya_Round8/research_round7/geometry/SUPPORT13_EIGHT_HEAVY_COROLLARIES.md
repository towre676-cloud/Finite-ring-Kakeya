# Weight restrictions when exactly eight fibres are heavy

Assume a Kakeya set in either of the two rings, in dimension five, has
pair-active support of size thirteen, at most ninety-three points, and
maximum fibre weight at most eighteen. Call a fibre heavy when its weight
is at least four. The preceding `SUPPORT13_HEAVY_FIBRES.md` proves that
there are at least eight heavy fibres.

If there are exactly eight, the five light fibres have weights two or
three. Write $t$ for the number of these five fibres with weight three.
Then the following additional necessary restrictions hold:

| Maximum fibre weight | Restriction with exactly eight heavy fibres |
|---:|---|
| At most thirteen | Impossible; there must instead be at least nine heavy fibres |
| Fourteen or fifteen | $t=5$: every light fibre has weight three |
| Sixteen, seventeen, or eighteen | $t\ge4$: at least four light fibres have weight three |

These are weight-profile restrictions. They do not assert exclusion of
every profile or every marked placement at support thirteen.

## Eight binary points determine at most twenty-five directions

Let $H$ be an eight-point subset of $\mathbb F_2^5$. The binary matrix
whose columns are the augmented vectors $(1,x)$, $x\in H$, has six rows
and eight columns. Its kernel therefore has dimension at least two. A
nonzero kernel vector has even weight, and cannot have weight two because
the points of $H$ are distinct.

If there were no weight-four relation, every nonzero kernel vector would
have weight six or eight. Choose two distinct nonzero vectors in the
kernel. If one has weight eight, their sum has weight two. If both have
weight six, their supports intersect in at least four positions, so their
nonzero sum has weight at most four. Both alternatives contradict the
assumed absence of weight-two and weight-four vectors. Hence four points
of $H$ sum to zero, forming an affine plane.

That plane has three nonzero directions, each represented by two distinct
unordered pairs. The total of $\binom82=28$ pairs in $H$ consequently
determines at most $28-3=25$ distinct directions:

$$
|D(H)|\le25.
\tag{1}
$$

## The remaining directions force light-fibre resources

At least six of the thirty-one nonzero residue directions lie outside
$D(H)$. Every edge in these directions has a light endpoint, and the
total required capacity is at least $6\cdot16=96$.

The five light fibres have total directional pair resource

$$
C_L=(5-t)\binom22+t\binom32=5+2t.
\tag{2}
$$

If the maximum fibre weight is $m\le17$, every other endpoint has pair
count at most $\lfloor m/2\rfloor$. Charging each edge to one light
endpoint as in the preceding lemma gives

$$
96\le\lfloor m/2\rfloor(5+2t).
\tag{3}
$$

For $m\le13$, the right side is at most $6\cdot15=90$, impossible.
For $m\le15$ and $t\le4$, it is at most $7\cdot13=91$, impossible.
For $m\le17$ and $t\le3$, it is at most $8\cdot11=88$, impossible.

For $m=18$, the exceptional nine-pair directions contribute at most
$n_{18}$ additional units, where $n_{18}$ counts eighteen-point fibres.
The weight budget implies

$$
93\ge18n_{18}+4(8-n_{18})+2\cdot5=42+14n_{18},
$$

so $n_{18}\le3$. If $t\le3$, the required capacity would therefore obey

$$
96\le8(5+2t)+n_{18}\le88+3=91,
$$

again impossible. This proves all the listed restrictions.

The direction-space argument is a short linear-algebra proof and needs
no affine orbit census. The local capacity bound needs no sumset table.
