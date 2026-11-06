# Spectral realization and forced concentration in binary Kakeya geometry

## Abstract

The fibre formulation of the Kakeya problem over the four-element local rings reduces the lower-bound question to simultaneous constraints on binary autocorrelations. This chapter gives an exact realization criterion for those autocorrelations, a complete finite description in dimensions at most four, and uniform restrictions on configurations with few large fibres. The realization criterion separates the square magnitudes of Walsh coefficients from their compatible signs. In dimension four this distinction has a particularly explicit form: there are 5,227 admissible square-spectral types, of which exactly 1,260 fail one four-frequency parity condition. The remaining 3,967 types are exactly the pair vectors of actual subsets of the sixteen-point binary space. The corresponding independently checked classification takes seconds and uses integer arithmetic only.

The concentration theorem applies in every dimension. If a Kakeya set has no full residue fibre and has $h$ fibres of size greater than two, then

\[
(h-1)^2\ge 2^n-1.
\]

Thus dimension five requires at least seven such fibres. A sharper inequality retains the largest fibre size and the difference set of their base points. With at most two fibres of size greater than two, the sharp law $3\cdot2^n-2$ holds in every dimension, and equality is exactly the full-fibre construction with an own-direction pair over every other base point.

The statements below concern the shared binary fibre geometry. They apply to both $A_{2,2}=\mathbb Z/4\mathbb Z$ and $A^\flat_{2,2}=\mathbb F_2[t]/(t^2)$. They do not assume that the two rings have the same direction-labelled incidence system.

## 1. Pair vectors and defect data

Put $V=\mathbb F_2^n$, $N=2^n$, and $H=N/2$. For a subset $A\subseteq V$ of size $s$, define

\[
p_A(v)=\frac12|A\cap(A+v)|\quad(v\ne0),
\qquad c_A(0)=s,\quad c_A(v)=2p_A(v),
\qquad d_A(v)=s-c_A(v).
\]

Thus $p_A(v)$ counts the unordered pairs in $A$ with difference $v$, $c_A$ is its autocorrelation, and $d_A(v)=|A\setminus(A+v)|$. These quantities satisfy

\[
\sum_{v\ne0}p_A(v)=\binom{s}{2},\qquad
0\le p_A(v)\le\lfloor s/2\rfloor,
\qquad
d_A(v+w)\le d_A(v)+d_A(w).
\]

The local defect relaxation, denoted $T$, keeps these conditions together with $0\le d_A(v)\le\min(s,N-s)$ and the integral parity of the defects. It does not require the existence of $A$.

For a ring Kakeya set, write $A_a\subseteq V$ for the fibre over $a\in V$, and put $p_a=p_{A_a}$. The shared counting inequality is

\[
\sum_{\{a,a+v\}}p_a(v)p_{a+v}(v)\ge H
\qquad(v\ne0).
\tag{1}
\]

Every theorem about families satisfying (1) therefore supplies a lower bound for both rings. The positional covering condition in the uploaded monographs is stronger than (1); no converse is used here.

## 2. Exact Fourier realization

For $\xi,x\in V$, let $\chi_\xi(x)=(-1)^{\xi\cdot x}$, and use the unnormalized Walsh transform

\[
\widehat f(\xi)=\sum_{x\in V}f(x)\chi_\xi(x).
\]

### Theorem 1. Square-spectrum constraints

For every actual pair vector, define

\[
W_\xi=s+2\sum_{v\ne0}\chi_\xi(v)p_A(v).
\]

Then

\[
W_\xi=\widehat{1_A}(\xi)^2,
\qquad W_0=s^2,
\qquad \sum_\xi W_\xi=Ns.
\tag{2}
\]

For every nonzero $\xi$, $W_\xi$ is the square of an integer $r_\xi$ satisfying

\[
0\le r_\xi\le\min(s,N-s),\qquad r_\xi\equiv s\pmod2.
\tag{3}
\]

