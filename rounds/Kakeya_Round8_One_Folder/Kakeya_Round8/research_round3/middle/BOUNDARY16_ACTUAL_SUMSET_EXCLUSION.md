# Excluding the boundary profile(16,8^6,5,4^2,2^8)

This analytic argument uses actual quotient sumsets to break equality in the
resource bounds. It applies uniformly to both target rings.

Choose the first eight fibres, with weights(16,8^6,5), as heavy. Their missing
directions F have size either six or at least nine. The light fibres have
weights(4,4,2^8), total pair mass20. All nonhub heavy caps are at most four.
The sixteen-point hub has cap eight. Over any collection of missing directions,
capacity is at most four times light pair mass plus four times the light pair
mass on hub edges. The latter is at most the sum of all light caps, namely12.
Thus capacity is at most4*20+4*12=128. Nine missing directions would require144,
so|F|=6.

The missing set lies in a character halfspace and spans a four-dimensional
linear space U. The light pair mass over F is at most

    floor(4^2/4)+floor(4^2/4)+8=16.

The hub has at most six light neighbors through F. Their pair counts are at
most the six largest light caps, whose sum is2+2+1+1+1+1=8. Therefore

    96 <= capacity(F) <=4*16+4*8=96.                        (1)

All inequalities must be equalities. In particular both four-point light
fibres are active toward the hub with count two, and four two-point light
fibres are active toward it with count one. All six hub edges must attain
their product caps, requiring the hub pair count to equal eight in every
direction of F.

A count-eight direction of a sixteen-point set is a translation period.
Because F spans U of dimension four, the entire U is a period subgroup.
The sixteen-point hub is therefore exactly one affine coset of U.

A four-point set with a count-two direction is an affine plane. Equality in
its halfspace pair-mass bound forces its pair mass over F to equal four,
so exactly two of its three period directions belong to F. These two directions
span its tangent two-space, which consequently lies inside U.

Consider either edge between the hub and a four-point light fibre, in its
residue direction d in F. In V/<d>, the hub pair-label set is an affine
three-flat, while the light pair-label set is an affine line whose direction
lies in that three-flat's direction space. Their sum is therefore an affine
three-flat of cardinality eight. The ring carry merely translates it.

But equality in(1) required that edge to cover its product cap8*2=16.
Its actual capacity is only eight. This contradiction excludes the complete
weight multiset over both rings.

No affine shape assumption was imposed in advance: equality in the pair
resource inequalities forced both the hub flat and the light planes.
