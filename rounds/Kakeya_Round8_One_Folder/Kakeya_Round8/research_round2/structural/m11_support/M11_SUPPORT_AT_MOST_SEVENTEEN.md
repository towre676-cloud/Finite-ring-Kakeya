# Final M11 continuation: pair-active support is at most seventeen

## Theorem and exact frontier change

For either R=Z/4Z or R=F_2[epsilon]/(epsilon^2), every Kakeya set K subset R^5 with |K|<=93 and exact maximum residue-fibre size11 has pair-active residue support of size at most17.

This excludes **73 whole affine-support classes** from the previously open130-class M11 frontier. The new frontier contains **57 open classes**, distributed as follows:

| Pair-active support size | 13 | 14 | 15 | 16 | 17 |
|---|---:|---:|---:|---:|---:|
| Remaining classes | 4 | 9 | 16 | 23 | 5 |

The previously completed support>=19 stage excluded59 classes. The present extension excludes the14 additional classes of support18. These are cumulative counts, not disjoint claims to be added again to the73 total.

The complete independent replay covers **121,336** normalized weight partitions: **121,147** are excluded by exact complete-graph resource inequalities, and the remaining **189** by the analytic geometry below. The latter comprise the previous29 boundary profiles at support19 or20 and160 additional profiles at support18.

The M11 branch itself remains open, as does the unrestricted n=5 Kakeya theorem. No support17 search was undertaken in this continuation.

## 1. Normalization and arithmetic stage

The normalization, pair budgets, maximal-direction quotas, sharp three-point sumset cap, and complete-graph inequality are proved in `M11_SUPPORT_AT_MOST_EIGHTEEN.md` and its stated dependencies. The same proof applies with s>=18: singleton fibres can be deleted, and the existing pair-active fibres can be padded to total93 without exceeding11, because 18*11>93 and one original fibre already has size11.

Thus it suffices to enumerate every nonincreasing partition of93 with first part11, all other parts at least2, and support18..32. The producer uses forward dynamic programming; the independent verifier uses backward allocation recursion, freshly regenerates every partition, and does not trust producer decisions.

There are21,469 such exact-maximum-eleven partitions with support18. The resource inequality excludes21,309, leaving160. The rest of this note supplies complete geometric certificates for those160, as well as the earlier29.

## 2. Geometric facts about eight and nine heavy residues

For eight residues T subset F_2^5, let F be the set of missing pair differences and r=|F|. The proved eight-residue gap theorem states

    either r=6 or r>=9.

When r=6, T and F admit the normal form

    T=<h,b> union {c,d,e,h+c+d+e},
    F={b,b+h}+{c+d,c+e,d+e},

where h,b,c,d,e form a basis of F_2^5. In particular F lies in one character halfspace.

For completeness, the gap uses only elementary pair counting. Every eight-set in F_2^5 contains an affine plane by the augmented relation-code argument. If one direction supports three pairs, the contained union of those three parallel pairs already has duplicate excess8. Otherwise all pair counts are at most two, and duplicate excess equals three times the number of affine planes. Thus duplicate excess between3 and5 must equal3, giving exactly six missing directions. The full normal-form proof is in `../PROFILE_B_SUPPORT19_ANALYTIC_EXCLUSION.md`.

The nine-residue theorem used here is

    every nine-point subset of F_2^5 determines at most28 nonzero differences.

Its complete analytic proof is in `../../middle/DIFFERENCE_AND_LIGHT_RESOURCE_LEMMAS.md`, with an independent root audit. No affine-orbit census is needed for either fact.

### A new consequence: at most three heavy neighbours through F

In the eight-point normal form, every residue a has

    #{d in F : a+d in T} <=3.                                (2.1)

To prove this, quotient by H=<h>. In that quotient, the two classes0 and b each contain two points of T, while the four classes

    O={c,d,e,c+d+e}

each contain one. Put E=<c+d,c+e>\{0}; F projects to b+E.

Write the projected a as beta*b+w, w in <c,d,e>. If beta=0, the translate a+F can meet only the T-class b, giving at most two points. If beta=1 and w lies in the even-parity plane <c+d,c+e>, it can meet only the T-class0, again giving at most two. In the remaining case, w+E consists of three of the four odd-parity classes O, giving exactly three or fewer points. This proves(2.1).

## 3. The strict eight-heavy and nine-heavy cuts

All fibre pair counts are at most five. Choose any eight residues as heavy, and call the remaining fibres low. For a direction d missing from the heavy pair differences, every contributing residue edge has a low endpoint. If m_d is total low pair mass in that direction, its capacity is at most5m_d, so

    m_d>=4.                                                 (3.1)

Write

    P_8=sum_low binom(w_i,2),
    Q_8=sum_low floor(w_i^2/4).

