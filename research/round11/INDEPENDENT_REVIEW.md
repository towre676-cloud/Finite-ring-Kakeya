# Independent verification of Round 11

Reviewed PR head `30f4adca0208a737879fe5b1cde436dff674ddfd` against base `67c0b623a59b4eb9893f6e93135b34d2b77ca8e9`. The scope is dimension five over both coordinate rings, with total mass at most 93. The audit reproduced the profile overlay and the heavy-residue restrictions. Round 11 earns zero new whole-profile or whole-affine-class exclusions. The unrestricted lower bound of 94 remains open.

## Profile reconciliation

The Round 8 verifier reproduced 950 exclusions from 183,476 input profiles. A separate scan keyed every input and output row by its sorted weight tuple and checked uniqueness, support size, exact maximum, minimum weight and total budget. Every surviving row was present byte-for-byte in the input. The survivor file has SHA-256 `1eaf4e100d9b9a4a65556c5251249fd1e7062d51e8771b7af83761ffabbd4423`.

| Support | Exact maximum | Before Round 8 replay | Excluded by Round 8 | In the Round 8 survivor ledger | Removed by Round 10 overlay |
|---:|---:|---:|---:|---:|---:|
| 13 | 12 | 9,799 | 10 | 9,789 | 9,789 |
| 13 | 13 | 11,968 | 6 | 11,962 | 11,962 |
| All other cells | | 161,709 | 934 | 160,775 | 0 |
| Total | | 183,476 | 950 | 182,526 | 21,751 |

The coverage replay checked 169 hub transports. At each of the two closed maxima, the 28 inherited masks and the 27 masks in the recovered campaign are disjoint and together exhaust the 55 marked roles. The recovered campaign contributes 29 Round 9 acceptances and 25 Round 10 acceptances across the two maxima. The 26 Round 10 receipts include two accepted variants of one case. The overlay acts on the two exact support/maximum keys in the post-Round-8 ledger. It leaves 32 of the original 34 cells, and the 16 entries already removed by Round 8 are outside the overlap.

The audit restored and hash-checked 433 Round 10 evidence files. The baseline proof for mask 1101613334 at exact maximum 12 was independently replayed. The regenerated CNF matched its pinned SHA-256, DRAT-trim reconstructed LRAT with SHA-256 `09077211b7fe7fe3aac6e6ca1e113fb0f1c9dcd26618b9cbdc05fdf0298a3be4`, and the pinned CakeML checker accepted it. The other Round 10 acceptances were checked through their scopes and checker-log hashes. The earlier marked-role proofs are inherited evidence.

The C++ affine grouping replay reproduced the archived output byte-for-byte. The supports 14 through 17 have 88, 113, 131 and 145 marked catalogue masks in 21, 23, 30 and 30 unmarked classes, respectively. The profile ledger and these geometry catalogues have no complete feasibility join. The separate exact-maximum-11 ledger retains 42 classes on supports 14, 15 and 16, split 9, 16 and 17.

## Heavy-difference-cover theorem

For support 13 at maxima 14 and 15, the inherited incidence argument forces at least ten heavy fibres. In a missing heavy direction, each light incidence supplies at most seven of the 16 lifted directions. For nine or more heavy residues, the missing directions cannot contain a binary plane, since the heavy residues would then occupy at most eight cosets with one residue each. A three-point light fibre can therefore supply at most two missing-direction incidences. With exactly ten heavies, three lights give at most six incidences, permitting at most two missing directions. With eleven or more heavies the two available lights cannot cover even one missing direction. A light-light edge consumes two of the three available lights while supplying at most one lift, so any missing direction with ten heavies requires three distinct heavy partners.

**Two missing directions.** Each of the three lights has weight three and is active only in the plane spanned by the two missing directions. Every heavy vertex is incident to a private heavy edge outside that plane. The Python search covers all affine normal forms containing the six-point affine basis, since the 29 represented directions force affine rank five. It checked 14,950 sets, including 5,220 with exactly two missing directions. In the separate C++ search, fixing the two directions to 1 and 2 leaves only the empty set, singletons and the two diagonals as possible occupations of each plane coset. It checked 1,141,504 sets, including 43,008 with exactly two missing directions.

A private edge must cover all 16 lifts. At an endpoint with at most two quotient pair points, the product ceiling is at most 14. With three pair points, each coset of their two-plane must contain at least two points of the partner to cover all four outputs there. Four cosets require at least eight partner points, exceeding the ceiling of seven. Both endpoint weights must therefore be at least eight. The resulting minimum mass is 95 at maximum 14 and 96 at maximum 15. The same reasoning gives 95 in the scoped support-14, maximum-11 sector with ten heavies and two missing directions, where all four lights must participate.

**One missing direction.** The 27 open marked roles at each maximum are the exact complement of inherited exclusions. Marking a maximum allows ties. The enumeration chooses every three-element light set away from the marked hub. It requires the three distinct heavy partners and covers the weight-two option and every plane triple through the missing direction for each weight-three light. Projection onto incident directions preserves active edges, including light-light edges, which require activity at both endpoints.

For three quotient pair points, a coset with zero, one or at least two partner points contributes at most zero, three or four outputs. Optimizing the four coset occupancies gives `q+8` for partner ceilings 5 through 7. Every other entry uses the product ceiling capped at 16. I compared all 64 ceiling pairs with independent integer allocation and checked monotonicity, which is needed for inverting the bound. For each projected light choice, a private heavy edge forces the even lower weight eight. Other adjustable heavy weights start at the even lower bound four, while the hub is fixed at the exact maximum. Raising the pair ceiling of any adjustable partner by one costs at least two points. The subsequent recursion enumerates every integer assignment up to the exact maximum under the remaining mass budget.

