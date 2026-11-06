# A capacity bound coupling the affine direction spaces of two fibres

## Statement

Let A,B be subsets of binary n-space.  Write H_A and H_B for the linear
direction spaces of their affine hulls.  For a nonzero d, let P_A(d) be
the set of d-pair classes of A in the quotient by the line spanned by d.
Thus |P_A(d)|=p_A(d).  Define P_B(d) similarly.

If both pair sets are nonempty, then d belongs to H_A intersect H_B and

\[
|P_A(d)+P_B(d)|\le 2^{\dim(H_A+H_B)-1}.
\]

In particular, if both H_A and H_B lie in a subspace L containing d,
the edge covers at most |L|/2 lifted directions.  This includes capacity
bounds 2,4,8 when L has dimension2,3,4.  In dimension5 the quotient has
16 points, so only proper L supplies a new bound.

## Proof

A pair x,x+d in A proves d is a difference of two points of A, hence
d belongs to H_A.  Choose a translate t_A+H_A containing A.  Quotienting
by the line spanned by d sends every pair class in P_A(d) into the image
of t_A+H_A.  The analogous statement holds for B.  Their sum is contained
in the image of t_A+t_B+H_A+H_B.  Since d belongs to both spaces, the image
has exactly 2^(dim(H_A+H_B)-1) points.  This proves the bound.

The ring carry translates this quotient sumset and preserves its size.
Consequently the inequality is necessary in both rings under study.
If one pair set is empty its capacity is zero, already enforced by the
original pair-count capacity table.  This handles all degenerate cases.

## A strict improvement over pair counts alone

Take independent vectors e1,e2,e3,e4, put d=e1, and set
H_A=span(e1,e2,e3), H_B=span(e1,e2,e4).  The fibres A=H_A and B=H_B each
have four d-pairs.  Product counting permits16 lifted directions, while
the sumset is the eight-point image of H_A+H_B in the d-quotient.
The bound8 is sharp for these two fibres.  When H_A=H_B is a three-space,
the exact sumset has four points although product counting still permits16.

## CNF extension and one-way soundness

The wrapper retains the frozen joint-maximum encoder with its earlier
strengthening disabled.  It introduces one Boolean inside(v,L), equivalent
to the disjunction of the existing H-selector choices contained in L.
For any actual fibre, choose its true affine direction space and set
inside(v,L) to that true containment relation.

A separate family of16 unary edge-capacity bits is introduced.  For an
actual Kakeya set, set those bits through the actual quotient sumset size.
The original capacity table bounds these bits as before.  The new guarded
clause forbids capacity greater than |L|/2 whenever both endpoints'
direction spaces lie in L.  The lemma proves each such clause.  Finally,
the per-direction totalizers require coverage at least16, satisfied by
the actual sumset sizes in a Kakeya set.

This constructs an extension of every genuine counterexample assignment.
The duplicate capacity variables intentionally avoid depending on hidden
variable numbers in the original encoder.  They need not equal the old
relaxation's capacity bits in every satisfying assignment: the one-way
extension assigns both families their actual cardinalities.

No CNF refutation or new support exclusion is implied by this lemma alone.
It is a necessary structural strengthening, not a proof that the complete
global relaxation is exact.  Translation phases and overlap of different
edge sumsets remain unmodelled.