**Proof.** The autocorrelation is $c_A(v)=\sum_x1_A(x)1_A(x+v)$. Substituting $y=x+v$ into its Walsh transform gives

\[
\widehat c_A(\xi)
=\sum_{x,y}1_A(x)1_A(y)\chi_\xi(x+y)
=\widehat{1_A}(\xi)^2.
\]

At the zero character the sum is $s$, and Walsh inversion at $v=0$ gives the last identity in (2). Every Walsh coefficient is a sum of $s$ signs, proving its parity and the bound by $s$. For a nonzero character, the sum over all of $V$ is zero, so the coefficient for the complement is its negative; this gives the additional bound by $N-s$. ∎

The square condition is stronger than nonnegativity or a positive-semidefinite autocorrelation matrix. It retains the arithmetic of a zero-one function on a finite binary space.

### Theorem 2. Integral sign completion

Let $s\in\{0,\ldots,N\}$ and let $p(v)$ be integer candidate pair data. Set $c(0)=s$, $c(v)=2p(v)$, and $W=\widehat c$. Assume $W_0=s^2$ and that every $W_\xi$ is a nonnegative integer square. Then $p$ is the pair vector of a subset of size $s$ if and only if there are signed square roots

\[
b_0=s,\qquad b_\xi\in\{+\sqrt{W_\xi},-\sqrt{W_\xi}\}\quad(\xi\ne0)
\]

such that

\[
\sum_\xi b_\xi\chi_\xi(x)\equiv0\pmod N
\qquad\text{for every }x\in V.
\tag{4}
\]

When (4) holds, the realizing subset is recovered by

\[
1_A(x)=\frac1N\sum_\xi b_\xi\chi_\xi(x).
\tag{5}
\]

**Proof.** Necessity follows by taking $b=\widehat{1_A}$. Conversely, (4) makes the inverse transform $f$ in (5) integer-valued. Orthogonality and $b_0=s$ give $\sum_xf(x)=s$. Parseval and $\sum_\xi W_\xi=Nc(0)=Ns$ give $\sum_xf(x)^2=s$. Hence

\[
\sum_xf(x)(f(x)-1)=0.
\]

For an integer $z$, $z(z-1)\ge0$, with equality exactly at $z=0,1$. Thus every value of $f$ is zero or one. Its autocorrelation has Walsh transform $b_\xi^2=W_\xi$, so Walsh inversion identifies it with $c$. ∎

The criterion is exact in every dimension. It supplies a finite sign-and-congruence completion problem rather than relying on a bounded numerical approximation. It does not assert that sign completion is inexpensive in arbitrary dimension.

### Proposition 3. Complement transport

If $B=V\setminus A$, then

\[
|B|=N-s,\qquad p_B(v)=H-s+p_A(v),\qquad
\widehat{1_B}(\xi)^2=\widehat{1_A}(\xi)^2\quad(\xi\ne0).
\tag{6}
\]

**Proof.** Expand $(1-1_A(x))(1-1_A(x+v))$ and sum over $x$. The nontrivial-character assertion follows because $\widehat1(\xi)=0$. ∎

## 3. A complete four-frequency phase theorem

### Theorem 4. Balanced four-frequency spectra

Let $n\ge4$, $s=N/2$, and let $\xi_1,\ldots,\xi_4$ be distinct nonzero characters. Specify the spectrum

\[
W_0=\frac{N^2}{4},\qquad
W_{\xi_i}=\frac{N^2}{16}\quad(1\le i\le4),\qquad
W_\xi=0\text{ otherwise}.
\tag{7}
\]

Its inverse autocorrelation yields an integral pair vector satisfying every local $T$ constraint and every square-spectrum constraint. It is realizable by a subset if and only if

\[
\boxed{\xi_1+\xi_2+\xi_3+\xi_4=0.}
\tag{8}
\]

**Proof.** Inversion gives

