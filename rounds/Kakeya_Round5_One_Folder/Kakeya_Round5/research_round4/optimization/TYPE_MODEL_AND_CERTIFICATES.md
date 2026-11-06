# A systematic type model, its exact certificates, and the carry obstruction

## Status

The proposed optimization strategy is mathematically sound after specifying
the type domains and their geometric embeddings. This note gives an exact
finite-domain integer formulation, an outer linear relaxation, and a rational
dual certificate format. A working standard-library implementation and an
independently written verifier accompany it.

The implementation is demonstrated on complete dimension-two domains. It
does **not** enumerate all dimension-five fibre types, solve the remaining
middle branch, or establish any new dimension-five exclusion. Its purpose is
to make the next optimization architecture concrete and test the distinctions
between cardinality, labelled coverage, fractional consistency, and actual
realizability.

“Independent” below describes separate implementations and different finite
computations. Both implementations and this analysis were produced within
the same model-agent session; this is not an independent human review.

## 1. Types must retain a common embedding

Put V=F2^n. Fix a residue support S. At residue a, let T_a be a finite domain
of possible tangent fibres. The exact version of a type is an actual subset
A subset V, in the same coordinate system as the residue support.

An affine-equivalence class is a useful compressed index, but it is not an
embedded type. A representative B must be accompanied by a linear embedding
g and a translation t, giving A=g(B)+t. Different incidences of a must use
the same g and t. Permuting the entries of a pair-spectrum histogram
independently does not enforce this. The pair spectrum as a multiset loses
direction labels; even the labelled vector p_A(d) does not determine the
pair-label sets inside the quotients.

There are two sound ways to reduce domains:

1. A complete catalogue with embeddings, after explicitly justified symmetry
   reductions.
2. A superset or a verified upper envelope for every omitted possibility.

An infeasible LP over a restricted collection of promising types is not a
global exclusion. In column generation, every omitted column must pass a
complete pricing oracle before the dual becomes a certificate for the full
domain. The same requirement applies to omitted type-pair constraints.

For a fixed profile, one may assign a size to each residue in advance, or
allow several weights in T_a and impose global multiplicity equations.
The second approach covers every placement of that profile in one model.

## 2. Carry changes labels, not single-edge cardinalities

Use the coordinatewise binary section sigma:V->R^n, with pi=2 or epsilon.
An actual ring point is sigma(a)+pi*u. A primitive vector is
sigma(d)+pi*v, with d nonzero. Its unit-multiple class is indexed by
v modulo <d>.

Write q_d:V->V/<d> for the quotient map and

    P_A(d)={q_d(u):u,u+d belong to A}.

For the residue edge {a,b}, d=a+b, its exact label set is

    L_ab^R(A,B)=P_A(d)+P_B(d)+c_R(a,d),

where

    c_dual(a,d)=0,
    c_Z4(a,d)=q_d(a coordinatewise-multiplied by d).

The latter expression is the binary carry in sigma(a)+sigma(d).
Changing the selected endpoint changes the carry by q_d(d)=0, so the edge
label set is well-defined. If A=A0+t_a and B=B0+t_b, its additional shift
is q_d(t_a+t_b). The same t_a occurs at every edge incident to a.

Crucially,

    |L_ab^Z4(A,B)|=|L_ab^dual(A,B)|.

Adding the carry to a table of single-edge **capacities** cannot make that
table ring-specific: translating a set preserves its size. Ring dependence
enters the label-incidence coefficients and the common translations across
the whole support. These coefficients should be ring-aware from the start.
One parameterized verifier can check both rings; the two coefficient arrays
need not be identical.

For example in V=F2^2, take residues a=1,b=2,d=3 and both tangent fibres
equal to {0,3}. With canonical quotient representatives {0,1}, the edge
covers label {0} over dual numbers and label {1} over Z4. Both capacities
equal one. The verifier checks this by literal four-point ring lines.

## 3. Exact finite-domain IP and its local-marginal LP

For every a and type A in T_a introduce x_a,A. For each residue edge
e={a,b} introduce y_e,A,B. The constraints are

    x>=0, y>=0,
    sum_A x_a,A=1,
    sum_B y_ab,A,B=x_a,A,
    sum_A y_ab,A,B=x_b,B.

When a profile has n_w fibres of weight w, add

    sum_(a,A:|A|=w) x_a,A=n_w.

The cardinality relaxation adds, for each d nonzero,

    sum_(ab:a+b=d) sum_(A,B) C_ab(A,B)*y_ab,A,B >= 2^(n-1),

where C_ab is a valid actual-sumset upper bound. Exact cardinalities may be
used when actual pair-label sets are available. The product bound, shared
period bounds, and affine-rank bounds are safe upper relaxations.

The label model instead adds, for every quotient label z,

    sum_(ab:a+b=d) sum_(A,B:z in L_ab^R(A,B)) y_ab,A,B >= 1.

