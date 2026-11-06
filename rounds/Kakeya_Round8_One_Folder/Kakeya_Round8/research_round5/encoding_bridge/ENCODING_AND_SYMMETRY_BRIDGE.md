# From ring Kakeya sets to a complete marked-support certificate contract

## Result and scope

The reported Claude run is a substantial computational update, but its
results file, exact conditions (A)–(E), encoder source, CNFs, and DRAT files
are not present in this workspace. No claim below verifies those unseen
artifacts or replaces the user's stated trust qualifications.

This work establishes two concrete pieces of the semantic and completeness
bridge that a final exclusion needs:

1. There are exactly **13 hub-marked difference-covering support classes of
   size 11 and 25 of size 12**, hence **38** in total. A separate finite checker
   proves coverage and disjointness without assuming the old affine catalogue
   is complete. Every one of the 102,324 normalized covering supports has an
   explicit invertible-linear-map witness to a named representative.
2. A pinned Lean module proves a dimension-independent line-to-pair and
   pair-sum equivalence in the canonical coordinate models of both rings,
   including the carry for Z/4Z. The Z/4 coordinate operations are checked
   against literal arithmetic modulo four. This is a semantic ingredient,
   not a formal proof of Claude's CNF encoder.

The number 38 therefore agrees exactly with a mathematically natural complete
case universe. Agreement of the count does not identify Claude's actual cases
with these representatives; the supplied mapping contract makes that next
comparison precise.

## 1. Canonical coordinates and the four points of a primitive line

Let V=F2^n. Write pi=2 for Z/4Z and pi=epsilon for the dual-number ring. Every
point has a unique representation sigma(a)+pi*u, where a,u belong to V and
sigma is the coordinatewise binary section. Represent a scalar by its two
binary coefficients (t,s), corresponding to sigma(t)+pi*s.

For bits a,u,d,v, multiplication of the two coefficient pairs is the same
in both rings:

    (t,s)*(d,v) = (t*d, t*v+s*d).

Addition differs by the carry. Define

    c_dual(a,d)=0,
    c_Z4(a,d)=a coordinatewise-multiplied by d.

Then

    (a,u)+(d,v)=(a+d,u+v+c_R(a,d)),

where all displayed coefficient operations are binary. The high coefficient
of a general line point is

    u+t*v+s*d+c_R(a,t*d).

For a primitive direction sigma(d)+pi*v, d is nonzero. The four scalar
choices give precisely

    (a,u),
    (a,u+d),
    (a+d,u+v+c_R(a,d)),
    (a+d,u+v+c_R(a,d)+d).                         (1)

Thus a primitive line uses two distinct tangent points in each of two
distinct residue fibres. A singleton fibre cannot contain part of any such
line. Removing all singleton fibres preserves the Kakeya property.

If A_a is the tangent fibre at residue a, define the oriented pair predicate

    Pair(A,d,u)  iff  u in A and u+d in A.

Writing w=u+v+c_R(a,d), (1) gives the exact equivalence

    line(a,u;d,v) is contained in K
      iff Pair(A_a,d,u) and Pair(A_(a+d),d,w).       (2)

The endpoint operation w=u+v+c_R(a,d) is an involution in v. Therefore

    some line over residue edge {a,a+d} has direction(d,v)
      iff there exist u,w with
          Pair(A_a,d,u), Pair(A_(a+d),d,w),
          v=u+w+c_R(a,d).                          (3)

Equations (2) and (3), for every index type and therefore every dimension,
are the main conclusions compiled in CarryBridge.lean.

## 2. Quotient labels and common necessary conditions

The two units in either ring identify high direction coefficients v and v+d.
Thus a primitive direction with residue d is indexed by the quotient

    q_d: V -> V/<d>.

Put P_A(d)={q_d(u):Pair(A,d,u)}. The exact quotient-label set supplied by an
edge is

    L_(a,a+d)^R=P_(A_a)(d)+P_(A_(a+d))(d)+q_d(c_R(a,d)).       (4)

Each unordered tangent pair contributes exactly one quotient label, so

    |P_A(d)|=p_A(d)=|A intersect(A+d)|/2.

The division by two is essential: the intersection counts both endpoints.
For dimension five, the quotient has 16 labels. The necessary coverage
condition in each nonzero residue direction is

    union_(edges of direction d) L_edge^R = V/<d>.

It implies the ring-independent inequality

    sum_(edges of direction d) min(16,p_a(d)*p_b(d)) >=16.    (5)

Carry translates each individual label set and preserves its cardinality.
Consequently a correct necessary-condition CNF using only such capacities
can be shared by both rings. An exact labelled-coverage CNF must instead
retain the appropriate carry and common fibre translations. Thirty-eight
common necessary-condition proofs need not be doubled to seventy-six.

