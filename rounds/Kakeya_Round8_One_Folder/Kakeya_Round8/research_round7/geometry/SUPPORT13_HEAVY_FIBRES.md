# Thirteen support points require at least eight heavy fibres

## Statement

Let $R$ be either $\mathbb Z/4\mathbb Z$ or
$\mathbb F_2[\epsilon]/(\epsilon^2)$. Suppose a Kakeya subset of $R^5$
has pair-active support of size thirteen, and every fibre has at most
eighteen points. Then **at least eight fibres have weight at least four**.

This necessary condition does not use the total-weight bound ninety-three,
a fibre-spectrum census, an affine support catalogue, or a SAT result. It
does not by itself exclude a support or settle the dimension-five problem.

## Proof

Write $V=\mathbb F_2^5$ and let $S\subseteq V$, $|S|=13$, be the
pair-active support. Thus every fibre $A_v\subseteq V$ has weight
$2\le w_v\le18$. For $d\ne0$, let $p_v(d)$ count the disjoint
$d$-pairs in $A_v$.

Call a vertex **heavy** if $w_v\ge4$, and put

$$
H=\{v\in S:w_v\ge4\},\qquad h=|H|,
\qquad D(H)=\{a+b:a,b\in H,\ a\ne b\}.
$$

The remaining fibres are **light**: their weights are two or three, and
each directional pair count is zero or one. Set

$$
C_L=\sum_{v\in S\setminus H}\binom{w_v}{2}.
$$

Each unordered pair in a fibre has one nonzero binary difference, so

$$
\sum_{d\ne0}p_v(d)=\binom{w_v}{2},
\qquad C_L\le3(13-h).
\tag{1}
$$

For each residue direction $d$, the quotient $V/\langle d\rangle$
has sixteen elements. Covering all lifted directions requires total
edge capacity at least sixteen. The capacity of an edge with endpoints
$a,b$, $a+b=d$, is at most $p_a(d)p_b(d)$. Ring carries only translate
the relevant quotient sumsets, so this bound holds for both rings.

If $d\notin D(H)$, every such edge has a light endpoint. Charge the
edge to one light endpoint, choosing either one when both are light.
Each vertex is incident to at most one edge in any fixed direction.
Ordinarily an edge costs at most eight times its charged pair count:
every fibre of weight at most seventeen has $p_v(d)\le8$.

The only possible excess is an edge to an eighteen-point fibre with nine
pairs in that direction. Nine pairs cover that entire fibre, so
$A_v+d=A_v$. An eighteen-point fibre can have **at most one** such
nonzero period. Two distinct nonzero periods generate a two-dimensional
subgroup, whose four-element orbits would partition the fibre, forcing
$4\mid18$. This is impossible. Consequently each eighteen-point fibre
can create at most one exceptional edge, with excess at most one.

Writing $n_{18}$ for the number of eighteen-point fibres, summing these
charges yields the stronger intermediate inequality

$$
\boxed{16\bigl(31-|D(H)|\bigr)\le8C_L+n_{18}.}
\tag{2}
$$

Now $|D(H)|\le\binom h2$, $C_L\le3(13-h)$, and $n_{18}\le h$.
If $0\le h\le7$, (2) would therefore imply

$$
16\left(31-\binom h2\right)\le24(13-h)+h.
$$

The left side minus the right side equals

$$
184+31h-8h^2.
$$

It is a concave quadratic, positive at both endpoints of $[0,7]$:
its values there are $184$ and $9$. It is therefore positive throughout
that interval. This contradiction proves $h\ge8$.

## Encoding consequence

In any faithful support-thirteen formula whose fibre domains all have
weights between two and eighteen, one may add

$$
\sum_{v\in S}[w_v\ge4]\ge8.
$$

The accompanying `heavy_fibre_cut.py` defines thirteen indicators by
equivalence to the existing spectrum choices of weight at least four,
then uses the baseline encoder's bidirectional unary counter. It appends
clauses only, checks the domain assumptions, and does not alter the
frozen baseline or variant encoders. The wrapper has not been credited
with any new UNSAT certificate.

The finite replay checks every light fibre, all normalized eighteen-point
fibres with a specified nonzero period, all two-period invariant subsets
for one representative two-space, all eight numerical contradictions,
and the complete $2^{13}$ Boolean table of the added cardinality cut.
The proof above establishes the result without this finite corroboration.
