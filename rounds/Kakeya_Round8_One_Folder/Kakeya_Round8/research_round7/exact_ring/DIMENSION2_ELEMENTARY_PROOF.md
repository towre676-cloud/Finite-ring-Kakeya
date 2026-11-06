# An elementary proof that the minimum in dimension two is ten

The statement holds for both R=Z/4Z and R=F₂[ε]/(ε²). Reduce a Kakeya set
modulo the maximal ideal. Each active residue fibre is a subset of F₂².
Delete any singleton fibres: no primitive four-point line uses such a
fibre, so this does not destroy the Kakeya property.

For a nonzero residue direction d there are two lifted direction classes.
An edge joining residue fibres A and B can cover at most p_A(d)p_B(d) of
them. A fibre of weight at most three has at most one d-pair, while a full
four-point fibre has two in every direction.

At most two active residues cannot supply all three nonzero residue
directions. Consider the two remaining support sizes.

**Three active residues.** Their three edges have three different
directions. Each edge must itself cover both lifts, so its pair-count
product is at least two. Therefore every edge touches a full four-point
fibre. Covering all three edges of a triangle needs at least two such
fibres. The third fibre must contain pairs in its two distinct incident
directions, so it has at least three points. The total is at least eleven.

**Four active residues.** If any fibre is full, the total is at least
4+2+2+2=10. Otherwise every directional pair count is at most one. Each
residue direction has exactly two support edges, so both edges must make
a positive contribution in order to cover both lifts. Every fibre must
therefore have a pair in all three nonzero directions, requiring at least
three points per fibre. The total is at least twelve.

Thus every Kakeya set has at least ten points. For the upper bound take
the full fibre A₀=F₂² and A_a={0,a} at each of the other three residues.
For any nonzero d the edge {0,d} covers both quotient lift classes because
the full fibre supplies every pair class. Its carry at zero vanishes in
both rings. This is a ten-point Kakeya set.

Consequently **k_R(2)=10 for both rings**. This proof is independent of
the census and of any SAT result. The exact-ring encoder separately
reproduces the lower bound with four checked refutations (three- and
four-point supports, in both rings) and supplies the same explicit
ten-point upper-bound witness in both rings.