Other elementary necessary data for a fibre of weight w are

    0<=p_A(d)<=floor(w/2),
    sum_(d!=0) p_A(d)=binom(w,2),
    Q(A)=sum_(d!=0) p_A(d)^2.

The last identity combined with (5) gives total energy at least 992 in
dimension five. Full pair-spectrum membership is also a necessary condition
when the domain catalogue is complete. These statements are listed as
independently derived ingredients; they are **not asserted to be Claude's
unavailable conditions (A)–(E)**. Every additional row, implication, or
symmetry-breaking clause in that actual encoder needs its own justification.

## 3. Affine support normalizations lift over both rings

Let g be an invertible binary matrix and b a binary translation. Choose the
matrix G over R whose entries are the same zeroes and ones. Since det(G)
reduces to the nonzero determinant of g modulo the maximal ideal, det(G) is
a unit. Hence G is invertible over either target ring.

The affine ring map

    F(x)=Gx+sigma(b)

is a bijection that sends every primitive line to a primitive line and
permutes all primitive directions. It preserves the Kakeya property and
cardinality. Define delta_(g,b)(a) by the unique decomposition

    G*sigma(a)+sigma(b)=sigma(g*a+b)+pi*delta_(g,b)(a).

For a general point,

    F(sigma(a)+pi*u)
      =sigma(g*a+b)+pi*(g*u+delta_(g,b)(a)).           (6)

Thus the fibres transform by

    A'_(g*a+b)=g*A_a+delta_(g,b)(a).                  (7)

