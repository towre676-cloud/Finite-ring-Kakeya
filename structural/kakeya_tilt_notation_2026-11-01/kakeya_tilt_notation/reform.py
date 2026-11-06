"""reform.py -- one-shot rewrite of kakeya_across_the_tilt.html into the notation of NOTATION.md."""
s = open('kakeya_across_the_tilt.html').read()


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (old[:70], n)
    s = s.replace(old, new)


def sub_between(start, end, new):
    global s
    i = s.index(start); j = s.index(end, i)
    s = s[:i] + new + s[j:]


rep('certified SAT campaign · 25 October 2026', 'certified SAT campaign · notation reform 1 November 2026')
rep(r'over $\mathbb{Z}/p^k$ and $\mathbb{F}_p[t]/(t^k)$, settled',
    r'over $A_{p,\ell}=\mathbb{Z}/p^\ell$ and its tilt $A^\flat_{p,\ell}=\mathbb{F}_p[t]/(t^\ell)$, settled')

rep(r'Write $k(R,n)$ for the least cardinality of a set $K\subseteq R^n$ containing a full line $\{x+sv:s\in R\}$ for every direction $[v]\in\mathbb{P}^{n-1}(R)$.</p>',
    r'Write $\kappa_n(R)$ for the least cardinality of a set $K\subseteq R^n$ containing a full line $\{x+sv:s\in R\}$ for every direction $[v]\in\mathbb{P}^{n-1}(R)$, and $\Delta_n(p,\ell)=\kappa_n(A_{p,\ell})-\kappa_n(A^\flat_{p,\ell})$ for the tilt defect. The rings and the remaining symbols are fixed in §0′.</p>')

table = r'''<div class="well"><table>
<tr><th>Pair $(p,\ell)$</th><th>$n$</th><th>$\kappa_n(A_{p,\ell})$</th><th>$\kappa_n(A^\flat_{p,\ell})$</th><th>$\Delta_n$</th><th>Status</th><th>Wall time</th></tr>
<tr><td class="num">$(2,2)$</td><td class="num">2</td><td class="num">10</td><td class="num">10</td><td class="num">0</td><td><span class="label cert">certified</span></td><td class="num">&lt;0.1 s</td></tr>
<tr><td class="num">$(2,2)$</td><td class="num">3</td><td class="num"><b>22</b></td><td class="num"><b>22</b></td><td class="num">0</td><td><span class="label cert">certified</span> new</td><td class="num">27 s, 30 s</td></tr>
<tr><td class="num">$(2,3)$</td><td class="num">2</td><td class="num"><b>34</b></td><td class="num"><b>34</b></td><td class="num">0</td><td><span class="label cert">certified</span> new</td><td class="num">0.2 s</td></tr>
<tr><td class="num">$(3,2)$</td><td class="num">2</td><td class="num">45</td><td class="num">45</td><td class="num">0</td><td><span class="label cert">certified</span> (third proof)</td><td class="num">3.8 s, 4.5 s</td></tr>
<tr><td class="num">$(5,2)$</td><td class="num">2</td><td class="num">$[151,310]$</td><td class="num">$[151,309]$</td><td class="num">$[-158,159]$</td><td><span class="label open">open</span></td><td class="num">—</td></tr>
<tr><td class="num">$(2,2)$</td><td class="num">4</td><td class="num"><b>46</b></td><td class="num"><b>46</b></td><td class="num">0</td><td><span class="label cert">certified</span> new (§9)</td><td class="num">≈40 min</td></tr>
<tr><td class="num">$(2,2)$</td><td class="num">$n$</td><td class="num">$\le 3\cdot 2^n-2$</td><td class="num">$\le 3\cdot 2^n-2$</td><td class="num">—</td><td><span class="label new">proved</span> bound, tight $n=2,3,4$</td><td class="num">—</td></tr>
<tr><td class="num">$(p,2)$, $p$ odd</td><td class="num">2</td><td class="num">$\le (p+1)p^2+p^2M(p)$</td><td class="num">same</td><td class="num">—</td><td><span class="label new">proved</span> bound, tight $p=3$</td><td class="num">—</td></tr>
</table></div>
'''
sub_between('<div class="well"><table>\n<tr><th>Ring pair', '<p>In every case decided exactly', table)
rep(r'In every case decided exactly, the mixed-characteristic ring and its equal-characteristic tilt have the same minimum, and in every case the extremal sets found on the two sides have the same fibre profile over $\mathbb{F}_p^n$.',
    r'In every case decided exactly $\Delta_n=0$, and in every case the extremal sets found on the two sides have the same fibre profile $\phi_K$ over $\mathbb{F}_p^n$.')

