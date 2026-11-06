# One-way soundness of the imported support-orbit CNF

## Finding and exact scope

**I found no unsound constraint in conditions (A)–(E), or in their supplied
CNF implementation.** The argument below constructs all variables of a
satisfying assignment from any actual Kakeya counterexample in a named case.
It includes the auxiliary variables, rather than only the intended meanings
of the spectrum and pair-count choices.

This is a hand mathematical and source-code review by a model agent. It is
not a proof-assistant formalization or independent human review. The spectrum
census remains a finite computational dependency.

The imported source is preserved unchanged:

    imported_claude_round4/src/encode_cnf2.py
    SHA256 8d4bde67dfcf3776fd2588329adff674f6b643f25e9a91c98607d8b8f92478bd

Its input is a list T of distinct nonzero residues, an exact maximum m, the
spectrum table, the capacity table, and all binary subspaces. The distinguished
hub has weight m. Outer weights are in [2,m], ties are allowed, and the default
outer budget is 93-m. The supplied case generator obtains T from a bitmask.

## 1. Normalization and the two rings

Write a point as $\widetilde a+\pi x$, with $a,x\in\mathbb F_2^5$ and
$\pi=2$ or $\epsilon$. A primitive line meets each of its two residue fibres
in two distinct points. Deleting singleton fibres therefore preserves every
line that witnesses the Kakeya property. Translate a largest surviving fibre
to residue zero.

Every invertible binary matrix lifts to an invertible matrix over either
ring, since its determinant lifts to a unit. It maps primitive lines to
primitive lines. On each tangent fibre the induced transformation is
invertible affine, so it preserves weight, pair histogram, and affine rank.
This justifies replacing the distinguished-hub support by a representative
of its linear orbit.

For each nonzero residue direction d, quotient by its one-dimensional span.
There are sixteen lifted direction labels. The residue edge {a,a+d} covers
the sumset of its two sets of d-pair classes, translated by a carry:
zero in the dual-number ring and coordinatewise a AND d in the other ring.
Translation does not change its cardinality. Kakeya coverage thus requires
the sum of the edge sumset cardinalities in each direction to be at least
sixteen.

This is a common necessary-condition relaxation for both rings. It forgets
the actual quotient labels and their overlaps; those omissions weaken the
model. A satisfying assignment need not be a Kakeya set. A reverse
interpretation is not needed for an UNSAT-based exclusion.

## 2. Spectrum and subspace enumeration

Every nonempty set of weight at most sixteen and affine rank r can be moved
by an affine automorphism to a set containing $0,e_1,\ldots,e_r$ inside the
coordinate r-space. The remaining possible points are exactly the non-basis
vectors of that space. The supplied spectrum program visits all subsets of
those remaining vectors, retaining weights at most sixteen, and directly
computes the 31 directional pair counts and affine rank. Duplicate visits
do not affect completeness.

The largest optional-vector list has length 26. Its enumeration bound fits
the 32-bit unsigned type used in this environment. For weights seventeen
through thirty-one the program directly records complements of sets of
weight one through fifteen. Every such large set is covered because its
complement has a normalized representative. The full 32-point set is added
separately. Thus the algorithm is complete; the correctness of its concrete
finite output remains a computational dependency.

The CSV contains 360 rows. The Python loader merges equal weight/histogram
rows and retains their minimum and maximum recorded ranks, yielding 359
choices. Only one histogram, of weight six, has ranks four and five. Allowing
all ranks in such an interval is safe: it includes every actual rank and
could only add spurious possibilities, never discard a true one.

The subspace enumerator takes the spans of all sets of at most five nonzero
vectors. Every binary subspace has such a basis. It returns 374 distinct
subspaces with dimension counts 1,31,155,155,31,1. The supporting replay
checks closure and these Gaussian-binomial counts.

## 3. The capacity table needs only a short analytic bound

For arbitrary X,Y in a sixteen-point group,

$$|X+Y|\le\min(16,|X||Y|).$$

Every delivered table entry equals this expression except the symmetric
pairs (3,5), (3,6), (3,7), where the entries are 13,14,15.

Translate a three-set X into a four-point plane H. Within each of the four
H-cosets, an occupancy t of Y contributes zero sumset points if t=0, three
if t=1, and four if t is at least two. To maximize the total, place first
points in different cosets and then place second points. Third and fourth
points in a coset add nothing. The upper bounds at total weights five,
six, and seven are therefore 13,14,15.

This proves the safety of every table entry. The finite replay compares all
289 entries, including row and column zero, with this formula. Proving that
every upper bound is attained is unnecessary for one-way soundness.

## 4. Assignment of the primary variables

Fix a hypothetical normalized counterexample of at most 93 points.

**Spectrum selectors.** At each fibre, select the true weight and pair
histogram, which exists in the complete census. All other spectrum selectors
at that fibre are false.

**Pair-count selectors.** For every incident direction, select its actual
pair count. The variable domain runs from zero to the largest count in any
allowed spectrum, so it includes this value. Incident directions at a fixed
vertex are distinct. Therefore their values form a sub-multiset of the full
31-direction histogram, satisfying every guarded histogram bound.

**Affine-space selectors.** Select the actual direction space H of the
fibre's affine hull. Its rank is allowed by the selected spectrum. Every
direction with positive pair count is a difference of fibre points and
therefore lies in H. If the spectrum has a unique rank r and exactly
$2^r-1$ positive directions, those directions must be precisely
$H\setminus\{0\}$. The stronger guarded positivity clauses are therefore valid.
For ambiguous ranks the source omits that extra constraint, safely weakening
the relaxation.

