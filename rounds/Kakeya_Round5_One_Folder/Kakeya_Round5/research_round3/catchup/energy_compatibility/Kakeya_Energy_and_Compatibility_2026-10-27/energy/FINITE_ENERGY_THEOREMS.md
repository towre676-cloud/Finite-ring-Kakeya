# Exact finite energy and alignment certificates

Prepared 27 October 2026. These are finite combinatorial statements motivated by the idea of preserving global compatibility in an energy argument. They are proved below and checked by `finite_energy.py`. They do **not** assert that the Euclidean auxiliary PDE transfers to finite rings, and they do **not** close an unrestricted dimension-five maximum-fibre case.

The inherited work already contains the directional pair-capacity energy, its mismatch identity, exact individual quotient-sumset bounds, and several shape-sensitive bounds. The new layer here concerns **overlap between different base edges** and the compatibility of their **internal translation phases across different directions**.

## 1. Exact coverage objects and the translation warning

Let `V=F2^n`, `d!=0`, and `Q_d=V/<d>`, with `q=2^(n-1)`. For actual internal fibres `A_x`, put

\[
P_x(d)=\{u+\langle d\rangle:\{u,u+d\}\subseteq A_x\}.
\]

For each unordered base edge `e={x,x+d}`, define its actually covered lift classes

\[
S_e=P_x(d)+P_{x+d}(d)+c_R(x,d),
\]

where `c_dual=0` and `c_Z4=x&d` modulo `d`, using the binary section. Exact Kakeya coverage above `d` is

\[
\bigcup_e S_e=Q_d.
\tag{1}
\]

If a canonical fibre shape is translated by `t_x`, the corresponding edge set is translated by `t_x+t_{x+d}`. Thus its cardinality is unchanged, but its overlaps with other edge sets need not be unchanged. This is why independent internal-translation gauges, valid for the inherited individual-sumset relaxation, cannot simply be retained after adding the following exact alignment constraints. One must restore translation variables, or prove a bound valid for every choice of those variables.

## 2. Cross-edge collision budget

Discard empty edge sets and let their number be `L`. Define

\[
\nu(b)=\sum_e1_{S_e}(b),\qquad
T=\sum_e|S_e|,\qquad
J=\sum_{e<f}|S_e\cap S_f|.
\]

### Theorem 1: collision correction

If (1) holds, then

\[
2J\le L(T-q),\qquad\text{equivalently}\qquad
T-\frac{2J}{L}\ge q.
\tag{2}
\]

More generally, `L` may be replaced by any proven uniform upper bound on `nu(b)`.

**Proof.** Coverage gives `1<=nu(b)<=L` for every `b`. Hence

\[
\nu(b)(\nu(b)-1)\le L(\nu(b)-1).
\]

Sum over the quotient and use `sum nu=T` and `sum nu(nu-1)=2J`. QED.

In particular, when `T=q`, coverage requires all the nonempty edge sets to be pairwise disjoint. This is information that summing exact individual sumset cardinalities does not retain.

The inequality is a necessary condition, not an equivalence. It can be weak if `L` greatly exceeds the actual maximum overlap. One can strengthen it by proving a smaller overlap ceiling or restricting to an appropriate subfamily after accounting for the other covered classes.

## 2a. A bound valid for every internal translation

For canonical output sets `S_e`, define the unavoidable overlap

\[
m(e,f)=\min_{h\in Q_d}|S_e\cap(S_f+h)|.
\tag{2a}
\]

This quantity is unchanged by independent translations of either set. In a sixteen-point quotient it is certified by checking precisely sixteen intersection counts.

### Theorem 1B: tree overlap bound

For any tree `T_tree` on the nonempty output sets, and any independent translations `h_e`,

\[
\left|\bigcup_e(S_e+h_e)\right|
\le\sum_e|S_e|-\sum_{\{e,f\}\in T_{\rm tree}}m(e,f).
\tag{2b}
\]

Taking a maximum spanning tree gives the strongest bound of this form. Any independently verified tree certificate is valid; correctness does not require trusting that the tree optimizer found the maximum.

