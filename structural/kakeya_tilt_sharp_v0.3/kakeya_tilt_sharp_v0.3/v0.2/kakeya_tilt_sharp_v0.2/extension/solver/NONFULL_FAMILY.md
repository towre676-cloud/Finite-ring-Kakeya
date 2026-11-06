# A 24-point family without a full fibre

Let V=F₂³ with basis e1,e2,e3, encoded by binary integers 1,2,4.
For either R=Z/4Z or R=F₂[t]/(t²), write K in residue fibres A_a⊂V.
Choose the following five nonempty fibres, with every displayed translation
parameter arbitrary:

\[
\begin{aligned}
A_0&=V\setminus(c_0+\langle7\rangle),\\
A_1&=V\setminus(c_1+\langle3\rangle),\\
A_2&=c_2+\langle1,2\rangle,\\
A_4&=c_4+\langle1,4\rangle,\\
A_7&=c_7+\langle1,6\rangle.
\end{aligned}
\]

The remaining fibres A3,A5,A6 are empty. The total size is

\[
|K|=6+6+4+4+4=24,
\]

and every fibre has size at most six. There are four choices for each deleted
two-point coset and two choices for each four-point plane coset, giving exactly
4·4·2·2·2=128 different sets in this fixed residue placement.

**Theorem. Every one of these 128 sets is Kakeya in both rings.**

For a nonzero direction v, work in the four-element quotient Q_v=V/⟨v⟩.
If A is the complement of a two-point coset with difference d, then P_v(A)
has three elements when v=d. If v≠d, P_v(A) is a two-element coset with period
[d] in Q_v. If A is a coset of a two-dimensional subspace U containing v,
then P_v(A) is a two-element coset with period U/⟨v⟩.

Two two-element cosets in Q_v with different nonzero periods have sum Q_v.
A three-element set plus a two-element set also has sum Q_v, because the
complement of the three-element set has only one element.

The following single residue edge covers every lifted direction above each v:

| v | Fibre edge | Pair-set sizes | Reason the sum is Q_v |
|---:|---|---|---|
| 1 | {0,1} | 2,2 | periods [7] and [3] are different modulo ⟨1⟩ |
| 2 | {0,2} | 2,2 | periods [7] and [1] are different modulo ⟨2⟩ |
| 3 | {1,2} | 3,2 | size 3 plus size 2 fills a group of order 4 |
| 4 | {0,4} | 2,2 | periods [7] and [1] are different modulo ⟨4⟩ |
| 5 | {1,4} | 2,2 | periods [3] and [1] are different modulo ⟨5⟩ |
| 6 | {1,7} | 2,2 | periods [3] and [1] are different modulo ⟨6⟩ |
| 7 | {0,7} | 3,2 | size 3 plus size 2 fills a group of order 4 |

Each sum is the entire quotient before the carry translation is applied.
Translations of the fibres and the mixed-characteristic carry therefore
preserve coverage. The exact fibre-cover identity proves the theorem.

The retained `nonfull_period_n3_lift.json` enumerates all 128 sets and records
that every one is Kakeya in both rings, together with an explicit point list.
This computation supplements the proof above.

## Why the preceding 24-point profile was insufficient

The older exact-local relaxation point used the same sizes but placed the
last plane at residue 6 and assigned the second six-point fibre a deleted
pair of difference 5. In direction 6 only the edge {0,6} contributes. Both
pair sets then have two elements and the same period [1] in Q6. Their sum
has two elements, leaving two lifted directions uncovered. Every one of its
128 possible local realizations fails, in both rings.

The adjustment above changes the incidence between residue support and
internal periods. It gives a concrete distinction between local realizability
and simultaneous line coverage, and shows the shared-period cut selecting a
fully realizable family.
