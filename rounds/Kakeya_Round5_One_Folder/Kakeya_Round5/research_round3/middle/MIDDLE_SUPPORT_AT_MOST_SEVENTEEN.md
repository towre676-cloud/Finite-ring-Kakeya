# Middle maximum fibres: the support is at most seventeen

## Theorem and exact scope

Let R be Z/4Z or F2[epsilon]/(epsilon^2), and suppose K is a Kakeya subset
of R^5 with |K|<=93. If its maximum tangent-fibre size m satisfies

    12 <= m <= 18,

then its pair-active residue support has at most seventeen points:

    s <= 17.

Here pair-active support means the residue classes with at least two points
of K. Singleton fibres cannot participate in a primitive four-point line
and may be deleted. The theorem is uniform over all residue arrangements
and actual tangent-fibre shapes, over both rings.

This strengthens the frozen round-two theorem s<=18. It is a complete
support-eighteen exclusion for all seven middle maxima. It does not exclude
these maximum-fibre strata on supports seventeen or lower, and does not
establish the unrestricted lower bound |K|>=94.

## Why the finite list is exhaustive

After singleton deletion, retain the existing support and enlarge its fibres
to total weight 93 without exceeding the original maximum m. This is possible
at support eighteen because 18*m>93. Existing complete lines persist under
enlargement. Thus it suffices to exclude every nonincreasing partition of 93
into eighteen parts between two and eighteen, with largest part between
twelve and eighteen. There are exactly 239,246 such partitions.

The earlier theorem already excludes every support from nineteen through
thirty-two. Its proof and exhaustive replay are frozen in
research_round2/middle/MIDDLE_MAXIMA_SUPPORT_THEOREM.md and
MIDDLE_MAXIMA_SUPPORT_COMPLETION.json. Combining that theorem with the
complete support-eighteen replay proves the stated result.

## Complete accounting, without overlapping cuts

| Exclusion stage | Weight multisets excluded | Remaining |
| --- | ---: | ---: |
| All normalized support-eighteen partitions | — | 239,246 |
| Inherited global pair budgets and maximal-direction quotas | 238,744 | 502 |
| Inherited exact pair-spectrum assignment certificates | 217 | 285 |
| Eight heavy bases: six missing directions or at least nine | 188 | 97 |
| Three heavy bases: only one exceptional light vertex | 12 | 85 |
| Two heavy bases: retain the deleted-direction pair correlation | 13 | 72 |
| Prices for available heavy-neighbor positions | 42 | 30 |
| At most three heavy neighbors through the six missing directions | 12 | 18 |
| Nine heavy bases and heavy-neighbor prices | 1 | 17 |
| Maximal-direction bonus in the missing halfspace | 8 | 9 |
| Missing directions of nine heavy bases are sum-free | 1 | 8 |
| Ten heavy bases: weak unique-edge demand | 4 | 4 |
| A forced sixteen-flat and four-point planes have insufficient actual sumsets | 1 | 3 |
| Cube directions coupled to residual pair energy | 3 | **0** |

The 217 inherited exact-spectrum cuts are a subset of the round-two selected
23,381 cuts on supports fifteen through eighteen. They are counted only once
here. The new round-three contribution is a complete exclusion of the 285
support-eighteen profiles that survived the inherited stages.

Several experimental missing-six-direction catalogues and price screens also
appear in this directory. They are not needed for the proof chain above and
are not credited with additional disjoint cuts.

## Main new mathematical constraints

RESOURCE_COMPATIBILITY_LEMMAS.md proves the resource inequalities used by the
first eight new stages. These retain information that is lost when each edge
is optimized separately:

* The same small fibre has one pair budget shared by all missing directions.
* A heavy base can meet only one light base in a fixed direction.
* A quota-three light fibre can simultaneously attain its maximum toward
  three fixed heavy bases at only one possible residue location.
* Pair counts in the three directions of one binary plane must come from
  the same fibre, rather than three unrelated local choices.
* More than eight heavy bases force their missing direction set to be
  sum-free, so Mantel's theorem limits every light fibre's pairs there.

The eight-base geometry is analytic: its missing set has size six or at least
nine. In the six case it is an affine three-flat minus a line, lies in a
character halfspace, spans a four-space, and permits at most three heavy
neighbors from any outside residue. The proof dependencies are listed in
the replay receipt.

The last eight profiles use short analytic arguments. Four have insufficient
light pair mass to compensate for the unique heavy-heavy directions touching
weak heavy fibres. One forces equality in a resource bound; equality forces
a sixteen-point affine four-flat hub and two affine-plane light fibres.
Their actual quotient sumsets have size eight where equality required sixteen.
This proof is BOUNDARY16_ACTUAL_SUMSET_EXCLUSION.md.

### The final three profiles

The three last weight multisets are

    C = (12, 8^6, 6^2, 4, 3, 2^7),
    D = (12, 8^6, 6, 5^2, 3, 2^7),
    E = (12, 8^6, 6, 5, 4^2, 2^7).

Their energy budgets force at least five of the six eight-point fibres to
be actual affine three-flats. A cube has only seven period directions.
Moreover, cube-cube edges of actual capacity sixteen form a triangle-free
graph. Pricing the cube directions while charging the other fibres' pair
energy yields the general inequality

    C_total <= E_R/2 + 7*r*lambda
                  + (16-2*lambda)*floor(r^2/4)
                  + sum_{A in R} H_A(r,lambda),

where r is the number of selected cubes, E_R bounds the remaining fibres'
pair-square energy, 4<=lambda<=8, and H_A bounds the sum over at most r
distinct directions of

    max(0, min(16,4*p_A(d)) - p_A(d)^2/2 - lambda).

At lambda=11/2, ordinary maximal-direction quotas bound these local terms.
The resulting doubled capacity bounds for r=5 and r=6 are respectively

    C: 972, 991;    D: 954, 972;    E: 962, 980.

Every Kakeya configuration needs doubled capacity at least 992. Hence all
three profiles are excluded. The complete proof, including every energy
dependency and the triangle-free graph argument, is
CUBE_ENERGY_SUPPORT18_EXCLUSIONS.md. Both the root reviewer and the separate
structural reviewer independently checked the analytic argument.

## Reproduction and audit boundary

From the workspace root run

    python research_round3/middle/verify_support18_completion.py

The script uses only Python's standard library and reads the round-two files
without changing them. It performs the following complete replay:

1. Regenerate all 239,246 partitions and recompute the inherited quota bound
   using the earlier independent Python verifier, which differs from the
   original C++ producer.
2. Check every needed exact integer assignment dual for the 217 inherited
   support-eighteen spectrum cuts. No matching solver is run or trusted.
3. Recompute every round-three local resource optimum with backward recursion,
   independently of the producers' forward dynamic programs. The three-heavy
   stage uses direct tuple enumeration. The plane correlation catalogue is
   regenerated by combining actual subsets of eight four-point cosets.
4. Verify stage inputs equal the preceding complete survivor sets, verify all
   recorded bounds and strict inequalities, and verify the final analytic
   boundary arithmetic against every relevant pair spectrum.
5. Confirm that no support-eighteen weight profile remains and write a receipt
   with exact counts and hashes of all certificate and proof dependencies.

The receipt is MIDDLE_SUPPORT18_INDEPENDENT_REPLAY.json. The short final
arithmetic certificates are FINAL_ANALYTIC_SUPPORT18_CERTIFICATES.jsonl.
The verifier checks arithmetic and finite exhaustiveness; the geometric
lemmas are proved in the cited notes and independently reviewed. This is
not a machine formalization of those analytic proofs.
