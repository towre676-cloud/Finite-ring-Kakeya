# Dense fibres inside four-dimensional flats

**Status: analytic structural lemmas, with a complete finite corroboration.
No new support exclusion, SAT result, or performance improvement is claimed.**

These restrictions address dense fibres whose maximal-pair subspace is
trivial. The earlier maximal-subspace coset lemma imposes no additional
pair-count equalities when that subspace is $\{0\}$.

## 1. Precise setup and complement identity

Let $F=t+H$ be an affine four-dimensional flat in a binary vector space,
where $H$ is its **linear direction space**. Let $A\subseteq F$, put
$w=|A|>8$, and let $B=F\setminus A$. For a nonzero direction $d$, write

$$p_A(d)=\tfrac12|A\cap(A+d)|,\qquad Q(A)=\sum_{d\ne0}p_A(d)^2.$$

For every nonzero $d\in H$,

$$\boxed{p_A(d)=w-8+p_B(d).}$$

Indeed, $F+d=F$ and inclusion-exclusion gives

$$
|A\cap(A+d)|
=16-|B\cup(B+d)|
=16-2|B|+|B\cap(B+d)|
=2w-16+2p_B(d).
$$

For $d\notin H$, the two containing affine flats are disjoint, so
$p_A(d)=0$. Thus the formula uses directions in $H$, not necessarily
points in the affine coset $F$. Translating $F$ to the origin changes
none of the pair counts.

Since $w>8$, the affine hull of $A$ is exactly $F$. Classifying its small
complement therefore gives labelled restrictions on its entire pair
spectrum.

## 2. Weight twelve

Here $|B|=4$ and $p_A(d)=4+p_B(d)$ inside $H$.

### A four-point affine plane

If $B$ is a coset of a two-space $J\subset H$, then its pair count is two
on $J\setminus\{0\}$ and zero elsewhere. Consequently

$$
p_A(d)=
\begin{cases}
6,&d\in J\setminus\{0\},\\
4,&d\in H\setminus J,\\
0,&d\notin H.
\end{cases}
$$

Thus $Q(A)=3\cdot6^2+12\cdot4^2=300$. Its maximal-pair subspace is $J$.

There are 35 two-spaces in a fixed four-space and four affine cosets per
two-space. Hence this type consists of **140 subsets**, with **35 distinct
labelled pair-count profiles**.

### Four affinely independent points

Otherwise $B$ has affine rank three. After translation write

$$B=\{0,e_1,e_2,e_3\}$$

with the $e_i$ independent, and let $J=\langle e_1,e_2,e_3\rangle$ and
$u=e_1+e_2+e_3$. The six pair differences are exactly

$$P=J\setminus\{0,u\}.$$

Each occurs once. Therefore $p_A=5$ on $P$, $p_A=4$ on the other nine
nonzero directions of $H$, and zero outside $H$. It follows that

$$Q(A)=6\cdot5^2+9\cdot4^2=294.$$

The six directions with pair count five span precisely the three-space
$J$. Among its nonzero directions, **exactly one has pair count four**.
The maximal possible pair count for weight twelve is six, which is absent,
so the maximal-pair subspace is trivial.

There are $\binom{16}{4}-140=1680$ subsets of this type. Their labelled
profiles are specified by a three-space $J$ and a missing nonzero $u$,
giving $15\cdot7=105$ profiles.

### Necessary clauses for the second type

Let $z$ select the weight-twelve, rank-four, energy-294 histogram, and let
$y_{d,k}$ mean that direction $d$ has pair count $k$.

For any four linearly independent incident directions $d_1,\ldots,d_4$,
the following clause is necessary:

$$\neg z\ \vee\ \bigvee_{i=1}^4\neg y_{d_i,5}.$$

For three independent incident directions $d_1,d_2,d_3$, and two distinct
other incident directions $e,f$ in their span, one also has

$$
\neg z\ \vee\
\neg y_{d_1,5}\vee\neg y_{d_2,5}\vee\neg y_{d_3,5}
\vee\neg y_{e,4}\vee\neg y_{f,4}.
$$

The second clause follows because three independent five-pair directions
span $J$, which contains only one four-pair direction. These are conditional
necessary constraints; they are not asserted for arbitrary weight-twelve
spectra or for fibres of affine rank five.

## 3. Weight eleven

Here $|B|=5$ and $p_A(d)=3+p_B(d)$ inside $H$. The affine rank of $B$ is
three or four.

