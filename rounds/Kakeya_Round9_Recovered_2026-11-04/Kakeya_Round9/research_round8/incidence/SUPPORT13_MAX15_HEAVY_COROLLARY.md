# Support thirteen, maximum fifteen: at least ten heavy fibres

## Statement and scope

Let a Kakeya configuration in either of the two coordinate rings have thirteen pair-active residue fibres in $\mathbb F_2^5$, each of weight between $2$ and $15$. Call a residue **heavy** when its fibre has weight at least $4$. Then

$$
\boxed{|H|\ge 10.}
$$

This statement does **not** require a total-weight bound, a fibre-spectrum census, a quotient-sumset table, an enumerated support catalogue, or a SAT computation. It extends the maximum-thirteen consequence proved in `MISSING_DIRECTION_INCIDENCE.md`. The already frozen encoder and its original scope are unchanged by this note.

The analytic direction bounds used below are proved in the pinned Round7 note `research_round7/dense_encoder/NINE_POINT_DIFFERENCE_ANALYTIC_PROOF.md`: an eight-point subset of $\mathbb F_2^5$ has at most $25$ nonzero pair differences, and a nine-point subset has at most $28$.

## Counting active light incidences

Write $h=|H|$, $L=13-h$, and

$$
M=(\mathbb F_2^5\setminus\{0\})\setminus D(H).
$$

Let $P=\lfloor m/2\rfloor\le7$, where $m$ is the maximum fibre weight. For each $d\in M$, no support edge in direction $d$ has two heavy endpoints. A light fibre has weight $2$ or $3$, so its pair count in any direction is at most one. A heavy–light edge therefore has capacity at most $P$. A light–light edge has capacity at most one and uses two active light endpoints. Since the support edges in a fixed direction form a matching, the total capacity is at most $P$ times the number of light fibres active in that direction. Covering the sixteen lifted directions consequently needs at least

$$
r=\left\lceil\frac{16}{P}\right\rceil\ge3
$$

active light incidences in every direction of $M$.

A weight-two fibre is active in one direction; a weight-three fibre is active in exactly three directions. Without any assumption on $h$, summing over $M$ thus gives the weaker universal bound

$$
r|M|\le L_2+3L_3\le3L.
\tag{1}
$$

When $h\ge9$, $M$ cannot contain all three nonzero vectors of a binary two-space. Otherwise $H$ would contain at most one point in each of the eight cosets of that two-space. The three directions of a weight-three fibre form precisely such a plane. Therefore at most two lie in $M$, yielding the stronger incidence inequality

$$
r|M|\le L_2+2L_3\le2L.
\tag{2}
$$

This is the general theorem already established in `MISSING_DIRECTION_INCIDENCE.md`. Ring-specific carry terms translate quotient sumsets and do not alter any capacity bound used here.

## Excluding every heavy count below ten

If $0\le h\le7$, the elementary pair bound gives $|M|\ge31-\binom h2$. Combining this with (1) and $r\ge3$ would require

$$
31-\binom h2\le13-h.
$$

The gap is

$$
18+h-\binom h2>0\qquad(0\le h\le7).
$$

For example, its minimum on these eight integers is $4$, at $h=7$. Thus these cases are impossible.

If $h=8$, the analytic bound $|D(H)|\le25$ leaves at least six missing directions. Equation (1) would require

$$
18\le r|M|\le3(13-8)=15,
$$

again impossible.

If $h=9$, the analytic bound $|D(H)|\le28$ leaves at least three missing directions. Equation (2) would require

$$
9\le r|M|\le2(13-9)=8,
$$

which is the final contradiction. Hence $h\ge10$.

The same calculation also shows $|M|\le2$ once $h\ge10$. If $h\ge11$, there are at most two light fibres, so a missing direction has capacity at most $2P\le14<16$. Thus

$$
|D(H)|\ge29,\qquad h\ge11\Longrightarrow D(H)=\mathbb F_2^5\setminus\{0\}.
$$

These additional consequences are analytic observations; this extension makes no new SAT-encoding or solver claim.

## Exact inherited-frontier consequence

The pinned Round7 frontier contains exactly **128** support-thirteen profiles with maximum at most fifteen and fewer than ten heavy fibres. All have exactly nine heavy fibres. Their maxima are distributed as follows:

| Maximum fibre weight | Excluded whole profiles | Previously recorded in the sixteen-profile stage |
|---|---:|---:|
| 12 | 10 | 10 |
| 13 | 6 | 6 |
| 14 | 69 | 0 |
| 15 | 43 | 0 |
| **Total** | **128** | **16** |

There are **112 additional exclusions** beyond that frozen intermediate stage. Of the 128 profiles, 127 have four light fibres of weight three, giving the exact contradiction $9>8$; one has light weights $3,3,3,2$, giving $9>7$.

The complete profile ledger consequently changes from $183{,}476$ to **$183{,}348$**, with its support-thirteen row changing from $85{,}340$ to **$85{,}212$**. Every other support-size row remains unchanged. This removes whole weight profiles in every placement and in both rings; it gives no extra credit to the separate SAT-role ledger.

Replay with:

```bash
python3 research_round8/incidence/verify_extended_incidence_profiles.py
```

The replay checks every source line, each displayed integer contradiction, all prior sixteen exclusions, and byte-for-byte preservation and ordering of every retained line. It also verifies that the final frontier can be obtained by removing exactly the additional 112 profiles from the frozen intermediate frontier. The two earlier profile artifacts and their verifier remain unchanged.
