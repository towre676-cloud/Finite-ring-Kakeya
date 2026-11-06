# Teichmüller fibre traces at every length

## A complete carry law and the first nonlinear separation of the two ring geometries

**Abstract.** For the pair
\[
A_{p,\ell}=\mathbb Z/p^\ell\mathbb Z,
\qquad
A_{p,\ell}^{\flat}=\mathbb F_p[t]/(t^\ell),
\]
we give an explicit length-three fibre-trace formula and an exact recursion valid at every length. The formula includes the carries created when different terms of a product enter the same digit. It yields a complete criterion for a length-three trace to be an affine plane in digit coordinates, and an exact count of affine traces in every dimension at odd primes. Every length-three trace is affine when \(p=2\), including in mixed characteristic. The first possible nonlinear separation is sharp: mixed-characteristic traces can be nonaffine at length three for every odd prime, and at length four for \(p=2\). Equal-characteristic traces remain affine at all lengths. We also give the length-three replacement for the integer-slope reparametrisation in the supplied notation reform.

The proofs below hold for all primes, all indicated lengths, and every ambient dimension. The accompanying standard-library program independently checks the formulas using direct arithmetic in the two rings. It also performs complete line-fibre censuses in five pairs of small planes. The results concern the incidence machinery underlying the Kakeya problems; an equality or inequality between the Kakeya minima requires an additional extremal argument.

## 1. Coordinates and the two carry functions

Write \(R\) for either member of the pair and \(\pi=p\) or \(t\), respectively. Reduction modulo \(\pi\) is \(\rho\). Each element has a unique expansion
\[
z=[z_0]+\pi[z_1]+\cdots+\pi^{\ell-1}[z_{\ell-1}],
\qquad z_i\in\mathbb F_p.
\]
The brackets denote the Teichmüller lift in mixed characteristic and the constant lift in equal characteristic. Vector digits and every carry below are read coordinatewise.

For mixed characteristic a useful representative is
\[
\tau_m(a)=a^{p^{m-1}}\pmod {p^m},\qquad 0\le \tau_m(a)<p^m.
\tag{1}
\]
It is the unique lift of \(a\) satisfying \(z^p=z\pmod {p^m}\). To see uniqueness without invoking a lifting theorem, a root modulo \(p^j\) has possible next lifts \(z+c p^j\); the equation changes by \(-c p^j\) modulo \(p^{j+1}\), so exactly one \(c\in\mathbb F_p\) works. The power formula follows by repeatedly applying the binomial theorem to Fermat's congruence. Products of roots are roots, so uniqueness also proves
\[
[a][b]=[ab].
\tag{2}
\]
Subtracting the residue lift and dividing by \(\pi\) repeatedly proves existence and uniqueness of the digit expansion.

Define \(\gamma_R\) and \(\eta_R\) by
\[
[a]+[b]=[a+b]+\pi[\gamma_R(a,b)]+\pi^2[\eta_R(a,b)]
\pmod {\pi^3}.
\tag{3}
\]
Both are zero on the equal-characteristic side. On the mixed-characteristic side the first carry is the one already fixed in the supplied notation reform:
\[
\gamma(a,b)=G_p(a,b)\pmod p,
\qquad
G_p(a,b)=\frac{a^p+b^p-(a+b)^p}{p}.
\tag{4}
\]
Here and below one may evaluate the integer expressions on representatives \(0,\ldots,p-1\). The second carry has the exact expression
\[
\eta(a,b)=
\frac{a^{p^2}+b^{p^2}-(a+b)^{p^2}-pG_p(a,b)^p}{p^2}
\pmod p.
\tag{5}
\]
The power and division in (5) are integer operations before the final reduction. One may replace \(G_p(a,b)\) by a congruent integer representative if its integer \(p\)-th power is retained; the binomial congruence below shows the answer is unchanged. Replacing that power by its residue-field value before division need not preserve the answer.

**Proof of (4)–(5).** If integers \(u,v\) are congruent modulo \(p\), the binomial theorem gives
\(u^{p^j}\equiv v^{p^j}\pmod {p^{j+1}}\). Thus, with \(c=a+b\pmod p\),
\(\tau_2(c)\equiv(a+b)^p\pmod {p^2}\). Subtracting from \(\tau_2(a)+\tau_2(b)\) proves (4). At precision three, \(\tau_3(c)\equiv(a+b)^{p^2}\pmod {p^3}\). Put \(g=G_p(a,b)\pmod p\). Since \(\tau_3(g)\equiv G_p(a,b)^p\pmod {p^2}\), subtracting \(\tau_3(c)+p\tau_3(g)\) from \(\tau_3(a)+\tau_3(b)\) leaves a multiple of \(p^2\), whose quotient modulo \(p\) is (5). This also proves that the quotient in (5) is integral. □

