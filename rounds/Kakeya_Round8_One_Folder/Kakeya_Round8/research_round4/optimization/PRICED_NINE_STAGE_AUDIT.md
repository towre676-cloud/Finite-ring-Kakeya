# Audit of the single-heavy priced-nine stage

**Verdict: PASS.** This is a bounded mathematical/code cross-check within
the same model-agent session, not external human review.

The stage starts from the frozen276,267-profile middle inventory, excludes
512 additional profiles, and leaves275,755. Exactly one support/maximum cell
becomes empty: support17, maximum18. The hand proof of its sole previous
profile is in `M18_SUPPORT17_BOUNDARY_PROOF.md`.

## Validity of the priced resource inequality

Choose nine heavy residues and let F be their missing directions, r=|F|.
The nine-point difference bound gives r>=3; the missing set is sum-free.
For a light fibre of weight w, its pair mass in F is at most floor(w^2/4),
and at most(q(w)+1)/2 of those directions attain its maximum pair count.
Each of its nine heavy-neighbour directions is distinct.

Let ell dominate every light pair cap. Charge a nonnegative price t for
each positive light pair count on an edge to the selected largest heavy
vertex. The local doubled resource score is

    ell*mass+max sum_j [2M(x_j,h_j)-ell*x_j-t*[j=0 and x_j>0]].

The selected heavy vertex has at most one such edge in each direction of F,
so restoring all price charges costs at most r*t. Let U be the sum of light
row maxima. Then

    2*C_F<=U+r*t.

If U+3t<96 and0<=t<=32, then for every r>=3,

    U+r*t-32r=(U+3t-96)+(t-32)(r-3)<0.

This contradicts the necessary doubled coverage32r. The proof counts
positive light incidences even if the heavy endpoint has no pair; this is
a safe overcount, and there are still at most r incidences.

## Exact inactive/active split

For each light fibre, let a_i be the maximum unpriced score conditional on
zero pair count toward the priced heavy, and b_i the maximum conditional on
a positive count there. The exact priced row is

    max(a_i,b_i-t).

The producer computes the other eight slots by forward DP and uses prefix
maxima for their available mass and maximal-count budgets. The audit uses
a separate backward recursion through all nine slots, forcing the final
hub slot to be zero or positive. Both apply the same proved pair and quota
constraints; the local maximizing allocations may differ between fibres,
which only enlarges this upper relaxation.

## The integer price bank is complete for this family

Put delta_i=max(0,b_i-a_i). Then

    min_(t>=0) [3t+sum_i max(a_i,b_i-t)]
      =sum_i a_i +sum of the three largest delta_i.

For any t, the rightmost sum is at most3t+sum_i(delta_i-t)_+.
Equality holds at a threshold between the third and fourth largest positive
delta values, or at t=0 if at mostthree are positive.

All local scores are integers. Removing the active hub allocation leaves
an allocation feasible for the inactive row, so

    b_i-a_i<=max_(p>=1)[2M(p,h_0)-ell*p]<=32-ell<=31.

Thus an integer price in0..32 attains the exact continuous optimum. This is
not merely a numerical sampling of the one-parameter family. It also does
not optimize the larger family of independent prices on all nine heavies.

## What the bounded checker verifies

`review_priced_nine_stage.py` imports no producer or inventory verifier. It
recomputes370 distinct inactive/active row modes across every saved cut,
checks all512 strict coverage witnesses, and verifies that each saved
witness equals the closed-form continuous optimum above. The minimum gap
is two in doubled units.

Each cut occurs exactly once in the prior276,267-profile list and occurs in
none of the earlier generic or joint-cube cuts. Streaming subtraction
reproduces `after_priced_nine_survivors.txt` byte-for-byte, checked by SHA-256.
The only newly empty cell is(17,18).

The saved machine receipt is `PRICED_NINE_STAGE_AUDIT.json`. Replay:

    python3 research_round4/optimization/review_priced_nine_stage.py

This bounded audit checks the supplied cuts and their exact subtraction.
The branch owner's full stage verifier additionally checks the entire
survivor complement against the complete one-hub price screen.