If x is binary, its normalization chooses one actual fibre at each residue.
The marginal equations force y onto exactly the selected endpoint pair;
y need not be declared binary separately. Thus the label model is exact for
the stated finite domains. The cardinality model still loses union overlap,
even with binary x.

Relaxing x to real variables gives a necessary LP. An actual configuration
defines an integral feasible point, so LP infeasibility excludes it. A
fractional feasible point is not a distribution on globally compatible
configurations: pairwise marginal consistency alone need not extend around
cycles. Higher-order marginals and geometric cuts address this gap.

The implementation `type_model.py` builds these rows, complete type-pair
tables, and nonnegative variables. It uses actual embedded subsets and exact
integer incidence coefficients. It has an optional profile-multiplicity
constraint parameter; it does not silently assume a domain is exhaustive.

## 4. A directly checkable dual certificate

In label mode choose nonnegative rational weights lambda_d,z. Define the
reward of an edge-type pair by

    R_ab(A,B)=sum_(z in L_ab^R(A,B)) lambda_(a+b),z.

Choose rational endpoint messages u_ab(A), numbers beta_a, and, when needed,
profile multipliers mu_w. Verify, for every permitted pair and node type,

    R_ab(A,B) <= u_ab(A)+u_ba(B),
    sum_(b neighbor a) u_ab(A) <= beta_a+mu_|A|.

Then every compatible type assignment, and indeed every feasible marginal
point, satisfies

    sum_(d,z) lambda_d,z
      <= sum_a beta_a + sum_w mu_w*n_w.

A strict reversed numerical inequality is therefore an exclusion. The left
side is required by coverage; the right side follows by summing the verified
local inequalities and using the common marginals. For cardinality mode,
replace R_ab by lambda_d*C_ab and the left side by
2^(n-1)*sum_d lambda_d.

This recovers the current resource certificates as specially structured
message choices. It also states exactly what a full pricing oracle must
certify for unlisted types. After clearing denominators, all verification is
integer arithmetic. A floating-point optimizer may discover a candidate
dual, but the accepted certificate must pass these exact inequalities.

The supplied checker also supports a conventional Farkas representation.
Write the generated LP as Az<=b, Ez=f, z>=0. A certificate supplies
lambda>=0 and unrestricted mu such that

    lambda*A+mu*E >= 0 coordinatewise,
    lambda*b+mu*f < 0.

These two facts contradict z>=0. `verify_optimization_demo.py` verifies them
with Python Fractions and checks the generated rows against independent
direct ring arithmetic.

## 5. Weighted AM-GM is useful, but is already inside the dual architecture

For theta=a/b>0,

    2*p*q <= theta*p^2+theta^(-1)*q^2

is certified exactly by

    a^2*p^2+b^2*q^2-2*a*b*p*q=(a*p-b*q)^2>=0.

The hub example p=9,q=1 improves from41 to9 at theta=1/9. No numerical
tolerance is needed. The implementation verifies700 rational-weight cases
and the exact hub arithmetic.

There are two qualifications. A theta chosen for a weight-class pair must
remain valid through the subsequent maximization over all actual pair counts;
one cannot select a different favorable theta after spending the same local
energy elsewhere. Also theta=1/9 is poor for p=q=1, so one choice is not a
uniform improvement on every incidence of those weight classes.

Weighted squares are one permissible endpoint-message family. They are not
stronger than an exact p*q or actual-sumset table at a single edge. The
existing full-spectrum screens already optimize scores involving the sharper
M(p,q), with integer assignment duals. The opportunity is a more systematic
global message optimization and common-type coupling, not replacing a sharp
edge value by another upper bound.

## 6. Geometric facts supply rows that pairwise consistency does not discover

The cube-energy inequality is a dual certificate of an aggregate relaxation
containing an incidence budget and a Mantel bound on capacity16 cube edges.
The LP machinery does not prove Mantel's geometric applicability by itself.
That theorem supplies a valid nonlocal row, which the dual can combine.

For general affine tangent spaces H_A,H_B and an active direction d,

    C_ab <= min(2^(n-1),
                2^(dim H_A+dim H_B-dim(H_A intersect H_B)-1)).

A common two-space implies capacity at most8 when both tangent spaces have
dimension at most3. A common two-space alone is not sufficient for arbitrary
larger-rank types.

Similarly, a shared period subgroup H of the two quotient pair-label sets
gives |P+Q|<=|P||Q|/|H|. The old own-period theorem forces such a subgroup
from residue information. Hall roles arise by projecting forced eligibility
conditions onto counts of possible fibre attributes.

Useful nonlocal extensions include triangle marginals, cube-edge density
cuts after branching on the cube count, unavoidable-overlap cuts, and XOR
cycle constraints for common translations. Every added cut needs a proved
validity statement or a complete finite certificate.

## 7. A complete common-type exclusion demonstration

