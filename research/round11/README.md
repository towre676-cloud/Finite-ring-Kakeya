# Dimension five after Round 10

Base revision `67c0b623a59b4eb9893f6e93135b34d2b77ca8e9`. All results concern both $\mathbb Z/4\mathbb Z$ and $\mathbb F_2[\epsilon]/(\epsilon^2)$, dimension five, and a counterexample budget of 93 points. The pair-active support $S$ consists of residues whose fibres have at least two points. Removing singleton fibres preserves primitive lines. A marked role singles out one largest fibre, allowing ties, then moves its residue to zero.

## Reconstructed coverage

The established exclusions leave pair-active support at least 13. Exact maxima at most 10 and at least 20 are excluded by inherited reductions. Exact maximum 19 is closed using the inherited support-11/12 reduction and the checked maximum-19 collection, which excludes 3,798 tracked profiles. Exact maximum 11 on support 13 is closed by Round 8 and its inherited affine-class exclusions. These older proof streams retain their historical status. [Round 8 frontier](https://github.com/towre676-cloud/Finite-ring-Kakeya/blob/67c0b623a59b4eb9893f6e93135b34d2b77ca8e9/rounds/Kakeya_Round8_One_Folder/Kakeya_Round8/Kakeya_Research_Frontier_Round8.json)

On support 13 at each of maxima 12 and 13, the marked catalogue has 55 roles in 13 affine classes. Twenty-eight inherited roles plus 27 recovered or Round 10 roles cover each cell. The recovered campaign has 29 historical acceptances and 25 Round 10 acceptances. The 25 are backed by 26 accepted checker receipts because one case has two accepted variants. The audit checked the receipt scope and checker-log hashes, verified the 169 hub transports with the maintained Round 9 checker, and recomposed both sets of 55 roles. One Round 10 baseline proof was also replayed independently in this pass, as recorded in the verification receipts. [Round 10](https://github.com/towre676-cloud/Finite-ring-Kakeya/pull/1)

The maintained profile ledger has 182,526 sorted weight multisets in 34 cells. A fresh run of the Round 8 profile verifier reproduced all 950 certificates and the exact survivor-file hash. Intersecting its exact support and maximum keys with the two closed Round 10 cells gives 9,789 profiles at (13, 12) and 11,962 at (13, 13). These 21,751 profiles are excluded by complete placement coverage. The combined view therefore contains **160,775 profiles across 32 cells**. Partial marked exclusions at maxima 14–18 and the new heavy-label exclusions below receive zero whole-profile credit.

| Pair-active support | Max 12 | Max 13 | Max 14 | Max 15 | Max 16 | Max 17 | Max 18 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 13 | closed | closed | 15,535 | 13,596 | 16,122 | 11,095 | 6,847 |
| 14 | 11,683 | 11,472 | 15,243 | 10,806 | 13,911 | 7,381 | 3,543 |
| 15 | 4,665 | 2,888 | 4,013 | 2,142 | 4,069 | 1,217 | 368 |
| 16 | 1,101 | 500 | 709 | 347 | 889 | 204 | 43 |
| 17 | 123 | 45 | 76 | 39 | 91 | 12 | empty |

On support 13, the exact maxima 14, 15, and 16 each have 27 marked roles lacking a complete exclusion, distributed across 13 affine classes. Maximum 17 has 24 such roles across 13 classes, and maximum 18 has 16 across 10 classes. `coverage.json` gives every mask and class ID.

For middle maxima on supports 14–17, the profile counts are exact in the inherited ledger. The separate difference-cover catalogue contains 88, 113, 131 and 145 marked geometries, grouped here into 21, 23, 30 and 30 affine classes. The masks and affine groups are in `affine_orbits.txt`. These lists give the geometry before intersecting it with the weight constraints. The maintained evidence supplies no complete class-by-profile feasibility or exclusion table for these cells, so the audit records the two coordinates separately.

Exact maximum 11 has 42 affine classes without complete exclusion. Their class IDs belong to the maintained maximum-11 reduction, and `affine_orbits.txt` also maps them to the canonical geometry catalogue.

| Support | Remaining maximum-11 class IDs |
|---:|---|
| 14 | 126, 130, 131, 132, 133, 134, 139, 141, 142 |
| 15 | 151, 152, 153, 155, 156, 157, 158, 161, 163, 164, 165, 166, 167, 168, 169, 171 |
| 16 | 178, 181, 182, 183, 184, 185, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 204 |

## New exclusion on support 13 at maxima 14 and 15

Let $H$ be the heavy residues, whose fibres have weight at least four. Let $D(H)$ be their nonzero differences and write $M$ for the nonzero directions outside $D(H)$.

**At exact maximum 14 or 15 and support 13, every size-at-most-93 candidate must satisfy $D(H)=\mathbb F_2^5\setminus\{0\}$.** The [inherited incidence argument](../../rounds/Kakeya_Round8_One_Folder/Kakeya_Round8/research_round8/incidence/SUPPORT13_MAX15_HEAVY_COROLLARY.md) gives at least ten heavy fibres and at most two missing directions. If there are at least eleven heavy fibres, two light fibres supply at most $2\lfloor15/2\rfloor=14$ lifts in a missing direction. Only ten heavy fibres with one or two missing directions require new work.

In either case all three lights must have heavy partners and be active in every missing direction. Two active lights supply at most 14 lifts. A light-light edge consumes two lights and supplies at most one lift, so at most eight lifts are available in that case. The pair counts of any light are at most one per direction.

### Two missing directions

If $M=\{d,e\}$, each light fibre has weight three and its exact pair directions are $d,e,d+e$. All directions outside this plane rely entirely on heavy-heavy edges. The following exact finite geometry statement applies to every ten-point set $H$ with exactly two missing directions.

> Every vertex of $H$ belongs to an edge whose difference occurs on just that edge of $H$ and lies outside the missing plane.

The Python replay checks the 14,950 sets containing a fixed affine basis, of which 5,220 have exactly two missing directions. Normalization is complete because $D(H)$ has 29 directions, which cannot lie in a proper linear subspace. An independent C++ enumeration fixes the missing directions to the first two unit vectors. In each of their eight plane cosets it enumerates the empty set, each singleton, and either diagonal. That checks 1,141,504 ten-point sets, including 43,008 with exactly two missing directions, and verifies the same assertion.

An edge required to supply all sixteen lifts needs at least four quotient pair points at each endpoint. For pair-set size at most two the product bound gives at most 14. For a three-point pair set, its affine plane partitions binary four-space into four cosets. A partner occupying zero, one, or at least two points in a coset contributes at most zero, three, or four sums there. Full coverage requires two partner points in each coset, impossible with at most seven. Thus every heavy fibre has weight at least eight. The total mass is at least $9+9\cdot8+14=95$ at maximum 14, and at least 96 at maximum 15.

The same proof applies to support 14, maximum 11, ten heavy fibres, and two missing differences. In that scope a missing direction requires all four light fibres, since three supply at most 15 lifts. Every light has weight three and is active in the same plane. The mass is at least $12+9\cdot8+11=95$. On the nine open support-14 affine representatives, 3,176 ten-heavy labelings miss two directions. Only four have all required heavy partners, all in class 131. The two-missing sector is excluded throughout. This result adds zero whole-class exclusions to the maximum-11 ledger.

### One missing direction

Let $d$ be the unique missing direction. A weight-two light fibre contributes exactly the direction $d$. A weight-three light fibre has one of the fifteen direction triples $\{d,e,d+e\}$. The replay takes all choices at all three lights and identifies choices with the same weight and the same active directions on incident support edges. This projection preserves every edge capacity. For light-light edges it checks activity at both ends.

For a weight $w_a$ let $p_a=\lfloor w_a/2\rfloor$. For each active edge with endpoint pair ceilings $p,q\le7$, use
$$
C(p,q)=\begin{cases}
q+8,&p=3,\ 5\le q\le7,\\
p+8,&q=3,\ 5\le p\le7,\\
\min(16,pq),&\text{otherwise}.
\end{cases}
$$
The exceptional bound follows by maximizing the sum over the four plane cosets. An optimum places one point in every coset before assigning second points, since moving a second or later point into an empty coset increases the upper bound. This maximum also follows by enumerating integer occupancies of the four cosets. Ring carry translates edge sumsets and preserves their cardinalities.

A unique active heavy-heavy edge forces both weights to be at least eight. This gives a lower mass for each light choice. The three heavy partners in direction $d$ must have pair ceilings summing to at least sixteen. Each additional unit of pair ceiling above an adjustable lower weight costs at least two points because that lower weight is even. The hub has its fixed exact maximum, so this cost argument also applies when the hub is a partner.

For each choice surviving these lower bounds, the replay enumerates every integral heavy-weight assignment under the cap and budget. It rejects any direction whose active edge ceilings sum to less than 16. In the remaining assignments, if the other edges in a direction have upper capacity $U$, the chosen edge must contribute at least $16-U$. Inverting the same elementary bound with one endpoint fixed at its ceiling gives a lower bound on the other endpoint's directional pair count. One endpoint is incident to at most one edge in any direction, so the resulting multiset of requirements must fit in a single actual fibre spectrum.

| Replay count | Exact maximum 14 | Exact maximum 15 |
|---|---:|---:|
| Effective light choices | 114,466 | 114,466 |
| Rejected by private-edge weight floor | 109,345 | 111,925 |
| Rejected by missing-direction weight floor | 4,407 | 2,483 |
| Choices entering weight enumeration | 714 | 58 |
| Exact labelled weight assignments checked | 48,840 | 3,190 |
| Assignments rejected by directional capacities | 48,752 | 3,186 |
| Assignments rejected by a spectrum witness | 88 | 4 |
| Remaining in the one-missing sector | 0 | 0 |

The one-missing calculation covers the 27 roles previously open at each maximum. The other 28 have inherited exact-maximum coverage, so the statement holds on the whole support-13 catalogue. The 27 roles contain 519 ten-heavy labelings with one missing direction, of which 86 have all three required partners. Their 92 surviving weight leaves carry explicit spectrum witnesses. The independent leaf checker recomputes each displayed demand from the active edges and uses actual affinely normalized fibres. Weight eight requires 491 normalized subsets and yields seven pair histograms. Weight nine requires 2,930 subsets and yields nine. Every leaf has an obstruction at one of these two weights, giving a second route to the spectrum step with no dependence on completeness of the inherited spectrum file for these leaves.

### Clauses for a subsequent campaign

For each still-open marked role, let $L$ run through subsets of at most three nonhub residues. Whenever $S\setminus L$ misses a direction, no candidate can have all of $L$ light. Emit the clause $\bigvee_{a\in L} \operatorname{heavy}(a)$ for each inclusion-minimal such $L$. This uses the Round 10 positive-heavy projection format. No existing encoder guard or historical DIMACS input changes.

The replay tests all 8,073 heavy/light labelings per exact maximum across the 27 roles. The 735 minimal positive-heavy clauses reject 7,345 labelings and leave 728 full-cover labelings per maximum, including 74 with exactly ten heavies. These counts measure the geometry of labels. Some labels were already incompatible with earlier incidence bounds. The new result closes every remaining non-cover label, and neither maximum cell has a complete support-level exclusion. The conditional tetrahedral cut remains available to a later SAT campaign with its original type flags. The exclusion here uses the separate small-pair plane bound.

## Replay and scope

See the [independent verification report](INDEPENDENT_REVIEW.md) for the separate ledger reconstruction, the proof audit and the first proposed certification target.

Run from a checkout of the base revision with the proposed files applied. Restore the Git-hosted evidence and the Round 10 review archive using their maintained scripts. For the new mathematical exclusion, no SAT solver is needed.

```sh
r8=rounds/Kakeya_Round8_One_Folder/Kakeya_Round8
r9=rounds/Kakeya_Round9_Recovered_2026-11-04/Kakeya_Round9
r11=research/round11
python3 restore_evidence.py
python3 "$r9/research_round10/restore_round10.py" /path/to/Finite_Ring_Kakeya_Round10_Review.zip

python3 "$r11/audit_frontier.py" . > /tmp/kakeya-coverage.json
python3 "$r11/verify_missing.py" . /tmp/kakeya-coverage.json > /tmp/kakeya-exclusions.json
python3 "$r11/check_spectrum_leaves.py" /tmp/kakeya-exclusions.json
cmp "$r11/coverage.json" /tmp/kakeya-coverage.json
cmp "$r11/exclusions.json" /tmp/kakeya-exclusions.json

g++ -std=c++17 -O3 -Wall -Wextra -Werror "$r11/check_two_missing.cpp" -o /tmp/kakeya-two
/tmp/kakeya-two

imported="$r8/research_round6/imported_claude_round4"
g++ -std=c++17 -O3 -Wno-return-type -I "$imported/src" \
    "$r11/group_affine_orbits.cpp" -o /tmp/kakeya-orbits
/tmp/kakeya-orbits "$imported/data/orbits_all.txt" "$r11/maximum11_representatives.txt" \
    > /tmp/kakeya-orbits.txt
cmp "$r11/affine_orbits.txt" /tmp/kakeya-orbits.txt
```

The receipts distinguish fresh finite verification, archived proof evidence, and fresh historical proof replay. The replayed Round 10 target is mask 1101613334 at exact maximum 12, with unchanged CNF SHA-256 `e32ef48ad3630327a4feb64ab8ea4e37414c445c8c1266953e81b776aac9e795`. The compiler in this environment needed `-D_DEFAULT_SOURCE` to expose `getc_unlocked` when building the pinned DRAT-trim source in C99 mode. The source pin and proof input were unchanged. No new SAT search or proof-assistant formalization was used.

The remaining support-13 work at maxima 14 and 15 can start with the full-difference-cover labels. Support 14 at maximum 11 still requires its one-missing and full-cover sectors and the separate support-15/16 class ledger. The unrestricted 94-point lower bound and the all-dimensional law remain open.
