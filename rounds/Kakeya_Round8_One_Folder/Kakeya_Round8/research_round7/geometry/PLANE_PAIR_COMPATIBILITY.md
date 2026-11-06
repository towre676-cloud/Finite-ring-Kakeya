# Exact compatibility of three directional pair counts

## Result and scope

Let $A\subseteq\mathbb F_2^5$, let $w=|A|$, and let $d,e$ be distinct
nonzero directions. Write

$$
p=p_A(d),\qquad q=p_A(e),\qquad r=p_A(d+e),
\qquad p_A(u)=\tfrac12|A\cap(A+u)|.
$$

**The following condition is necessary and sufficient for these four
integers to be realized by some subset of binary five-space.** Put

$$
s=p+q+r,\qquad m=\min(p,q,r).
$$

There must exist nonnegative integers $a,b$ such that

$$
2a+b\le m,\qquad
w-2s+8a+3b\ge0,\qquad
8-w+s-3a-b\ge0.
\tag{1}
$$

All of $w,p,q,r$ must also be nonnegative integers. The criterion itself
then forces the elementary bounds $w\le32$ and $p,q,r\le w/2$.

This theorem describes one fibre on one two-dimensional direction space.
It is independent of the spectrum census, support classification, ring
carry, and SAT solver. It is **not** a complete characterization of a
fibre's thirty-one directional pair counts: different planes must still
be realized by the same set. No new whole-support exclusion is credited
to this theorem without a checked global certificate.

## Proof

Let $L=\langle d,e\rangle$. Its eight affine cosets partition the ambient
space, and every pair in any of the three directions under consideration
lies entirely in one such coset.

Identify one coset with the four points $0,d,e,d+e$. Its possible
contributions to $(w,p,q,r)$ are exactly

$$
\begin{array}{c|c}
\text{occupancy} & (w,p,q,r)\\ \hline
0 &(0,0,0,0)\\
1 &(1,0,0,0)\\
2 &(2,1,0,0),\ (2,0,1,0),\ (2,0,0,1)\\
3 &(3,1,1,1)\\
4 &(4,2,2,2).
\end{array}
$$

Let $a$ be the number of full cosets and $b$ the number with three
points. The two-point cosets must occur in the respective numbers

$$
c_d=p-2a-b,\quad c_e=q-2a-b,\quad c_{d+e}=r-2a-b.
$$

Their nonnegativity is precisely the first inequality in (1). Counting
points and then cosets determines the remaining two numbers:

$$
n_1=w-2s+8a+3b,\qquad
n_0=8-w+s-3a-b.
$$

These are the other two inequalities. This proves necessity.

Conversely, given integers satisfying (1), the seven displayed numbers

$$
a,b,c_d,c_e,c_{d+e},n_1,n_0
$$

are nonnegative and sum to eight. Assign that many of the eight cosets to
each occupancy type, choosing the indicated pair direction in each
two-point coset. The resulting subset has exactly the requested weight
and three pair counts. This proves sufficiency.

The same argument works in any binary dimension $n\ge2$, replacing eight
by $2^{n-2}$. The supplied table and clause implementation use $n=5$.

## Readable consequences

The translation defect

$$
D_A(u)=w-2p_A(u)=\tfrac12|A\triangle(A+u)|
$$

satisfies the triangle inequality. Therefore

$$
p_A(d)+p_A(e)-p_A(d+e)\le\lfloor w/2\rfloor.
\tag{2}
$$

Permuting the three directions gives the other two inequalities. These
constrain **near-maximal** pair counts, whereas closure of the maximal
directions alone only handles the extremal case.

Let the eight coset occupancies be $t_1,\ldots,t_8\in\{0,1,2,3,4\}$.
Then

$$
p+q+r=\sum_{i=1}^8\binom{t_i}{2}.
$$

Concentrating the points gives the sharp upper bound

$$
p+q+r\le6\lfloor w/4\rfloor+\binom{w\bmod4}{2}.
\tag{3}
$$

Balancing the occupancies gives the sharp lower bound

$$
p+q+r\ge8\binom{\lfloor w/8\rfloor}{2}
 +(w\bmod8)\lfloor w/8\rfloor.
\tag{4}
$$

The full condition (1) contains more information than these scalar
inequalities. One particularly simple specialization is

$$
p_A(d)=0
\quad\Longrightarrow\quad
w-8\le p_A(e)+p_A(d+e)\le\lfloor w/2\rfloor.
\tag{5}
$$

Indeed $m=0$ forces $a=b=0$, so (1) becomes

$$
2(q+r)\le w\le8+q+r.
$$

Thus a nine-point fibre cannot have zero pairs in all three directions of
a binary plane. A sixteen-point fibre with no pairs in direction $d$
must satisfy $p_A(e)+p_A(d+e)=8$ for every $e\notin\{0,d\}$.

## Complete finite table and efficient clauses

Adding eight copies of the seven local contribution types produces
**2,233 distinct tuples** $(w,p,q,r)$. There are **629 distinct triples**
$(p,q,r)$. For each of those triples, the attainable weights form one
integer interval. The interval property is exhaustively checked against
the complete table; it is not assumed as an unproved claim in arbitrary
dimension.

For a selected local triple $(p,q,r)$ with weight interval $[\ell,h]$,
the CNF wrapper adds

$$
\bigl(p_A(d)=p\ \wedge\ p_A(e)=q\ \wedge\ p_A(d+e)=r\bigr)
\Longrightarrow\ell\le w\le h.
$$

If the triple has no attainable weight among the current fibre's spectrum
choices, it is forbidden outright. Clauses already implied by the
spectrum histogram are omitted. This omission weakens the added clause
set and does not threaten the one-way assignment argument. The weight
threshold auxiliaries are each defined as the disjunction of the
existing selected spectrum variables with sufficiently large weight;
both directions of each equivalence are included.

Only planes whose three nonzero directions already occur in that
vertex's incident direction list are used. No unobserved direction or
new fibre shape is silently selected. Every real fibre extends the
formula by setting the new threshold variables to its actual weight.

For the full maximum range two through eighteen, a local plane contributes
336 unconditional forbidden triples, 282 lower-weight implications, and
184 upper-weight implications: **802 substantive clauses**. The fourteen
weight thresholds and their definitions are shared by every plane at the
same fibre. Restricted hub domains can give different counts.

## Replay and limits

Run from the package root:

    python3 research_round7/geometry/verify_plane_cuts.py

The replay performs the following substantive checks:

* all sixteen subsets of a four-point coset give exactly the seven types;
* all 65,536 subsets of binary four-space give exactly the four-coset
  recurrence's 201 tuples;
* each of the 2,233 five-space tuples has an explicit subset witness whose
  pair counts are recomputed;
* all 162,129 candidate quadruples with $0\le w\le32$ and
  $0\le p,q,r\le16$ agree with the independent integer criterion (1);
* all 629 weight intervals are contiguous and exactly match the table;
* 1,558 actual fibre witnesses of weights two through eighteen satisfy
  the appended clauses;
* all 2,006 census-compatible but locally impossible quadruples in that
  weight range violate the wrapper, while all 1,558 possible ones pass.

The executable `plane_cuts.py` leaves the inherited encoder untouched and
exports `add_plane_cuts(formula, support, spectra)`. The full relation is
saved as `PLANE_PAIR_TABLE.json`; the replay receipt binds the code,
table, inherited encoder, and spectrum census by SHA256.

This is a finite mathematical argument with a complete replay. It is not
a proof-assistant formalization, and local exactness alone does not prove
the dimension-five Kakeya bound. Solver performance must be measured on
matched support cases before these clauses are enabled generally.
