# Round-three M11 result: all remaining support-seventeen classes are excluded

## Verified conclusion

The five remaining exact-maximum-eleven affine-support classes of pair-active support17, with frozen orbit IDs

    367,373,374,376,377,

are now excluded over both Z/4Z and F_2[epsilon]/(epsilon^2), for total size at most93. Together with the inherited complete support reduction and round-two support bound, this reduces the M11 frontier from57 to **52 open classes**, all of support13 through16:

| Support | 13 | 14 | 15 | 16 |
|---|---:|---:|---:|---:|
| Open classes | 4 | 9 | 16 | 23 |

This closes whole support classes, not just selected weight assignments. The inherited affine-support census, frozen local energy envelopes, and minimum-weight constraints are explicit dependencies; this continuation does not claim to rederive that census. The unrestricted theorem and the full M11 branch remain open.

## 1. Partition normalization and exact assignment duals

Delete singleton fibres and pad the existing pair-active fibres to total93 without exceeding11. This preserves coverage, support17, and the pre-existing maximum11. Every hypothetical example therefore yields a nonincreasing partition of93 into seventeen parts between2 and11, with first part11.

There are21,822 such partitions. The independently replayed, previously proved complete-graph resource inequality excludes21,081; round-two geometry excludes631 further partitions. This leaves110 partitions.

For a fixed support S and residue a, the frozen source supplies a valid local active-direction pair-energy envelope Q_a(w), and a necessary minimum weight m_a. Every Kakeya realization satisfies

    992 <= sum_a Q_a(w_a).

For each of the110 partitions and five support classes, we maximize this right side over assignments of the weights to residues, respecting the minimum weights. The exact assignment producer outputs integer potentials alpha_a,beta_j such that

    alpha_a+beta_j >= Q_a(w_j)

for every allowed assignment edge. Their sum is an upper bound on every assignment's total energy. A sum below992 excludes the entire support/profile pair. The independent verifier checks these550 sets of integer inequalities directly; it does not run or trust an assignment optimizer.

Two additional globally valid profile exclusions then finish classes373 and376. Only the three profiles P,Q,R below remain on the other three supports.

The exploratory full-spectrum calculation is not needed for any claimed exclusion in this result. All its34 cuts also follow from the frozen local envelopes and assignment duals.

## 2. Two universal nine-heavy profile exclusions

The profiles are

    A=(11,8^8,3^2,2^6),
    B=(11,8^8,4,2^7).

Choose the nine large fibres as heavy. A nine-point residue set determines at most28 nonzero differences, so at least three directions have no heavy-heavy edge. All pair counts are at most five; in any such direction, total low pair mass must be at least four to cover sixteen lifted directions.

The low pair budgets are12 and13 respectively. Hence exactly three directions are missing. Those three directions are linearly independent: if they were the three nonzero elements of a two-space, the heavy set could occupy at most one point in each of its eight cosets, contradicting its size nine.

The missing directions therefore lie in a character halfspace. A three-point fibre supplies at most two pairs there, and a four-point fibre at most four. The actual restricted low budgets are at most

    2+2+6=10  for A,
    4+7=11    for B,

both below the required12. These exclusions are uniform over all residue placements and tangent sets.

## 3. The only remaining support/profile pairs

After the assignment-dual and preceding geometric cuts, the exact list is:

| Profile | Weights | Supports still requiring analysis |
|---|---|---|
| P | (11,8^7,7,4,3,2^6) | 367,374,377 |
| Q | (11,8^7,6^2,2^7) | 377 |
| R | (11,8^7,7,5,2^7) | 377 |

The independent verifier exhaustively checks this list against all110 partitions on each support. No omitted partition or weight assignment is assumed harmless.

## 4. Exact low-fibre patterns for P and R

Choose the nine largest fibres as heavy. For P the remaining pair budget is6+3+6=15, so the missing heavy directions are exactly three independent vectors F={d_1,d_2,d_3}.

For R the remaining pair budget is10+7=17, permitting at most four missing directions. A missing set for nine heavy points cannot contain a triangle, by the same two-space coset argument. If four directions were missing, the difference graph induced on a five-point low fibre would be triangle-free and thus have at most6 edges. Together with the seven two-point fibres, the restricted budget would be at most13, below4*4=16. Thus R also has exactly three independent missing directions.

For three independent directions, the difference graph is a disjoint union of three-dimensional cube graphs. A four-point subset has at most4 edges, with equality only for a square. A three-point subset has at most2 edges, with equality a two-edge path. A five-point subset has at most5 edges: a bipartition of sizes2 and3 could have6 only by containing K_(2,3), but two cube vertices have at most two common neighbours. Equality5 is a square with one additional leaf.

Therefore P has restricted low budget at most4+2+6=12, and R at most5+7=12. Both must attain equality, so every missing direction has exactly four low pairs, every low fibre attains its indicated maximum, and every two-point low fibre places its sole pair in F.

