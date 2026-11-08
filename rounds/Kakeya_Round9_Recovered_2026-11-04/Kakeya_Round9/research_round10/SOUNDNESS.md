# Heavy-fibre projections for the recovered dimension-five relaxation

Scope: pair-active support S of size 13 in F2^5, distinguished hub 0 of
exact maximum weight 12 or 13, all fibre weights at least 2, total at most
93. Both Z/4Z and F2[epsilon]/(epsilon^2) are covered. Ties for the maximum
are allowed. No statement here removes other support sizes or maxima.

## The four proposed constraints already occur in the recovered formula

`research_round9/recover.py:formula` calls the enabled
`research_round8/incidence/encode_next_frontier.py:encode`. That function
adds all-edge tetrahedral capacities and the next-frontier incidence cuts,
including their optional pair-count propagation. The nested queue metadata
is a preserved pre-recovery snapshot, not evidence that these cuts were
absent from the hashed recovered CNF.

Let H be the heavy residues (weight at least 4), h=|H|, and let M be the
nonzero directions outside D(H). Let L2,L3 count weight-2 and weight-3
fibres. Every direction has sixteen lifts to cover. Its residue edges
form a matching. A light endpoint has at most one pair in a direction;
any endpoint has at most floor(13/2)=6 pairs. Carries only translate the
quotient sumset contributed by an edge, leaving its cardinality unchanged.

1. **Incidence budget.** For h>=9, M contains no complete binary plane
   triple: otherwise H meets each of its eight cosets in at most one point.
   A weight-2 fibre supplies one pair direction; a weight-3 fibre supplies
   a plane triple and therefore at most two directions of M. A missing
   heavy direction needs at least ceil(16/6)=3 active light incidences.
   Hence 3|M| <= L2+2L3.
2. **At least ten heavy fibres.** For h<=7, the universal light capacity
   bound 16(31-binomial(h,2)) <=18(13-h) fails; the positive difference is
   262+26h-8h^2. Eight points have at most 25 differences, giving required
   capacity 96 versus at most 90. Nine points have at most 28 differences,
   giving incidence requirement 9 versus at most 8. Thus h>=10. The
   eight- and nine-point bounds have the symbolic proof in Round8's
   `research_round7/dense_encoder/NINE_POINT_DIFFERENCE_ANALYTIC_PROOF.md`.
3. **Full difference cover for eleven heavy fibres.** At most two light
   fibres remain; their maximum capacity in a missing direction is 12<16.
   Thus M is empty. For h=10 the incidence inequality also gives |M|<=2.
4. **All-edge tetrahedral capacity 14.** Two nonplanar four-point subsets
   of F2^4 have at most fourteen distinct sums. Their three-dimensional
   direction spaces intersect in at least a plane, and removing each
   set's one missing difference leaves a shared nonzero difference. The
   resulting two distinct sum collisions remove at least two of sixteen
   possible sums. The active sufficient flags require affine rank exactly
   four and either weight8/energy64/one four-pair direction, or
   weight11/energy205. This is *not* an unconditional bound for every
   four-pair edge: planar four-sets are not covered. Round8's
   `research_round7/support13/four_pair_cut/FOUR_PAIR_CAPACITY_LEMMA.txt`
   proves the type implications. In particular the weight12/energy294
   family's planar exceptional direction must not be flagged by this rule.

These arguments justify the existing one-way interpretation for actual
Kakeya configurations. The census, normalization, support catalogue and
encoder remain separate mathematical/computational premises; this is not
an end-to-end proof-assistant formalization.

## Additional projected clauses

The new `encode_projected.py` leaves every existing variable and clause
unchanged and appends clauses using only the exported heavy flags and
pair-count selectors. It adds no variables. It explicitly checks its
support and maximum scope and pins the entry encoder's SHA-256.

### Light-set clauses

For each candidate set L of at most three nonhub light residues, set
Hmax=S\L. In a direction absent from D(Hmax), every edge touches L. An
edge with two L endpoints has capacity at most 1; an edge with one has
capacity at most 6. Therefore, if

    U_d(L) = 6 * (# edges with exactly one L endpoint)
             + (# edges with two L endpoints) < 16,

not all residues of L can be light. Append the positive clause

    OR(a in L) heavy[a].

The same clause is valid if Hmax misses more than two directions, by the
already established incidence consequence. These contradictions are
monotone when more residues are light: H only shrinks and capacities do
not increase. Thus inclusion-minimal forbidden L suffice, even though
the other residues have not explicitly been assumed heavy.

There are 1+12+66+220=299 complete heavy/light patterns consistent with
hub0 heavy and h>=10. Exhaustive finite validation compares the emitted
clauses to a separate direct edge-capacity calculation on all 299
patterns for each of the 25 cases. Surviving patterns are not satisfying
assignments of the complete CNF and are not Kakeya configurations.

### Missing-direction pair projections

If exactly three specified residues L are light and d is a missing heavy
direction, each light residue must have a heavy partner a+d in S, have
p_a(d)=1, and its partner must have at least four pairs. Losing an edge
leaves at most 12 capacity; a light-light edge leaves at most 7. The three
heavy partners are distinct, with pair counts p1,p2,p3 in {4,5,6}, and

    p1+p2+p3 >=16.

For a partial choice of k partner counts q1,...,qk for which
sum(qi)+6(3-k)<16, append

    OR(a in L) heavy[a] OR OR(i selected) NOT y[partner_i,d,qi].

Only inclusion-minimal partial choices are emitted. In particular two
counts 4 and 5 cannot coexist, and three counts 5 cannot coexist. These
clauses expose consequences of the existing exact directional capacity
and incidence constraints; they add no new geometric premise. The
validation exhausts all 27 count triples for each retained missing
direction. Values below 4 are already excluded by the frozen propagation.

## Certificate boundary

A projected refutation is checked against its complete new DIMACS input,
not attributed to the old hash. The unchanged target formula is also
searched and checked separately. Search preprocessing adds untrusted RUP
units, whose proof prefix must be checked along with the solver stream
against the original input formula. Acceptance requires:

- exact regeneration of the case scope and baseline hash;
- post-search regeneration of the exact searched formula;
- pinned checker source verification;
- DRAT-trim reconstruction of LRAT;
- `s VERIFIED UNSAT` from the pinned CakeML checker;
- retained compressed input/proof bytes, hashes and checker receipts.

Timeouts, partial traces, SAT-relaxation models, branch-pattern pruning,
and source-level mathematical arguments alone confer no SAT-case credit.
Independent proof checking here means a separate proof-checking program;
it does not mean an independent human research replication.
