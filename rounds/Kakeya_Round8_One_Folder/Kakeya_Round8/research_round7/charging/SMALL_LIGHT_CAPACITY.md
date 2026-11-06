# Three small pair sets give elementary capacity bounds

Let $P,Q\subseteq\mathbb F_2^4$, with $|P|=p$ and $|Q|=q$.
For the light pair counts used by every one of the 3,006 accepted integer
certificates, the following bounds suffice:

$$
|P+Q|\le B(p,q),\qquad
B(p,0)=0,\quad B(p,1)=p,\quad
B(p,2)=\min(2p,16),\quad
B(p,3)=\min(3p,p+8,16).
$$

The first three statements follow from counting translates and the size
of the ambient group. For the last, translate the three-point set $Q$
into its two-dimensional direction space $W$. The space $\mathbb F_2^4$
has four cosets of $W$. In each such coset let $B$ be the part of $P$
lying there, and write $r=|B|$.

If $r=0$, that coset contributes no sum. If $r=1$, it contributes exactly
three sums. If $r\ge2$, two distinct translates of a three-point subset
of a four-point plane have different missing points and together fill
the plane. Thus its contribution is exactly four. In particular, the
contribution of a nonempty coset is at most $r+2$. Summing over at most
four nonempty cosets gives $|P+Q|\le p+8$. The other two bounds, $3p$
and $16$, hold by ordinary product and ambient-size counting.

These bounds are sharp: for $q=3$ and $p\le4$, place one point in each
of $p$ distinct cosets; for $4\le p\le8$, put a first point in all four
cosets and then a second point in $p-4$ of them; for $p\ge8$, the four
cosets can all be filled by sums. Sharpness is not needed for exclusion.

## Consequence for the integer certificates

All 3,006 accepted profile certificates use a light weight ceiling
$4\le\ell\le7$, hence a light pair count $q\le3$. The independent
verifier computes every price coefficient directly from $B(p,q)$.
It also checks agreement with the older table, as a provenance check.
The older quotient-sumset census is therefore **not a mathematical
premise of these new profile exclusions**. The full fibre-spectrum
census remains a premise for the weight-dependent maxima $G_w$.

The heavy/light charging proof applies unchanged: replace its table
$M(p,q)$ by the elementary bound $B(p,q)$. Define

$$
g(p)=\max\bigl(0,\max_{1\le q\le\lfloor\ell/2\rfloor}
       [2B(p,q)-u q]\bigr),\qquad u\ge\lfloor\ell/2\rfloor.
$$

Every displayed certificate then verifies a strict integer inequality
between the required capacity and an upper bound on all available
charges. Ring carries translate quotient sumsets and leave their sizes
unchanged, so this proof applies to both rings.
