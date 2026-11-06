# A bounded Lean formalization of the cube master argument

## What is kernel-checked

`CubeMaster.lean` contains thirteen proved theorems over finite types and
real numbers. It compiles with Lean4.24.0 and Mathlib commit
`f897ebcf72cd16f89ab4577d0c826cd14afaafc7` (the v4.24.0 release).

The main theorem, `KakeyaRound4.cube_master_bound`, is a general finite
incidence theorem. Let `RR`, `CC`, and `CR` index remaining-remaining,
cube-cube, and cube-remaining active edges. Its input data include:

1. An injective map `(RR x Bool) + CR -> Slot` assigning every remaining
   endpoint incidence to a distinct energy slot. In the intended application,
   a slot is a pair `(remaining fibre,direction)`. Its weight is nonnegative.
2. An injective map `(CC x Bool) + CR -> Cube x Fin7`, assigning at most
   seven incidences to each cube. Each cube-cube edge has two incidences.
3. Every RR edge's doubled capacity is at most the sum of its two slot
   energies. The ordinary AM-GM implication from a pair-product capacity
   bound is itself proved separately in the module.
4. Every CC capacity is at most16, every edge outside the designated
   expensive class has capacity at most8, and there are at most `B`
   expensive edges.
5. Every CR edge obeys the doubled local row
   `2*capacity <= reserved_slot_energy +11+gain`.

From these hypotheses Lean proves

    2*(sum RR capacities + sum CC capacities + sum CR capacities)
      <= sum remaining slot energies
           +77*(number of cubes)+10*B+sum CR gains.

The proof derives disjoint remaining-energy use from the first injection,
derives the cube-incidence budget from the second injection, sums the actual
edge inequalities, and performs the final real-linear deduction. It does
not merely assume that summed master inequality as an input.

Taking `B=floor(r^2/4)` is the separate triangle/Mantel input. Bounding the
gain sum by `2*sum_A H_A` gives the paper's doubled lambda11/2 form.

Other proved statements include:

* Ordinary pair-product AM-GM.
* Weighted AM-GM with denominator cleared:
  `0<=theta` and `capacity<=p*q` imply
  `2*theta*capacity <= (theta*p)^2+q^2`.
  For positive theta this is equivalent, by division, to the user's
  weighted inequality.
* The local doubled cube-to-other surplus row from
  `capacity<=min(16,4*q)`.
* The surplus values for pair counts0,1,2,3,4, namely0,0,1,4,5, and its
  vanishing for every real pair count at least5.
* All six final boundary arithmetic inequalities and the critical exact
  equality `388+77*6+10*(6^2/4)+51=991`.
* Contradiction between the resulting upper bound991 and doubled demand992.

The module uses no `sorry`, `admit`, `native_decide`, or new axiom
declarations. The printed dependency audit for every theorem contains only
Lean/Mathlib's standard `propext`, `Classical.choice`, and `Quot.sound`.

## What remains outside this formalization

The module does **not** formalize:

* Actual subsets of `F2^5`, their pair sets, or affine planes.
* The double-counting identity `Q(A)=binom(|A|,2)+6 Z_4(A)`.
* The analytic twelve-point maximum300 or its equality classification.
* The construction of the two incidence injections from an actual Kakeya
  configuration.
* Quotient sumset capacity bounds, cube triangle geometry, or Mantel's
  theorem.
* The local spectrum/period arguments that justify each profile's residual
  energy and gain constants.
* The exhaustive support18 case reduction or the unrestricted Kakeya theorem.

Those are explicitly separate geometric and finite-case obligations. This
module establishes the general finite-sum aggregation step and its stated
algebraic consequences; it is not a formal proof of the whole support18
theorem.

## Reproduction

With elan and Lake available, work in this directory:

```bash
lake update
lake exe cache get
lake env lean CubeMaster.lean
python3 verify_lean.py
```

The toolchain and Mathlib commit are pinned by the adjacent files. The cache
download fetches dependencies; the research archive does not contain a Lean
installation or the Mathlib build cache.

The receipt can also be regenerated using an existing pinned Mathlib checkout:

```bash
python3 verify_lean.py --mathlib /path/to/mathlib4 --lean-bin /path/to/lean/bin
```

`verify_lean.py` verifies the Mathlib commit and Lean version, invokes the
actual compiler, checks all thirteen printed axiom audits, and records the
source/log hashes in `LEAN_REPLAY_RECEIPT.json`. A source grep alone is not
being used as evidence of proof completion.
