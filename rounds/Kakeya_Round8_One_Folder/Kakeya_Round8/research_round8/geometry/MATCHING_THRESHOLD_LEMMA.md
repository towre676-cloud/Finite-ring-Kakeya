# A matching threshold from the actual heavy-fibre weights

## Statement

Consider a dimension-five Kakeya configuration over either
$\mathbb Z/4\mathbb Z$ or $\mathbb F_2[\epsilon]/(\epsilon^2)$.
Its pair-active residue support lies in $\mathbb F_2^5$. A fibre of
weight at least four is **heavy**; the remaining active fibres have
weight two or three and are **light**.

Suppose there are exactly nine heavy fibres and $L\le8$ light fibres.
List the heavy weights in decreasing order and put

$$
q_1\ge q_2\ge\cdots\ge q_9,
\qquad q_i=\left\lfloor\frac{w_i}{2}\right\rfloor\ge2,
\qquad Q_k=\sum_{i=1}^k q_i,\quad Q_0=0.
$$

Define the **matching threshold**

$$
\rho=\min\{k:Q_k\ge16\}.
\tag{1}
$$

It exists and satisfies $\rho\le8$, since $Q_8\ge16$.
Let $H$ be the nine heavy residues, let

$$
M=(\mathbb F_2^5\setminus\{0\})\setminus D(H),
$$

and let $L_2,L_3$ count the light fibres of weights two and three.
Then every actual configuration satisfies

$$
\boxed{\rho|M|\le L_2+2L_3.}
\tag{2}
$$

Every nine-point subset of $\mathbb F_2^5$ has at most 28 nonzero
differences. Consequently

$$
\boxed{3\rho\le L_2+2L_3.}
\tag{3}
$$

A weight profile violating (3) is impossible in **every placement and
for every choice of fibre shapes, in both rings**. The statement itself
does not require a total-weight bound, a fibre-spectrum census, a
quotient-sumset table, a support catalogue, or SAT.

The nine-point difference bound is the analytic lemma in
`research_round7/dense_encoder/NINE_POINT_DIFFERENCE_ANALYTIC_PROOF.md`.
The plane-free missing-direction argument below is also the core of
`research_round8/incidence/MISSING_DIRECTION_INCIDENCE.md`.

## The one-direction matching bound

Fix $d\in M$. The residue edges in direction $d$ are the disjoint pairs
$\{a,a+d\}$. No edge has two heavy endpoints, because $d\notin D(H)$.
Only edges having a positive pair count at both endpoints can supply
any of the sixteen lifted directions.

Let $t$ be the number of such active heavy-light edges and $u$ the
number of active light-light edges. They use exactly

$$
k=t+2u
$$

light vertices. In particular, $k\le L\le8<9$.

A light endpoint has pair count one. An edge with heavy partner $i$
therefore has capacity at most its heavy pair count, which is at most
$q_i$. A light-light edge has capacity at most one. The $t$ heavy
partners are distinct, because the residue edges form a matching.
Writing $I$ for their index set gives

$$
C_d\le\sum_{i\in I}q_i+u,
\qquad |I|=t.
\tag{4}
$$

Choose any $2u$ additional heavy indices outside $I$. There are enough:
$t+2u=k\le9$. Each additional $q_i$ is at least two, so their sum is
at least $4u$, and in particular at least $u$. Thus a set $J$ of $k$
distinct heavy indices satisfies

$$
C_d\le\sum_{i\in J}q_i\le Q_k.
\tag{5}
$$

This last comparison uses the decreasing ordering of the $q_i$.
Since all sixteen lifts must be covered, $16\le C_d\le Q_k$.
Definition (1) therefore forces **at least $\rho$ active light
vertices in each missing direction**.

The proof still works if one counts every light fibre with a positive
pair count in direction $d$, including one whose residue neighbour is
absent or inactive: this only increases the counted number of lights.
No heavy endpoint is used twice in (4). Ring-specific carry terms
translate quotient sumsets and do not change their cardinalities.

## Summing over missing directions

The set $M$ cannot contain all three nonzero vectors of a binary
two-space $K$. If it did, no two heavy residues could lie in the same
coset of $K$. There are only eight such cosets, contradicting $|H|=9$.

A weight-two fibre is active in one direction. A weight-three fibre
is active in the three nonzero directions of a binary two-space, so
at most two of its active directions belong to $M$. Consequently the
total number of light incidences across $M$ is at most $L_2+2L_3$.
The lower bound $\rho$ for each direction proves (2).
Finally $|D(H)|\le28$ gives $|M|\ge3$ and hence (3).

If $\rho>L$, even one missing direction is already impossible. No
separate exceptional case is needed: then
$3\rho>2L\ge L_2+2L_3$, so (3) rejects the profile as well.

## Relation to the earlier maximum-only bound

With $P=\max_i q_i$ and $r=\lceil16/P\rceil$, one has $Q_k\le kP$,
so $\rho\ge r$. Thus the matching bound retains every earlier
exclusion using $3r>L_2+2L_3$ and can exclude additional profiles.
For example, if the heavy ceilings are

$$
(9,6,2,2,2,2,2,2,2),
$$

the maximum-only threshold is $r=2$, while $Q_2=15<16\le Q_3=17$
gives $\rho=3$. Two light fibres cannot both use the same heavy
ceiling nine: a fixed-direction residue matching forbids that reuse.

## Finite controls and scope

`verify_matching_threshold.py` supplies corroborating finite checks;
the proof above is independent of their outcome. The controls cover
every decreasing nine-entry ceiling vector with values in $2,\ldots,9$
(the full range needed for inherited maxima at most eighteen), every
subset of actual heavy partners, and every feasible number of
light-light edges using at most eight active light vertices. They
also enumerate literal small matchings, check the threshold bracket,
and exhibit failures when a heavy partner is improperly reused or the
nine-heavy plane-free premise is dropped.

This note introduces no SAT formula or SAT exclusion. A separate
profile certificate must bind exact inherited rows and verify their
prefix sums before changing any ledger count.
