# Exact dense-fibre constraints: one-way soundness

## Status and scope

The implementation `encode_dense_types.py` appends two conditional local
models to the frozen joint-maximum encoder. It does not modify any Round 6
source. It calls the introspectable baseline in
`research_round6/encoder_audit/encode_maximal_cosets.py` with
`strengthen=False`; in that mode the original CNF is byte-identical to
`research_round6/joint_maxima/encode_joint_maxima.py`.

The new rows constrain **labelled pair counts** of two particular
four-dimensional fibre types. They do not constrain translations, actual
sumset-union coverage, or ring carry phases. Local exactness is not a claim
that the global relaxation is exact.

For a fibre A in F₂⁵, write p_A(d)=|A∩(A+d)|/2 for d≠0. If A lies in an
affine four-flat F=t+H and B=F\A, then

    p_A(d)=|A|−8+p_B(d) for 0≠d∈H,
    p_A(d)=0 for d∉H.

This identity and the classifications used below were proved and completely
checked in `research_round6/next_frontier/DENSE_FIBRE_COMPLEMENT_LEMMAS.md`.
The constructive converses are recorded in `DENSE_TYPE_ENCODING_DESIGN.txt`.

## Precise gates

The new constraints activate only at the existing census selectors with
the following entire signatures, including the affine rank:

| Name | Weight | Pair histogram h₀,h₁,… | Rank | Energy |
|---|---:|---|---:|---:|
| w11_q205 | 11 | h₀=16, h₃=5, h₄=10; all others zero | 4 | 205 |
| w12_q294 | 12 | h₀=16, h₄=9, h₅=6; all others zero | 4 | 294 |

The implementation checks that each signature occurs exactly once in the
loaded merged census. It does not gate on weight or energy alone.
Every new clause, including hidden-variable cardinality, XOR, membership,
and selector clauses, contains the negative literal of its own type gate.
When a type is inactive all its new clauses are therefore true, regardless
of the old variables or the auxiliary choices.

The selected H is the **same direction-space selector already used by the
baseline**, and both new models explicitly require its dimension to be four.

## Weight eleven: a circuit represented without ordering symmetry

Choose an indicator c_d for each of the 31 nonzero vectors d. Require,
conditional on the type gate,

    sum_d c_d = 5,
    XOR of the five selected vectors = 0,
    every selected vector lies in H.

Because indicators select a set, repeated vectors are impossible. Five
distinct nonzero vectors with sum zero automatically form a binary
five-circuit. A proper zero-sum subset cannot have size one or two; a
zero-sum subset of size three or four would leave a zero-sum complement
of size two or one. Thus every four selected vectors are independent.
Their span has dimension four and, being contained in H, equals H.

Define C={d:c_d=1}. For every incident direction link the existing one-hot
pair variable to the complete profile

    p(d)=3 on C;
    p(d)=4 on H\({0}∪C);
    p(d)=0 outside H.

These are equivalences, and pair values outside {0,3,4} are forbidden
while the type is selected. There is no ordering of five hidden vectors,
so this formulation avoids their 5! permutation symmetry.

Necessity is the five-point-complement classification. For the converse,
write C={c₀,…,c₄}. Set fᵢ=c₀+cᵢ for i=1,…,4. The four fᵢ form a basis
of H and their sum is c₀. The complement in H of
{0,f₁,f₂,f₃,f₄} has exactly this pair profile. Thus the model describes
all and only the possible profiles of this local type, with 168 profiles
in each H and 5,208 across the 31 four-spaces.

## Weight twelve: one three-space and one omitted nonzero point

Choose exactly one three-space J among the 155 three-spaces in F₂⁵ and
one nonzero vector u. Require J⊂H and u∈J. Link every incident direction
to the profile

    p(d)=5 on J\{0,u};
    p(d)=4 on H\(J\{0,u}), for d≠0;
    p(d)=0 outside H.

All structural choices and links are gated. The H selector is shared with
the old encoder. The constraints use the existing census type selector;
they do not introduce another independently selected fibre type.

Necessity follows from the four-point-complement classification. Conversely
choose a basis e₁,e₂,e₃ of J with e₁+e₂+e₃=u. Such a basis exists because
GL(J) is transitive on nonzero vectors. The complement in H of
{0,e₁,e₂,e₃} realizes the displayed profile. There are 15 choices of J in
each H and seven choices of u in J, hence 105 profiles per H and 3,255
across all four-spaces.

## Boolean primitives

The at-most-one clauses use the same sequential-prefix construction as the
baseline. Every actual one-hot choice extends by setting each prefix to
the OR of choices up to that point. Exact cardinality five uses a fully
bidirectional totalizer, fixing output 5 true and output 6 false. Its
auxiliary outputs have their usual threshold-count assignment.

Each two-input XOR is represented by its four truth-table clauses. Chaining
them separately in the five coordinates and setting each final parity to
zero enforces the vector sum. OR-membership variables are equivalent to
the disjunction of the already selected subspaces containing that vector.
All these clauses are emitted through the compulsory gate wrapper.

The verifier constructs these auxiliary truth values directly and checks
every emitted clause. It does not rely on a SAT solver to find witnesses.

## Extension of an actual Kakeya assignment

Take the satisfying assignment obtained from an actual Kakeya set by the
baseline's one-way soundness argument. At an inactive dense-type gate,
give arbitrary values to the new variables; every new clause is true. At
an active gate, choose the actual fibre's C or J,u supplied by the
classification. Use its actual direction space H, which is already
selected. Set all prefix, totalizer, membership, and parity auxiliaries to
their explicit Boolean meanings. The profile links hold on every incident
direction by construction. Thus the old assignment extends to a satisfying
assignment of the stronger formula.

Consequently a checked UNSAT proof for a strengthened formula excludes
exactly its stated support/maximum/budget case in both rings, under the
same census and baseline semantic dependencies. This implication is a
manual mathematical/code argument, not a proof-assistant formalization.

## Finite validation and its limits

`verify_dense_encoder.py` enumerates all 6,188 four- and five-point
complements in a fixed affine four-flat, checks their actual pair counts,
and transports the resulting local profiles to every four-space. It
separately enumerates all five-circuits and every J,u model. The two sets
of labelled profiles coincide exactly: 5,208 and 3,255.

Every one of these 8,463 profiles receives an explicit assignment satisfying
every new local clause. The verifier also checks inactive-gate vacuity,
six deliberate incorrect witnesses, and exact original-CNF byte identity
when the extension is disabled. The incorrect-witness tests show that
particular malformed assignments fail; alone they do not prove absence
of a different auxiliary extension. That broader conclusion follows from
the Boolean-model equivalences and the complete local profile comparison.

Separate primitive controls exhaust both input bits and auxiliary bits for
small totalizer, sequential one-hot, parity, and OR instances. These check
all satisfying auxiliary extensions in the examined truth tables and
confirm that deactivating the type gate accepts every assignment.

No global support exclusion or performance claim follows merely from
this finite local validation. Those require completed solver proofs and
their separate checker acceptance against exact formula bytes.
