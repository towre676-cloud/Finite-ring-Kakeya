# Effective pair spaces of the eleven-point energy-211 type

## Exact local geometry

Let $A$ be an eleven-point set in an affine four-flat of $\mathbb F_2^5$,
with pair energy $Q(A)=211$. After translation its ambient flat is a
four-space $H$. The complement $B=H\setminus A$ has five points, and

$$
p_A(d)=3+p_B(d)\quad(0\ne d\in H),\qquad
Q(A)=205+6Z_4(B).
$$

Thus $B$ contains exactly one affine plane. Translate again so that this
plane is a two-space $K$. The fifth point is $u\notin K$, giving

$$
A=H\setminus(K\cup\{u\}),\qquad L=K+\langle u\rangle,
\qquad \dim K=2,\quad\dim L=3.
\tag{1}
$$

The full labelled pair counts are

$$
p_A(d)=
\begin{cases}
5,&d\in K\setminus\{0\},\\
4,&d\in L\setminus K,\\
3,&d\in H\setminus L,\\
0,&d\notin H.
\end{cases}
\tag{2}
$$

In particular $K$ is exactly the maximal-pair subspace already selected
by the baseline encoding.

For $d\ne0$, let $\pi_d$ be projection to $\mathbb F_2^5/\langle
d\rangle$, and let $P_A(d)$ be the set of quotient classes of complete
$d$-pairs. If $p_A(d)=4$, the eight paired points are $H\setminus L$.
Consequently $P_A(d)$ is an affine plane with direction space $\pi_d(K)$.
If $p_A(d)=3$, the two cosets $u+K$ and $u+d+K$ would supply four pairs,
but the missing point $u$ removes one. Consequently $P_A(d)$ is an affine
plane parallel to $\pi_d(K)$ with one point removed.

Therefore, in **every nonmaximal active direction** $d$, the actual
quotient pair-set spans an affine two-plane with direction space
$\pi_d(K)$. Equivalently its lifted pair-direction space is

$$
K+\langle d\rangle,
\tag{3}
$$

a three-space, although the whole fibre has affine rank four. This is
the additional geometric information used by the optional wrapper.

## Consequences for edge capacities

Let an actual residue edge have direction $d$. If both endpoint pair-sets
lie in affine copies of $J/\langle d\rangle$, where $J$ is a linear
space containing $d$, then their sumset has at most

$$
2^{\dim J-1}
\tag{4}
$$

elements. For an ordinary endpoint, containment of its full affine
direction space in $J$ is sufficient. For a type-(1) endpoint with
pair count three or four, the weaker condition $K\subseteq J$ is
already sufficient. The two containment conditions may be used in any
combination at the endpoints.

When $\dim J=4$ and both pair counts equal three, (4) improves from
eight to **seven**. Each three-set has a two-dimensional difference
space in the quotient three-space. Those two direction spaces meet
nontrivially. A shared nonzero difference creates two distinct collisions
among the nine ordered sums, leaving at most seven values.

All these are bounds on individual sumset cardinalities. Ring carries
only translate the edge sumset, so the bounds hold for both rings.

## Optional clause module

`q211_paired_spaces.py` appends these bounds to the explicitly exposed
Round8 edge-capacity variables. It reads the named spectrum, pair-count,
affine-span and maximal-pair-subspace selectors. No hidden variable
number or clause position is inferred.

For each endpoint and each tested $J$, it defines the two indicators

$$
h=[H_A\subseteq J],\qquad
k=[\text{the selected maximal-pair subspace is a two-space contained in }J].
$$

For each incident direction it also defines
$q=[A\text{ has type (1) and }p_A(d)\in\{3,4\}]$. Its effective
containment indicator is exactly

$$
e=h\lor(q\land k).
$$

If both endpoint indicators are true, the edge capacity is bounded by
(4); the three-by-three case receives the additional seven bound when
$\dim J=4$. The module also reproduces the ordinary common-full-span
bound when both $h$ indicators hold. In every actual configuration,
assigning the indicators their displayed meanings and the edge capacities
their actual sumset cardinalities satisfies every new clause.

The public API is

```python
append_q211_pair_space_cuts(formula, support, spectra, subspaces,
                           dimensions=(3, 4), enabled=True)
```

It requires the named maps `z`, `y`, `h_selectors`, `k_selectors`, and
`r8_edge_capacity`. Disabling the module changes no variable or clause.
The implementation remains separate from all frozen accepted Round8
formulas. **No new SAT exclusion or search-speed claim depends on it.**

## Further alignment information, not encoded here

If a type-(1) four-pair endpoint meets a tetrahedral four-pair endpoint,
capacity sixteen requires that their quotient direction spaces meet in
exactly the tetrahedron's one missing nonzero difference. Otherwise the
capacity is at most twelve (or eight when the planar direction space is
contained in the tetrahedron's three-space). For the energy-205
eleven-point type, that missing quotient difference is represented by
the two circuit directions whose sum is the edge direction. This could
support a later exact alignment model, but is not a premise of the
current optional wrapper.
