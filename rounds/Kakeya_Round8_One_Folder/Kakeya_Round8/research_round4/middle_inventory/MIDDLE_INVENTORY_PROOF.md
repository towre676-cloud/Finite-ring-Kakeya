# Complete middle-range weight inventory

## Result and scope

This checkpoint enumerates every normalized weight multiset for a hypothetical
Kakeya set of size at most93 in either target ring, with exact maximum fibre
weight12 through18 and pair-active support10 through17. There are **2,163,945**
such total93 profiles. The certified screens leave **276,267** profiles.

All56 support/maximum cells remain nonempty. This is a complete **weight-profile
inventory**, not an enumeration of residue placements, tangent shapes, or
Kakeya constructions. The full middle branch remains open.

The earlier report's support ceiling18→17 was a genuine theorem, but it did
not describe the size of the region beneath that ceiling. The present list
provides that missing denominator and an explicit residual set.

## Exhaustive normalization

The binary residue support must satisfy S+S=F2^5. The inherited analytic
nine-point theorem states that nine residues determine at most28 nonzero
differences. It rules out support9, strengthening the elementary pair-count
condition binom(s,2)>=31. Smaller supports are also impossible.

At the other end, the complete Round3 theorem rules out support18 and the
earlier checkpoint rules out every larger support for maximum12..18.
Thus the remaining support range is exactly10..17 as a necessary range.

Delete all singleton fibres, which cannot participate in a primitive
four-point line. At fixed support s and exact maximum m in the current
range, sm>=10*12=120>93. Existing active fibres can therefore be enlarged
to total93 while never exceeding m. The original maximum remains present,
the support is unchanged, and every existing line persists. Hence every
<=93 candidate in this region is represented by one of the total93 profiles.

The forward producer enumerates nonincreasing part sequences. A separate
C++ verifier enumerates multiplicities of weights and independently checks
every resulting multiset. Both produce all56 cells and2,163,945 profiles.

## Complete disjoint accounting

| Stage | Profiles excluded | Remaining |
|---|---:|---:|
| All normalized middle profiles | — | 2,163,945 |
| Global pair-budget/maximal-direction-quota bounds | 1,728,113 | 435,832 |
| Inherited selected exact-spectrum certificates | 23,164 | 412,668 |
| Generic applications of accepted geometric/resource lemmas | 135,877 | 276,791 |
| Joint-spectrum cube-energy certificates | 524 | **276,267** |

The23,164 inherited spectrum cuts comprise17,381 at support15,4,696 at16,
and1,087 at17. They were already proved and are not credited as new cuts.
Their complete candidate, dual, and census files are identified by the
unchanged hashes in the earlier exact replay receipt.

The136,401 additional cuts are applications of established lemmas to this
newly enumerated range. They are disjoint from the inherited selected cuts
and from one another in the recorded stage order.

| Support | All weight profiles | After global quota screen | Final remaining |
|---|---:|---:|---:|
| 10 | 102,620 | 21,587 | 3,220 |
| 11 | 179,804 | 55,343 | 24,708 |
| 12 | 257,792 | 91,018 | 61,048 |
| 13 | 317,624 | 110,317 | 86,075 |
| 14 | 348,184 | 94,141 | 76,019 |
| 15 | 348,408 | 47,053 | 20,584 |
| 16 | 324,384 | 13,349 | 4,150 |
| 17 | 285,129 | 3,024 | 463 |

The exact56-cell table is in MIDDLE_COMPLETE_INVENTORY.json. For convenience,
the final table by exact maximum is:

| s | m12 | m13 | m14 | m15 | m16 | m17 | m18 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 10 | 178 | 332 | 528 | 581 | 615 | 554 | 432 |
| 11 | 1,600 | 2,488 | 3,739 | 4,029 | 5,153 | 4,395 | 3,304 |
| 12 | 5,249 | 7,224 | 10,044 | 9,994 | 12,242 | 9,547 | 6,748 |
| 13 | 10,239 | 12,058 | 15,668 | 13,670 | 16,306 | 11,192 | 6,942 |
| 14 | 12,886 | 11,691 | 15,433 | 10,862 | 14,065 | 7,454 | 3,628 |
| 15 | 5,397 | 3,009 | 4,211 | 2,196 | 4,127 | 1,241 | 403 |
| 16 | 1,265 | 516 | 782 | 381 | 929 | 221 | 56 |
| 17 | 156 | 49 | 92 | 48 | 100 | 17 | 1 |

