# Frozen M19 frontier after four round3 stages

The current M19 checkpoint has **3,798 remaining tracked profiles**:
896 with pair-active support size 11 and 2,902 with support size 12.
Round3 excludes **26,673 whole profiles** from its 30,471-profile input.
Every cut applies to all residue placements and all tangent fibre shapes
matching the profile, for both rings in the project.

These objects are weight/own-direction profiles. They are not actual Kakeya
sets, not affine support classes, and not counts of individual placements.
Survival means that the necessary conditions used so far do not exclude a
profile. It does not show that the profile is realizable.

## The four disjoint steps

| Step | Support 11 excluded | Support 12 excluded | Combined remaining |
|---|---:|---:|---:|
| Frozen round2 input | — | — | 30,471 |
| Common affine-rank modes | 11,527 | 6,077 | 12,867 |
| Analytic deleted-direction profile | 1 | 0 | 12,866 |
| Common own-periodic modes | 95 | 136 | 12,635 |
| Actual unique-edge support roles | 8,837 | 0 | 3,798 |

The final lists are `s11_final_round3_survivors.txt` and
`s12_final_round3_survivors.txt`. The consolidated manifest binds each
stage's input, certificate, verifier, proof, replay receipt, and survivor
hashes. `M19_ROUND3_DISJOINT_EXCLUSIONS.jsonl` records the stage credited
with each newly excluded parent profile. No round2 file was changed.

## What the new mathematics contributes

The first stage fixes one affine-rank mode for each positive-own fibre of
weight 6, 7, or 8. The same mode must work for every edge involving that
fibre. If two such fibres have rank at most 3, own positivity forces a
shared two-dimensional residue span, limiting their actual quotient
capacity to 8. For a group of r such fibres, the outside-support mutual
capacity is at most 4 floor(r^2/2). Exact pair spectra and integer matching
duals enforce the resulting endpoint budgets.

The second stage has a short analytic proof. For parent profile 63342,
delete the direction joining the hub and the weight-12 fibre. The other
30 directions require doubled capacity 960. Seven own-zero weight-8
fibres contribute at most 128 each and two own-positive weight-3 fibres
at most 30 each: 7*128+2*30=956. This contradiction uses the joint
three-direction geometry inside a two-plane.

The third stage fixes whether each even positive-own fibre is invariant
under its own residue direction. Two own-periodic fibres have pair-label
sets with a common nonzero quotient period, so their actual sumset has
size at most half the product of the two pair counts. The exact periodic
block census comes from all 50,642 relevant subsets of F_2^4. The
nonperiodic channel uses a stated upper relaxation.

The fourth stage uses actual support incidence. A unique edge in an
outside-support direction forces both endpoint weights to be at least
8, under the checked outer-weight bound 14. A unique hub edge forces
its outer endpoint to be own-positive with weight at least 4. Every
covering support of size 11 has at most one vertex lacking both roles.
A complete normalized census yields only 10 role-count patterns for
size 11 and 15 for size 12. Hall obstructions between these roles and
fibre attributes account for the final 8,837 cuts.

## Exact frontier for a further attack

The next unresolved constraint is the simultaneous placement of all
fibre attributes on one actual marked support, together with directional
capacities on every edge. The current role test retains only counts of
vertex roles. It does not retain which two forced vertices are joined,
which directions share their endpoints, or the capacities left in a
direction after its hub contribution is accounted for.

For support size 11, every one of the 896 surviving profiles has an
attribute allocation that passes at least one of the 10 role patterns.
That allocation may still fail the actual edge incidence or the common
shape requirements. A useful next test would assign the weight/flag
types to representatives of each marked support, retain the exact
direction edge matchings, and prove that every assignment violates a
directional demand or a common-fibre resource bound. A contradiction
for one placement alone must not be counted as a whole-profile cut.

For support size 12, the role census includes a pattern with no forced
vertices. Thus no further whole-profile exclusion follows from these
two roles alone. Supports in that pattern have at least two residue
edges in every direction. Their paired-edge geometry must be coupled
to the assigned weights and own flags; using the same scalar capacity
independently in each direction would discard the new geometric issue.

An optional structured subcase is the period-paired size-12 support:
six cosets of a nonzero residue period. There are five outer coset
pairs besides the hub coset. Cross-directions between two coset pairs
impose two different matching inequalities on the same four fibre
caps. These are promising necessary constraints, but **no new cut
from this observation is credited in the checkpoint**.

The M19 branch and the unrestricted dimension-five theorem remain open.
This checkpoint provides proved exclusions and exact, reproducible
survivor lists for continuing the attack.

## Replay order

Run the four verifiers in order:

    python research_round3/m19/verify_common_shape_certificates.py
    python research_round3/m19/verify_deleted_direction_profile.py
    python research_round3/m19/verify_own_periodic_certificates.py
    python research_round3/m19/verify_unique_edge_roles.py
    python research_round3/m19/build_m19_round3_manifest.py

The verifiers use exact integers and the frozen round2 spectrum data.
The last command checks disjoint profile IDs and exact sequential set
subtraction, then writes the manifest and final survivor lists. Replay
receipts include elapsed times, so their file hashes can change on a
fresh replay; mathematical certificate and survivor hashes remain fixed.