**Proof.** Root the tree and add sets in an order in which every parent precedes its children. When adding a child, its intersection with the previously added union contains its intersection with its parent. The latter has size at least `m(parent,child)`, whatever the two translations. Summing the increments proves (2b). Equivalently, at each covered quotient point the selected tree edges induced by the sets containing it form a forest, so its number of vertices minus its number of induced tree edges is at least one. QED.

Thus exact coverage necessarily satisfies

\[
\sum_e|S_e|-\operatorname{MaxTree}(m)\ge q.
\tag{2c}
\]

This cut **does preserve the existing independent internal-translation gauges**. The ring carries are themselves translations and are already covered by the universal quantifier in (2b). Other active edges may be included in the tree or left outside it; a bound for a selected subtree can be subtracted from the sum of all edge cardinalities.

### Dimension-five example with maximum fibre sixteen

Take `d=16` and

\[
S=\{0,1,2,3,4,6,8,9\}\subseteq Q_d.
\]

Use two base edges `{0,16}` and `{1,17}`, with pair-set factors `{0},S` on each. Replacing every quotient point by its `d`-coset realizes fibre weights `2,16,2,16`. Each individual edge has exact sumset cardinality eight. However,

\[
\min_h|S\cap(S+h)|=2,
\qquad
\max_{h,k}|(S+h)\cup(S+k)|=14.
\]

Therefore no translations of these fibres cover all sixteen lifts in this direction, in either ring. Summing their exact individual cardinalities gives sixteen and misses the obstruction. The tree certificate consists of one edge of weight two, giving the uniform upper bound fourteen.

All 256 pairs of output translations are checked. An attaining translation is also checked directly with coordinate ring arithmetic for both rings, yielding fourteen covered lifts. This fixture is a local obstruction and does not constitute a new full maximum-sixteen theorem. The relevant eight-point shift-intersection fact also appears in the inherited quotient atlas; the additional use here is to enforce overlap **between different base edges**, rather than within a single edge sumset.

The portable functions `unavoidable_overlap`, `tree_overlap_bound`, and `verify_tree_overlap_certificate` are in `finite_energy.py`. The verifier recomputes the shift intersections by point membership, checks that the supplied graph is a tree by union-find, and checks the final integer bound. It does not trust the spanning-tree optimizer.

## 3. Exact Fourier positivity, and its relation to hyperplane cuts

Let `Q` be any binary vector space of size `q` and let `nu:Q->Z_{>=0}` be a coverage multiplicity. For each character `chi`, write

\[
\widehat\nu(\chi)=\sum_{b\in Q}\nu(b)\chi(b).
\]

Index a real matrix by all the characters and define

\[
M_{\chi,\psi}=\widehat\nu(\chi\psi)-q1_{\chi=\psi}.
\tag{3}
\]

### Theorem 2: exact finite positivity certificate

The matrix `M` is positive semidefinite if and only if `nu(b)>=1` for every `b`.

**Proof.** If `H_{chi,b}=chi(b)` is the Walsh matrix, orthogonality gives `HH^T=qI`, and

\[
M=H\operatorname{diag}(\nu(b)-1)H^T.
\]

Congruence by an invertible real matrix preserves positive semidefiniteness. In fact the eigenvalues are precisely `q(nu(b)-1)`. QED.

Every diagonal entry is `T-q`, so its two-by-two principal minors imply

\[
|\widehat\nu(\chi)|\le T-q\qquad(\chi\ne1).
\tag{4}
\]

These are the signed halfspace-capacity conditions: both halves of the quotient must receive at least `q/2` incidences. The full matrix retains simultaneous constraints that its two-by-two minors can miss. Formula (3) is an exact reformulation of coverage, not by itself a cheaper algorithm or a new lower bound. The useful relaxations are selected small minors, collision consequences, and parity identities with independently checkable certificates.

The same construction applies to representation multiplicity `r(b)=sum_e (1_Px*1_Py)(b+c_R)` instead of covered-set multiplicity. Its support is the same union. The covered-set version separates internal collisions within an edge, already treated by the inherited sumset atlas, from cross-edge overlap, which is the additional issue here.

### A dimension-five example beyond every one-character cut