## Global resource screen

The necessary doubled coverage demand is992. The global screen uses the
same proved heavy/light inequalities as Round2, with scalar cap

    M(p,q)=min(16,pq), except M(3,5)=13,M(3,6)=14,M(3,7)=15.

The exceptional three-point bounds follow by placing the three-point set
inside a binary plane and counting its four cosets. The local pair budget
is binom(w,2); at most q(w) directions attain floor(w/2), where

    q(w)=2^v2(w)-1                                   for even w,
    q(w)=max(2^v2(w-1),2^v2(w+1))-1                 for odd w.

All cutoffs0..9 are considered, in the fixed order2,3,1,4,0,5,6,7,8,9.
Endpoint heavy-edge losses are combined by the valid maximum of the
largest endpoint loss and half the total endpoint loss rounded upward.

The forward-DP producer and backward-recursion verifier agree on all
435,832 survivors, including each survivor's exact reported bound. The
independent checker also verifies every profile outside that list has a
strict bound below992. It does not trust a producer exclusion flag.

## Generic geometric screens and their hypotheses

These applications use the lemmas in
research_round3/middle/RESOURCE_COMPATIBILITY_LEMMAS.md. All selected heavy
fibres are the largest indicated number of weights. Each light pair cap
is at most the largest light cap ell. The local forward DP is independently
recomputed by backward recursion in the Python verifier.

The disjoint method counts are:

| Method | Additional cuts |
|---|---:|
| Total pair-square energy | 844 |
| Three heavy bases: one quota-three exception | 7,417 |
| Two heavy bases: correlated deleted direction | 1,855 |
| Eight heavy bases: six missing directions or at least nine | 113,067 |
| Nine heavy bases: sum-free missing directions | 5,377 |
| Maximal-direction bonus in the missing halfspace | 6,877 |
| Ten heavy bases: weak unique directions | 440 |
| **Total** | **135,877** |

The energy screen uses the frozen complete F2^5 pair-spectrum census to
bound sum Q(A). It excludes only when that sum is strictly below992.

The three-heavy test restricts every quota-three light fibre to two maximal
counts toward the three heavy bases, then permits the largest single uplift.
Only one residue can attain all three maxima, because the three maximal
directions form the nonzero points of a binary two-space.

The two-heavy test deletes their connecting direction. Its doubled demand
is960. It retains the correlated pair counts in all three directions of
the corresponding binary plane. The verifier regenerates the feasible
triples by taking every actual subset of a four-point plane and convolving
over all eight cosets, with total size at most18.

For eight heavy bases, the at-least-nine-missing-directions branch uses
unrestricted pair mass and a doubled threshold288. The exactly-six branch
uses the character-halfspace pair bound floor(w^2/4) and at mostthree
positive heavy-neighbour directions from each light vertex. Its doubled
threshold is192. Both branches must be strictly excluded.

For nine heavy bases, there are at leastthree missing directions and the
missing set is sum-free. The test uses floor(w^2/4) light pair mass and
at most(q(w)+1)/2 maximal-pair directions in the missing set. Its doubled
threshold is96. The prices are zero, so the bound is independent of the
number of missing directions and remains valid if there are more thanthree.

The halfspace bonus is used only after the eight-heavy at-least-nine branch
was separately excluded and only when every light cap is at mosteight.
For a heavy cap c>4, its extra contribution above four times the light pair
mass is bounded by (c-5)X+Y, where X uses the six largest light caps and Y
uses only the maximum-direction quota within the halfspace. The undoubled
threshold is96.

The ten-heavy test is applied only when exactly one heavy has cap six,
all other heavies have caps at mostfour, and every light weight is at most
three. If k heavy vertices have caps at mostthree and the total light pair
mass is L, then L>=min(3k,12) is necessary. No broader cap hypothesis is
silently substituted. Maximum13 is permitted here because its pair cap is
six, exactly as for maximum12; the lemma is expressed in pair caps.