notation = r'''<h2><span class="sec">§0′</span>Notation</h2>
<p><span class="label new">reform</span>This section replaces the conventions of the October rounds, in which $k$ was both the Kakeya number and the ring length, $\pi$ was the reduction map, $\varepsilon$ was written inside $\mathbb{Z}/4$, and the comparison between the two rings was carried by two unrelated correction terms. For a prime $p$ and a length $\ell\ge1$ the pair under comparison is
$$A_{p,\ell}=W_\ell(\mathbb{F}_p)=\mathbb{Z}/p^\ell,\qquad A^\flat_{p,\ell}=\mathbb{F}_p[t]/(t^\ell),$$
the two length-$\ell$ quotients of the complete discrete valuation rings $\mathbb{Z}_p$ and $\mathbb{F}_p[[t]]$ with residue field $\mathbb{F}_p$. The subscript $p$ is dropped when it is fixed, and $R$ denotes either member of a pair when a statement holds for both. The $\flat$ names the program's tilt at finite level and is a mnemonic only; it is not Scholze's tilt, since $\mathbb{Z}_p$ is not perfectoid. On both sides $\pi$ is the uniformiser ($p$, respectively $t$) and $\rho:R^n\to\mathbb{F}_p^n$ is reduction modulo $\pi$. The fibre profile of a set is $\phi_K(a)=|K\cap\rho^{-1}(a)|$, written as a multiset with multiplicities such as $(16,6^{\times3})$; plain exponents would collide with fibre sizes that are themselves powers of $p$.</p>
<p>Coordinates are Teichmüller digits. The lift $[\cdot]:\mathbb{F}_p\to R$ is $[a]=\tilde a^{\,p^{\ell-1}}$ in $A_{p,\ell}$ and the constant lift in $A^\flat_{p,\ell}$. Every $x\in R$ is uniquely $\sum_{i<\ell}\pi^i[x_i]$ with $x_i\in\mathbb{F}_p$, coordinatewise for vectors. The lift is multiplicative on both sides, so the two rings differ only in addition. At length 2 that difference is the carry cocycle
$$[a]+[b]=[a+b]+\pi[\gamma(a,b)]\ \ (\mathrm{mod}\ \pi^2),\qquad \gamma(a,b)=\tfrac{1}{p}\big(a^p+b^p-(a+b)^p\big)\bmod p\ \text{ on }A_{p,\ell},\qquad \gamma\equiv0\ \text{ on }A^\flat_{p,\ell}.$$
At $p=2$, $\gamma(a,b)=ab$, coordinatewise $a\wedge b$, which is the correction the earlier rounds called $\kappa(a,\alpha)$. <code>checks.py</code> (N1) confirms the closed form from the ring tables at $p=2,3,5,7$.</p>
<div class="thm"><p><span class="label new">proved</span><span class="label cert">certified</span><b>Lemma 0 (fibre-trace law, $\ell=2$).</b> Let $x=[a]+\pi[b]$ and $v=[\alpha]+\pi[\beta]$ with $\alpha\ne0$. The line $\{x+sv:s\in R\}$ lies over the base line $a+\mathbb{F}_p\alpha$. Over the base point $a+\sigma\alpha$ its digit set is the coset
$$b+\sigma\beta+\gamma(a,\sigma\alpha)+\langle\alpha\rangle .$$</p></div>
<p><i>Proof.</i> Write $s=[\sigma]+\pi[r]$. Modulo $\pi^2$, $sv=[\sigma][\alpha]+\pi([\sigma\beta]+[r\alpha])$ and $[\sigma][\alpha]=[\sigma\alpha]$ by multiplicativity. Adding $x$ contributes the single carry $[a]+[\sigma\alpha]=[a+\sigma\alpha]+\pi[\gamma(a,\sigma\alpha)]$, and the remaining additions occur inside $\pi R$, where they are digitwise. As $r$ ranges over $\mathbb{F}_p$ the second digit sweeps the coset. $\square$ <code>checks.py</code> (N2) confirms the law against brute-force line enumeration for every $x$, $v$ and $\sigma$ at $(p,n)\in\{(2,2),(2,3),(3,2),(3,3),(5,2)\}$, in both rings: $3{,}435{,}322$ incidences per ring, no mismatch.</p>
<p>So every statement about the pair is a statement about one family of incidence systems in which $\gamma$ is switched on or off. The direction classes over $\alpha$ are indexed by $\beta\in\mathbb{F}_p^n/\langle\alpha\rangle$, and the trace of a chosen line over $\{a,a+\sigma\alpha\}$ differs between the two rings only by the shift $\gamma(a,\sigma\alpha)$. The lemma is stated and certified at $\ell=2$. At $\ell\ge3$ the carry is the full tower of Witt addition polynomials, and the length-3 statements below keep their direct form until the general law is written and checked.</p>
<div class="well"><table>
<tr><th>Earlier</th><th>Now</th></tr>
<tr><td>$k(R,n)$</td><td>$\kappa_n(R)$</td></tr>
<tr><td>$\mathbb{Z}/p^k$, $\mathbb{F}_p[t]/t^k$</td><td>$A_{p,\ell}$, $A^\flat_{p,\ell}$</td></tr>
<tr><td>length $k$, recursion $a_k$, design dimension $k$</td><td>$\ell$, $a_\ell$, $d$</td></tr>
<tr><td>$\pi^{-1}(0)$</td><td>$\rho^{-1}(0)$</td></tr>
<tr><td>$\varepsilon$ in $\mathbb{Z}/4$</td><td>$\pi$ with Teichmüller digits</td></tr>
<tr><td>$\kappa(a,\alpha)=a\wedge\alpha$</td><td>$\gamma(a,\alpha)$</td></tr>
<tr><td>$c_a(\sigma)$ in Proposition 3</td><td>eliminated (coordinate artifact, §3)</td></tr>
<tr><td>line variable $y_{d,\ell}$, transversal $\ell^*$</td><td>$y_{d,L}$, $L^*$</td></tr>
<tr><td>profile $16+6+6+6$</td><td>$\phi_K=(16,6^{\times3})$</td></tr>
<tr><td><code>Z4 D2 Z8 T8 Z9 D3 Z25 D5</code></td><td><code>W2^2 T2^2 W2^3 T2^3 W3^2 T3^2 W5^2 T5^2</code></td></tr>
</table></div>

'''
rep('<h2><span class="sec">§1</span>What changed: the solver</h2>', notation + '<h2><span class="sec">§1</span>What changed: the solver</h2>')
rep(r'The earlier campaign posed $k(R,n)$', r'The earlier campaign posed $\kappa_n(R)$')
rep(r'For a chain ring of length $k$ there are $k+1$ such orbits', r'For a chain ring of length $\ell$ there are $\ell+1$ such orbits')
rep(r'$k(\mathbb{Z}/4,3)=k(\mathbb{F}_2[t]/(t^2),3)=22$', r'$\kappa_3(A_{2,2})=\kappa_3(A^\flat_{2,2})=22$')
rep(r'$\{0,\varepsilon\}^2$-intercept', r'$\{0,\pi\}^2$-intercept')