In dimension two, take any three residue bases and assigned weights(4,4,2).
Both full fibres are fixed; the two-point fibre can be any of the six actual
two-point subsets of F2^2. Each of its two incident directions needs capacity2
from its unique residue edge. A two-point fibre has only one pair direction,
so it cannot meet both requirements.

The per-edge maxima each equal2 and do not reveal the contradiction. Common
type normalization does. Summing the two coverage demands requires capacity4,
while every single low-fibre type supplies total capacity at most2 along
those two edges. The generated Farkas certificate has nonnegative residual
coefficients and combined rhs -2.

The demonstration covers all three positions of the low fibre, both rings,
and both capacity and label models:12 exact certificates. All domain states
are exhaustive, and literal ring enumeration confirms zero realizations.
This is an architecture test, not a new claim about the known exact minimum.

## 8. A ring-sensitive counterexample to the sufficiency of the basic LP

Take full residue support in F2^2 and four fibres of size3. There is only one
affine shape class, but its four translations matter. Write

    A_a=F2^2 minus {t_a},
    T=t_0+t_1+t_2+t_3=(T_0,T_1).

For a direction d, the pair-label set of A_a is the quotient point opposite
q_d(t_a). Adding two such pair-label sets cancels that opposite-point shift.
Each of the two residue edges in direction d therefore supplies one label.
They cover both quotient labels exactly when their labels differ.

For directions1 and2 this requires T_1=1 and T_0=1. For direction3 it requires

    T_0+T_1=1  over dual numbers,
    T_0+T_1=0  over Z4.

The first system is inconsistent; the second holds exactly when T=(1,1).
Among all4^4=256 choices, there are **zero** dual-number realizations and
**64** Z4 realizations. This statement concerns the profile(3,3,3,3), not
the two rings' unrestricted minima.

Nevertheless the label LP has the same feasible fractional witness in both
rings: x_a,A=1/4 for every node type and y_ab,A,B=1/16 for every pair. Each
edge covers each label with marginal probability1/2, so the two edges give
the required total1. All node and pair marginals agree. This proves directly
that ring-aware label tables are necessary but not sufficient to close the
local-marginal relaxation; global consistency still matters.

The independent checker enumerates all256 actual assignments using literal
arithmetic in each ring, verifies the exact LP witness, and checks the parity
criterion. It also checks every table entry in all14 demonstrations.

## 9. First useful dimension-five coarse type split

The separate round4 twelve-point energy proof gives a useful analytic type
catalogue. A twelve-point fibre has either:

* Affine rank5 and energy at most222.
* Rank4, equal to an affine4-flat minus an affine plane: energy300, with
  pair counts6 on3 directions,4 on12 directions, and0 on16 directions;
  its period space has dimension2.
* Rank4, equal to an affine4-flat minus an affinely independent four-set:
  energy294, with pair counts5 on6 directions,4 on9 directions, and0 on16
  directions; it has no nonzero translation period.

The first item is a safe coarse bucket, not a single shape. Any master problem
must retain all its possible directions or use proved upper envelopes for
them. The latter two are actual affine types, whose orientations and
translations still need to be shared across every incidence.

For the old C,D,E boundary profiles, rank5 at the twelve-point fibre would
give total energy at most982,969,974 respectively, already below992. Thus
those particular profiles force a rank4 twelve-fibre. No claim is made that
all surviving middle profiles force the same conclusion.

The proof source is `research_round4/energy12/ENERGY12_ANALYTIC_PROOF.md`.

## 10. A practical next formulation

There is no need in principle to build a completely separate matrix for each
weight profile. Allow an empty type at every residue, fix a maximum-weight
hub at residue0 by translation, put every other fibre size in0 or2..m, and
minimize total point mass. The label rows enforce coverage, and the support
ceiling is a linear bound on nonempty-type variables. Profile multiplicities
can be imposed only when they make a useful branch.

This universal finite-domain IP is exact if its domains are complete. Its
naive size is enormous, and the basic LP is weak under symmetry. A sensible
hierarchy is: coarse energy/rank/period types; spectrum-based local pricing;
embedded direction and pair-label refinement at tight vertices; then
selected higher-order or translation constraints. Every incomplete type
bucket needs a valid encompassing relaxation until it is fully split.

The new middle inventory should supply the actual residual scale before
choosing how much of this hierarchy to implement. Neither a smaller support
nor a heavier maximum automatically implies that every scalar bound becomes
weaker; that is an empirical and mathematical question for the complete
inventory, not an assumption.

## Replay

From the workspace root:

    python3 research_round4/optimization/build_demo.py
    python3 research_round4/optimization/verify_optimization_demo.py

Only the second command is needed for supplied demo files. It does not import
the producer. Expected result:14 examples,12 exact Farkas certificates,
348 independently checked ring edge-table entries, two exact fractional
witnesses, and integer realization counts0 versus64 for the(3,3,3,3) case.
The machine receipt is `OPTIMIZATION_DEMO_VERIFICATION.json`.