For \(p=2\), \(\gamma(a,b)=ab\) and \(\eta(a,b)=0\). The second carry is also zero for \(p=3\): the Teichmüller representatives are \(0,1,-1\), and their pairwise sums require no second carry. It is already nonzero at \(p=5\); for example,
\[
\gamma(1,1)=4,\qquad \eta(1,1)=3.
\]
Indeed, in \(\mathbb Z/125\mathbb Z\), \([2]=57\), \([4]=124\), and \([3]=68\), giving \(57+5\cdot124+25\cdot68\equiv2\pmod {125}\).

## 2. The explicit length-three trace law

Let
\[
x=[a]+\pi[b]+\pi^2[c],\qquad
v=[\alpha]+\pi[\beta]+\pi^2[\delta],
\qquad \alpha\ne0,
\]
and write a scalar parameter as
\[
s=[\sigma]+\pi[r]+\pi^2[u].
\]
All the displayed vector sums and scalar products outside brackets now take place in \(\mathbb F_p\).

For fixed \(\sigma\), set
\[
g_\sigma=\gamma_R(a,\sigma\alpha),
\qquad
B_\sigma=b+\sigma\beta+g_\sigma,
\qquad
q_\sigma(r)=\sigma\beta+r\alpha.
\]
Define
\[
\begin{aligned}
H_\sigma(r)={}&c+\sigma\delta+r\beta+\eta_R(a,\sigma\alpha)\\
&+\gamma_R(\sigma\beta,r\alpha)
+\gamma_R(b,q_\sigma(r))
+\gamma_R(b+q_\sigma(r),g_\sigma).
\end{aligned}
\tag{6}
\]

**Theorem 1 — Length-three fibre trace.** The points of the line \(x+Rv\) over the residue point \(a+\sigma\alpha\) have precisely the higher digits
\[
\boxed{
\mathcal T_\sigma(x,v)
=\{(B_\sigma+r\alpha,\ H_\sigma(r)+u\alpha):r,u\in\mathbb F_p\}.
}
\tag{7}
\]
The parametrisation is injective, so every residue fibre contains \(p^2\) points.

**Proof.** Multiplicativity of the bracket gives
\[
sv=[\sigma\alpha]
+\pi\bigl([\sigma\beta]+[r\alpha]\bigr)
+\pi^2\bigl([\sigma\delta]+[r\beta]+[u\alpha]\bigr).
\]
Normalising the sum in the coefficient of \(\pi\) contributes
\(\gamma_R(\sigma\beta,r\alpha)\) to the top digit. Adding \([a]\) to the zeroth digit contributes \(g_\sigma\) at the first level and \(\eta_R(a,\sigma\alpha)\) at the second. The remaining first-level sum is
\[
[b]+[q_\sigma(r)]+[g_\sigma].
\]
Adding its terms in that order produces first digit \(b+q_\sigma(r)+g_\sigma\) and top carry
\(\gamma_R(b,q_\sigma(r))+\gamma_R(b+q_\sigma(r),g_\sigma)\). All further sums are already multiplied by \(\pi^2\), so they add in the residue field. This proves (6)–(7). Equality of the first higher digit determines \(r\), because \(\alpha\ne0\); equality of the second then determines \(u\). □

### Why the product carry is essential

Multiplicativity of individual Teichmüller lifts does not make multilevel multiplication a carryless convolution. The term
\[
\gamma_R(\sigma\beta,r\alpha)
\tag{8}
\]
records the addition of two products arriving at the same digit. At \(p=2\), length three, take \(s=v=1+2=3\). In \(\mathbb Z/8\mathbb Z\), \(sv=1\). Carryless coefficient convolution would give digits \((1,0,1)\), hence the incorrect value \(5\). The carry \(\gamma(1,1)=1\) cancels that top digit and gives the correct digits \((1,0,0)\).

The supplied reform correctly confines its closed trace formula to length two. Its statement about multiplicativity is correct for the bracket map; at higher length the complete product must include (8).

