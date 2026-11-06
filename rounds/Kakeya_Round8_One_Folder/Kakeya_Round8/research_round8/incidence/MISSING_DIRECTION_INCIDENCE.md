# A light-incidence bound for missing heavy directions

Let $S\subseteq\mathbb F_2^5$ be the pair-active residue support of a
Kakeya set over either of the two rings. Every fibre has weight at least
two and at most $m$. Define

$$
H=\{a\in S:|A_a|\ge4\},\quad h=|H|,\quad
M=(\mathbb F_2^5\setminus\{0\})\setminus D(H),\quad
P=\lfloor m/2\rfloor,\quad r=\left\lceil\frac{16}{P}\right\rceil.
$$

Let $L_2,L_3$ count fibres of weights two and three. These are precisely
the light fibres, so $L_2+L_3=|S|-h$.

**Incidence theorem.** If $h\ge9$, then

$$
\boxed{r|M|\le L_2+2L_3.}
\tag{1}
$$

This is a necessary condition for actual Kakeya sets in both rings. It
uses no total-weight bound, fibre-spectrum census, orbit catalogue, or
SAT result.

## Proof of the incidence theorem

The set $M$ cannot contain all three nonzero elements of a binary
two-space $K$. Otherwise no difference of two points of $H$ lies in
$K\setminus\{0\}$. Each coset of $K$ would contain at most one heavy
residue. There are eight cosets, contradicting $h\ge9$.

For $d\in M$, every residue edge in direction $d$ has a light endpoint.
The edges form a matching. A light fibre has $p_a(d)\le1$, while every
other endpoint has $p_b(d)\le P$. Charging each edge to a light endpoint
gives

$$
16\le P\sum_{a\ \mathrm{light}}p_a(d).
$$

The sum on the right is an integer, so at least $r$ light pair-direction
incidences are required for each $d\in M$.

A weight-two fibre has only one positive pair direction. A weight-three
fibre has the three nonzero directions of a binary two-space. Since $M$
contains no complete such triple, that fibre contributes at most two
incidences in all of $M$. Summing over $M$ proves (1).

The same lower bound of $r$ holds if one counts only light vertices on
actually contributing edges, rather than also counting possible fibre
pairs whose residue partner is absent. This sharper interpretation is
used in the conditional propagation below.

## Two next-frontier consequences

The following two scopes are covered:

| Support size $s$ | Maximum fibre weight | Largest $P$ | Smallest $r$ |
|---:|---:|---:|---:|
| 13 | at most 13 | 6 | 3 |
| 14 | at most 11 | 5 | 4 |

In either scope,

$$
\boxed{h\ge10,\qquad |D(H)|\ge29,\qquad h\ge11\implies D(H)=\mathbb F_2^5\setminus\{0\}.}
\tag{2}
$$

Here is a direct proof. For any $h$, charging all directions outside
$D(H)$ to light fibres gives

$$
16(31-|D(H)|)\le3P(s-h).
\tag{3}
$$

For $h\le7$, substitute $|D(H)|\le\binom h2$. In the support-thirteen
scope, the gap between the required and available sides is at least
$262+26h-8h^2$, positive on $0\le h\le7$; its endpoint values are
$262$ and $52$. In the support-fourteen scope the corresponding gap is
$286+23h-8h^2$, with endpoint values $286$ and $55$.

For $h=8$, the elementary bound $|D(H)|\le25$ makes the required
capacity at least $96$, whereas either scope supplies at most $90$.
For $h=9$, the elementary bound $|D(H)|\le28$ gives $|M|\ge3$.
Equation (1) then requires $9\le8$ in the support-thirteen scope or
$12\le10$ in the support-fourteen scope. Thus $h\ge10$.

The eight- and nine-point difference bounds have symbolic proofs at
`research_round7/dense_encoder/NINE_POINT_DIFFERENCE_ANALYTIC_PROOF.md`.
No enumeration is a premise for those bounds.

With $h\ge10$, (1) implies $|M|\le2$ in both scopes. If $h\ge11$,
the number of remaining light vertices is at most two or three
respectively. Their maximum capacity in a missing direction is at most
$2\cdot6=12$ or $3\cdot5=15$, both below sixteen. Therefore $M$ is
empty. More generally, the same argument forces $M=\varnothing$
whenever $h\ge s-r+1$.

## Exact integer form for a Boolean encoding

Let $b_a$ denote weight at least four and let $n_a$ denote weight
different from three. Under the weight-domain assumption $w_a\ge2$,

$$
\sum_a n_a=h+L_2=s-L_3.
$$

Consequently (1) is exactly

$$
\boxed{r\sum_{d\ne0}[d\in M]+\sum_a b_a+\sum_a n_a\le2s.}
\tag{4}
$$

The general encoding gates (4) by the exact condition $h\ge9$.
Every heavy flag and weight-three flag is equivalent to the appropriate
OR of existing spectrum selectors. Each heavy-heavy edge flag is an
exact AND of its endpoint heavy flags. The covered-direction flag is
an exact OR over those edge flags; the missing-direction flag is its
negation. Thus no auxiliary can declare a heavy difference present
without a real heavy-heavy residue edge.

An exact bidirectional unary counter implements (4), with each missing
flag repeated $r$ times. Repeated literals implement integer coefficients
by counting occurrences; they are not treated as independent Boolean
variables. The scope-specific wrapper checks the two domains in the
table before appending the consequences (2).

## Optional propagation when exactly ten fibres are heavy

In the cases where $s-10=r$, put $L=s-10$. Assume $h=10$ and
$d\in M$. Every one of the $L$ light vertices must lie on an active
heavy-light edge in direction $d$. Indeed, losing a light endpoint
leaves capacity at most $(L-1)P<16$. A light-light edge uses two light
vertices and leaves capacity at most $1+(L-2)P<16$.

Therefore a light residue $a$ must satisfy

$$
a+d\in H,\qquad p_a(d)=1,\qquad
p_{a+d}(d)\ge16-P(L-1).
\tag{5}
$$

The last bound follows because all other $L-1$ edges contribute at most
$P$ each. For support thirteen with maximum twelve or thirteen, this
requires the heavy neighbour to have at least four pairs. For support
fourteen with maximum ten or eleven it requires at least one pair; if
the maximum is eight or nine it requires four.

If additionally $|M|=2$, (1) becomes $2L\le L+L_3$, so every light
fibre has weight three. The optional clauses for (5) and this weight-three
consequence are explicitly gated by exactly ten heavy fibres and the
relevant missing-direction flags. When the residue neighbour is absent,
the corresponding gated clause forbids that light/missing combination.

These are propagation aids derived from the same capacity argument.
They are not new accepted SAT exclusions and do not alter any frozen
Round7 or earlier Round8 encoder.