### A five-set of affine rank three

Let $C=s+L$ be the affine hull of $B$, with $\dim L=3$. Its complement
$T=C\setminus B$ has three points. Their pair differences form the three
nonzero points of a two-space $J\subset L$.

Applying the complement identity in the eight-point flat $C$ gives
$p_B(d)=1+p_T(d)$ for nonzero $d\in L$. Hence

$$
p_A(d)=
\begin{cases}
5,&d\in J\setminus\{0\},\\
4,&d\in L\setminus J,\\
3,&d\in H\setminus L,\\
0,&d\notin H.
\end{cases}
$$

In particular,

$$Q(A)=3\cdot5^2+4\cdot4^2+8\cdot3^2=211.$$

The maximal-pair subspace is $J$. A fixed four-flat has thirty affine
three-flats, and each contains $\binom85=56$ such five-sets. Each five-set
has a unique affine hull. The count is therefore **1680 subsets**.
The labelled profiles are the **105 flags** $J\subset L\subset H$ with
dimensions two and three.

### A five-set of affine rank four

Now $B$ is an affine basis. After translation write

$$B=\{0,e_1,e_2,e_3,e_4\},\qquad u=e_1+e_2+e_3+e_4.$$

Its ten pair differences are the vectors of coordinate weight one or two
in this basis. The missing five nonzero vectors are

$$\mathcal C=\{u,u+e_1,u+e_2,u+e_3,u+e_4\}.$$

Thus $p_A=4$ on the ten pair differences and $p_A=3$ on $\mathcal C$.
This gives

$$Q(A)=10\cdot4^2+5\cdot3^2=205.$$

The five vectors in $\mathcal C$ sum to zero, and **every proper subset is
linearly independent**. To see uniqueness of the relation, put
$v_0=u$ and $v_i=u+e_i$. If $\sum_{i=0}^4 a_i v_i=0$ and
$\sigma=\sum_i a_i$, coefficient comparison gives $a_j=\sigma$ for
$j=1,\ldots,4$. Then $\sigma=a_0+4\sigma=a_0$, so all five coefficients
are equal. The only relations are the empty relation and the full one.

Consequently the three-pair directions form a five-element binary circuit.
Again the maximal-pair subspace is trivial, because pair count five is
absent.

There are $\binom{16}{5}-1680=2688$ subsets of this type. The number of
five-circuits is $|\mathrm{GL}_4(2)|/(5\cdot4!)=20160/120=168$, because
choosing which circuit vector to omit and ordering the other four gives
an ordered basis. These are the **168 distinct labelled profiles**.

### Necessary clauses for the second type

Let $z$ select the weight-eleven, rank-four, energy-205 histogram. For any
three or four distinct incident nonzero directions $d_1,\ldots,d_r$ whose
XOR is zero, one has the necessary clause

$$\neg z\ \vee\ \bigvee_{i=1}^{r}\neg y_{d_i,3},
\qquad r\in\{3,4\}.$$

Such a set cannot be a proper subset of the five-circuit. In characteristic
two, checking these three- and four-element relations, together with
distinctness, excludes every dependence among at most four selected
three-pair directions.

## 4. Complete finite corroboration

The standard-library verifier enumerates every four- and five-point
complement in a fixed sixteen-point flat: **6188 subsets in total**.
It computes pair counts directly, including zero counts outside the flat,
and checks the complement identity, ranks, subspace flags, missing
directions, circuit relations, and the proposed conditional restrictions.

| Fibre weight | Energy | Subsets | Labelled pair profiles | Maximal-pair subspace size |
|---:|---:|---:|---:|---:|
| 12 | 300 | 140 | 35 | 4 |
| 12 | 294 | 1680 | 105 | 1 |
| 11 | 211 | 1680 | 105 | 4 |
| 11 | 205 | 2688 | 168 | 1 |

Run:

    python3 research_round6/next_frontier/verify_dense_complements.py

The receipt is DENSE_COMPLEMENT_REPLAY.json. Affine invariance transfers the
proved identities to every affine four-flat in the ambient binary
five-space, and in higher binary dimensions as well.

These proposed rows have not been added to the main encoders or tested in
a solver. Their immediate contribution is a rigorous set of labelled
geometric constraints for two dense types with trivial maximal-pair
subspace. **The Round 6 certificate and frontier counts are unchanged.**