### A compact normal form

Put
\[
C_\sigma=c+\sigma\delta+\eta_R(a,\sigma\alpha)
+\gamma_R(b,\sigma\beta)
+\gamma_R(b+\sigma\beta,g_\sigma).
\tag{8a}
\]
Adding the constant first-level terms before \([r\alpha]\) gives the equivalent form
\[
\boxed{
\mathcal T_\sigma
=\{(B_\sigma+r\alpha,
C_\sigma+r\beta+u\alpha+\gamma_R(B_\sigma,r\alpha)):
r,u\in\mathbb F_p\}.
}
\tag{8b}
\]
This is the same ring sum regrouped: the first-level terms are
\([b]+[\sigma\beta]+[g_\sigma]+[r\alpha]\). In this form all nonlinear dependence on the lower scalar parameter is isolated in a single carry \(\gamma_R(B_\sigma,r\alpha)\).

## 3. Affine traces and their exact obstruction

Let
\[
Q_\alpha=\mathbb F_p^n/\langle\alpha\rangle,
\qquad h_\sigma(r)=H_\sigma(r)\pmod {\langle\alpha\rangle}.
\]
The top parameter \(u\) in (7) already sweeps \(\langle\alpha\rangle\), so only this quotient matters for curvature. Define
\[
\mathcal C_\sigma(r)
=h_\sigma(r)-h_\sigma(0)-r\bigl(h_\sigma(1)-h_\sigma(0)\bigr).
\tag{9}
\]

**Theorem 2 — Affine-plane criterion.** The length-three fibre trace is an affine two-dimensional subspace of \(\mathbb F_p^{2n}\) if and only if
\[
\mathcal C_\sigma(r)=0\quad\text{for every }r\in\mathbb F_p.
\tag{10}
\]
In particular, every length-three trace over either binary ring is an affine two-plane.

**Proof.** Project (7) onto its first higher layer. The image is the affine line \(B_\sigma+\langle\alpha\rangle\), and the fibre of this projection is the line \(\{0\}\times\langle\alpha\rangle\). After quotienting by that latter line, the trace is the graph of \(r\mapsto h_\sigma(r)\). This graph is an affine line precisely when its function is affine, which is exactly (10). Conversely, if (10) holds, choose a representative \(D\) of \(h_\sigma(1)-h_\sigma(0)\). Any remaining component of \(H_\sigma(r)-H_\sigma(0)-rD\) lies in \(\langle\alpha\rangle\) and is absorbed by reparametrising \(u\). The trace then has independent direction vectors \((\alpha,D)\) and \((0,\alpha)\). For \(p=2\), every function on the two-element parameter set is affine, so (10) is automatic. □

This criterion is more precise than testing whether the expression \(H_\sigma(r)\) itself is affine: a nonlinear term parallel to \(\alpha\) does not change the trace, because \(u\) absorbs it.

**Corollary 2.1 — Complete odd-prime support criterion.** For mixed characteristic and odd \(p\), the length-three trace is affine if and only if there is a scalar \(\lambda\in\mathbb F_p\) such that
\[
(B_\sigma)_i=\lambda\alpha_i
\quad\text{at every coordinate with }\alpha_i\ne0.
\tag{10a}
\]
The coordinates of \(B_\sigma\) outside the support of \(\alpha\) are unrestricted.

**Proof.** By (4), the vector-valued function \(r\mapsto\gamma(B_\sigma,r\alpha)\) has degree at most \(p-1\). Its leading coefficient is the negative of the vector obtained by restricting \(B_\sigma\) to the support of \(\alpha\), because \(\alpha_i^{p-1}=1\) on that support. For odd \(p\), this is a coefficient of degree at least two. Theorem 2 and uniqueness of polynomial functions of degree below \(p\) force that coefficient into \(\langle\alpha\rangle\), giving (10a). Conversely, multiplicativity of the Teichmüller lift implies \(\gamma(za,zb)=z\gamma(a,b)\). Under (10a), the entire vector carry is therefore \(\alpha\gamma(\lambda,r)\), including its zero coordinates. It is absorbed by the parameter \(u\), so the trace is affine. □