Take `d=16`, so quotient representatives are `Q={0,...,15}`, viewed as `F2^3 x F2`. On two base edges choose pair-set factors

\[
P_0=\{0,8\},\quad P_{16}=\{1,2,3,4,5,6,7\},
\]
\[
P_1=\{0,8\},\quad P_{17}=\{1,2,3\}.
\]

Replace each quotient point by its entire two-point `d`-coset to realize these as actual internal fibres. Their weights are `4,14,4,6`, so the maximum fibre is fourteen. Both products are injective, and their covered sets are

\[
S_1=(\mathbb F_2^3\setminus\{0\})\times\mathbb F_2,
\qquad
S_2=(\{0,1,2,3\}\setminus\{0\})\times\mathbb F_2.
\]

Thus `|S1|=14`, `|S2|=6`, `T=20`, `J=6`, `L=2`, but the union has only fourteen classes. All fifteen inequalities (4) hold: each nontrivial Fourier coefficient has absolute value at most four, exactly the available surplus `T-q=4`. Nevertheless (2) fails, since

\[
2J=12>8=L(T-q).
\]

The exact slack matrix has eigenvalues `-16` twice, `0` eight times, and `16` six times. Its failure is therefore not visible in any two-by-two principal minor. The point-level ring-arithmetic checker independently finds fourteen covered lifts for both rings in this direction.

This is a fixed-translation local regression. Translating its fibres can change its coverage. It is **not** a full Kakeya candidate or an exclusion of every translation of these shapes. The next theorem provides an obstruction that holds for every translation.

## 4. A three-matching translation-parity theorem

Fix four base vertices. Suppose three residue directions give the three perfect matchings of those vertices. Assume, in each of the three directions, that:

1. These two matching edges are the only edges contributing covered classes.
2. Each edge covers exactly one affine hyperplane of `Q_d`.
3. The two hyperplanes have the same nonzero normal `ell_d`, viewed as a linear functional on `V` with `ell_d(d)=0`.

For canonical internal fibre shapes, include the ring carry in the two hyperplane phases `alpha_{d,0}, alpha_{d,1}`. Translate the four fibres independently by `t_x`, and write `T0=xor_x t_x`.

### Theorem 3: exact parity certificate

Coverage in direction `d` is equivalent to

\[
\ell_d(T_0)=1+\alpha_{d,0}+\alpha_{d,1}.
\tag{5}
\]

Consequently, any XOR combination of these equations whose left side is zero and right side is one excludes **every** choice of internal translations.

**Proof.** A hyperplane coset of phase `alpha` translated by `t_x+t_y` has phase `alpha+ell_d(t_x+t_y)`. Two hyperplane cosets with the same nonzero normal cover the quotient exactly when their phases differ. The matching uses each of the four vertices once, so the sum of the two translated phases equals `alpha_{d,0}+alpha_{d,1}+ell_d(T0)`. This proves (5); XOR inconsistency proves the final assertion. QED.

This is an ordinary finite linear certificate, not a conjectural analogue of a differential conservation law. It enforces that phases in different directions come from the **same** internal translations.

### A genuine dimension-five forbidden block with twelve-point fibres

Write the internal space as `V=U+W`, where `U={0,1,2,3}` and `W={0,4,8,...,28}`. Use the four base vertices `U`. Choose the following distinct two-dimensional subspaces of `W`:

\[
H_0=\{0,8,16,24\},\quad H_1=\{0,4,16,20\},
\]
\[
H_2=\{0,12,16,28\},\quad H_3=\{0,4,8,12\}.
\]

Set

\[
A_x=(U\setminus\{0\})+H_x\qquad(x\in U).
\tag{6}
\]

Every fibre has twelve points. Any two of the distinct `H_x` sum to all of `W`. Therefore, for each `d=1,2,3`, each of its two base edges has an eight-point quotient sumset: an affine hyperplane in the sixteen-point quotient. The three normals are, respectively, `ell_2`, `ell_1`, and `ell_1+ell_2`, where `ell_i` reads the corresponding low coordinate.

The four `H_x` also have union `W`, avoiding an unnecessary absent internal direction in this regression fixture. This does not establish feasibility of a full extension to all residue directions.