**Maximal-pair subspace selectors.** Let

$$K=\{0\}\cup\{d\ne0:p_A(d)=\lfloor|A|/2\rfloor\}.$$

For even weights this is the translation stabilizer. For odd weights use
$D(d)=|A\setminus(A+d)|$. This function is subadditive and, for nonzero d,
positive and odd. Two distinct maximal directions have deficit one; the
deficit of their sum is at most two and odd, hence one. Thus K is a subspace
in either parity. Its size is one plus the histogram's maximal-count entry.
Select this actual K. Its size and all guarded membership clauses hold.
If there are no maximal nonzero directions, select the trivial subspace,
which is present in the list.

## 5. Assignment of every auxiliary family

### Exactly-one constraints

For at most six choices the source adds a positive disjunction and all
pairwise exclusions. The unique true selector satisfies them. For a longer
list it uses sequential prefix variables. Assign each prefix true exactly
when a selected input has appeared by that position. The selected-input
implication, prefix monotonicity, and exclusion of a later selected input all
hold.

The source's comment writes a prefix equivalence although its clauses do
not need to force every prefix variable to equal that OR. This does not
affect soundness: the explicit prefix assignment works, and the emitted
clauses still enforce at most one selected input.

### Totalizers

At each recursive totalizer node set its j-th output true exactly when the
subtree has at least j+1 true inputs.

The forward clauses say that left count at least i and right count at least
j imply total count at least i+j. The reverse clauses say that left count
at most i and right count at most j imply total count at most i+j. Both hold
for the actual integer counts, including boundary clauses with omitted
antecedents. The empty and singleton base cases have the same meaning.

### Spectrum-derived guards

Set the full-affine-space guard to the OR of selected spectra meeting that
condition. Set each top-count guard to the OR of selected spectra having
that top count. The source supplies both directions of each equivalence;
the empty OR is correctly false.

### Weight thresholds and budget

For each outer fibre and j=1,...,m, set its threshold bit true iff the actual
weight is at least j. Its OR-of-spectrum equivalence holds. The sum of these
bits equals the sum of outer weights, which is at most 93-m. Thus the
forbidden next totalizer threshold is false. This uses an inequality; no
padding to exactly 93 is assumed.

### Edge capacities and directional coverage

For each edge let c be the actual cardinality of its quotient sumset.
Set its sixteen unary capacity bits true exactly through c. The ordering
clauses hold. Only the actual two pair-count choices activate a capacity
bound, and the analytic table proves $c\le M[p][q]$. All other guarded
capacity clauses have a false selector and are automatic.

In each residue direction, Kakeya coverage gives a sum of these actual
cardinalities at least sixteen. The required totalizer threshold is
therefore true. If no edge has a particular direction, adding an empty
clause is safe: no actual Kakeya set has that support.

These choices assign every variable family and satisfy every emitted
clause. A real counterexample therefore produces a satisfying assignment of
the exact formula.

## 6. The joint-maximum variant

I reviewed the complete diff in the new variable-maximum encoder, including
the frozen copy in the joint_maxima directory. For every input interval

$$2\le\mathrm{hub\_min}\le m\le32,$$

it permits hub weights in that interval, includes the hub in the threshold
sum, and adds a guarded prohibition of outer weights exceeding each
selected hub weight h. The actual hub spectrum activates only its own
guard. Every outer weight is at most h by definition of the chosen largest
fibre. Ties remain allowed. The sum counts all fibres exactly once against
the total budget 93.

Thus the same one-way proof applies. In particular, an UNSAT certificate
with hub_min=2 and m=18 excludes all maximum weights two through eighteen
for that marked support. It need not inherit the earlier maximum-at-most-ten
screen.

The optional parameter still named outtotal now means the total budget in
this variant, unlike the outer budget in the imported encoder. Callers must
follow the changed contract. The default clauses are correct.

## 7. New strengthening and practical issues

The accompanying maximal-subspace proof establishes, in every binary
dimension,

$$d,e\ne0,\quad d+e\in K\quad\Longrightarrow\quad p_A(d)=p_A(e).$$

For odd weights the key statement is that A differs by a single point from
a K-invariant set. The imported encoder only specifies membership in K; it
does not impose this additional coset constancy. The necessary containment
$K\subseteq H$ is also absent. These are valid strengthenings, not defects
in the previous relaxation.

The optional imported soundness scripts refer to stale development paths:
../spec32.csv, ../Mtable.txt, and ../T11.txt. They do not run directly from
the packaged layout without path adjustments. The principal replay uses
paths anchored to its own directory and the data subdirectory; its paths
are correct.

The supporting replay checks 8,191 exactly-one assignments, 2,047 totalizer
assignments, the analytic capacity table, spectrum and subspace metadata,
every dimension-four subset of weight at least two, and 1,877 reproducible
dimension-five examples for the new coset lemma. These are corroborating
finite checks, not substitutes for the universal arguments.

## Remaining trust boundary

An end-to-end formal theorem would still require machine-checked versions
of the normalization, complete census, assignment construction, and exact
encoder execution, connected to the accepted refutation of every exact
CNF. This audit spells out the semantic bridge; it does not claim that
the bridge has been formalized.
