# Carry, direction labels, and exact transfer

## Setting

Let $V=\mathbb F_2^n$ and identify the underlying sets of $A_{2,2}^n$ and
$(A_{2,2}^{\flat})^n$ with $V\times V$ by the Teichmüller digits
$a+\pi u$. A primitive direction is $(v,[w])$, with $v\ne0$ and
$[w]\in V/\langle v\rangle$. Put $c(a,v)=a\odot v$, where the product is
coordinatewise. The mixed-characteristic line through $(a,u)$ has points

$$
(a,u),\quad(a,u+v),\quad
(a+v,u+w+c(a,v)),\quad(a+v,u+w+c(a,v)+v).
$$

For the equal-characteristic ring the same formula holds with $c=0$.
All sums in this note are in $V$.

## G1. Unlabelled incidence agrees in every dimension

**Theorem.** Under the digit identification, the collections of four-point
lines in the two rings are equal for every $n\ge1$. Their assignments to
primitive direction classes need not agree.

**Proof.** Fix an unordered base pair $\{a,a+v\}$. A line consists of one
$v$-coset $u+\langle v\rangle$ in the first fibre and one $v$-coset
$u'+\langle v\rangle$ in the second. Every pair of cosets occurs in both
rings: its lifted direction is $[u+u']$ in the flat ring and
$[u+u'+c(a,v)]$ in the mixed ring. Thus the four-point sets are identical.
The base pair is recovered from the points, so taking their union over all
base pairs proves the claim. $\square$

This completes the all-dimensional argument implicit in the original
monograph's explanation of its finite incidence checks. It does not identify
the direction partitions, which are part of the Kakeya condition.

## G2. No universal fibre-translation gauge

**Theorem.** For $n\ge2$ there are no functions $f:V\to V$ and
$\tau:V\setminus\{0\}\to V$ satisfying

$$
f(a)+f(a+v)+a\odot v+\tau(v)\in\langle v\rangle
\qquad(a\in V,\ v\ne0).
$$

Consequently, fibre translations $(a,u)\mapsto(a,u+f(a))$, even combined with
an arbitrary translation of the lifted direction labels over each $v$, cannot
remove the mixed-characteristic carry globally.

**Proof.** Set $v=e_i$. For $j\ne i$, the displayed relation gives
$f_j(a)+f_j(a+e_i)=\tau_j(e_i)$, independently of $a$. Subtracting these
linear terms shows that $f_j$ depends only on $a_j$; a function of one binary
variable is affine. Hence $f(a)=Ma+b$ is affine, and
$f(a)+f(a+v)=Mv$ is independent of $a$. Now take $v=e_i+e_j$ with $i\ne j$.
Subtract the claimed equations at $a=0$ and $a=e_i$. The result would put
$e_i$ in $\langle e_i+e_j\rangle$, a contradiction. $\square$

The obstruction already has a six-equation certificate on a two-dimensional
coordinate plane. `carry_transfer.py` records those equations and verifies
that their binary sum is $0=1$. The theorem concerns this specified class of
gauges; it is not a classification of arbitrary incidence automorphisms.

## G3. A finite linear criterion for a prescribed family

Let $A_a\subseteq V$ be the digit fibres of a point set. For the base edge
$e=\{a,a+v\}$ define the full inverse image of its contributed direction set

$$
S_e=\{u+u':u,u+v\in A_a,\quad u',u'+v\in A_{a+v}\}\subseteq V.
$$

The set $S_e$ is invariant under $v$. Define its period subspace

$$
H_e=\{h\in V:S_e+h=S_e\}.
$$

For $S_e=\varnothing$, take $H_e=V$, as the definition itself does.
The period set is a vector subspace and contains $\langle v\rangle$.

**Theorem.** Fibre translations $f(a)$ make the mixed-characteristic
contribution of every edge equal to the flat contribution translated by a
common $\tau(v)$ over that residue direction if and only if

$$
f(a)+f(a+v)+a\odot v+\tau(v)\in H_e
\quad\text{for every }e=\{a,a+v\}.
$$

These are linear equations over $\mathbb F_2$. Whenever they are solvable,
they transfer a Kakeya set from either ring to the other while preserving
every fibre cardinality, and hence the total size.

**Proof.** Translating the two fibres shifts $S_e$ by $f(a)+f(a+v)$.
The mixed ring contributes the additional $a\odot v$. Two translates of
$S_e$ are equal precisely when their shift difference belongs to $H_e$.
This proves the equivalence. Pairing the required shift with a basis of
$H_e^\perp$ gives binary linear equations. For a fixed $v$, their common
translation $\tau(v)$ can be pulled outside the union over edges. Covering
$V/\langle v\rangle$ is invariant under that translation. The same equations
work in reverse because the characteristic is two. $\square$

This criterion is exact for equality of every individual edge contribution.
It is a sufficient transfer criterion for Kakeya sets. An inconsistent system
does not exclude a transfer that changes the fibres' shapes or uses only
equality of their total unions.

**Concrete transfer.** The flat Kakeya set with packed mask
`0x505656d650c6d2d2` has 29 points in dimension three. In these coordinates it
is not mixed Kakeya. Translating only its fibre over $7$ by the digit vector
$2$ produces a mixed Kakeya set with the same profile and 29 points. The
receipt supplies both full point sets, the binary solution, all 28 edge
equalities, and direct checks of all primitive direction classes.

## G4. The complete discrepancy in the plane

Identify $V=\mathbb F_2^2$ with binary vectors and write $e_1+e_2=(1,1)$.

**Theorem.** A subset of the common digit plane is Kakeya over the flat ring
only if it is Kakeya over the mixed ring. The mixed-only sets are exactly

$$
A_a=V\setminus\{m_a\}\quad(a\in V),
\qquad \sum_{a\in V}m_a=e_1+e_2.
$$

There are $4^3=64$ of them. Every one has 12 points and fibre profile
$(3,3,3,3)$.

**Proof.** Each residue direction has two base edges and two lifted direction
classes. A fibre with four points supplies both $v$-cosets for every $v$; a
three-point fibre supplies one for every $v$; a two-point fibre supplies one
for exactly one $v$; smaller fibres supply none.

If a full fibre occurs, the edge containing it contributes either no class
or both classes, independently of the carry. If it contributes none, the
other edge must contribute both, which also requires a full fibre. Thus the
Kakeya condition is identical in the two rings in this case. If no full
fibre occurs and a fibre has at most two points, choose a direction in which
it supplies no pair. Its edge contributes nothing and the other edge at
most one class, so the set is not Kakeya in either ring. The only remaining
case is four three-point fibres.

Put $z=\sum_a m_a$. For any nonzero $v$, the single coset contained in
$V\setminus\{m_a\}$ is the coset other than $[m_a]$ in the two-element
quotient. The two complements cancel when two fibres are paired. In the
flat ring the two edge contributions are therefore different exactly when
$z\notin\langle v\rangle$. No vector can avoid all three one-dimensional
subspaces of $V$, so no such set is flat Kakeya.

In the mixed ring the sum of the two edge carries is $0$ for $v=e_1$ and
$v=e_2$, and $e_1$ modulo $\langle e_1+e_2\rangle$ for $v=e_1+e_2$.
The first two conditions force $z=e_1+e_2$, and that value satisfies the
third condition. Three missing points are arbitrary and the fourth is
forced, giving $4^3=64$. $\square$

The complete independent enumeration of all $2^{16}=65,536$ subsets gives:

| Cardinality | Flat Kakeya sets | Mixed Kakeya sets |
|---:|---:|---:|
| 10 | 32 | 32 |
| 11 | 240 | 240 |
| 12 | 628 | 692 |
| 13 | 560 | 560 |
| 14 | 120 | 120 |
| 15 | 16 | 16 |
| 16 | 1 | 1 |
| Total | 1,597 | 1,661 |

The original campaign had already observed the 64-set difference. The
argument above identifies its entire mechanism and establishes the
classification without a solver. In dimension three inclusion in the same
digit coordinates fails in both directions; the accompanying bounded scout
retains explicit examples, and the transfer criterion can repair some of
them by a single fibre translation.

## Reproduction

Run `python carry_transfer.py` for the exact linear certificates, complete
plane census, fixed transfer example, and independent checks. Run
`python greedy_scout.py` to reproduce the bounded deterministic search for
the three-dimensional examples. The search is exploratory; each retained
example is verified separately. Neither calculation asserts an all-dimensional
equality of Kakeya minima.
