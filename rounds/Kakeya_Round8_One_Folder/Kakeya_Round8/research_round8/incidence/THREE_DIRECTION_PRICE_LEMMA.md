# A three-direction price inequality for missing heavy differences

## Statement

Let the pair-active fibres of a Kakeya configuration over either
$\mathbb Z/4\mathbb Z$ or $\mathbb F_2[\epsilon]/(\epsilon^2)$ lie above
residues in $\mathbb F_2^5$. A heavy fibre has weight at least four; the
other pair-active fibres have weight two or three. Let $H$ be the set of
heavy residues, and let $M$ be the nonzero directions absent from $H+H$.

Assume $|H|\ge9$ and $|M|\ge3$. Write $n_2,n_3$ for the numbers of
weight-two and weight-three fibres and put

$$
B=n_2+2n_3.
$$

For $0\le k\le3$, define $E_k(w)$ to be the maximum number of pairs of a
$w$-point subset of $\mathbb F_2^5$ in $k$ prescribed independent
directions. In particular, $E_0(w)=0$.

For every real $\lambda\ge\tfrac12$, a necessary condition is

$$
\boxed{
48\ \le\ \lambda B+
\sum_{a\in H}\max_{0\le k\le3}\bigl(E_k(w_a)-\lambda k\bigr).
}
\tag{1}
$$

For the exact certificates in this checkpoint, it is enough to try the
nine integers $\lambda=1,\ldots,9$. A value strictly below 48 is a
refutation. Trying these nine values makes no claim of optimizing over
every possible real price or every geometric relaxation.

If $|H|=9$, the premise $|M|\ge3$ follows from the analytic bound
$|D(H)|\le28$. That bound is proved in the pinned Round7 note
research_round7/dense_encoder/NINE_POINT_DIFFERENCE_ANALYTIC_PROOF.md.
The present inequality has no total-weight premise and does not use a
full fibre-spectrum census, a quotient-sumset table, or SAT.

## Why three missing directions are independent

No three distinct directions $u,v,u+v$ can all belong to $M$. If they
did, no two elements of $H$ could lie in the same coset of the
two-dimensional space $\langle u,v\rangle$. There are only eight such
cosets, contradicting $|H|\ge9$.

Consequently any three distinct directions chosen from $M$ are
linearly independent. Fix such a triple $d_1,d_2,d_3$.

A weight-two fibre has only one pair direction. The three pair
directions of a weight-three fibre form a binary plane, so at most two
can belong to the chosen missing triple. Across this triple, the total
number of active light-fibre incidences is therefore at most $B$.

## The small cube tables

Let $g_k(z)$ be the maximum number of induced edges in a $z$-vertex
subset of the ordinary $k$-dimensional binary cube, with edges in its
$k$ coordinate directions. The complete small tables are

$$
\begin{aligned}
g_1&=(0,0,1),\\
g_2&=(0,0,1,2,4),\\
g_3&=(0,0,1,2,4,5,7,9,12).
\end{aligned}
$$

Each entry is a finite graph statement. Enumerating all subsets checks
these tables using $4+16+256=276$ masks in total. Edges are counted once,
and the index of each entry is the number of selected vertices.

For any $k$ independent directions in $\mathbb F_2^5$, their span has
$2^{5-k}$ cosets. The graph of pairs in those directions is a disjoint
union of that many $k$-cubes. Therefore

$$
E_k(w)=
\max_{\substack{0\le z_i\le2^k\\
                \sum_i z_i=w}}
\sum_{i=1}^{2^{5-k}}g_k(z_i).
\tag{2}
$$

The right side is evaluated exactly with integer maximum-plus
convolution. One may initialize $F_0(0)=0$, mark other entries
unreachable, and use

$$
F_{j+1}(w)=
\max_{0\le z\le\min(2^k,w)}
\bigl(F_j(w-z)+g_k(z)\bigr).
$$

Then $E_k(w)=F_{2^{5-k}}(w)$. This is complete because every fibre splits
among these cosets; conversely, maximizing subsets can be chosen
independently in the distinct cosets. The computation never enumerates
all subsets of the 32-point ambient space.

## Charging the actual edges

There are no heavy-heavy support edges in any of the selected missing
directions. A heavy-light edge has capacity at most the heavy endpoint's
pair count in that direction, because the light endpoint has at most
one pair. A light-light edge has capacity at most one.

For each heavy residue $a$, let $I_a$ be the subset of the three
directions in which an active heavy-light edge uses $a$, and put
$k_a=|I_a|$. Edges in one direction form a matching, so a heavy residue
is used at most once in that direction. Equation (2) gives

$$
\sum_{i\in I_a}p_{A_a}(d_i)\le E_{k_a}(w_a).
$$

Let $u$ be the number of active light-light edges over the three
directions. The heavy-light edges use $\sum_a k_a$ light incidences,
and those light-light edges use $2u$. Thus

$$
\sum_a k_a+2u\le B.
\tag{3}
$$

Covering all sixteen lifts in each of three directions requires total
edge capacity at least 48. It follows that

$$
48\le\sum_a E_{k_a}(w_a)+u.
$$

For $\lambda\ge\tfrac12$, write the right side as

$$
\sum_a\bigl(E_{k_a}(w_a)-\lambda k_a\bigr)
+\lambda\bigl(\sum_a k_a+2u\bigr)
+(1-2\lambda)u.
$$

The last term is nonpositive. Apply (3) and maximize each heavy
endpoint's excess independently to obtain (1).

The ring carry translates the relevant quotient sumsets. It changes
neither the heavy-light cardinality bound nor the light-light bound.
The argument is therefore necessary in both rings.

## A certificate that the matching threshold alone misses

Consider the support-17 profile

$$
(15,10,8,8,8,8,7,6,6,3,2,2,2,2,2,2,2).
$$

Its total weight is 93. It has nine heavy fibres, seven weight-two
fibres and one weight-three fibre, so $B=9$.

The three largest heavy pair ceilings are $7,5,4$. Their sum reaches
16, so the preceding matching threshold only requires three active
lights in each missing direction. Its total requirement of nine
incidences is exactly the available budget and does not exclude this
profile.

Use $\lambda=4$ in (1). The weight-15 fibre has
$(E_1,E_2,E_3)=(7,14,21)$, giving maximum excess 9. The weight-10 fibre
has $(5,9,13)$, giving maximum excess 1. Each of the remaining seven
heavy fibres has maximum excess zero. Consequently

$$
48\le4\cdot9+9+1=46,
$$

which is impossible. This example shows why a joint bound across
three directions adds information beyond a per-direction partner
threshold.

## Certificate and trust scope

The final profile replayer reconstructs the 276 small cube masks, the
integer tables (2), and every displayed price certificate. It scans
every original Round7 profile and compares direct and staged
regeneration of the surviving text file. Earlier profile stages and
their semantic inputs remain immutable.

The final cumulative list combines the already checked matching
exclusions with the additional exclusions from (1). Neither family
removes a marked SAT role merely by changing a whole-profile count.
The finite graph calculation and Python certificate replay are
explicit computational components, not proof-assistant
formalizations. The analytic implication (1) is proved above.