prop23 = r'''<div class="thm"><p><span class="label new">proved</span><span class="label cert">certified</span><b>Proposition 2 (one full fibre).</b> For $R=A_{2,2}$ or $A^\flat_{2,2}$ and every $n\ge 1$, $\kappa_n(R)\le 3\cdot 2^n-2$. Equality holds for $n=2,3,4$ (Theorems 1 and 5).</p></div>
<p><i>Proof.</i> Take $K\supseteq\rho^{-1}(0)$, the full fibre of $2^n$ points over the origin. Fix $\alpha\ne0$. By Lemma 0 with $a=0$, the line through $\pi[b]$ in direction $[\alpha]+\pi[\beta]$ has trace $b+\langle\alpha\rangle$ over $0$, which lies in the full fibre, and trace $b+\beta+\gamma(0,\alpha)+\langle\alpha\rangle=b+\beta+\langle\alpha\rangle$ over $\alpha$. The choice $b=\beta$ puts the trace of every lift of $\alpha$ on the single coset $\langle\alpha\rangle$. Hence $|K|=2^n+2(2^n-1)$. The carry never enters, because every chosen line starts at the base point $0$ and $\gamma(0,\cdot)=0$; this is the precise sense in which the bound does not see the tilt. <code>checks.py</code> (N4) builds the set in Teichmüller coordinates and verifies it by brute force for $n=2,3,4,5$ in both rings, with sizes $10,22,46,94$. $\square$</p>
<p><span class="label cert">settled</span>The earlier question whether $\kappa_4(A_{2,2})=46$ is closed by Theorem 5 (§9). Every extremal set found at $n=2,3$ has profile $\phi_K=(2^n,2^{\times(2^n-1)})$, one full fibre and one tangent line over every other base point, and the independent $n=4$ witness of §9 has the same profile. The length-3 analogue also has a single full fibre: both $34$-point sets over $A_{2,3}$ and $A^\flat_{2,3}$ have profile $(16,6^{\times3})$ over $\mathbb{F}_2^2$. This fits the recursion $a_\ell=4^{\ell-1}+3(a_{\ell-1}-4^{\ell-2})$ through $a_1=3$, $a_2=10$, $a_3=34$, which predicts $a_4=118$ for $A_{2,4}=\mathbb{Z}/16$. <span class="label open">open</span>That prediction is untested; the first SAT attempt hit its time limit.</p>

<div class="thm"><p><span class="label new">proved</span><span class="label cert">certified</span><b>Proposition 3 (pencil and transversal).</b> Let $p$ be odd and $M(p)=\min_{g:\mathbb{F}_p\to\mathbb{F}_p}\sum_{\sigma\in\mathbb{F}_p\setminus\{0,1\}}\big|\{g(\delta)+\sigma\delta:\delta\in\mathbb{F}_p\}\big|$. Then for both $R=A_{p,2}$ and $R=A^\flat_{p,2}$, $\kappa_2(R)\le(p+1)p^2+p^2M(p)$. Exhaustive search gives $M(3)=1$, $M(5)=8$, $M(7)=19$, so the bound is $45$, $350$ and $1323$, and it is tight at $p=3$.</p></div>
<p><i>Proof.</i> In the base plane take the transversal $L^*=\{x=1\}$ and the $p$ lines through $O$ of slopes $a\in\mathbb{F}_p$. Put full fibres over $O$ and over the $p$ points of $L^*$. Every lift of the direction $(0,1)$ has a line inside the full fibres over $L^*$. For the lift $v=([1],[a]+\pi[\delta])$ use the line through $(0,\pi[g(\delta)])$. By Lemma 0 with base point $0$, its trace over $(\sigma,a\sigma)$ has second-coordinate offset $g(\delta)+\sigma\delta$, with no carry, in both rings. So at each of the $p-2$ non-full points of a pencil line the number of distinct tangent lines is $|\{g(\delta)+\sigma\delta\}|$. Each such point lies on exactly one chosen base line, so no cross-direction interaction occurs. The total is $(p+1)p^2+p\cdot p\cdot M(p)$. <code>checks.py</code> (N4) builds and verifies all six sets ($p=3,5,7$, both rings) by brute force, with the minimisers $g$ recorded in <code>results/notation_checks.json</code>. $\square$</p>
<p><span class="label cert">certified</span><b>Remark (the vanished carry).</b> The October proof wrote the lift as $(1,a+\varepsilon\delta)$ with $a$ an integer representative and carried a term $c_a(\sigma)$, described as the Witt carry of $[\sigma][a]$. That term is not a carry. The construction's lines start at $x=0$, where $\gamma(0,\cdot)=0$, and the Teichmüller product $[\sigma][a]=[\sigma a]$ is exact. The integer $a$ has second digit $e(a)=(a-[a])/p$, nonzero for some $a$ at every odd $p$ tested ($e(a)\in\{0,1\}$ at $p=3$, $\{0,1,2,4\}$ at $p=5$, $\{0,1,3,5\}$ at $p=7$). Its trace offset is therefore $g(\delta)+\sigma(\delta+e(a))$, a relabelling $\delta\mapsto\delta+e(a)$ of the lifts over $a$ that leaves every count in the proof unchanged. <code>checks.py</code> (N3) verifies both offsets for all $a,\delta,g$ and $\sigma\notin\{0,1\}$ at $p=3,5,7$. The only genuine carry in Propositions 2 and 3 is therefore zero, and $\Delta=0$ for these two constructions is structural rather than a cancellation.</p>
<p>At $p=3$ the construction is exactly the extremal configuration: profile $\phi_K=(9^{\times4},3^{\times3})$, three base lines through a full fibre at $O$ and a fully lifted transversal. It is the configuration the v4 master pins as optimal. At $p\ge 5$ it is not optimal, as §4 shows.</p>

'''
sub_between('<div class="thm"><p><span class="label new">proved</span><span class="label cert">certified</span><b>Proposition 2', '<h2><span class="sec">§4</span>', prop23)