**Binary implementation formula.** In mixed characteristic, all products below are coordinatewise products in \(\mathbb F_2^n\). Formula (7) becomes
\[
\begin{aligned}
B_\sigma&=b+\sigma\beta+\sigma a\alpha,\\
C_\sigma&=c+\sigma\delta+\sigma b\beta
+\sigma a\alpha b+\sigma a\alpha\beta,\\
D_\sigma&=\beta+\sigma\alpha\beta+b\alpha+\sigma a\alpha,
\end{aligned}
\]
and
\[
\mathcal T_\sigma
=(B_\sigma,C_\sigma)
+\langle(\alpha,D_\sigma),(0,\alpha)\rangle.
\tag{11}
\]
On the equal-characteristic side, \(B_\sigma=b+\sigma\beta\), \(C_\sigma=c+\sigma\delta\), and \(D_\sigma=\beta\). Thus a length-three binary incidence solver may work with affine planes on both sides, with the different plane embeddings specified exactly by (11).

## 4. The first nonlinear separation is sharp

**Theorem 3 — Exact boundary for universal affine residue traces.** Fix a prime \(p\) and consider all primitive lines in all dimensions \(n\ge2\).

1. In \(A_{p,\ell}^{\flat}\), every residue fibre trace is an affine subspace of digit space, of dimension \(\ell-1\), at every length.
2. In \(A_{p,\ell}\), every such trace is affine at lengths one and two. At length three this remains true for \(p=2\).
3. For every odd prime, a nonaffine trace exists in \(A_{p,3}^2\). For \(p=2\), a nonaffine trace exists in \(A_{2,4}^2\). These examples persist at all greater lengths.

Consequently the first length at which universal affineness fails in mixed characteristic is three for odd primes and four for the prime two.

**Proof.** In equal characteristic the digit map identifies addition with vector addition, and multiplication by fixed \(v\) is \(\mathbb F_p\)-linear in the scalar digits. Fixing the residue scalar therefore gives an affine subspace. Its dimension is \(\ell-1\) because a unit coordinate of \(v\) makes the scalar parametrisation injective. The mixed-characteristic positive statements follow from the length-two law and Theorem 2.

For an odd prime, take the origin line in \((\mathbb Z/p^3\mathbb Z)^2\) with
\[
v=(1,1+p),\qquad \sigma=1.
\]
Its higher digit trace is
\[
\{((r,1+r),(u,u+r+\gamma(1,r))):r,u\in\mathbb F_p\}.
\tag{12}
\]
The function \(r\mapsto\gamma(1,r)\) is not affine. It vanishes at both \(r=0\) and \(r=-1\), because the odd-prime Teichmüller lifts satisfy \([-1]=-1\). An affine function with these two zeros would be identically zero. But if \(\gamma(1,r)=0\) for every \(r\), repeated use of \([1]+[r]=[1+r]\pmod {p^2}\) would give \(p[1]=[0]=0\) in \(\mathbb Z/p^2\mathbb Z\), a contradiction. In the quotient by \(\alpha=(1,1)\), the last two coordinates of (12) have difference \(r+\gamma(1,r)\). Theorem 2 therefore proves nonaffineness.

For \(p=2\), take \(v=(1,3)\), \(x=(0,0)\), and the residue fibre \(\sigma=0\) in \((\mathbb Z/16\mathbb Z)^2\). Write
\(s=2r+4u+8w\). Teichmüller digits here are ordinary binary digits. The three higher layers are
\[
\bigl((r,r),(u,r+u),(w,u+w+ru)\bigr),
\qquad r,u,w\in\mathbb F_2.
\tag{13}
\]
The term \(ru\) is a genuine bilinear obstruction. Concretely the fibre contains \((2,6)\) and \((4,12)\), but it does not contain their digitwise sum \((6,10)\): the line point with first coordinate \(6\) is \((6,2)\). Since the fibre contains zero, it cannot be affine. In the equal-characteristic ring the corresponding formula has final layer \((w,u+w)\), with no \(ru\) term.

Finally, reduction to the smallest indicated length is a linear projection in digit coordinates. An affine trace at a larger length would have an affine projection, contradicting the examples just proved. □

The conclusion identifies exactly where an affine-fibre reduction ceases to describe every line. It does not identify a nonzero Kakeya tilt defect: minimum-cardinality configurations can agree even when the local embeddings differ.

