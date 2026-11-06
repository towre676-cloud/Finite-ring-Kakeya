# Bounded audit of the complete middle inventory's new screens

**Verdict: PASS.** This is a mathematical and code cross-check by another
model agent in the same research session. It is not external human review
or epistemic independence.

I read the complete `MIDDLE_INVENTORY_PROOF.md`, the generic C++ screen,
the joint-cube Python producer, and the complete Python inventory verifier.
The companion `review_middle_cube_inventory.py` imports none of those files.
It independently recomputes every joint local optimum by bounded-choice
dynamic programming, checks all cube-count branches, audits the recorded
generic-test hypotheses and thresholds, and checks disjoint subtraction.

## Joint-spectrum cube inequality

The transformation of the established master inequality is correct. With
`L=2*lambda`, doubling the coverage upper gives

    2C <= 7Lr+(32-2L)floor(r^2/4)
          + sum_A [Q(A)+top_r max(0,2min(16,4p_A(d))-p_A(d)^2-L)].

The allowed bank `8<=L<=16` is precisely `4<=lambda<=8`. The coefficient of
the Mantel term stays nonnegative. The same fibre's energy and surplus are
evaluated together before the maximum over its spectrum; the code does not
combine separate maximizing shapes. Selecting the largest r gains is a safe
relaxation because a nonselected residue has at most one edge to each cube,
and those incident directions are distinct.

Let k be the number of weight-eight fibres. The saved certificate for every
cut covers exactly `r=0,...,k`. The r selected fibres are actual affine cubes;
every other weight-eight fibre is therefore a noncube. Excluding exactly the
histograms with `h[4]=7` is valid: those seven full pair counts are seven
translation periods, which force an eight-point set to be an affine cube.
Conversely every affine cube has that spectrum.

Different r branches may use different certified prices. This is ordinary
case analysis and does not require one price to work simultaneously for all
r. The finite price bank may miss exclusions, but cannot invalidate any
strict branch inequality. The range r<=10 is complete because total mass is
93 and there is already a fibre of size at least12.

The separate bounded-choice DP reproduces **all1,683 local table entries**,
covering24,750 individual permitted spectrum evaluations. It checks every
saved attaining spectrum, all524 cut profiles, and all2,498 actual-cube-count
branches. Every branch is strictly below992; the minimum doubled gap is1.
The equality of the finite table is computational. The master inequality's
geometric validity remains the separately proved analytic dependency.

## Generic geometry hypotheses

All recorded profiles have support10..17, maximum12..18, sorted weights at
least2, and total93. In particular the eight-heavy and nine-heavy tests
always have the light vertices required by their implementations. Padding
is valid throughout, since s*m>=120>93.

The following uses of the earlier lemmas are correct:

* Total energy uses the complete saved spectrum maxima and the strict992
  threshold. Its census dependency is explicit.
* The three-heavy test permits at most one quota-three light fibre its full
  three-maxima uplift. The exceptional residue is uniquely determined by
  the three heavy bases. Heavy and light resource terms are counted with
  the same doubled convention.
* The two-heavy test deletes their sole mutual direction and uses doubled
  demand960. Its three pair counts are correlated through eight binary
  two-plane cosets; both implementations construct all such local patterns.
* For eight heavy bases the missing count is6 or at least9. The two tests
  use doubled thresholds192 and288 respectively. The six-direction branch
  correctly uses both the halfspace pair budget and at mostthree positive
  heavy neighbours. Both branches must fail.
* For nine heavy bases the missing set has at leastthree directions and is
  sum-free. The light pair budget is floor(w^2/4), and its maximal-direction
  quota in that set is at most(q(w)+1)/2. The zero-price upper is independent
  of how many directions are missing, so the96 threshold is sufficient for
  every larger missing count too.
* The halfspace bonus is used only after the at-least-nine branch fails and
  only when all light pair caps are<=8. Then light-light capacity is at most
  four times the endpoint pair mass. The quantities X and Y use at mostsix
  distinct light neighbours and the correct halfspace maximum-direction
  quota. Its96 threshold is undoubled, as intended.
* The ten-heavy test checks one cap6, every other heavy cap<=4, and every
  light weight<=3. Its unique-edge counting demands min(3k,12) light pair
  units. Maximum13 is legitimate because its pair cap is6. The code does
  not silently apply this lemma to the other middle maxima.

The forward resource DP and backward verifier implement the same valid
relaxation. Both permit unused light pair mass; that enlarges an upper bound.
The producer's bounded mass applies only inside its allocation recurrence,
while the full budget remains in the constant term, matching the proof.

This bounded audit does not reperform every generic resource optimum or
the2,163,945-profile quota enumeration. Those are computed by the complete
inventory verifier. It checks their hypotheses and stored strict thresholds
for all159,041 preceding cut records and independently reviews the formulas.

## Disjoint accounting

Every new joint cut is absent from the23,164 inherited spectrum cuts and
135,877 preceding generic geometry cuts. Every joint cut occurs exactly once
in the276,791-profile input to the cube stage. Streaming subtraction of those
524 lines reproduces the final survivor file byte-for-byte, verified by its
SHA-256. Its final length is276,267 profiles.

The exact local table, branch certificates, method scopes, and subtraction
therefore support the524 additional whole-weight-profile exclusions.
They do not close any support/maximum cell or count residue placements and
fibre realizations. The unrestricted middle branch remains open.

The machine receipt and all reviewed file hashes are recorded in
`MIDDLE_CUBE_SCREEN_AUDIT.json`. Run the bounded audit with

    python3 research_round4/optimization/review_middle_cube_inventory.py