For the dual-number ring the canonical phases are zero. Thus (5) requires

\[
\ell_2(T_0)=1,\quad \ell_1(T_0)=1,\quad
(\ell_1+\ell_2)(T_0)=1.
\]

Their XOR is `0=1`. **No translations of these four twelve-point fibres can cover all lifts in the three directions.** Each direction separately is satisfiable, and every individual exact-sumset cardinality bound is saturated at sixteen. The obstruction is their joint alignment.

The same conclusion persists if other fibres are added but produce no additional base edges in these three directions. For example, one may add at most one active base vertex in each other `U`-coset. This is a conditional forbidden-block theorem, not a statement that all remaining dimension-five cases have this structure.

For `Z/4`, the matching carry phases are `0,0,1` in directions `1,2,3`. The system becomes

\[
\ell_2(T_0)=1,\quad \ell_1(T_0)=1,\quad
(\ell_1+\ell_2)(T_0)=0,
\]

which is consistent. Shifts `(t0,t1,t2,t3)=(3,0,0,0)` cover all sixteen lifts in each of those three directions. Direct arithmetic modulo four verifies this. Thus dropping the carry would create a false exclusion for `Z/4`.

The verifier checks all `4^4=256` assignments of the effective low-coordinate shifts: none succeeds for the dual ring; sixty-four succeed for `Z/4`. High-coordinate translations do not affect these quotient sumsets, because each is a full `W`-coset. The 256 checks therefore represent all `32^4` internal translation choices for this block. This remains only a three-direction local construction, not a full forty-eight-point Kakeya set.

## 5. A limitation of a tempting PSD relaxation

Suppose canonical fibre shapes are fixed but their translations are unknown. For one character `ell`, set `sigma_x=(-1)^ell(t_x)`. Each nontrivial Fourier coverage coefficient is a sum of terms

\[
c_{xy}\sigma_x\sigma_y\qquad(x\ne y),
\]

with known real coefficients from the shapes and carries. The usual rank-one relaxation replaces `sigma sigma^T` by an arbitrary matrix `X>=0` with diagonal one.

### Proposition: the uncoupled character PSD relaxation is vacuous here

If the only additional constraints are the single-character bounds `|sum c_xy X_xy|<=surplus`, with nonnegative surplus, then `X=I` satisfies all of them.

**Proof.** Every term uses a genuine base edge, hence an off-diagonal entry. All these entries vanish in `I`, and `I` is PSD with unit diagonal. QED.

Therefore adding generic positivity at this level cannot improve a cardinality-feasible instance. One must retain Boolean/rank constraints, joint character identities such as `sigma_(ell+m)=sigma_ell sigma_m`, selected higher moments, or exact phase equations such as Theorem 3. This is a concrete obstacle to a naive use of the continuous proof's word "positivity".

## 6. Verification and next use

Run:

```text
python finite_energy.py
```

The receipt records:

- The 94-point full-hub star satisfies exact coverage and saturates the collision/PSD slack for all 31 nonzero residue directions in both rings: 62 positive-control rows.
- The fourteen-point-union regression passes every one-character cut and fails the collision budget by four integer units.
- The maximum-sixteen two-edge fixture has a verified tree-overlap bound of fourteen for every internal translation, checked against all 256 output-translation pairs and direct ring arithmetic.
- The twelve-point-fibre block has a three-row XOR contradiction for the dual ring and a directly checked carry-corrected completion for `Z/4`.
- Both the collision inequality and the independently certified tree-overlap bound are checked on all 4,096 triples of subsets of a four-point quotient, including 2,401 full covers.

The accompanying `../compute/` directory implements a translation-completion layer for fixed shape assignments: it retains one vector offset per fibre, computes the canonical edge sumsets, and encodes exact coverage. Its saved short refutations independently corroborate the parity and forced-overlap obstructions. The parity certificate can also be verified directly by XORing its bit rows. A solver using only pair counts or per-edge sumset cardinalities cannot discover the cross-direction obstruction, regardless of its search effort.

No additional full maximum-fibre case is declared excluded by this note.