Every positive low pair count must face a heavy partner. An inactive count p>=1 leaves total capacity at most5(4-p)<=15. A low-low edge with positive counts p,q leaves capacity at most

    pq+5(4-p-q)<=11,

since p+q<=4. Both fail to cover16 lifted directions.

These equality cases determine the complete low-fibre pair spectra, independently of tangent translations:

- A four-point square using d_i,d_j has pair count2 on d_i,d_j,d_i+d_j and zero elsewhere.
- A three-point path using d_i,d_j has pair count1 on those same three directions.
- A five-point square-plus-leaf has count2 on a two-dimensional direction plane's three nonzero vectors, and count1 on its complementary coset inside span(F). Its counts on F are a permutation of(2,2,1).
- A two-point fibre has count1 on its selected direction in F and zero elsewhere.

Thus a complete finite placement check needs no search over tangent point subsets: it enumerates heavy residues, the finitely many low pair-count patterns, and the positions of weights11 and7 among the heavy fibres.

## 5. Independent complete P/R placement replay

For each of the four support/profile cases, the verifier regenerates all24,310 nine-subsets of the seventeen-point support. It keeps exactly those with28 differences, derives F, and requires every selected low pair direction to have a heavy partner. It then assigns every low two-point pair to one of the three directions, subject to the necessary four-pairs-per-direction equality.

Finally it assigns the weights11 and7 to every possible pair of distinct heavy residues. It rejects minimum-weight violations, then applies the frozen active-energy envelope, then checks all31 per-direction capacities with the exact low pair spectra and heavy endpoint caps.

| Support/profile | Heavy subsets with28 differences | Low direction assignments | Assignments meeting minimum weights | Passing energy | Passing all capacities |
|---|---:|---:|---:|---:|---:|
| 367/P | 1,983 | 48 | 0 | 0 | 0 |
| 374/P | 1,971 | 492 | 864 | 0 | 0 |
| 377/P | 2,082 | 432 | 0 | 0 | 0 |
| 377/R | 2,082 | 360 | 2,592 | 1,872 | 0 |

The C++ producer and independently written Python replay agree on these counts. No solver, timeout, node cap, or assumed affine equivalence enters this placement enumeration.

## 6. Profile Q: a forced-period rank obstruction

Choose its ten large fibres as heavy, leaving seven two-point fibres. Let r count missing heavy directions. Deleting a heavy vertex leaves nine points and hence at most28 differences. If u(a) counts the directions whose unique heavy-heavy edge is incident to a, then

    u(a)>=max(0,3-r).

Call the two six-point heavy fibres weak. A unique heavy edge incident to one weak vertex has capacity at most15 and needs at least one low pair. If both endpoints are weak, capacity is at most9 and one low pair adds at most5, so it needs at least two low pairs. Missing directions cost at least four each. Thus

    7 >=4r+u(a)+u(b) >=4r+2max(0,3-r).

For r>=1 the right side is at least8. Therefore all31 directions occur among the ten heavy residues.

The support377 has exactly96 ten-subsets with this property. For each, the verifier considers all45 placements of the two weak weights. If u(a)+u(b)>7, the preceding budget excludes the placement. There are2,304 such cases. In each of the remaining2,016 cases the sum is exactly6, so at most one low pair can be used in any direction outside the weak unique-edge directions.

For a nonweak heavy vertex v, define E_v to be its unique-heavy-edge directions whose other endpoint is also nonweak. In a direction of E_v with no low pair, the unique heavy edge must cover all16 lifted directions by itself. If v has weight8, its pair count must therefore be four: a count at most three against the other endpoint's cap at most five supplies at most15.

Hence all but at most one direction of E_v must be translation periods of the eight-point tangent fibre. The verifier provides at least two nonweak vertices v for every one of the2,016 cases such that

    rank(E_v after deleting any one direction)>=4.

At most one of these vertices can receive the weight11. Another has weight8 and would have a period group of order at least16, impossible for an eight-point set. This excludes every placement of Q.

The rank certificate checks the actual96 heavy subsets of support377. It does not rely on a global classification of ten-point difference bases.

## 7. Exact outputs and replay

Run both independent verifiers:

    python verify_s17_envelope_duals.py
    python verify_remaining_s17_placements.py

Authoritative receipts are `S17_ENVELOPE_INDEPENDENT_REPLAY.json` and `S17_PLACEMENT_INDEPENDENT_REPLAY.json`. The assignment certificate file contains550 exact duals. `Q_FORCED_PERIOD_RANK_CERTIFICATES.json` records the2,016 surviving weak-placement cases and their explicit robust direction sets.

The frozen support and energy source file is hashed in the receipts. The new frontier file removes exactly the five named orbit IDs from the previous57 open classes. Every remaining maximum-eleven support of size17 is thereby closed; no claim is made about any support16 class.
