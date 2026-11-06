# Bounded support-thirteen trials

## Result

**One additional hub-marked support-thirteen class is excluded for every
maximum fibre weight from two through eighteen, in both rings.** Both the
baseline joint-maximum encoder and the strengthened encoder produced direct
LRAT proofs, and the pinned CakeML checker accepted each against its exact
CNF. A separate replay regenerated all four trial CNFs byte-for-byte and
accepted both completed proofs again.

The excluded representative, with a largest fibre distinguished at zero, is

$$
S=\{0,1,2,4,5,6,8,9,10,15,16,22,25\}.
$$

The nonzero-residue bitmask is 37848950. The conclusion applies to the entire
distinguished-hub linear orbit of this support, for total size at most 93.
It does not assert that all possible choices of largest vertex on the same
unmarked affine support are excluded, unless their marked cases are
separately identified with this orbit.

**The new maximal-subspace constraints did not demonstrate a search-speed
improvement in this small sample.** They remain sound mathematical
strengthenings, but these results do not justify enabling them globally on
performance grounds.

## Paired outcomes

Each run used the same solver binary, the interval [2,18], total budget 93,
direct textual LRAT output, and a sixty-second wall limit. Only one solver
from this diagnostic was run at a time; other research processes shared
the environment.

| Marked support mask | Formula | Solver time | Result | LRAT size |
|---|---|---:|---|---:|
| 37848950 | Baseline | 4.983 s | CakeML accepted | 37,108,041 bytes |
| 37848950 | Maximal-subspace constraints | 5.481 s | CakeML accepted | 33,814,238 bytes |
| 1022358 | Maximal-subspace constraints | 60.005 s | Timeout; uncertified | 1,177,374,720 unfinished bytes, discarded |
| 1022358 | Baseline | 60.007 s | Timeout; uncertified | 999,452,672 unfinished bytes, discarded |

The incomplete proof streams were hashed before removal. Their hashes are
provenance for discarded diagnostic output, not certificates. A timeout
establishes neither satisfiability nor unsatisfiability.

For the accepted support, the stronger formula adds 403 variables and
36,387 clauses to the baseline's 45,124 variables and 400,297 clauses. Its
uncompressed proof is smaller, but its observed solve time is slightly
longer. Single runs in a shared environment cannot establish a reliable
speed ratio.

The second representative is

$$
\{0,1,2,4,7,8,11,12,15,16,17,18,19\}.
$$

The original fixed-maximum exploration classified these representatives as
relatively easy and intermediate: their largest reported individual
fixed-maximum times were 5.6 and 49.1 seconds. Those historical runs used a
different solver setup and different formulas, so those times are only the
selection rationale and are not directly comparable to the new timings.

A third, harder representative was initially selected. That trial was
interrupted while stopping after two paired cases to conserve resources for
the main support-twelve certification. No result or proof from that third
case is retained or credited.

## What this says about the next attack

The joint-maximum domain is useful: one accepted formula covers all maxima
two through eighteen for the selected marked support. The two accepted
proofs here exclude **one** case, not two; they prove the same mathematical
case through two relaxations.

The maximal-subspace theorem remains useful for mathematical deductions and
for targeted experiments on period-rich spectrum branches. The bounded
comparison provides no evidence that adding its clauses universally will
accelerate the remaining support sweep. A prudent next use is a small
branch-specific trial or an analytic application, rather than replacing
the successful baseline encoder everywhere.

The intermediate case also shows why proof-size handling matters:
one minute of unsuccessful search can produce roughly a gigabyte of LRAT.
Live outputs were kept outside the shared workspace and unfinished
certificates discarded. Only completed, checked proofs were compressed and
published, with decompression hashes verified.

## Replay and exact scope

From the package root:

    python3 research_round6/strengthened_trials/verify_strengthened_trials.py

The replay rebuilds the pinned checkers from bundled sources, verifies the
semantic input hashes, regenerates all four exact formulas, checks the
stored compressed formula bytes, and replays the two accepted LRAT proofs.
It explicitly leaves the two timeout outcomes uncertified.

No SAT solver is needed for this replay. Python, a C compiler, and the
same supported Linux x86-64 checker environment are required. The recorded
fresh replay completed in about nine seconds.

The producer is preserved for inspection and refuses to overwrite completed
case folders. A repeat search should use a separate checkpoint copy with
its completed diagnostic results moved aside. The formal scope remains unchanged: upstream verified checker
acceptance establishes unsatisfiability of the exact CNFs; the separate
one-way mathematical encoder audit supplies their interpretation. The
Kakeya encoder itself is not proof-assistant formalized.