rep(r'$\mathbb{F}_5[t]/t^2$ best (360 s)', r'$A^\flat_{5,2}$ best (360 s)')
rep(r'$\mathbb{Z}/25$ best (360 s)', r'$A_{5,2}$ best (360 s)')
rep(r'gives 310 for the dual numbers and 310 for $\mathbb{Z}/25$', r'gives 310 for $A^\flat_{5,2}$ and 310 for $A_{5,2}$')
rep(r'concentrated sets of size 309 in $\mathbb{F}_5[t]/(t^2)$ and 310 in $\mathbb{Z}/25$', r'concentrated sets of size 309 in $A^\flat_{5,2}$ and 310 in $A_{5,2}$')

rep(r'$(\mathbb{Z}/4)^n$ and $(\mathbb{F}_2[t]/t^2)^n$', r'$A_{2,2}^n$ and $(A^\flat_{2,2})^n$')
rep(r'$|AGL_3(\mathbb{Z}/4)|', r'$|AGL_3(A_{2,2})|')
rep(r"the carry $a\wedge\alpha$ through the class of $b''-b-\kappa(a,\alpha)$ modulo $\langle\alpha\rangle$",
    r"the carry through the class of $b''-b-\gamma(a,\alpha)$ modulo $\langle\alpha\rangle$ (Lemma 0 with $\sigma=1$)")