\[
c(v)=\frac N4+\frac N{16}\sum_{i=1}^4\chi_{\xi_i}(v),
\qquad
d(v)=\frac N8\bigl|\{i:\chi_{\xi_i}(v)=-1\}\bigr|.
\tag{9}
\]

Because $n\ge4$, the nonzero-direction values $c(v)$ are even integers between zero and $s$. The formula for $d$ is a multiple of the Hamming weight of the linear map $v\mapsto(\xi_i\cdot v)_{i=1}^4$; it is subadditive. The pair budget and all remaining local conditions follow from (7)–(9).

Any sign completion has inverse

\[
f(x)=\frac12+\frac14\sum_{i=1}^4\sigma_i\chi_{\xi_i}(x),\qquad\sigma_i\in\{\pm1\}.
\]

This is zero or one exactly when the sum of the four signs is $-2$ or $2$, which is equivalent to their product being $-1$. Consequently a completion exists precisely when

\[
\left(\prod_i\sigma_i\right)\chi_{\xi_1+\cdots+\xi_4}(x)=-1
\quad\text{for all }x.
\]

At $x=0$ the product of the σ-signs must be $-1$. The remaining condition is that the displayed character be trivial, which is (8). Conversely, if (8) holds, any choice with $\prod_i\sigma_i=-1$ gives a zero-one inverse and a realizing subset. ∎

This is an infinite family in which metric compatibility and square magnitudes leave one exact algebraic condition unresolved. The missing condition is visible in the support of the spectrum, before any generic sign search is attempted.

For $N=16$, there are $\binom{15}{4}=1365$ possible four-frequency supports. Exactly

\[
\frac{(N-1)(N-2)(N-4)}{24}=105
\]

have zero sum: choose three distinct nonzero frequencies with no zero sum and let the fourth be their sum, then divide by $4!$. The other $1365-105=1260$ supports are the complete exceptional family in the next theorem.

## 4. Exact local classification through dimension four

### Theorem 5. Dimension-three realization

For $V=\mathbb F_2^3$, a local $T$ vector is realizable if and only if it satisfies the square-spectrum constraints of Theorem 1. There are 46 distinct types $(s,p)$, including the empty and singleton types. At size four, $T$ admits 35 vectors, whereas exactly 14 are realizable; the square condition removes all 21 extra vectors.

**Structural proof.** By complement transport it suffices to treat $s\le4$. At sizes zero and one the vector vanishes. At size two it has a single entry equal to one. At size three the pair budget and triangle inequality force the three nonzero entries to be the three nonzero elements of a two-dimensional subspace, which is the pair vector of a triangle.

At size four let $P=\{0\}\cup\{v:p(v)=2\}$. The triangle inequality makes $P$ a subgroup. The pair budget restricts its order to one, two or four. Order four gives a plane, with $p=2$ on its three nonzero directions. Order one gives $p=1$ on six directions and zero on the seventh; these are the pair vectors of affinely independent four-point subsets. Each case has seven types. If $P$ has order two, the pair vector is constant on its nonzero cosets. The quotient autocorrelation has values $(4,0,2,2)$ in some order, and its lifted spectrum contains the value eight. This is not an integer square. There are seven choices of the nonzero period and three choices of the zero coset, giving 21 excluded types. ∎

One explicit rejected vector, with directions ordered $1,\ldots,7$, is

\[
s=4,\quad p=(0,0,2,1,1,1,1),\quad
W=(16,0,0,8,0,0,0,8).
\]

### Theorem 6. Dimension-four realization

For $V=\mathbb F_2^4$, the conditions in Theorem 1, the integral correlation bounds

\[
c(0)=s,\qquad c(v)\in2\mathbb Z,\qquad
\max(0,2s-N)\le c(v)\le s\quad(v\ne0),
\]

and the exclusion of the nonzero-sum four-frequency spectra of Theorem 4 are an exact characterization of realizable pair vectors. All the square-spectral candidates automatically satisfy the local $T$ conditions in this dimension.