The odd-prime obstruction also has an explicit polynomial degree. Expanding (4) gives
\[
\gamma(1,r)=-\sum_{j=1}^{p-1}\frac{1}{p}\binom pj r^j\pmod p.
\tag{13a}
\]
Its coefficient of \(r^{p-1}\) is \(-1\), so its unique representative of degree below \(p\) has degree exactly \(p-1\). Subtracting the affine part in (9) leaves that leading coefficient unchanged. Thus the trace in (12) has quotient curvature of degree exactly \(p-1\), while the first binary obstruction in (13) is bilinear in the two lower scalar digits.

### 4.1. An exact affine census in every dimension

Count incidences \((L,a)\), where \(L\) is a distinct primitive affine line in \((\mathbb Z/p^3\mathbb Z)^n\) and \(a\in\rho(L)\) is one of its \(p\) residue points. Different lines may produce the same trace subset; this census counts their incidences separately. Affineness is measured in the fixed, coordinatewise Teichmüller digit system.

**Theorem 3.1 — All-dimensional affine-incidence count.** For an odd prime \(p\) and \(n\ge1\), the total number of line-fibre incidences is
\[
N_{p,n}=p^{5n-4}\frac{p^n-1}{p-1}.
\tag{13b}
\]
Exactly
\[
\boxed{
N^{\mathrm{aff}}_{p,n}=p^{4n-3}\frac{(2p-1)^n-p^n}{p-1}
}
\tag{13c}
\]
have affine traces. The remaining \(N_{p,n}-N^{\mathrm{aff}}_{p,n}\) are nonaffine.

**Proof.** Fix a residue projective direction \(\alpha\) with support size \(m\). Choose a nonzero pivot coordinate, and normalise its coordinate in the full direction to one. There are \(p^{2(n-1)}\) lifted directions with that fixed residue direction. A unique transversal intercept has pivot coordinate zero and arbitrary other coordinates, giving \(p^{3(n-1)}\) lines per lifted direction. Each line has \(p\) residue fibres. Thus the contribution per residue projective direction is \(p^{5n-4}\), proving (13b) after summing over \((p^n-1)/(p-1)\) residue directions.

For the normalised intercept, \((B_\sigma)_{\rm pivot}=0\), and \(\alpha_{\rm pivot}=1\). Corollary 2.1 therefore forces \(\lambda=0\). The other \(m-1\) coordinates in the residue-direction support must have middle offset zero. For fixed residue intercept, top intercept, direction, and \(\sigma\), each of these middle offsets is the corresponding middle intercept digit plus a fixed field element. Consequently exactly the fraction \(p^{1-m}\) of the incidences for this residue direction are affine.

There are \(\binom nm(p-1)^{m-1}\) residue projective directions with support size \(m\). Summing gives
\[
\begin{aligned}
N^{\mathrm{aff}}_{p,n}
&=\sum_{m=1}^{n}\binom nm(p-1)^{m-1}p^{5n-3-m}\\
&=p^{4n-3}\frac{(2p-1)^n-p^n}{p-1},
\end{aligned}
\]
as asserted. □

For the plane this becomes the particularly simple exact census
\[
N_{p,2}=p^6(p+1),\qquad
N^{\mathrm{aff}}_{p,2}=p^5(3p-1),\qquad
N_{p,2}-N^{\mathrm{aff}}_{p,2}=p^5(p-1)^2.
\tag{13d}
\]
At fixed odd \(p\), the affine fraction satisfies
\[
\frac{N^{\mathrm{aff}}_{p,n}}{N_{p,n}}
\sim p\left(\frac{2p-1}{p^2}\right)^n
\longrightarrow0.
\tag{13e}
\]
Thus almost all mixed-characteristic length-three line-fibre incidences become nonaffine as dimension grows in these digit coordinates. Every equal-characteristic incidence remains affine. This gives an exact measure of the incidence geometry that a higher-length comparison must retain.

## 5. An exact recursion at arbitrary length

Let scalar digit sequences \(x_k,v_k,s_k\in\mathbb F_p\), \(0\le k<\ell\), represent \(x,v,s\). For a vector calculation apply the following procedure separately to each coordinate, using the same scalar sequence \(s_k\).