These are specified certified screens. The inventory does not claim that
every possible price vector, every possible heavy subset, or every further
consequence of the lemmas has been optimized. The final list is the exact
complement of the credited disjoint cuts.

## Systematic joint-spectrum cube certificates

Let k be the number of weight-eight fibres. Branch on the actual number
r=0,...,k that are affine cubes. Every remaining weight-eight fibre is then
a noncube. For other weights no additional affine-shape hypothesis is made.

For a pair-count histogram h, put

    E(h)=sum_p h_p*p^2,
    g_L(p)=max(0,2*min(16,4p)-p^2-L).

Let T_r(h,L) be the sum of the r largest entries of the multiset containing
h_p copies of g_L(p). Define

    J(w,r,L)=max_h [E(h)+T_r(h,L)].

For w!=8 the maximum uses every complete-census spectrum of weight w.
For w=8 it omits precisely the cube spectrum h_4=7. Crucially, energy and
surplus are evaluated on the **same histogram before taking the maximum**.
This avoids combining the energy maximum of one shape with the surplus
maximum of another.

The accepted cube-direction theorem, with L=2lambda, gives the necessary
upper bound

    2*C_total <= 7*L*r + (32-2*L)*floor(r^2/4)
                 + sum_{nonselected fibres} J(w,r,L),    (1)

for every8<=L<=16. This screen searches the integer bank L=8,...,16.
For each excluded profile it records one valid L for every r=0,...,k,
with the right side of(1) strictly below992. There are524 excluded profiles
and2,498 covering r-branches. The local table has1,683 entries, every one
independently checked against every permitted full pair spectrum.

The independent verifier computes the largest r gains by consuming a
gain/multiplicity table, rather than using the producer's expanded sorted
list. It checks the saved attaining spectrum and the exact upper bound.
It then checks every recorded integer-price witness and every r branch.
For every final survivor, at leastone cube-count branch survives the full
finite price bank.

This is automatic certificate selection within one proved dual family.
It is not the full type-coupled LP proposed by the user. In particular,
270,164 of the276,267 final profiles already pass the r=0 noncube-energy
branch. Only6,103 profiles force at leastone cube by this energy test.
Thus this family alone cannot address most of the residual inventory
without additional shape-forcing constraints. Global unlabelled spectra
still discard actual residue adjacencies and orientation compatibility.

## Strategic interpretation

The middle region is now explicitly inventoried, but remains large:
276,267 weight profiles, before residue and shape realization. The maximum11
class count and maximum19 own-flag profile count measure different objects,
so they cannot be directly compared as fractions of the full search.

The assertion that every lower support is harder is not literally reflected
by this screen. Absolute residual counts peak at support13, and support10
has fewer survivors than support11. Both the number of raw profiles and the
effectiveness of the constraints vary with support. A sparse support can
also create more unique or missing directions and strengthen geometric
obstructions. This nonmonotonicity does not make the middle branch small;
it identifies where its present residual mass is concentrated.

Every support/maximum cell has survivors. No complete middle maximum stratum
and no entire support within10..17 is newly closed. The next structural
optimization must retain actual direction labels and common fibre shapes,
with ring-specific label translations at the exact-coverage layer.

## Reproduction and artifacts

Run from the workspace root:

    python3 research_round4/middle_inventory/verify_middle_inventory.py

This compiles and runs the independent C++ quota verifier, then performs the
Python arithmetic checks, verifies inherited certificate hashes, and checks
every stage's exact survivor subtraction. It requires a C++17 compiler and
Python's standard library; no optimization solver is needed.

The full final list is after_cube_weight_survivors.txt. Each line contains

    support maximum inherited_quota_upper weight_1 ... weight_support

The final bound column is the earlier quota bound, not an assertion that
the profile is realizable or an optimum under all later inequalities.
All56 cell counts, stage counts, and dependency hashes are recorded in
MIDDLE_COMPLETE_INVENTORY.json. The verifier can reuse a just-completed
quota replay via --reuse-quota-replay; the default command reruns it.

No Round2 or Round3 file was modified.
