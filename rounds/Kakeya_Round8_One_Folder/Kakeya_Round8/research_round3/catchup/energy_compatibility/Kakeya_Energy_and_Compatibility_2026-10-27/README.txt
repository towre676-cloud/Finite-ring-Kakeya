KAKEYA: FINITE ENERGY, TRANSLATION COMPATIBILITY, AND IMAGE STRUCTURE
Research continuation, 27 October 2026

RESULT AND SCOPE

This package proves three conditional all-dimension extensions of the
image-map approach, adds translation-invariant cross-edge overlap cuts,
and implements an exact translation-completion stage for fixed fibre shapes.
It includes complete written proofs, source code, ten small SAT/UNSAT cases,
and independent verification of their witnesses and refutations.

The unrestricted dimension-five lower bound 94 and the unrestricted
all-dimension formula k(R,n)=3*2^n-2 remain open in this work. No entire
maximum-fibre stratum is newly closed by this package. The term "new" below
means an addition to the recovered project work, not a literature-priority
claim. The written mathematical proofs are not Lean formalizations.

R is Z/4Z or F2[e]/(e^2), pi is 2 or e, G=R^n, and N=2^n.
A Kakeya set contains a translate of Rv for every primitive direction v.
For a line selection f:G->G define

    S_t = {f(v)+tv : v in G},       K_f = union_{t in R} S_t.

Every K_f is Kakeya. Conversely one can select f with K_f contained in
any given Kakeya set: choose its primitive lines, and choose the smaller
nonprimitive lines inside suitable primitive ones. The additional image
conditions in our theorems are substantive; we have not shown how to force
them for an arbitrary small Kakeya set.

1. THREE N-POINT IMAGES SUFFICE, WITH A SHARP GAP

If any three of the four S_t have cardinality N, then |K_f|>=3N-2.
More precisely there is a power of two h dividing N such that

    |K_f| >= 4N-h-N/h-1.

If the remaining image is larger than N, then 1<h<N and

    |K_f| >= (7/2)N-3.

That remaining image cannot have size N+1. Both gaps are jointly sharp:
for every n>=2 and both rings the package constructs image sizes
(N,N,N+2,N) with union (7/2)N-3. For n=5 these are sizes
(32,32,34,32) and union 109. Thus even a two-point departure from the
balanced fourth image forces a substantial gap in this structural class.

The proof starts from the exact difference tiling A x B -> G obtained
from two unit-separated N-point images. The third N-point image forces B
to be invariant under H0=span(pi A). Projection counting forces every
inequality in N<=|pi A|*|pi B|<=|H0|*(N/|H0|)=N to be equality.
The resulting transversal/coset structure makes four intersections exact,
giving 4N-h-N/h-1. See analytic/THREE_MINIMUM_IMAGES_THEOREM.txt for
the complete proof and both explicit sharp constructions.

2. TWO N-POINT IMAGES SUFFICE IF ONE IS AN ADDITIVE COSET

Suppose S_s,S_t both have size N, t-s is a unit, and at least one of
these images is a coset of an additive subgroup. Then |K_f|>=3N-2.
Neither of the other two images has to be a coset or have size N;
f itself need not be additive.

After normalization A is a subgroup and B is a transversal for A.
The next image C=(1-pi)A+pi B is a union of N-point cosets. Its only
nontrivial case has size 2N and is itself a subgroup, since its two
cosets differ by an order-two element. Writing h=|A intersect C| gives

    |A union B union C|
      >=4N-h-min(N,2N/h) >=3N-2.

See analytic/TWO_IMAGES_ONE_COSET_THEOREM.txt. The exact-pair-tiling
case in which both N-point images are noncosets is still unresolved
in general, as is the existence of such an N-point pair for arbitrary K.

3. FOUR ADDITIVE-COSET IMAGES SUFFICE

If all four S_t are additive cosets, then |K_f|>=3N-2. For n>=2,
if they are not all N-point images, the stronger bound is 3N-1.
In particular this proves the bound for every affine additive f.
Over the dual numbers it includes every affine F2-linear map, without
requiring its linear part to commute with pi.

