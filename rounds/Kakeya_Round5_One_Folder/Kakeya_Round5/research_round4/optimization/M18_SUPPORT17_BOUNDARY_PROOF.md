# The last support17, maximum18 profile has insufficient missing-direction capacity

## Analytic profile exclusion

For either target ring in dimension five, a Kakeya set cannot have the
pair-active weight profile

    (18,8^5,7,6^2,2^8).

Its total mass is93 and its support size is17. The proof holds for every
residue placement and every tangent-fibre shape with these weights.

Select the nine largest fibres as heavy. Their pair caps are

    (9,4,4,4,4,4,3,3,3).

The remaining eight fibres each have size two and therefore one unordered
pair. Let F be the nonzero directions missing from the heavy residue set's
difference set, and write r=|F|. The established nine-point difference theorem
gives r>=3.

Every contributing residue edge in a direction of F has a light endpoint.
For an edge to a heavy fibre other than the weight18 fibre, its actual
capacity is at most four times the light pair count. A light-light edge
also satisfies this bound after charging its two light endpoint counts:
their pair counts are each0 or1 and p*q<=4(p+q).

For an edge to the weight18 fibre, the capacity is at most nine times the
light pair count. Charge four times that count to the same baseline, and
allow an additional five. For any one direction there is at most one residue
edge incident to the weight18 base. Hence at most r such extra contributions
occur in F, each at most five.

The eight light fibres have at most eight pair units in F altogether.
Consequently the total actual sumset capacity in the missing directions is

    C_F <= 4*8+5r = 32+5r.

Kakeya coverage requires16 labels in each missing direction, so

    16r <= C_F <=32+5r,
    11r<=32.

This contradicts r>=3. The strict contradiction is already visible at r=3:

    C_F<=47<48.

No affine-shape hypothesis, exact pair-spectrum census, or numerical optimizer
is needed for this profile exclusion. Ring carries merely translate the
individual sumsets and preserve the product upper bound.

## Relation to the priced resource certificate

The nine-heavy light-row relaxation has cutoff ell=1. At an integer price t
on positive incidences at the cap9 heavy vertex, each two-point light row is

    1+max(17-t,7,5,0)=max(18-t,8).

At t=10 all eight rows equal8. With three missing directions, the doubled
upper is

    8*8+3*10=94<96.

For r missing directions it is64+10r, exactly twice the elementary bound
above. Since t=10<=32, its slope is below the doubled coverage slope32.
Thus this is an exact integer dual certificate of the same hand proof.

## Consequence for the maximum18 support ceiling

The complete frozen middle inventory
`research_round4/middle_inventory/MIDDLE_COMPLETE_INVENTORY.json` leaves
exactly one weight profile in its support17, maximum18 cell, namely the one
above. Its other profiles have already been excluded by the inventory's
certified screens. The earlier Round3 theorem excludes support18 and every
larger support for all middle maxima.

Combining those proved inputs with this analytic exclusion gives:

    For both rings, |K|<=93 and maximum fibre18 imply pair-active support<=16.

The full maximum18 stratum on smaller supports remains open. The standalone
profile argument above is analytic; the complete cell closure additionally
depends on the exact inventory and its inherited verified reductions.
