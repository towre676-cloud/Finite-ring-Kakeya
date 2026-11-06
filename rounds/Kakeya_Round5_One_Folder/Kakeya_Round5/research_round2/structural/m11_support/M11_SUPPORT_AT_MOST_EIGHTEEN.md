# A new whole-support exclusion for the exact maximum-eleven branch

## Theorem

Let R be Z/4Z or F_2[epsilon]/(epsilon^2). If K subset R^5 is Kakeya, has at most93 points, and has exact maximum residue-fibre size11, then its pair-active residue support has size at most18.

Consequently this continuation excludes all59 formerly open M11 affine-support classes of sizes19 through24, reducing the inherited130 open classes to71. This is a whole-support-class exclusion, not merely the exclusion of selected weight assignments.

The remaining class counts are:

| Support size | 13 | 14 | 15 | 16 | 17 | 18 |
|---|---:|---:|---:|---:|---:|---:|
| Remaining classes | 4 | 9 | 16 | 23 | 5 | 14 |

This does not close the entire M11 branch or the unrestricted n=5 theorem.

## 1. Complete normalization

Deleting singleton residue fibres preserves every primitive four-point line. Let s be the pair-active support size. For s>=19, after deleting singleton fibres, add tangent points to existing pair-active fibres until the total is93, never exceeding11. This is possible because 11s>=209>93; a pre-existing eleven-point fibre preserves exact maximum11. Padding preserves all original lines and does not change the pair-active support.

Thus every hypothetical example in the excluded range produces a nonincreasing partition

    11=w_1>=w_2>=...>=w_s>=2,       sum_i w_i=93,
    19<=s<=32.

The exhaustive arithmetic stage enumerates every such partition, with no assumption about its geometric realizability.

## 2. Necessary complete-graph capacity bound

For a fibre of weight w_i define c_i=floor(w_i/2) and b_i=binom(w_i,2). The pair allocations to distinct residue neighbours use distinct directions, so their total is at most b_i. At most

    r(w)=2^v2(w)-1                                 (w even),
    r(w)=max(2^v2(w-1),2^v2(w+1))-1                (w odd)

selected directions attain the maximum count c_i.

An edge with endpoint pair counts p,q covers at most M(p,q) lifted directions, where M=min(16,pq), except M(3,5)=13 and its symmetric value. This is the previously proved three-point sumset cap. All31 residue directions require16 lifted directions, so the total complete-graph capacity must be at least496.

For each cutoff ell, split the vertices into heavy c_i>ell and light c_i<=ell. Optimize each light endpoint's pair budget against all heavy capacities, charging remaining pairs at rate ell; optimize each heavy endpoint's budget against the other heavy capacities and subtract the unavoidable shared-edge deficit. These are precisely inequalities(1)-(2) in the accompanying earlier proof `research_round2/middle/GLOBAL_SUPPORT_REDUCTION_PROOF.md`.

The C++ producer uses a forward allocation dynamic program. The independently run Python verifier regenerates the partitions and uses backward allocation recursion, recomputing every exclusion. It does not read a producer decision or numerical solver result. A certified doubled capacity below992 excludes the whole weight partition.

This resource test excludes every partition at supports21..32. It leaves five partitions at support20 and twenty-four at support19. The next two lemmas exclude all29 together.

## 3. A gap theorem for the differences of eight residues

Let T be any eight-point subset of F_2^5, let q be its number of nonzero pair differences, and let r=31-q be its missing-direction count.

**Lemma.** Either r=6 or r>=9. If r=6, the six missing directions lie in one affine character halfspace; more precisely, they form an affine three-flat with an affine line removed.

First, T contains an affine plane. Form the augmented point matrix with columns (1,t). Its kernel has dimension at least two. With no weight-four relation, its nonzero vectors would have even weight at least six. Two independent vectors and their sum would have total weight at least18, whereas their coordinatewise total weight is at most16. Thus there is an affine plane, so at least three pair repetitions occur and q<=25, r>=6.

Write

    D=28-q=sum_{d!=0}(p_T(d)-1)_+.

If p_T(d)>=3 for some d, T contains six points forming three full d-cosets. Those six points are an affine three-flat with one d-coset removed: after translation they are the union of three of the four d-cosets in a three-flat. Their pair spectrum is one count three and six counts two, with total pair mass15 and only seven differences. They already have duplicate excess8. Adding points can never decrease duplicate excess, hence D>=8.

Therefore, if r<=8, then D=r-3<=5 and every pair count is at most two. Let Z be the number of affine planes in T. Each affine plane supplies exactly three partitions into parallel pairs, giving

    sum_d binom(p_T(d),2)=3Z.

With pair counts at most two, the left side is D. Thus D is a positive multiple of three and D<=5, forcing D=3 and r=6. This proves the gap.

For r=6 there is exactly one affine plane. The full analytic classification is proved independently in `../PROFILE_B_SUPPORT19_ANALYTIC_EXCLUSION.md`, Lemma2. In coordinates it says

    T=<h,b> union {c,d,e,h+c+d+e},

where h,b,c,d,e are independent, and its missing directions are

    F={b,b+h}+{c+d,c+e,d+e}
     =(b+<h,c+d,c+e>) \ (b+<h>).

All lie in the halfspace ell=1 with ell(b)=1 and ell(h,c,d,e)=0.

## 4. A uniform boundary-profile exclusion

Select the first eight fibres of any surviving partition as the heavy residue set T; all remaining fibres are low. Every fibre has pair count at most five, since every weight is at most eleven.

For a direction d missing from T+T there is no heavy-heavy residue edge. Let m_d be the total tangent d-pair count in all low fibres. Every heavy-low edge contributes at most five times its low pair count, and every low-low edge contributes at most five times the sum of its low endpoint counts. Thus

    16 <= 5m_d,
    m_d>=4.

Let

    P=sum_{low i} binom(w_i,2),
    Q=sum_{low i} floor(w_i^2/4).

The arithmetic certificate checks, separately for all29 boundary profiles,

    P<=31,       Q<=22.

Since 4r<=P, we have r<=7. The eight-residue gap theorem forces r=6. Its six missing directions lie in one character halfspace, so the total low pair mass in those directions is at most Q: in a w-point fibre, at most floor(w^2/4) pairs cross that halfspace cut.

Coverage therefore requires at least24 low pairs, but permits at most22:

    24 <= sum_{d in F}m_d <= Q <=22.

This contradiction excludes every remaining partition. The theorem follows.

## 5. Exact provenance and replay

The inherited set of130 open affine-support classes is read from

    research_sources/extracted/Kakeya_Reconciled_Proofs_2026-10-27/
      late_parallel_2214/extracted/m11_directional/M11_DIRECTIONAL_FRONTIER.json

and the support size of each orbit is read from the frozen

    .../inputs/CAP11_STRUCTURAL_REDUCTION.json.

The verifier checks the inherited size distribution, hashes both input files, intersects the new support>=19 theorem with the130 open orbit IDs, and records the precise59 newly excluded IDs and71 remaining IDs. No previously closed orbit is counted again.

Run from any working directory:

    python verify_cap11_support.py

The verifier writes `M11_SUPPORT_INDEPENDENT_REPLAY.json` and the29 exact boundary certificates in `M11_SUPPORT_GEOMETRIC_CERTIFICATES.json`. Its output includes partition counts, cutoff histograms, maximal verified resource bounds, source hashes, and the new orbit ledger.
