# Pair spectra descend through the maximal-pair subspace

**New necessary condition.** For $A\subseteq\mathbb F_2^n$ with $w=|A|\ge2$, set

$$
p_A(d)=\tfrac12|A\cap(A+d)|\quad(d\ne0),\qquad
K=\{0\}\cup\{d\ne0:p_A(d)=\lfloor w/2\rfloor\}.
$$

Then $K$ is a linear subspace and

$$
d,e\ne0,\quad d+e\in K\quad\Longrightarrow\quad p_A(d)=p_A(e).
\tag{F}
$$

Thus pair counts are constant on every coset outside $K$, and have the
common maximal value on $K\setminus\{0\}$. This holds for **both parities**.
The imported encoder imposes membership of the maximal directions in $K$,
but does not impose (F) for two directions outside $K$.

## 1. Why the maximal directions form a subspace

Set $D_A(k)=|A\setminus(A+k)|$, including $D_A(0)=0$. The triangle inequality
for symmetric difference gives

$$D_A(k+l)\le D_A(k)+D_A(l).$$

For nonzero $k$, the involution $x\mapsto x+k$ has two-element orbits, hence

$$D_A(k)=w-2p_A(k)\equiv w\pmod2.$$

If $w$ is even, maximal directions have deficit zero and are exactly the
nonzero periods of $A$. If $w$ is odd, they have deficit one. The sum of
two distinct such directions has deficit at most two, positive and odd,
hence one. In either case their union with zero is a subspace.

## 2. Even weights

Every $k\in K$ preserves $A$, so $A$ is a union of $K$-cosets and
$A+d=A+(d+k)$. This proves (F).

Let $h=|K|$ and let $q$ be the quotient map. Write $A=q^{-1}(C)$. For
$d\notin K$ one has the stronger formula

$$p_A(d)=h\,p_C(q(d)).$$

In particular, outside-$K$ pair counts are divisible by $h$.

## 3. Odd weights: a one-point perturbation theorem

For $K=\{0\}$, (F) is vacuous. Suppose $h=|K|>1$. In each $K$-coset $C$,
let $t_C=|A\cap C|$. Counting ordered pairs $(x,k)$ with $x\in A$, $k\in K$,
and $x+k\notin A$ gives

$$
\sum_C t_C(h-t_C)=\sum_{k\in K}D_A(k)=h-1.
$$

A partial coset contributes at least $h-1$, since

$$
t(h-t)-(h-1)=(t-1)(h-1-t)\ge0
\quad\text{for }1\le t\le h-1.
$$

There is exactly one partial coset, with occupancy one or $h-1$. All other
cosets are empty or full. Equivalently,

$$
\boxed{A=B\mathbin\triangle\{x\}\text{ for a }K\text{-periodic set }B.}
$$

For $d\notin K$, the number of $d$-pairs in $B$ depends only on $d+K$.
Adding or removing $x$ changes that number by one precisely when
$x+d\in B$, which also depends only on $d+K$. Therefore $p_A(d)$ is
constant on each outside coset, proving (F).

More explicitly, take $\sigma=+1$ when $A=B\cup\{x\}$ and $\sigma=-1$
when $A=B\setminus\{x\}$. If $B=q^{-1}(C)$, then

$$
w=h|C|+\sigma,\qquad
p_A(d)=h\,p_C(q(d))+\sigma\,1_C(q(x)+q(d))
\quad(d\notin K).
$$

For $h\ge4$, the residue of $w$ modulo $h$ determines the sign. Pair counts
outside $K$ consequently have residues $0,1$ if $w\equiv1\pmod h$, and
residues $0,-1$ if $w\equiv-1\pmod h$. For $h=2$ both descriptions are
available; no unjustified choice of sign is needed.

## 4. The containment in the affine direction space

If $H$ is the direction space of the affine hull of $A$, then

$$K\subseteq H.$$

Indeed, $w\ge2$ makes the maximal pair count positive, so every nonzero
member of $K$ is a difference of two points of $A$. The condition fails
as stated for a singleton, which is why the active-fibre hypothesis is
explicit.

## 5. Efficient CNF implementation

For every fibre $v$ and nonzero vector $r$, introduce a membership variable
$u_{v,r}$ equivalent to the OR of the selectors of maximal subspaces
containing $r$. Impose that $u_{v,r}$ implies membership of $r$ in the
chosen affine direction space. For each pair of incident nonzero
directions $d,e$, and every allowed pair-count value $t$, add

    -u[v,d XOR e]  -y[v,d,t]  y[v,e,t]

The one-hot value choices make these implications equality. One
orientation of each unordered pair suffices when all values are included.
There are only 31 new membership variables per fibre, avoiding a separate
copy of the equality clauses for every candidate subspace.

The optional encoder encode_maximal_cosets.py implements these clauses.
With strengthen=False it reproduces the joint-maximum baseline exactly.
The strengthened mode leaves every baseline variable and clause intact
and appends these new variables and clauses. Its finite replay constructs
actual-fibre assignments and verifies the additional clauses directly.

## Scope

This is an elementary proof valid in every binary dimension, not a Lean
formalization. The accompanying lemma replay checks all 65,519 subsets
of $\mathbb F_2^4$ of weight at least two, plus 1,877 reproducible
dimension-five examples. Those finite checks corroborate the proof.