After translating their common point to zero the images are subgroups.
Unit-separated images sum to G, so their product of cardinalities equals
N^2 times their intersection size. Since all orders are powers of two,
only a 2N-point maximum image needs additional work. In the exceptional
configuration, the image identities would force both pi G subset U
and U subset ker(pi), contradicting |U|=2N>N.
See analytic/COSET_IMAGE_THEOREM.txt for the full argument and rigidity.

4. FINITE ENERGY THAT RETAINS CROSS-EDGE OVERLAP

Let V=F2^n and Q_d=V/<d> for d nonzero. A fibre A_x supplies the
full-pair classes

    P_x(d)={u+<d> : {u,u+d} subset A_x}.

The base edge {x,x+d} covers S_e=P_x(d)+P_(x+d)(d)+c_R(x,d),
where the binary-section carry is zero for the dual ring and x&d
modulo d for Z/4. Exact coverage requires union_e S_e=Q_d.

Existing individual sumset capacities do not record overlap between
different edge outputs. For canonical sets define

    mu_ij = min_h |S_i intersect (S_j+h)|.

For every tree T on the nonempty outputs and all independent shifts,

    |union_i (S_i+h_i)| <= sum_i |S_i|-sum_{ij in T} mu_ij.

A maximum spanning tree gives the strongest bound of this form.
Every valid tree certificate can be checked independently; the checker
does not have to trust an optimization algorithm. Since mu is invariant
under translations, this cut can be used without undoing independent
translation gauges in the inherited individual-sumset relaxation.

An explicit n=5 fixture has two eight-class outputs in a sixteen-class
quotient, but their minimum relative overlap is two. The true union
capacity is at most 14 for all translations, although the sum of individual
capacities is 16. This is realized by fibre weights 2,16,2,16 and excludes
that fixed local shape pattern in both rings. It is not a theorem excluding
the whole maximum-sixteen stratum.

The package also proves the necessary collision inequality
2J<=L(T-q), with J the sum of pairwise output intersections, T their
total size, q=|Q_d|, and L an overlap ceiling. An exact Walsh-matrix
positivity reformulation is given with its limitations: positivity alone
is not a new lower bound or an automatic efficient algorithm.
See energy/FINITE_ENERGY_THEOREMS.md and energy/finite_energy.py.

5. SHARED TRANSLATIONS CAN OBSTRUCT DIFFERENT DIRECTIONS JOINTLY

Four twelve-point fibres at base vertices 0,1,2,3 give two half-quotient
outputs in each of directions 1,2,3. Every separate exact cardinality
condition is saturated. Nevertheless the dual-ring coverage requirements
for the XOR T0 of the four translation offsets are

    ell_2(T0)=1, ell_1(T0)=1, (ell_1+ell_2)(T0)=1.

Their XOR is 0=1. No translation assignment satisfies them jointly.
For Z/4, the carry changes the final right side to zero, and a completion
exists for these three directions. The distinction is directly verified
in the actual rings; dropping the carry would give a false exclusion.

This is a three-direction local theorem. It extends to larger families
only if no additional base edges contribute in those directions. The
Z/4 witness is not asserted to cover every residue direction.

6. EXACT FIXED-SHAPE TRANSLATION SOLVER

compute/translation_completion.py restores one n-bit offset per labelled
fibre shape and encodes exact coverage using the same offsets in every
direction. It includes the ring carry. Only a legitimate affine shear
gauge is fixed: t_x -> t_x+Lx+c. Remaining offsets are variables.

The saved cases contain six directly checked SAT witnesses and four short
UNSAT proofs. The dual twelve-point block is refuted by four nonempty RUP
lemmas; each two-edge forced-overlap fixture by six. The CNFs encode actual
coverage, without adding the analytic tree bound as an assumed axiom.
The two rings' full 94-point stars and larger 264-point controls are SAT.