In mixed characteristic choose the integer representatives \(\tau=\tau_\ell\) of (1), and set \(c_0=0\). For \(0\le k<\ell\), define
\[
\begin{aligned}
z_k&=c_k+\tau(x_k)+\sum_{i=0}^{k}\tau(s_i v_{k-i}),\\
y_k&=z_k\pmod p,\qquad 0\le y_k<p,\\
c_{k+1}&=\frac{z_k-\tau(y_k)}{p}.
\end{aligned}
\tag{14}
\]
The arguments of \(\tau\) are field elements. The carries \(c_k\) are ordinary signed integers; they need not lie in \(0,\ldots,p-1\). In equal characteristic set
\[
y_k=x_k+\sum_{i=0}^{k}s_i v_{k-i}\pmod p.
\tag{15}
\]

**Theorem 4 — All-length carry recursion.** The outputs of (14) or (15) are exactly the Teichmüller digits of \(x+sv\). The recursion requires \(O(\ell^2)\) digit products per coordinate and no table with \(p^{2\ell}\) entries.

**Proof.** Multiplicativity of \(\tau\) modulo \(p^\ell\) gives
\[
x+sv\equiv
\sum_{k=0}^{\ell-1}p^k
\left(\tau(x_k)+\sum_{i=0}^{k}\tau(s_i v_{k-i})\right)
\pmod {p^\ell}.
\]
Every division in (14) is exact, since \(\tau(y_k)\equiv y_k\equiv z_k\pmod p\). Rearranging its defining equality and telescoping yields
\[
\sum_{k<\ell}p^k
\left(\tau(x_k)+\sum_{i=0}^{k}\tau(s_i v_{k-i})\right)
=\sum_{k<\ell}p^k\tau(y_k)+p^\ell c_\ell.
\]
Reduction modulo \(p^\ell\), followed by uniqueness of digits, proves (14). In equal characteristic multiplication is ordinary truncated polynomial convolution, which is (15). There are \(1+2+\cdots+\ell\) diagonal products. □

### The trace tree

Fix \(s_0=\sigma\), and let \(\alpha=v_0\ne0\) in the vector problem. At every stage,
\[
y_k=s_k\alpha+
F_k(x_0,\ldots,x_k,v_0,\ldots,v_k,\sigma,s_1,\ldots,s_{k-1}),
\tag{16}
\]
because the only new occurrence of \(s_k\) is \(s_kv_0\) and the incoming carry depends only on earlier columns.

**Corollary 4.1 — Balanced triangular fibres.** A residue trace at length \(\ell\) contains exactly \(p^{\ell-1}\) points. Its first \(j\) higher layers have exactly \(p^j\) distinct prefixes, and every such prefix extends to exactly \(p^{\ell-1-j}\) full trace points. Once the first \(j-1\) scalar digits have been chosen, the possible \(j\)-th digits form an affine line parallel to \(\alpha\).

**Proof.** Equation (16) determines \(s_k\) uniquely from the next vector digit, because \(\alpha\ne0\). Induct on \(k\). Every unresolved scalar digit has \(p\) choices. □

Thus the two ring geometries have the same abstract branching and different carry-dependent embeddings. This distinction permits a common recursive incidence engine while retaining the arithmetic information needed for comparisons of minima.

## 6. Extending the integer-slope coordinate repair

Let the ordinary integer representative \(\widetilde a\in\{0,\ldots,p-1\}\) have mixed-characteristic digits
\[
\widetilde a=[a]+\pi[e_1(a)]+\pi^2[e_2(a)].
\]
The length-two correction in the supplied reform is \(\delta\mapsto\delta+e_1(a)\). At length three the complete correction is triangular.

**Proposition 5 — Length-three slope conversion.** The slope written as
\[
\widetilde a+\pi[\delta]+\pi^2[\varepsilon]
\]
has Teichmüller digits
\[
\boxed{
\bigl(a,\ e_1(a)+\delta,
\ e_2(a)+\varepsilon+\gamma_R(e_1(a),\delta)\bigr).
}
\tag{17}
\]
For each fixed \(a\), this is a bijection in the two lift indices. On the equal-characteristic side \(e_1=e_2=\gamma_R=0\).

**Proof.** Substitute the expansion of \(\widetilde a\). Normalising \([e_1(a)]+[\delta]\) inside the coefficient of \(\pi\) supplies exactly the additional top carry in (17). Its inverse first recovers \(\delta\), then \(\varepsilon\). □

At greater lengths the same normalization is triangular and therefore bijective. This preserves direction indexing when all accompanying line data are converted consistently. A single constant shift of the first lift index is insufficient to express the complete length-three change of coordinates.