| Replay stage | Max 14 | Max 15 |
|---|---:|---:|
| Projected light choices | 114,466 | 114,466 |
| Choices surviving both mass floors | 714 | 58 |
| Labelled weights tested | 48,840 | 3,190 |
| Directional capacity failures | 48,752 | 3,186 |
| Spectrum failures | 88 | 4 |

For each residual leaf, the sum of capacities on the other edges imposes a lower pair count on the selected endpoint. The matching property supplies at most one demand per vertex per direction. Sorted spectrum tails therefore give a necessary test. The standalone checker recomputed the demands and checked 491 normalized eight-point fibres and 2,930 normalized nine-point fibres, yielding seven and nine histograms. I also reran the entire one-missing enumeration with all other weights assigned unrestricted histograms. The same 92 leaves were rejected using only those actual eight- and nine-point subsets. The tracked coverage, exclusion and affine output files reproduced byte-for-byte.

## First certification target

Start with support 13, exact maximum 15, marked mask **2254541078** in affine class **108**. Of the 299 possible choices of up to three nonhub lights for this role, just 11 have full heavy difference cover. Their counts by number of light residues are 1, 4, 6 and 0, the smallest total among the 27 open roles. Thus every candidate in this role needs at least 11 heavy residues. Maxima 14 and 15 have the same geometric counts, and the weight-15 marked hub uses one additional point with the same pair ceiling of seven. This is a priority for a checked complete marked-role exclusion. Closing the full cell would require every still-open role. Small profile counts in higher-support cells do not provide a comparable bound on placements, since their feasibility join remains open.

## Reproduction

Use Python 3.12 and GCC/G++ 14 on x86-64, or compatible toolchains. Start at the reviewed head or apply the proposed audit patch to it. Run the restoration and Round 11 replay commands in [README.md](README.md). Also run the original Round 8 verifier from the repository root.

```sh
r8=rounds/Kakeya_Round8_One_Folder/Kakeya_Round8
r9=rounds/Kakeya_Round9_Recovered_2026-11-04/Kakeya_Round9
python3 "$r8/research_round8/incidence/verify_three_direction_profiles.py"

compiler=$(command -v gcc)
build_wrapper=$(mktemp -d)
printf '#!/bin/sh\nexec "%s" -D_DEFAULT_SOURCE "$@"\n' "$compiler" > "$build_wrapper/gcc"
chmod +x "$build_wrapper/gcc"
PATH="$build_wrapper:$PATH" python3 "$r9/research_round10/replay.py" \
  --case s13_T1101613334_m12_baseline
```

The historical replay writes its local receipt to `research_round10/REPLAY.json`. Keep that generated receipt outside any publication diff.

The following independent scan reproduces the intersection and target ranking. It also replays the one-missing search with the actual weight-eight and weight-nine fibres as its only restrictive spectra.

```sh
PYTHONPATH=research/round11 python3 - <<'PY'
from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import json

import verify_missing as v
from audit_frontier import PROFILE, R8, points
from check_spectrum_leaves import normalized_spectra, upper

def profiles(path):
    rows = {}
    for line in path.read_bytes().splitlines():
        s, m, _, *weights = map(int, line.split())
        key = tuple(sorted(weights))
        assert len(key) == s and key[-1] == m and key[0] >= 2
        assert sum(key) <= 93 and key not in rows
        rows[key] = line
    return rows

before = profiles(R8 / "research_round7/charging/after_integer_dual_survivors.txt")
after = profiles(PROFILE)
assert all(before.get(key) == row for key, row in after.items())
assert (len(before), len(after)) == (183476, 182526)
cells = Counter((len(w), max(w)) for w in after)
removed = Counter((len(w), max(w)) for w in before.keys() - after.keys())
closed = {(13, 12), (13, 13)}
assert {k: cells[k] for k in closed} == {(13, 12): 9789, (13, 13): 11962}
assert {k: removed[k] for k in closed} == {(13, 12): 10, (13, 13): 6}
print(len(cells), len(cells.keys() - closed), sum(cells[k] for k in cells.keys() - closed))
print(sha256(PROFILE.read_bytes()).hexdigest())

root = Path("research/round11")
coverage = json.loads((root / "coverage.json").read_text())
ranked = []
for role in coverage["support13_open_marked_roles"]["15"]:
    mask = role["mask"]
    support = set(points(mask | 1))
    counts = Counter(
        k for k in range(4) for light in combinations(support - {0}, k)
        if len({a ^ b for a, b in combinations(support - set(light), 2)}) == 31
    )
    ranked.append((sum(counts.values()), mask, role["class"], dict(counts)))
assert min(ranked) == (11, 2254541078, 108, {0: 1, 1: 4, 2: 6})
print(min(ranked))

for p in range(8):
    for q in range(8):
        assert upper(p, q) == v.capacity(p, q)
        assert p == 0 or v.capacity(p - 1, q) <= v.capacity(p, q)
spectra = {w: {(31,) * 8} for w in range(4, 16)}
for w in (8, 9):
    spectra[w] = {
        tuple(sum(p >= k for p in pairs) for k in range(8))
        for pairs in normalized_spectra(w)[1]
    }
v.load_spectra = lambda repo: spectra
replay = v.one_missing(Path("."), coverage)
stored = json.loads((root / "exclusions.json").read_text())["one_missing_support13"]
assert json.loads(json.dumps(replay["by_maximum"])) == stored["by_maximum"]
def leaf_keys(rows):
    return [{k: x for k, x in row.items() if k != "spectrum_deficits"} for row in rows]
assert json.loads(json.dumps(leaf_keys(replay["spectrum_leaf_witnesses"]))) == leaf_keys(stored["spectrum_leaf_witnesses"])
print("PASS: all 92 leaves excluded using only actual weight-eight and weight-nine spectra")
PY
```
