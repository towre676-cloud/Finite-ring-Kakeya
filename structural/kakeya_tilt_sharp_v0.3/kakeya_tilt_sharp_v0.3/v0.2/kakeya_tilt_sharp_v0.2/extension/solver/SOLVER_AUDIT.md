# Finite proofs and extremal geometry

## A self-contained dimension-three proof

**Finite theorem.** For each of the rings Z/4Z and F₂[t]/(t²), the least
Kakeya cardinality in dimension three is 22. Every minimum set has fibre
profile (8,2,2,2,2,2,2,2), and each ring has exactly 131,072 minimum sets.

The lower bound and profile assertion now have exhaustive, standard-library
proofs. The search domain is the complete table of autocorrelation vectors of
all 256 subsets of F₂³. There are 46 distinct vectors, of which one represents
a singleton. Singleton fibres can be deleted because they contain no pair
required by a primitive four-point line. Thus 45 local vectors suffice.

The search retains the exact directional pair budget and applies affine
coordinate symmetry to the fibre-size ordering. Every directional edge is
bounded using the largest pair counts remaining in its two endpoint domains.
If the four edge capacities sum to less than four, the state is impossible.
Global mass bounds, the energy inequality

\[
\sum_a\sum_{v\ne0}p_a(v)^2\ge N(N-1),
\]

and the external-direction resource theorem supply additional necessary
constraints. Branching partitions one local domain into its singleton choices.
Memoization occurs only after every child is exhausted. All arithmetic is
integer arithmetic.

The mass-21 search terminates with no feasible assignment after **1,037,085
nodes**. A separate search allowing mass at most 22 and excluding the profile
(8,2,2,2,2,2,2,2) terminates with no feasible assignment after **1,889,459
nodes**. The recorded running times were 114.70 and 184.01 seconds. These are
complete finite searches; optimizer status codes are not used in either proof.

The universal construction supplies 22 points. With the optimum profile now
established, the equality argument is short. Translate the full fibre to
residue zero. For a nonzero residue a, the corresponding two-point fibre
must have difference a: otherwise the other three residue edges can cover at
most three classes in V/⟨a⟩, which has four classes. Conversely, every choice
of a two-point coset of ⟨a⟩ works because the full fibre fills the quotient.
There are eight choices of the full residue fibre and four choices in each
of the seven remaining fibres, giving

\[
8\cdot4^7=131{,}072.
\]

The same argument works in both rings because a translation by a carry class
preserves a full quotient.

## Dimension two and the endpoint correction

An independent coordinate-tuple implementation enumerates every one of the
65,536 subsets of R² for each ring. Its direct line test agrees with the
fibre-cover identity on every subset. Both rings have minimum 10, with exactly
32 minimum sets, all of profile (4,2,2,2). In their common digit encoding the
two minimum families are identical.

The complete census also locates the arithmetic difference. Every
dual-number Kakeya subset in dimension two is Kakeya in the mixed-characteristic
ring under the common digit encoding. There are exactly 64 additional
mixed-characteristic sets, all of size 12. The size counts are:

| Cardinality | Z/4Z | F₂[t]/(t²) |
|---:|---:|---:|
| 10 | 32 | 32 |
| 11 | 240 | 240 |
| 12 | 692 | 628 |
| 13 | 560 | 560 |
| 14 | 120 | 120 |
| 15 | 16 | 16 |
| 16 | 1 | 1 |

Thus identical minima and identical extremizers coexist with a precisely
localized difference in the surrounding incidence geometry.

The equality-count formula

\[
2^n\,2^{(n-1)(2^n-1)}
\]

requires **n≥2**. At n=1 the full ring is the only Kakeya set, and both residue
fibres are full. Choosing a full-fibre anchor therefore counts the same set
twice. The corrected count at n=1 is one.

## Proof artifacts and bounded decisions

The dimension-two SAT decisions now include exact DIMACS formulas and ASCII
DRAT proofs. An independent Python checker validates every addition using
reverse unit propagation or the resolution asymmetric-tautology rule. The
Z/4Z proof has 120 additions; the dual-number proof has 129. Both derive the
empty clause. A deliberately premature empty clause is rejected by the
checker.

The original SAT timer called an unsupported CaDiCaL195 interrupt operation.
The replacement runs the solver in a child process and enforces its wall-clock
limit at the process boundary. A timeout returns `TIMEOUT`. It never becomes
an infeasibility result. The new CLI also removes the original unused options
for extra cuts and fibre ordering.

Three bounded dimension-four searches—square spectra, complete local tables,
and square spectra with the exact four-frequency phase rule—returned
`UNKNOWN` at the declared limits. They add no global dimension-four lower
bound. The notation overlay attributes dimension-four closure to older
certificate files that are not contained in these two uploads. The present
extension treats that attribution as an imported result rather than a new
replay.

The complete dimension-four **local** characterization is independently
established by the spectral and phase calculations. Its 3,967 local types
are available to the strengthened global solvers. The distinction is exact:
local realizability controls each fibre; the global problem additionally
requires the fibres' pair sumsets to cover every lifted direction together.
