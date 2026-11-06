# Actual unique-edge roles exclude 8,837 additional M19 profiles

## Scope and hypotheses

This is the fourth, disjoint M19 stage of research round3. Its inputs are the
9,733 support-size11 and2,902 support-size12 profiles surviving the common
own-periodic/nonperiodic stage. Each profile describes a weight19 hub fibre
at residue0 and other pair-active fibres of total weight74. Every outer
weight in these input files is at most14; the verifier checks this hypothesis
for every profile. These are exclusions of entire weight/own-flag profiles,
uniformly over all residue placements and fibre shapes.

Let V=F_2^5 and let S be the pair-active residue support, with0 in S. Its
size is11 or12. A necessary condition is S+S=V: each nonzero residue
direction must have at least one pair of active residues. For d nonzero put

    q_S(d) = number of unordered pairs {a,b} in S with a+b=d.

Each direction needs16 quotient lift labels. An edge between fibres whose
directional pair-label sets have sizes p and q contributes at most the
cardinality of their sumset in F_2^4. Translations arising from the carry
in Z/4Z do not change cardinalities, so the argument works for both rings
in the project.

## Two necessary vertex attributes

Define two subsets of the outer residues S\{0}:

- F consists of endpoints of edges {a,b} for which d=a+b is outside S and
  q_S(d)=1. Such an edge alone must cover its direction.
- H consists of residues a for which q_S(a)=1. The unique edge in this
  direction is the hub edge {0,a}.

Every vertex of F must receive a fibre of weight at least8. To prove this,
suppose one endpoint has weight at most7. Its pair-label set has size at
most3; the other endpoint has weight at most14, hence a pair-label set
of size at most7. Such two sets cannot sum to all of F_2^4. If the smaller
set has at most2 points, the product bound gives at most14 sums. If it
has3 points, translate it into a two-dimensional subspace U. To fill any
U-coset, the other set must meet that coset in at least2 points, since one
point gives only3 sums. Filling all four U-cosets therefore requires at
least8 points in the other set, a contradiction. Thus the sole edge cannot
supply16 labels.

Every vertex of H must receive an own-positive fibre of weight at least4.
Own positivity means p_A(a)>0. If this fails, its unique hub edge supplies
no labels. If the weight is2 or3, the own pair count is at most1, while
the weight19 hub has at most9 pairs in any direction. The hub edge then
supplies at most9 labels, again less than16.

These requirements are necessary only. No claim is made that satisfying
them produces a Kakeya set or satisfies the other capacity inequalities.

## A complete marked-support census without an orbit assumption

Because S+S=V, S spans V. Choose a basis from S and apply a linear
automorphism fixing the hub0. The transformed support contains

    {0,1,2,4,8,16}.

Consequently every possible marked support is represented among all sets
obtained by adding s-6 points from the remaining26 elements. This lists
65,780 normalized sets for s=11 and230,230 for s=12. There is no requirement
that these representatives be inequivalent. Multiple occurrences are
harmless; omitting a possible marked support would not be harmless.

The C++ census recomputes all unordered differences for every normalized
set and keeps exactly those for which all31 nonzero differences occur.
The independent Python verifier instead uses translated bit masks and
q_S(d)=|S intersect(S+d)|/2, deriving the roles from these intersections.
It does not read the inherited affine-class or marked-case catalogues.

The role vector is

    r=(|neither F nor H|, |F only|, |H only|, |F and H|).

The complete result for size11 is:

| r | Normalized covering sets |
|---|---:|
| (0,0,10,0) | 11 |
| (0,6,4,0) | 390 |
| (0,8,0,2) | 2,160 |
| (0,9,0,1) | 1,435 |
| (0,10,0,0) | 320 |
| (1,2,0,7) | 850 |
| (1,6,0,3) | 80 |
| (1,6,1,2) | 340 |
| (1,7,0,2) | 1,800 |
| (1,8,0,1) | 290 |

These multiplicities sum to7,676 covering normalized sets. They count
normalized sets, not affine classes or marked-support orbits.

For size12 the complete result is:

| r | Normalized covering sets |
|---|---:|
| (0,10,1,0) | 2,952 |
| (2,9,0,0) | 17,370 |
| (3,4,4,0) | 4,080 |
| (3,6,1,1) | 7,680 |
| (3,6,2,0) | 7,830 |
| (3,7,0,1) | 35,340 |
| (3,8,0,0) | 3,980 |
| (4,1,0,6) | 2,770 |
| (4,5,0,2) | 6,150 |
| (4,7,0,0) | 1,500 |
| (5,0,6,0) | 360 |
| (5,5,0,1) | 1,740 |
| (7,4,0,0) | 1,890 |
| (8,2,1,0) | 990 |
| (11,0,0,0) | 16 |

These multiplicities sum to94,648 covering normalized sets. In particular,
the last pattern has no constrained vertices, so this role-only argument
cannot exclude any whole size12 profile.

## Hall obstructions for assigning fibre attributes

A fibre has attribute L if its weight is at least8 and attribute P if it
is own-positive with weight at least4. Let

    a=(number with neither attribute, with L only, with P only, with both).

For a placement realizing role vector r, injectivity gives the necessary
inequalities

    r3 <= a3,
    r1+r3 <= a1+a3,
    r2+r3 <= a2+a3,
    r1+r2+r3 <= a1+a2+a3.

The four inequalities respectively count vertices needing both attributes,
needing L, needing P, and needing at least one attribute. They are elementary
Hall obstructions: a required set of vertices cannot have fewer eligible
fibres than vertices. A failed inequality excludes every placement with
that role vector. If each role vector in the complete census has a failed
inequality, the entire weight/own-flag profile is impossible.

One useful corollary is that every size11 covering support has at mostone
vertex in neither F nor H. A profile with at leasttwo fibres lacking both
attributes is therefore impossible. This simpler corollary accounts for
6,241 of the8,837 exclusions. The remaining2,596 use the other inequalities
or their combination across different role vectors.

## Exact result and certificate schema

For every excluded profile, the JSONL certificate records the parent ID,
the exact input profile line, its four attribute counts, and one failed
inequality for each role vector in lexicographic order. A witness is
[required,available,name], where name is both, large, sole_hub, or nonfree.
The verifier recomputes both integers from the profile and role vector
and checks required>available. No search tolerance or numerical optimizer
is involved.

All8,837 support-size11 candidate profiles have a verified obstruction for
each of the10 role vectors, for88,370 checked Hall witnesses. There are no
size12 candidates. Exact ID subtraction leaves896 size11 profiles and2,902
size12 profiles, for3,798 tracked M19 profiles in total after all four
round3 stages. The verifier also confirms that every surviving profile
passes at leastone role pattern, preventing accidental over-subtraction.

The four round3 stages are disjoint in sequence:

| Stage | Size11 cuts | Size12 cuts | Total remaining |
|---|---:|---:|---:|
| Round2 input | 0 | 0 | 30,471 |
| Common affine-rank mode | 11,527 | 6,077 | 12,867 |
| One analytic deleted-direction profile | 1 | 0 | 12,866 |
| Common own-periodic mode | 95 | 136 | 12,635 |
| Actual support roles | 8,837 | 0 | 3,798 |

The total new round3 exclusion count is26,673 whole tracked profiles.
Remaining profiles are survivors of necessary conditions, not realizable
examples. This result does not close the unrestricted dimension-five
theorem or the M19 branch.

## Reproduction

From this directory:

    g++ -O3 -std=c++17 build_unique_edge_role_census.cpp -o build_unique_edge_role_census
    ./build_unique_edge_role_census > UNIQUE_EDGE_ROLE_NORMALIZED_CENSUS.json
    python build_unique_edge_role_certificates.py
    python verify_unique_edge_roles.py

The last command independently reruns the complete normalized census,
checks all profile hypotheses and Hall witnesses, and writes
UNIQUE_EDGE_ROLE_VERIFICATION_RECEIPT.json. All required inputs, outputs,
and survivor hashes are recorded there. The inherited candidate census
from44/96 marked cases is a discovery aid only and is not a dependency of
the proof or verifier.