If P_8<=35, (3.1) forces r<=8, hence the gap theorem forces r=6. The six missing directions lie in a character halfspace, where total low pair mass is at most Q_8. Thus **P_8<=35 and Q_8<24 exclude the profile**.

This excludes154 of the160 support18 boundary profiles, and all29 support19/20 boundary profiles.

Alternatively select nine heavy residues. At least three directions are missing, by the nine-residue theorem. Inequality(3.1) then requires at least12 low pairs. Therefore **P_9<12 excludes the profile**. This removes one more support18 profile, with weights

    [11,8,8,8,8,8,8,8,8,2,2,2,2,2,2,2,2,2].

Exactly five support18 profiles remain after these two steps.

## 4. Four equality profiles excluded by the three-neighbour limit

The following four profiles all satisfy P_8<=35 and Q_8=24 when the first eight weights are selected as heavy:

    A: [11,9,8,8,8,8,7,7,7,4,2,2,2,2,2,2,2,2],
    B: [11,8,8,8,8,8,8,7,7,4,2,2,2,2,2,2,2,2],
    D: [11,8,8,8,8,8,8,6,6,5,3,2,2,2,2,2,2,2],
    E: [11,8,8,8,8,8,8,6,6,4,4,2,2,2,2,2,2,2].

The eight-heavy argument again forces r=6. Since the six directions require at least24 low pairs altogether and Q_8 permits at most24, equality holds throughout:

1. m_d=4 for each d in F;
2. every low fibre attains its maximum cross-halfspace pair count floor(w_i^2/4), with all those pairs having differences in F.

Moreover, **every positive low pair count in F must face a heavy partner**. If a low fibre has p>=1 pairs but no contributing partner, the other low pair counts total at most4-p, giving capacity at most5(4-p)<=15. If an active edge joins two low fibres with counts p,q>=1, then p+q<=4 and total capacity is at most

    pq+5(4-p-q)<=11.

Both contradict the required16. Thus all positive low counts in F must use heavy-low edges.

But by(2.1), each low residue can face heavy partners in at most three directions of F. In profiles A and B, the low seven-point fibre must contribute floor(49/4)=12 pairs in F. Three directions can supply at most3+3+3=9. In profiles D and E, the low six-point fibre must contribute floor(36/4)=9 pairs in F. A six-point fibre has at most one direction with three pairs, so any three directions supply at most3+2+2=7.

These contradictions exclude all four profiles, uniformly over all residue placements and tangent subsets.

## 5. The final profile: deletion and unique heavy edges

The final profile is

    C: [11,8,8,8,8,8,8,6,6,6,2,2,2,2,2,2,2,2].

Choose its first ten residues as heavy, leaving eight two-point fibres. Let r count the directions missing from the heavy-heavy edges. Each costs at least four low pairs, as before.

For a heavy residue a, let u(a) count directions whose unique heavy-heavy edge is incident to a. Removing a leaves nine heavy residues. A direction disappears upon deletion exactly when it had such a unique edge, so the nine-residue theorem gives

    (31-r)-u(a)<=28,
    u(a)>=max(0,3-r).                                       (5.1)

Call the three six-point heavy fibres weak. A direction with a unique heavy-heavy edge incident to one weak vertex has heavy capacity at most3*5=15, so it requires at least one low pair. If both endpoints are weak, its heavy capacity is at most9, and one additional low pair contributes at most five, still short of16; it requires at least two low pairs.

Thus the required number of low pairs is at least

    4r + sum_{three weak a}u(a)
      >=4r+3max(0,3-r)
      >=9.

Only eight low pairs exist. This contradiction excludes C. Missing-heavy directions and unique-heavy directions are disjoint, so the lower bound does not double-count demand. A direction with two weak endpoints is intentionally counted twice and does require two low pairs.

This argument was independently derived by the middle-maxima agent and independently audited by both root and the structural agent. Its reusable form and local controls are saved in `../../m11_extension/TEN_HEAVY_RESIDUES_AND_PROFILE_C.md`.

## 6. Replay and exact ledger

Run:

    python verify_cap11_support_through18.py

The verifier freshly checks all121,336 partitions, writes189 geometric certificates, validates the frozen130-class source frontier, and maps the support>=18 theorem to precisely73 newly excluded orbit IDs. It records the57 remaining IDs, their support distribution, and the hashes of both inherited source files.

Authoritative new outputs:

- `M11_SUPPORT_THROUGH18_INDEPENDENT_REPLAY.json`;
- `M11_SUPPORT_THROUGH18_GEOMETRIC_CERTIFICATES.json`.

The previous59-class receipt remains available as a separate intermediate stage. The final73-class receipt supersedes it for the current M11 frontier.
