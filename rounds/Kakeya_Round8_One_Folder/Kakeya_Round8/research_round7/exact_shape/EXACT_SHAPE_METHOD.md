# Actual fibre shapes with exact edge sumset cardinalities

## What the new formulation does

The earlier support formulas selected a realizable pair-count histogram
and imposed some consistency on its direction labels. This formulation
instead gives every residue fibre an **actual subset of binary five-space**.
It also computes the **actual cardinality of every quotient sumset** used
by an edge. Both changes are encoded by elementary Boolean gates.

It remains a necessary-condition relaxation of Kakeya: for each residue
direction it adds the cardinalities supplied by different support edges.
That sum can overcount labels shared by several edges. Therefore a
satisfying assignment is a family of real fibre shapes satisfying these
capacity tests, and need not be a Kakeya set. An unsatisfiability proof
does exclude the specified support and weight range in both rings.

**No pair-spectrum census, maximum-energy census, affine-rank catalogue,
maximal-pair subspace catalogue, or sumset maximum table is used.**
The marked-support classification remains a separate dependency whenever
many support instances are combined into a whole-support-size statement.

## Mathematical system

Fix a pair-active residue support $S\subseteq V=\mathbb F_2^5$ containing
zero. The distinguished largest fibre is over zero. The unknowns are
subsets $A_v\subseteq V$, one for each $v\in S$, satisfying

$$
2\le |A_v|\le |A_0|\le M,\qquad |A_0|\ge m_0,
\qquad \sum_{v\in S}|A_v|\le B.
\tag{1}
$$

The application uses $B=93$, $m_0=2$, and $M=18$, or an explicitly
specified subinterval of maximum weights.

For each nonzero direction $d$, identify $V/\langle d\rangle$ with

$$
Q_d=\{x\in V:x<x+d\},
$$

where integer labels use their binary-coordinate order. This is exactly
the hyperplane where the highest nonzero coordinate of $d$ is zero;
in particular it is closed under addition. The representative of the
class of $x$ is $\pi_d(x)=\min(x,x+d)$, a linear projection.

Define the quotient pair set

$$
P_v(d)=\{x\in Q_d:x,x+d\in A_v\}.
$$

For an edge $\{a,b\}\subseteq S$, with $d=a+b$, the exact cardinality
used by the relaxation is

$$
c_{ab}=|P_a(d)+P_b(d)|.
$$

Require

$$
\sum_{\{a,b\}\subseteq S:\ a+b=d}c_{ab}\ge16
\qquad(d\ne0).
\tag{2}
$$

## Why every Kakeya counterexample gives a solution

Write the two rings as $R=\mathbb Z/4\mathbb Z$ or
$R=\mathbb F_2[\epsilon]/(\epsilon^2)$. Reducing a primitive ring line
modulo its nilpotent ideal gives one residue edge in a nonzero binary
direction $d$. Its two pairs in the two endpoint fibres give a label in

$$
P_a(d)+P_b(d)+c_R(a,d)\subseteq V/\langle d\rangle.
$$

Here $c_R(a,d)$ is the carry translation: $a\mathbin{\mathrm{AND}}d$
for the usual binary lifts in the first ring, and zero in the second.
Its precise value does not affect the cardinality. A Kakeya set must
cover all sixteen quotient labels. The size of a union is at most the
sum of the sizes of its members, giving (2). The size and largest-fibre
conditions give (1).

Singleton residue fibres can be deleted: they occur on no primitive
four-point line. Translation puts one largest pair-active fibre over
zero. These are the same normalizations used by the marked support
catalogue.

## Independent fibre translation is a valid symmetry here

For any $t_v\in V$, replace $A_v$ by $A_v+t_v$. Then

$$
P_{A_v+t_v}(d)=P_{A_v}(d)+\pi_d(t_v).
$$

Consequently each endpoint sumset is translated by
$\pi_d(t_a+t_b)$, and its cardinality is unchanged. All weights are
unchanged as well. Choosing $t_v\in A_v$ therefore ensures

$$
0\in A_v\qquad\text{for every }v\in S
\tag{3}
$$