The full comparison is:

| Fibre size $s$ | Realizable types | Square-spectral types | Four-frequency exclusions |
|---:|---:|---:|---:|
| 0 | 1 | 1 | 0 |
| 1 | 1 | 1 | 0 |
| 2 | 15 | 15 | 0 |
| 3 | 35 | 35 | 0 |
| 4 | 140 | 140 | 0 |
| 5 | 273 | 273 | 0 |
| 6 | 526 | 526 | 0 |
| 7 | 715 | 715 | 0 |
| 8 | 555 | 1,815 | 1,260 |

The rows for $9\le s\le16$ follow by (6). There are **3,967 actual types**, **5,227 square-spectral types**, and **1,260 excluded spectra** in total.

**Finite proof.** `verify_theory.py` independently enumerates all 65,536 subsets and records their size and pair vector. It then enumerates every possible square spectrum permitted by (2)–(3). For each $s\le8$, the nontrivial square entries lie in the finite set \(\{r^2:0\le r\le s,\ r\equiv s\pmod2\}\), and their sum is $s(16-s)$. The checker exhausts the possible histograms and every assignment of each histogram to the fifteen nonzero frequencies. Integer Walsh inversion rejects invalid correlation values. The remaining vectors are compared as exact tuples with the subset enumeration. Their difference is exactly the family in Theorem 4 with nonzero frequency sum. Complement transport completes the upper half of the size table. No optimization solver or floating-point calculation is involved. ∎

For example, the pair vector

\[
p=(1,1,2,1,2,2,3,0,3,3,2,3,2,2,1),\qquad s=8,
\]

has nonzero spectral support $\{0,11,13,14,15\}$, with values 64 at zero and 16 at the other four positions. Their sum in $V$ is $7\ne0$, so it has no realization. The sign-completion checker rejects all sixteen choices. As a positive control, support $\{1,2,4,7\}$ has zero sum and the same magnitudes do admit a binary inverse.

### Corollary 7. The 3,967/3,966 type count

For exact pair vectors, a type of weight $s\ge2$ cannot be dominated componentwise by another type of weight at most $s$, unless the two types are equal. The singleton type is the sole redundancy, dominated by the empty type. Consequently the dimension-four table has exactly 3,966 nondominated types.

**Proof.** If $p'\ge p$ componentwise and $s'\le s$, then