Every fibre has the same size after the transformation. Pair counts satisfy

    p_(A'_(g*a+b))(g*d)=p_(A_a)(d).

For dual numbers with this zero-high-coefficient lift, delta is zero. For
Z/4Z it generally depends on the residue a. The use of affine support
symmetry is nevertheless valid because the whole actual configuration is
transformed by (6). Independently translating each edge would not be a
valid substitute for this common transformation.

The carry compatibility can be made explicit. Put kappa_g(d)=delta_(g,0)(d).
Comparing the two expansions of G(sigma(a)+sigma(d))+sigma(b) gives

    g*c_R(a,d)+delta_(g,b)(a+d)
      =delta_(g,b)(a)+kappa_g(d)+c_R(g*a+b,g*d).       (8)

The transformed high direction coefficient is g*v+kappa_g(d). Equation
(8) is precisely what makes the two endpoint descriptions of a transformed
line agree. A ring-specific exact label encoder must respect this relation
when it uses residue support symmetries.

## 4. Why a distinguished maximum is a marked support problem

Choose any maximum-weight fibre and translate its residue to zero. This
preserves its weight, all other fibre weights, and every primitive line.
The choice does not prove that the maximum is unique. In a maximum-19
encoding, other fibres must remain allowed to have weight 19 unless a
separate theorem excludes ties. Omitting the earlier outer-weight-14 cap
does not by itself establish that this detail is handled correctly.

At support 11 or 12, every set of size at most 93 and exact maximum 19 can
be padded to total 93 within the same support and maximum, since
19*s>93. Added tangent points preserve existing lines. This normalization
may create further maximum-weight fibres and is compatible with a
distinguished, rather than unique, maximum.

If S is an unmarked support and h,k belong to S, the marked supports
(S,h) and (S,k) are affinely equivalent exactly when an affine automorphism
of S sends h to k. Equivalently, S+h and S+k are linearly equivalent with
the marked vertex fixed at zero. If g(S+h)=S+k, then

    x -> g(x+h)+k

is the required affine automorphism of S. The converse follows by the same
identity.

The twelve inherited difference-covering representatives of sizes 11 and 12
have the following full affine automorphism and hub-orbit counts:

| Original ID | Support size | Affine automorphisms | Hub orbits |
|---|---:|---:|---:|
| 65 | 11 | 1,008 | 3 |
| 66 | 11 | 48 | 5 |
| 69 | 11 | 48 | 3 |
| 70 | 11 | 1,920 | 2 |
| 79 | 12 | 96 | 4 |
| 80 | 12 | 32 | 4 |
| 85 | 12 | 8 | 6 |
| 86 | 12 | 12 | 3 |
| 87 | 12 | 96 | 4 |
| 89 | 12 | 120 | 1 |
| 90 | 12 | 128 | 2 |
| 91 | 12 | 23,040 | 1 |
| **Total** | | **26,556** | **38** |

The support-11 subtotal is 13 marked classes; the support-12 subtotal is 25.
All 140 choices of a marked vertex in the twelve representatives are
explicitly mapped to these 38 classes. The old 44/96 numbers counted all
vertices of the four/eight unmarked supports; they were not the quotient
counts after identifying equivalent hub positions.

## 5. Direct completeness, without the inherited catalogue

The preceding candidates were discovered from an inherited catalogue. The
following independent certificate removes catalogue completeness as a
dependency of the 38-case conclusion.

A difference-covering support containing zero spans all of V. Choose five
independent points of the support and send them to the coordinate basis.
Every marked support of the relevant sizes therefore has a representative
containing

    {0,1,2,4,8,16}.

There are exactly

    binom(26,5)=65,780
    binom(26,6)=230,230

such normalized sets of sizes 11 and 12. The checker enumerates all 296,010.
It tests difference coverage by intersections with translated bit masks.
Exactly 7,676 and 94,648 sets cover every nonzero difference, respectively.

For each of these 102,324 supports, the CSV certificate supplies one of the
38 named representatives and five vectors from it forming an invertible
basis. The checker reconstructs the linear map directly, verifies that it
is a bijection on all 32 vectors, and verifies that its inverse image of
the representative is exactly the normalized support. Every normalized
covering support occurs once, and no noncovering support occurs.

The checker also independently computes the exact size of each normalized
marked orbit. If B(S) is the number of ordered linear bases contained in a
hub-zero support and Aut_lin(S) its linear automorphism group, then

    number of normalized images = B(S)/|Aut_lin(S)|.

Indeed, mapping a selected source basis to the coordinate basis gives a
normalized image. Two source bases give the same image precisely when their
normalizing maps differ by a linear automorphism of S. The group acts freely
on ordered bases, and every such fibre has exactly |Aut_lin(S)| elements.

The checker computes B(S) by a subspace dynamic program and recomputes the
linear automorphisms through partial affine-map extension, after normalizing
the source support to contain the coordinate basis. The supplied number of
distinct normalized witnesses for each case equals this exact quotient.
Hence each case's entire normalized orbit is present. Since the global
witness list contains no duplicate mask, the 38 marked orbits are disjoint.

This proves both completeness and inequivalence of the 38 cases without
reading the old 382-class catalogue. The latest authoritative receipt is
NORMALIZED_COVER_REPLAY.json. The earlier MARKED_SUPPORT_REPLAY.json records
the preceding candidate/automorphism stage, whose narrower scope still
mentions the inherited source catalogue.

## 6. The Lean boundary

CarryBridge.lean compiles with Lean 4.24.0 and Mathlib commit
f897ebcf72cd16f89ab4577d0c826cd14afaafc7. Its fifteen proved declarations use
only propext and Quot.sound where axioms occur; several finite arithmetic
statements use none. There is no sorry, admit, native_decide, or new axiom.

The module proves the canonical bit-pair encoding is injective, lies in
0..3, and realizes Z/4 addition, multiplication, and line arithmetic modulo
four. For the dual-number model, the coefficient operations are its defining
binary laws. It then proves the all-dimensional four-corner formula, the
two-pair equivalence, primitive pair distinctness, endpoint involution, and
the exact pair-sum witness equivalence.

It does not construct an abstract Ring instance and formal isomorphism for
the dual-number carrier. It also does not formalize quotient cardinalities,
the affine normalization proof above, support-census completeness, the
unavailable A–E definitions, the actual CNF translator, the DRAT checker, or
the maximum-19 exclusion. The coordinate-level theorem is a substantial
piece of the semantic bridge, with those boundaries explicit.

## 7. The exact remaining contract with Claude's result

To integrate the reported UNSAT results as verified exclusions, the actual
artifact chain must establish:

* Every listed CNF corresponds to its stated marked support, total-size
  bound, maximum, and allowable weight domains. Other maximum-weight
  vertices are allowed unless their exclusion is separately proved.
* The listed marked supports map onto all 38 contract IDs. The supplied
  map_marked_case.py produces an explicit affine map to the corresponding
  representative; a separate gate can check that map directly.
* Every actual Kakeya configuration in either ring has an assignment
  satisfying that case's conditions and all auxiliary CNF clauses. For an
  exclusion, this forward implication is the necessary semantic direction.
* Each checked proof is paired with the exact hashed input CNF; any
  preprocessing or transformation is included in the proof chain.
* The checker establishes UNSAT for that exact CNF. A checker success and
  encoder soundness are different obligations.

The first two points now have a concrete complete support contract and a
mathematical symmetry justification. The line/pair relation underlying the
third has a new Lean component. The actual A–E/CNF implication remains
unverified because its source is unavailable here. The claimed removal of
the outer-weight-14 cap is recorded as reported, not independently audited.

If all 38 actual instances meet these obligations and are UNSAT, then the
maximum-19 stratum on supports 11 and 12 is excluded, uniformly over all
placements and fibre shapes. Excluding maximum 19 at every support size
still uses either the inherited support reduction or the separately running
all-support sweep. Neither dependency is silently removed by this work.