rep(r'over $(\mathbb{Z}/4)^3$, $(\mathbb{F}_2[t]/t^2)^3$, $(\mathbb{Z}/8)^2$ and $(\mathbb{F}_2[t]/t^3)^2$', r'over $A_{2,2}^3$, $(A^\flat_{2,2})^3$, $A_{2,3}^2$ and $(A^\flat_{2,3})^2$')
rep(r'The conjecture these data support is $k(\mathbb{Z}/p^k,n)=k(\mathbb{F}_p[t]/t^k,n)$ for all $p,k,n$.', r'The conjecture these data support is $\Delta_n(p,\ell)=0$ for all $p,\ell,n$.')
rep('the carry cocycle restricted to a concentrated configuration', r'the carry cocycle $\gamma$ restricted to a concentrated configuration')

rep(r"Proposition 2's bound $k(R,n)\le 3\cdot2^n-2$ for $R=\mathbb{Z}/4,\ \mathbb{F}_2[t]/t^2$", r"Proposition 2's bound $\kappa_n(R)\le 3\cdot2^n-2$ for $R=A_{2,2},\,A^\flat_{2,2}$")
rep(r'$K_x=K\cap\pi^{-1}(x)$', r'$K_x=K\cap\rho^{-1}(x)$')
rep(r'$\dim V_a=k$', r'$\dim V_a=d$')
rep(r'$|F|2^k$', r'$|F|2^d$')
rep(r'$|F|\approx2^{n+1-k}$ with $k\approx(n+1)/2$', r'$|F|\approx2^{n+1-d}$ with $d\approx(n+1)/2$')
rep(r'which agrees with $k=22$. At $n=5$ ($k=3$,', r'which agrees with $\kappa_3=22$. At $n=5$ ($d=3$,')