## 7. Independent implementation and finite checks

`trace_law.py` is self-contained and uses only Python's standard library. Its formula engine implements (4)–(7) and (14)–(15). Its independent oracle:

- constructs Teichmüller representatives by lifting roots of \(z^p=z\), rather than by the engine's exponentiation formula;
- performs mixed-characteristic operations as ordinary integer addition and multiplication modulo \(p^\ell\);
- performs equal-characteristic operations by direct truncated polynomial arithmetic;
- builds an independent decoding table by enumerating digit expansions;
- compares complete vector fibre sets and checks every prefix multiplicity.

The standard profile covers primes \(2,3,5,7\) and lengths three and four in both rings. It exhausts all scalar triples \((x,v,s)\) at \(p=2,3\) for both lengths, and at \(p=5\) for length three. The larger cases use the exact, separately recorded domains in `trace_receipt.json`: element-by-element boundary coverage, all scalar products at zero intercept where specified, and seeded general triples. It additionally checks full vector fibre sets in dimensions two and three. These larger domains are not described as exhaustive.

Boundary checks exhaust all scalar triples at lengths one and two for the same four primes, including the length-one quotient where the uniformiser is zero. The engine accepts only positive integral lengths and prime residue sizes; its canonical code parser rejects malformed strings and composite residue sizes. The slope conversion (17) is checked over every \((a,\delta,\varepsilon)\) at the four primes.

The complete plane censuses enumerate every direction and every line in \(R^2\) for \((p,\ell)=(2,3),(2,4),(3,3),(3,4),(5,3)\), on both sides. A unique direction representative is either \((1,m)\), with \(m\in R\), or \((m,1)\), with \(m\in\pi R\). Unique intercept transversals are \((0,b)\) and \((b,0)\), respectively. Thus each census contains
\[
(p^\ell+p^{\ell-1})p^\ell
\]
distinct lines and \(p\) times as many line-fibre incidences. Affineness is decided by exact Gaussian elimination over \(\mathbb F_p\), comparing a trace's cardinality with the size of its affine span.

The completed standard run gives the following exact plane census. Each row compares the mixed and equal-characteristic rings at the same prime and length.

| \((p,\ell)\) | Line-fibre incidences per ring | Mixed: affine | Mixed: nonaffine | Equal characteristic: affine |
|---|---:|---:|---:|---:|
| \((2,3)\) | 192 | 192 | 0 | 192 |
| \((2,4)\) | 768 | 640 | 128 | 768 |
| \((3,3)\) | 2,916 | 1,944 | 972 | 2,916 |
| \((3,4)\) | 26,244 | 7,776 | 18,468 | 26,244 |
| \((5,3)\) | 93,750 | 43,750 | 50,000 | 93,750 |

Across both rings, the implementation run checked 6,174,476 scalar cases at lengths three and four, including 4,223,996 comparisons against each of the expanded and compact length-three formulas. The separate boundary run exhausted 269,140 scalar cases at lengths one and two. It checked 1,006 slope-coordinate conversions, 6,528 complete vector fibre sets containing 696,192 point incidences, and 247,740 line-fibre incidences in the complete plane censuses. All comparisons passed. The recorded runtime was 58.718 seconds on the execution environment; timings on other machines will differ.

The JSON receipt records exact domains, counts, seed, code hash, and runtime. A finite check establishes the correctness of those computations; the preceding algebraic proofs establish the general theorems.

## 8. Relation to the supplied work

The starting conventions and length-two law are those of [NOTATION.md](../../kakeya_tilt_notation/NOTATION.md), with the open higher-length task stated explicitly in [HANDOFF_ADDENDUM_2026-11-01.md](../../kakeya_tilt_notation/HANDOFF_ADDENDUM_2026-11-01.md). The source implementations [tilt.py](../../kakeya_tilt_notation/tilt.py), [checks.py](../../kakeya_tilt_notation/checks.py), and [reform.py](../../kakeya_tilt_notation/reform.py) were read without modification.

The length-two reform survives this extension. What changes at higher length is the amount of arithmetic that a line-incidence calculation must retain: diagonal product carries, the second carry of the base addition, and the triangular change of slope coordinates. The affine-plane theorem gives a direct route to length-three binary fibre models. The sharp nonaffineness theorem identifies the next regime where an affine-only model would omit valid line shapes. No priority claim is made for these algebraic identities or structural observations.