\[
\binom{s'}2=\sum p'\ge\sum p=\binom s2.
\]

For $s\ge2$, this forces $s'=s$. The equal sums then force equality in every coordinate. At sizes zero and one both pair vectors vanish. ∎

## 5. Subspace occupancy and quantitative periods

### Theorem 8. Exact subspace budgets

Let $U\le V$ have size $h$, and write $s=qh+r$, $0\le r<h$. Then every actual fibre satisfies

\[
\sum_{v\in U\setminus\{0\}}p_A(v)
\le q\binom h2+\binom r2,
\tag{10}
\]

or equivalently,

\[
\sum_{v\in U}d_A(v)\ge r(h-r).
\tag{11}
\]

If $m=N/h$ and $s=am+b$, $0\le b<m$, then also

\[
\sum_{v\in U\setminus\{0\}}p_A(v)
\ge(m-b)\binom a2+b\binom{a+1}2.
\tag{12}
\]

Both bounds are sharp as constraints on the coset occupancies.

**Proof.** If $s_C=|A\cap C|$ for the cosets $C\in V/U$, then

\[
\sum_{v\in U\setminus\{0\}}p_A(v)=\sum_C\binom{s_C}2,
\qquad
\sum_{v\in U}d_A(v)=\sum_Cs_C(h-s_C).
\]

For fixed sum $s$ and $0\le s_C\le h$, convexity maximizes the first sum by filling $q$ cosets and putting the remainder $r$ in one additional coset. It minimizes the first sum by making the $m$ occupancies differ by at most one. These are the displayed formulas, and each occupancy prescription can be realized by a subset. ∎

### Corollary 9. Quantitative divisibility from approximate periods

Let $v_1,\ldots,v_j$ be a basis of $U$, $h=2^j$, and $r=s\bmod h$. Then

\[
\boxed{\sum_{i=1}^j d_A(v_i)\ge\frac{2r(h-r)}h.}
\tag{13}
\]

In particular, if every $v_i$ is a period of $A$, then $h\mid s$.

**Proof.** Subadditivity gives $d_A(\sum_{i\in I}v_i)\le\sum_{i\in I}d_A(v_i)$. Summing over all $2^j$ subsets $I$ yields $\sum_{v\in U}d_A(v)\le(h/2)\sum_i d_A(v_i)$. Combine this with (11). ∎

The checker verifies (10)–(12) on all 3,967 dimension-four types and all 67 subspaces, giving 265,789 exact type/subspace comparisons.

## 6. The cost of external directions

Call a fibre **heavy** if its size is greater than two, and call a fibre **light** if its size is exactly two. Empty fibres and singletons make no contribution to (1). Let $B\subseteq V$ be the heavy base points, let $h=|B|$, and let $L$ be the number of light fibres. Define

\[
D=(B+B)\setminus\{0\},\qquad d=|D|,\qquad
E=V\setminus(D\cup\{0\}),\qquad e=|E|=N-1-d.
\]

For $v\in E$, its matching has no heavy-heavy edge. A light fibre has exactly one nonzero pair count, equal to one, so it can contribute to only one residue direction.

### Theorem 10. Directional allocation inequality

For $v\in E$, order the heavy capacities as

\[
P_1(v)\ge\cdots\ge P_h(v),\qquad
\{P_i(v)\}_{i=1}^h=\{p_a(v):a\in B\}.
\]

Put

\[
\lambda_v=
\min_{0\le j\le h}
\left[j+2\max\left(0,H-\sum_{i=1}^jP_i(v)\right)\right].
\tag{14}
\]

Every family of actual fibre types satisfying (1) obeys

\[
\boxed{\sum_{v\in E}\lambda_v\le L.}
\tag{15}
\]

**Proof.** In direction $v\in E$, suppose $j$ heavy-light matching edges contribute. They use $j$ distinct light fibres and contribute at most the sum of the $j$ largest heavy capacities. If that sum is less than $H$, at least $H-\sum_{i\le j}P_i(v)$ light-light edges are needed; each contributes at most one and uses two more light fibres. Hence the number of light fibres assigned to direction $v$ is at least (14). Light fibres assigned to distinct directions are disjoint, because their internal pair has a unique difference. Summing gives (15). The minimization may permit combinations of capacities not realizable by the positions of the fibres; this only weakens the lower bound and therefore preserves its validity. ∎

### Corollary 11. Maximum-size and support bounds

Suppose there is at least one heavy fibre, let $M=\max_a|A_a|$, $m=\lfloor M/2\rfloor$, and $q=\lceil H/m\rceil$. Then

\[
\boxed{q(N-1-d)\le L\le N-h.}
\tag{16}
\]

In particular, since $d\le\binom h2$,

\[
q\max\left(0,N-1-\binom h2\right)\le N-h.
\tag{17}
\]

**Proof.** A heavy-light edge contributes at most $m$ per light fibre. A light-light edge contributes one using two light fibres, also at most $m$ per light fibre. Every external direction therefore needs at least $\lceil H/m\rceil$ light fibres. ∎

### Corollary 12. A full-fibre-free configuration needs many heavy fibres

For $n\ge2$, every Kakeya set without a full residue fibre satisfies

\[
\boxed{(h-1)^2\ge N-1,\qquad
h\ge1+\lceil\sqrt{N-1}\rceil.}
\tag{18}
\]

Thus the required lower bounds on heavy counts in dimensions $2,3,4,5,6,7,8$ are respectively $3,4,5,7,9,13,17$.

**Proof.** If there are no heavy fibres, covering one direction requires all $N$ fibres to be light and to have their internal pair in that one direction. A second direction then cannot be covered, so this is impossible for $n\ge2$. Otherwise $M<N$, so $m\le H-1$, and $q\ge2$. From (16),

\[
2(N-1-d)\le N-h,
\qquad 2d\ge N+h-2.
\]

Using $2d\le h(h-1)$ gives $h(h-1)\ge N+h-2$, which is (18). ∎

The conclusion is stronger than a count of directions supported by heavy base points: it accounts for the fact that each two-point fibre can pay for only one external direction.

## 7. The sharp law with at most two heavy fibres

### Theorem 13. Uniform two-heavy-fibre theorem

Let $n\ge2$. Every family of actual fibre types satisfying (1) and having at most two heavy fibres has total size at least $3N-2$. It contains a full fibre. Equality holds precisely for one full fibre and an own-direction pair in every other fibre. If there are exactly two heavy fibres, the lower bound improves to $3N-1$, and this bound is attainable by an actual Kakeya set in either ring.

**Proof.** Zero heavy fibres are impossible by the argument in Corollary 12. Suppose first that there is one heavy base point, translated to zero. In every direction $v\ne0$, the $H-1$ matching edges away from zero contribute at most $H-1$. Therefore the edge \(\{0,v\}\) must contribute. Every other fibre is consequently light, with its unique pair in its own direction $v$. No light-light edge can then contribute: two distinct light fibres have distinct internal directions. Thus $p_0(v)\ge H$ for every nonzero $v$, forcing the zero fibre to be full. The total is exactly $N+2(N-1)=3N-2$.

Now suppose the two heavy points are $0,b$. There are $N-2$ external directions $v\notin\{0,b\}$. In each, the $H-2$ light-light matching edges cannot alone reach $H$, so at least one heavy-light edge is compulsory. These directions require $N-2$ distinct light fibres, and there are only $N-2$ nonheavy positions. Therefore all of them are light, every external direction receives exactly one heavy-light edge, and every light fibre is assigned to one such edge. No light-light edge contributes anywhere: its endpoints would have to have their pair direction equal to their joining difference, although each is already paired to a heavy endpoint in that direction. Hence each external direction is covered by a single heavy-light edge, and its heavy capacity must be $H$. Since $N-2>0$, at least one heavy fibre is full. The other has size at least three. Consequently

\[
\sum_a|A_a|\ge N+3+2(N-2)=3N-1.
\]

Adding a third point to one of the two-point fibres in the standard construction realizes this bound, in both rings. The only equality case at $3N-2$ is therefore the one-heavy case already described. ∎

The theorem depends only on the pair budget and (1), because a size-two pair vector has exactly one nonzero entry. It applies directly to the integer pair-budget and defect relaxations, even before imposing the additional spectral tests.

## 8. Compatibility between two realized fibres

Exact realization of each fibre is still not enough to make the product in (1) count distinct lifted directions. Shared periods force repeated representations of the same direction class. The following correction is determined entirely by the exact pair vectors.

### Theorem 14. Shared-period capacity

For an actual fibre $A$, its translation stabilizer is

\[
H_A=\{h:A+h=A\}=\{0\}\cup\{v\ne0:2p_A(v)=|A|\}.
\]

Fix $v\ne0$, and define subgroups of $V/\langle v\rangle$ by

\[
S_A(v)=(H_A+\langle v\rangle)/\langle v\rangle,
\qquad J_{A,B}(v)=S_A(v)\cap S_B(v).
\]

Then

\[
\boxed{
|P_v(A)+P_v(B)|
\le \min\left(H,\frac{p_A(v)p_B(v)}{|J_{A,B}(v)|}\right).
}
\tag{19}
\]

Consequently every ring Kakeya set satisfies the stronger necessary condition

\[
\sum_{\{a,a+v\}}
\min\left(H,
\frac{p_a(v)p_{a+v}(v)}{|J_{A_a,A_{a+v}}(v)|}\right)
\ge H
\qquad(v\ne0).
\tag{20}
\]

**Proof.** The set $A\cap(A+v)$ is invariant under $H_A$ and under translation by $v$. Thus $P_v(A)$ is invariant under $S_A(v)$, and similarly for $B$. Each common period $j\in J_{A,B}(v)$ acts on a representation $z=x+y$, with $x\in P_v(A)$, $y\in P_v(B)$, by

\[
(x,y)\longmapsto(x+j,y+j).
\]

This action is free and preserves the sum because the quotient has characteristic two. Every represented sum therefore has at least $|J_{A,B}(v)|$ representations. Counting all $p_A(v)p_B(v)$ pairs proves (19); the quotient itself has size $H$. The carry in the mixed-characteristic ring translates the sumset and preserves its size. Applying the union bound to the exact fibre covering identity proves (20). ∎

For nonempty pair sets, $|J_{A,B}(v)|$ divides both pair counts, so the expression in (19) is integral. Empty pair sets contribute zero. The subgroup $H_A$, and hence this correction, are recoverable directly from the pair vector; no choice of a particular realizing subset is needed.

### An exact separation from local realization

At dimension three, the locally realizable type assignment with base-point sizes

\[
(s_0,\ldots,s_7)=(6,6,4,0,4,0,4,0)
\]

has total size 24 and satisfies every original matching-product constraint. Its pair vectors, with directions $1,\ldots,7$, are

\[
\begin{aligned}
p_0&=(2,2,2,2,2,2,3),&
p_1&=(2,2,2,2,3,2,2),\\
p_2&=(2,2,2,0,0,0,0),&
p_4&=(2,0,0,2,2,0,0),\\
p_6&=(2,0,0,0,0,2,2),&
p_3=p_5=p_7&=0.
\end{aligned}
\]

In direction $v=6$, the only contributing edge is $\{0,6\}$. Both pair counts equal two, so the original bound assigns capacity four. But $H_{A_0}=\{0,7\}$ and $H_{A_6}=\{0,1,6,7\}$. After quotienting by \(\langle6\rangle\), the common period subgroup has size two. The corrected capacity is therefore $2\cdot2/2=2<4$. **No choice of realizing fibres or of carry shifts can lift this assignment to a Kakeya set.** This rejection concerns the directional pair vectors; it does not exclude the same size multiset with different pair vectors.

The checker verifies (19) for all 458,752 ordered subset-pair/direction triples in $\mathbb F_2^3$, using direct quotient sumsets independently of the period calculation. It also verifies the displayed separation directly from its type vectors.

## 9. Reproduction and delivered objects

Run

```bash
python extension/theory/verify_theory.py
```

from the combined bundle root. The standard-library script writes `theory_receipt.json` and `local_types_n4.json` beside itself. It verifies the dimension-three metric/square classification, independently compares every dimension-four subset type with every admissible square spectrum, checks the four-frequency sign obstruction and a positive control, replays the four-frequency theorem at dimensions four through eight, and checks all subspace budgets on the complete dimension-four type table. It also exhausts all 2,401 assignments of the seven local types at dimension two: 136 satisfy the matching capacities, and all obey the allocation and two-heavy-fibre theorems.

The file `local_types_n4.json` contains a realizing subset mask for every one of the 3,967 types, making each row independently inspectable. Removing its singleton row gives the 3,966-type nondominated catalogue. The general theorems above have written proofs; the dimension-four completeness table is a finite exhaustive computation with two independent enumerations. The shared-period capacity test adds a separate all-pairs verification of the interaction between realized fibres. This chapter does not claim a new proof of the unrestricted dimension-four Kakeya minimum or settle the unrestricted dimension-five problem.
