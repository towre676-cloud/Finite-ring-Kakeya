# Notation for the Kakeya tilt comparison (reform of 1 November 2026)

This file fixes the notation used in `kakeya_across_the_tilt.html`, `tilt.py`, `checks.py` and `kappa.py`. It replaces the mixed conventions of the October packages, in which the letter $k$ denoted both the Kakeya number and the ring length, $\pi$ denoted the reduction map, $\varepsilon$ was written inside $\mathbb{Z}/4$, and two different symbols ($\kappa(a,\alpha)$ and $c_a(\sigma)$) denoted what is shown below to be one cocycle plus one coordinate artifact.

## The pair of rings

For a prime $p$ and a length $\ell\ge1$ write $A_{p,\ell}=W_\ell(\mathbb{F}_p)=\mathbb{Z}/p^\ell$ (mixed characteristic) and $A_{p,\ell}^\flat=\mathbb{F}_p[t]/(t^\ell)$ (equal characteristic). These are the two length-$\ell$ quotients of the complete discrete valuation rings with residue field $\mathbb{F}_p$, namely $\mathbb{Z}_p$ and $\mathbb{F}_p[[t]]$. The subscript $p$ is dropped when fixed. The symbol $\flat$ is a mnemonic for the program's "tilt at finite level"; it is not Scholze's tilt, since $\mathbb{Z}_p$ is not perfectoid. The letter $R$ denotes either member of a pair when a statement holds for both.

The uniformiser is $\pi$ ($\pi=p$, respectively $\pi=t$). The map $\rho:R^n\to\mathbb{F}_p^n$ is reduction modulo $\pi$.

## Teichmüller digits and the carry cocycle

The Teichmüller lift $[\cdot]:\mathbb{F}_p\to R$ is $[a]=\tilde a^{\,p^{\ell-1}}$ in $A_{p,\ell}$ and the constant lift in $A^\flat_{p,\ell}$. Every $x\in R$ has a unique expansion $x=\sum_{i<\ell}\pi^i[x_i]$ with digits $x_i\in\mathbb{F}_p$, and vectors are expanded coordinatewise. The Teichmüller lift is multiplicative on both sides. The two rings differ only in addition, which at length 2 is recorded by the carry cocycle

$$[a]+[b]=[a+b]+\pi[\gamma(a,b)]\pmod{\pi^2},\qquad \gamma(a,b)=\frac{a^p+b^p-(a+b)^p}{p}\bmod p\ \text{ on }A_{p,\ell},\qquad \gamma\equiv0\text{ on }A^\flat_{p,\ell}.$$

At $p=2$, $\gamma(a,b)=ab$, which is coordinatewise $a\wedge b$ on $\mathbb{F}_2^n$ (the old $\kappa(a,\alpha)$).

## Fibre-trace law (length 2)

Let $x=[a]+\pi[b]$ and $v=[\alpha]+\pi[\beta]$ with $\alpha\ne0$. The line $\{x+sv\}$ lies over the base line $a+\mathbb{F}_p\alpha$. Its digit set over the base point $a+\sigma\alpha$ is the coset

$$b+\sigma\beta+\gamma(a,\sigma\alpha)+\langle\alpha\rangle .$$

Proof: write $s=[\sigma]+\pi[r]$. Multiplicativity gives $[\sigma][\alpha]=[\sigma\alpha]$, and the single addition $[a]+[\sigma\alpha]$ contributes $\gamma$. This is certified exhaustively by `checks.py` (N2) for $(p,n)\in\{(2,2),(2,3),(3,2),(3,3),(5,2)\}$ in both rings.

## Quantities

The Kakeya number $\kappa_n(R)$ is the least $|K|$ over Kakeya sets $K\subseteq R^n$, that is, sets containing a full line for every direction class $[v]\in\mathbb{P}^{n-1}(R)$ (unimodular $v$ modulo $R^\times$). The tilt defect is $\Delta_n(p,\ell)=\kappa_n(A_{p,\ell})-\kappa_n(A^\flat_{p,\ell})$; the tilt conjecture is $\Delta\equiv0$. The fibre profile is $\phi_K(a)=|K\cap\rho^{-1}(a)|$, written as a multiset with multiplicities $(16,6^{\times3})$; plain exponents are avoided because fibre sizes are powers of $p$.

## What changed, and one substantive consequence

| Old | New |
|---|---|
| $k(R,n)$ | $\kappa_n(R)$ |
| $\mathbb{Z}/p^k$, $\mathbb{F}_p[t]/t^k$, $\mathbb{F}_p[t]/(t^k)$ | $A_{p,\ell}$, $A^\flat_{p,\ell}$ |
| length $k$; recursion $a_k$ | length $\ell$; $a_\ell$ |
| design dimension $k$ (§8) | $d$ |
| $\pi^{-1}(0)$ | $\rho^{-1}(0)$ |
| $\varepsilon$ in $\mathbb{Z}/4$ | $\pi$ with Teichmüller digits |
| $\kappa(a,\alpha)=a\wedge\alpha$ | $\gamma(a,\alpha)$ |
| $c_a(\sigma)$ (Prop. 3) | eliminated |
| profile $16+6+6+6$ | $\phi_K=(16,6^{\times3})$ |
| codes `Z4 D2 Z8 T8 Z9 D3 Z25 D5` | `W2^2 T2^2 W2^3 T2^3 W3^2 T3^2 W5^2 T5^2` |

The term $c_a(\sigma)$ in Proposition 3 was described as the Witt carry of $[\sigma][a]$. It is not a carry. The construction's lines pass through $x=0$, where $\gamma(0,\cdot)=0$. The offset arises only because the slope $a+\varepsilon\delta$ was written with the integer representative $a$, whose second Teichmüller digit is $e(a)=(a-[a])/p$. That makes the trace offset $g(\delta)+\sigma(\delta+e(a))$, a reparametrisation $\delta\mapsto\delta+e(a)$ of the lift index. In Teichmüller slopes $[a]+\pi[\delta]$ the offset is exactly $g(\delta)+\sigma\delta$ in both rings. `checks.py` (N3) verifies both statements for $p=3,5,7$.

Scope: the fibre-trace law is stated and certified at $\ell=2$ only. At $\ell\ge3$ the carry is the full tower of Witt addition polynomials, and the length-3 statements of the monograph keep their direct form until the general law is written and checked.