without losing any solution to (1)–(2).

This normalization is justified by the **cardinality** relaxation.
Independent translations can change overlap between edge label sets, so
the same normalization is not automatically available in an encoder that
imposes their exact union coverage. The separate exact-ring encoder uses
its own common affine normalization.

## Boolean encoding and one-way assignment

There are $32|S|$ point variables $X_{v,x}$. A hypothetical Kakeya
counterexample supplies their values through the normalized fibres just
described. Every other variable has a deterministic honest value.

1. A pair variable is defined by
   $E_{v,d,x}\leftrightarrow(X_{v,x}\wedge X_{v,x+d})$.
2. For every edge, quotient label $\ell$, and $x\in Q_d$, a witness
   variable is defined by
   $W_{ab,\ell,x}\leftrightarrow(E_{a,d,x}\wedge E_{b,d,x+\ell})$.
3. An edge label variable is defined by
   $C_{ab,\ell}\leftrightarrow\bigvee_{x\in Q_d}W_{ab,\ell,x}$.
   Thus its truth set is exactly the endpoint sumset.
4. Bidirectional totalizers represent weight thresholds and the sum of
   the edge label variables in each direction. A positive threshold unit
   enforces the demand sixteen.
5. Fibre weights are at least two and at most $M$. For every outer fibre
   and every $k\in\{3,\ldots,M\}$, the clause
   $[|A_v|\ge k]\Rightarrow[|A_0|\ge k]$ permits ties and makes the hub
   largest. Its lower bound is imposed separately.
6. Because two points per fibre are already required, the total budget
   uses
   $$
   \sum_{v\in S}\sum_{k=3}^{M}[|A_v|\ge k]
   =\sum_{v\in S}(|A_v|-2)\le B-2|S|.
   $$
   This includes the hub. There is no outer-weight cap.

The AND and OR gates are encoded in both directions. A totalizer output
at index $k-1$ means that its input count is at least $k$. Arrays can
be truncated at the largest threshold used. The usual forward merge
clauses force every output up to the true count, while reverse merge
clauses force every later output false. A reverse clause could involve
the absent end of a truncated child only at a threshold at least as
large as the parent truncation; such a clause is not emitted. Thus the
truncated construction preserves the equivalence.

The actual fibre assignment and these gate values satisfy every clause.
Therefore a checked CNF refutation proves that no counterexample with
the specified support, hub interval, and budget exists. The solver is not
part of that implication. The encoding and the short mathematical
reduction still need review; the implementation is not formally verified
in a proof assistant.

## Size and validation

For the sample support

$$
\{0,1,2,4,7,8,10,11,12,16,17,19,20\},
$$

with maximum interval two through eighteen and budget 93, the formula has
33,059 variables and 171,191 clauses. It includes 416 point variables,
2,496 pair variables, 19,968 edge-label witnesses, and 1,248 exact sumset
label variables. This count does not establish faster solving.

Run the finite controls with

    python3 research_round7/exact_shape/verify_exact_shape.py

The replay checks both truth directions of every AND gate and every
sixteen-input OR gate, and 21,120 truncated totalizer merge cases. It
compares the generated formula with independently evaluated semantics on
all 3,584 normalized pair-active fibre families in binary two-space,
over every support containing zero. The minimum feasible weight of that
relaxation is ten; none has weight at most nine.

In dimension five it checks every quotient representative convention,
2,480 independently translated exact sumsets, and explicit assignments
for the actual 94-point star. The star satisfies the 94-budget formula.
Against budget 93 it violates exactly the single total-budget unit; all
other gates and coverage constraints remain satisfied. Deleting one point
from its full fibre gives a 93-point almost-star, rejected by coverage even
when the hub lower bound is relaxed.

These controls are reproducible evidence for the implementation and
exercise the off-by-one, hub-budget, translation, and quotient-label
issues. New dimension-five exclusions are counted only after proof-logged
search and acceptance by the pinned proof checker. A timeout is not an
exclusion, and a SAT result must be interpreted as a relaxation witness.
