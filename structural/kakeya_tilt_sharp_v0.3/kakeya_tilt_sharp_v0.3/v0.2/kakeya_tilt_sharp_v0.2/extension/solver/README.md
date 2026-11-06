# Exact local spectra, common periods, and executable finite proofs

This extension preserves both uploaded packages. Its standard-library audits
can be run without OR-Tools or PySAT. The optional solvers generate new
assignments, and every assignment retained here is checked with Python integer
arithmetic.

## Main results

The dimension-two census independently enumerates **all 65,536 subsets in
each ring**, using coordinate-tuple arithmetic separate from the input's bit
arithmetic. The minimum is 10, with 32 extremal sets in each ring. The two
families of extremal subsets coincide in the common digit encoding. The
fibre-cover identity agrees on every subset.

The complete local autocorrelation tables contain **7, 46, and 3,967** vectors
in dimensions two, three, and four, respectively, including the singleton
type. The square-spectrum identity is checked on every local subset through
dimension four. The accompanying theory extension proves its general form.

`finite_certificate.py` gives a **standard-library exhaustive proof** that the
exact-local counting relaxation in dimension three has no point of mass at
most 21. The recorded run visits 1,037,085 nodes in 114.70 seconds. This supplies
the lower bound 22 in both rings without trusting an optimizer's UNSAT status.
The universal 22-point construction gives the matching upper bound.

The old relaxation can contain assignments whose fibres are individually
realizable but whose pair sumsets collide. The recorded 24-point example has
128 choices of realizing fibres; none is Kakeya in either ring. In direction
6, both pair sets have two elements and the same nontrivial period, so their
sum covers only two of the four required classes. The common-period capacity
cut excludes this assignment.

A corrected 24-point assignment has **128 realizations, every one Kakeya in
both rings**, and no full fibre. Together with the retained lower-bound work
at 23, this supplies the sharp threshold for the non-full-fibre problem in
dimension three. The solver receipts and the separate finite-proof run state
their respective evidence explicitly.

## Replay

From this directory:

```bash
python audit_replay.py
python period_replay.py
python finite_certificate.py --ub 21 --nodes 2000000
```

The first two commands take a few seconds. The third is a complete exhaustive
search, usually about two minutes on the original runner. Node limits return
`NODE_LIMIT`; they never return `INFEASIBLE`.

Optional solver installation:

```bash
python -m pip install -r requirements.txt
python spectral_relaxation.py 3 --mode EP --smax 7 --seconds 30
python certified_sat.py Z4 2 9 --verify --prefix proof_Z4_n2_m9
```

The modes are `T` (input triangle relaxation), `S` (integer-square Walsh
spectra), `S4` (spectra plus the exact four-frequency phase condition in
dimension four), `E` (complete actual local autocorrelations), and `EP` (`E`
with common-period directional capacities). The finite-dimensional completeness
theorem for `S4` is proved and independently enumerated in the theory extension.

All three bounded dimension-four runs at mass 45 returned `UNKNOWN`: `S` at
120 seconds, `E` at 180 seconds, and `S4` at 120 seconds. They establish no new
dimension-four global lower bound. The notation overlay's historical
dimension-four claim cites older certificate files absent from these uploads.

## Source audit and repairs

1. The input's equality-count theorem needs **n at least two**. At n=1 both
   residue fibres are full, and there is one minimum set, the whole ring. The
   displayed general count would incorrectly give two because it counts the
   same set once per choice of full-fibre anchor. Its n=2 and n=3 counts are
   unaffected.
2. The old `sat_decide.py` timer calls `CaDiCaL195.interrupt()`. On the declared
   solver this raises `NotImplementedError: Limited solve is currently
   unsupported by CaDiCaL`. The replacement uses a child process and a real
   wall-clock termination, verified by a forced timeout control.
3. The old arguments `order_sym`, `extra_cuts`, and `forbid_sizes_above` are
   unused. The new CLI exposes only implemented modes and bounds. The old SAT
   docstring's fibre-order claim is not implemented; its fixed-line symmetry
   reduction is sound.
4. The old basic checker prints failures but does not assert them. The new
   independent audits assert every identity and terminate unsuccessfully on a
   mismatch.
5. The input UNSAT receipts have no proof files. The new dimension-two SAT
   receipts include the exact DIMACS formula and an ASCII DRAT proof. A
   separate standard-library RUP/RAT checker accepts both proofs. For large
   certificates, a specialist checker remains preferable for performance.

## Soundness of the solver-free finite proof

The domain of each fibre consists of the complete autocorrelation vectors
obtained from all subsets of the finite binary space. Singleton fibres can be
deleted: no four-point primitive ring line uses a singleton residue fibre.
For a minimum below the universal construction this deletion preserves the
Kakeya property and improves the objective.

An affine residue-coordinate change permits a largest fibre at zero, then a
largest remaining fibre at e1, then a largest fibre outside the preceding
linear span at each next basis vector. The finite search imposes only these
size comparisons, with every pair-count coordinate transformed simultaneously.

For a local row, write Q for the sum of squares of its pair counts. Summing
the necessary directional inequalities and applying 2xy at most x²+y² gives
the necessary global bound sum Q at least N(N−1). A domain's largest available
Q therefore gives an upper bound on its future energy contribution.

For a direction v, each residue fibre belongs to exactly one unordered edge
{a,a+v}. The largest pair count still in each endpoint domain gives an upper
bound on that edge's capacity. If the total upper bound is less than N/2,
the state is impossible. Otherwise subtracting the other edges' upper bounds
gives a necessary minimum pair count for either endpoint of an edge. This
filter never deletes a feasible row.

The mass filter uses the smallest available size at every other fibre. The
ordering filter uses only endpoint size minima and maxima. The energy filter
uses only the other fibres' maximum energy. Each is a necessary condition.

The external-direction filter is the uniform resource inequality proved in
the theory extension: with h heavy fibres, maximum fibre size M, and
q=ceil((N/2)/floor(M/2)), one must have

    q max(0,N−1−h(h−1)/2) <= N−h.

The separate at-most-two-heavy theorem excludes h≤2 below mass 3N−2.
Domains are filtered by the remaining possible heavy counts. A branch fixes
one fibre to one row, and the child branches partition its domain. A state
is memoized only after every child has been exhausted. Thus an `INFEASIBLE`
return is an exhaustive finite proof relative to the stated inequalities;
`NODE_LIMIT` makes no such claim.

The certificate verifier here is an executable finite proof, not a Lean
formalization. Every search domain and pruning rule is explicit and uses only
integer arithmetic.