No actual weight-at-most-93 fixed shape family passing every local capacity
condition was available in the recovered handoff. Weight profiles alone
do not determine this stage's input. Consequently this implementation has
not by itself completed an unrestricted search or closed another full
maximum-fibre class. See compute/README.md for exact input/output semantics.

7. THE FULL MAXIMAL-NORM ROUTE HAS AN ALL-p OBSTRUCTION

The earlier weighted 94-point star obstruction extends beyond p=5.
For any full functional estimate ||M_R f||_r<=A||f||_p, finite p>=1,
and any output exponent r>=1, applying only f=1_K can produce a real
cardinality bound no greater than

    2 sqrt(N(2N-2)).

For n=5 this is 89.08422980528034..., giving at most 90 after integer
rounding. For p=5 the ceiling is 87.8760782759306..., giving at most 88.
These are ceilings on that proof route, not lower bounds newly proved
for Kakeya sets. Set-specific arguments using additional structure are
not ruled out. See review/ALL_LP_MAXIMAL_OBSTRUCTION.txt.

8. VERIFICATION

From the extracted package root run:

    python verify_package.py

This uses only the Python standard library. It first checks SHA256 hashes,
then runs the finite verifiers in a temporary copy so saved receipts remain
unchanged. It reconstructs all ten CNFs, checks six witnesses by coordinate
ring arithmetic, and independently replays all four UNSAT proofs. It also
repeats the small exhaustive classifications, finite energy controls, and
independent sharp-construction tests. Do not run with Python -O or -OO.

Selected coverage of the checks:
  * 4,802 n=2 translation-shape/ring families;
  * 65,536 three-set/relative-translation tree-overlap checks in F2^2;
  * all 65,536 additive maps in the n=2 dual additive group, and all
    256 additive maps of (Z/4)^2;
  * all 3,920 dual and 1,136 Z/4 normalized N-point pair tilings for n=2;
  * 216 independently constructed tilings across n=1,...,6;
  * 24 sharp-construction checks across n=2,...,7 in the two rings;
  * full primitive-direction coverage of the n=5 94-point stars.

The original SAT-encoder audit additionally compared 12,578 gauged offset
assignments and 500 pinned n=3 fixtures with direct arithmetic. Repeating
that original solver audit or solving new cases requires the optional
python-sat package pinned in compute/requirements-solver.txt; checking the
saved witnesses and proofs does not. The unchanged inherited C RUP checker
source is included as a second optional proof replay route.

Finite tests check implementations and examples. The universal structural
claims rely on the complete mathematical proofs, independently reviewed
during this pass. No assertion of machine formalization is made.

9. RELATION TO THE RECOVERED PROJECT AND THE OPENAI WORK

The recovered continuation already had the balanced four-image theorem,
the mismatch/capacity energy, a quotient-sumset atlas, and some local shape
alignment results. This package extends those ingredients; it does not
relabel them as new. The newer recovered packages report full closures of
maximum-fibre 9 and 24, leaving maximum sizes 10 through 23 in the global
frontier, with 97 explicit active-support classes still recorded at cap10.
Those are inherited status reports, not large proof chains replayed here.
See SOURCES_AND_PROVENANCE.txt for the exact source records and boundary.

The recent OpenAI Euclidean local-smoothing/Kakeya work motivated examining
global compatibility and positivity. None of the results here asserts a
transfer of that PDE argument to these rings. The concrete useful outcome
is a finite combination of cross-edge overlap, shared phase constraints,
and image-map rigidity. A naive uncoupled character PSD relaxation is
shown to be vacuous in the relevant cardinality-feasible setting.

The remaining mathematical bridge is explicit: either force an arbitrary
putative small Kakeya set into one of the proved image classes, or provide
an exhaustive, certified enumeration of the remaining actual fibre shapes
and apply compatible overlap/translation constraints to all survivors.
This package supplies additional lemmas and a verified second stage; it
does not assume either missing bridge has been supplied.