rep(r'$k(\mathbb{Z}/4,4)=k(\mathbb{F}_2[t]/(t^2),4)=46=3\cdot2^4-2$. The family law $k=3\cdot2^n-2$',
    r'$\kappa_4(A_{2,2})=\kappa_4(A^\flat_{2,2})=46=3\cdot2^4-2$. The family law $\kappa_n=3\cdot2^n-2$')
rep(r'also of profile $16+2\times15$', r'also of profile $\phi_K=(16,2^{\times15})$')
rep(r'$R\in\{\mathbb{Z}/4,\mathbb{F}_2[t]/t^2\}$', r'$R\in\{A_{2,2},A^\flat_{2,2}\}$')
rep(r"it realises the class $b''-b-\kappa(a,\alpha)$", r"it realises the class $b''-b-\gamma(a,\alpha)$ (Lemma 0)")
rep(r'with $\kappa=a\wedge\alpha$ and $\kappa=0$ respectively', r'with $\gamma(a,\alpha)=a\wedge\alpha$ and $\gamma=0$ respectively')
rep(r'this proves $k(R,4)\ge46$', r'this proves $\kappa_4(R)\ge46$')
rep(r'$k(\mathbb{Z}/4,n)=k(\mathbb{F}_2[t]/t^2,n)=3\cdot2^n-2$', r'$\kappa_n(A_{2,2})=\kappa_n(A^\flat_{2,2})=3\cdot2^n-2$')

rep(r'<code>ksat.py CODE n br</code> computes an exact minimum with the branch table (rings <code>Z4 D2 Z8 T8 Z9 D3 Z16 T16 Z25 D5 Z27 T27 Z49 D7</code>).',
    r'<code>ksat.py CODE n br</code> computes an exact minimum with the branch table (legacy codes <code>Z4 D2 Z8 T8 Z9 D3 Z16 T16 Z25 D5 Z27 T27 Z49 D7</code>; <code>tilt.ring()</code> accepts these and maps them to <code>W2^2 T2^2 W2^3 T2^3 W3^2 T3^2 W2^4 T2^4 W5^2 T5^2 W3^3 T3^3 W7^2 T7^2</code>). The notation reform adds <code>tilt.py</code> (both rings in Teichmüller coordinates with the cocycle $\gamma$), <code>checks.py</code> (certificates N1–N4 of §0′ and §3, about one minute) and <code>kappa.py</code>, which recomputes $\kappa_2$ for the pairs $(2,2)$, $(2,3)$, $(3,2)$ in the new codes and writes $\Delta_2=0$ to <code>results/kappa2.json</code>. Its lower bounds are solver verdicts; the DRUP-checked certificates remain those in <code>cert_n3/</code> and <code>sat/counting/</code>.')

left = [p for p in [r'k(R', r'k(\mathbb', r'\kappa(a', r'\pi^{-1}', r'/t^', r'/(t^', r'\varepsilon b', 'a_k', 'dual numbers'] if p in s]
print('leftovers:', left)
open('kakeya_across_the_tilt.html', 'w').write(s)
