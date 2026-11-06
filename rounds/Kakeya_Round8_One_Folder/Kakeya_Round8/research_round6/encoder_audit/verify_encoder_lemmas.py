#!/usr/bin/env python3
"""Independent finite checks supporting the hand audit; no SAT solver needed."""
from pathlib import Path
import hashlib
import importlib.util
import itertools
import json
import random
import time

ROOT = Path(__file__).resolve().parent
IMPORTED = ROOT.parent / "imported_claude_round4"
PIN = "8d4bde67dfcf3776fd2588329adff674f6b643f25e9a91c98607d8b8f92478bd"


def load_encoder():
    path = IMPORTED / "src/encode_cnf2.py"
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != PIN:
        raise ValueError("Imported encoder changed: " + actual)
    spec = importlib.util.spec_from_file_location("imported_encoder_audit", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def satisfied(clauses, assignment):
    return all(any(assignment[abs(lit)] == (lit > 0) for lit in cl) for cl in clauses)


def verify_primitives(E):
    exactly_cases = totalizer_cases = 0
    for size in range(13):
        f = E.CNF()
        inputs = [f.new() for _ in range(size)]
        f.exactly_one(inputs)
        auxiliaries = list(range(size + 1, f.n + 1))
        if size > 6 and len(auxiliaries) != size:
            raise AssertionError("Unexpected sequential encoder structure")
        for bits in itertools.product((False, True), repeat=size):
            a = dict(zip(inputs, bits))
            if size > 6:
                seen = False
                for v, bit in zip(auxiliaries, bits):
                    seen = seen or bit
                    a[v] = seen
            if satisfied(f.cl, a) != (sum(bits) == 1):
                raise AssertionError(("exactly-one", size, bits))
            exactly_cases += 1

    class Trace(E.CNF):
        def __init__(self):
            super().__init__()
            self.nodes = []

        def unary_sum(self, lits):
            out = super().unary_sum(lits)
            self.nodes.append((list(lits), list(out)))
            return out

    for size in range(11):
        f = Trace()
        inputs = [f.new() for _ in range(size)]
        outputs = f.unary_sum(inputs)
        for bits in itertools.product((False, True), repeat=size):
            a = dict(zip(inputs, bits))
            for ins, outs in f.nodes:
                total = sum(a[x] for x in ins)
                for j, out in enumerate(outs):
                    a[out] = total > j
            if not satisfied(f.cl, a):
                raise AssertionError(("totalizer semantic extension", size, bits))
            if [a[x] for x in outputs] != [sum(bits) > j for j in range(size)]:
                raise AssertionError(("totalizer meaning", size, bits))
            totalizer_cases += 1
    return {"exactly_one_assignments": exactly_cases, "totalizer_assignments": totalizer_cases}


def verify_capacity_table(E):
    M = E.load_M(IMPORTED / "data/Mtable.txt")
    for p in range(17):
        for q in range(17):
            bound = min(16, p * q)
            if min(p, q) == 3 and max(p, q) in (5, 6, 7):
                bound = max(p, q) + 8
            if M[p][q] != bound:
                raise AssertionError(("capacity entry", p, q, M[p][q], bound))
    # Occupancy proof for a three-set in a binary affine plane.
    occupancies = {}
    for q in range(17):
        best = max(
            sum(0 if t == 0 else 3 if t == 1 else 4 for t in ts)
            for ts in itertools.product(range(5), repeat=4)
            if sum(ts) == q
        )
        occupancies[q] = best
        if best != M[3][q]:
            raise AssertionError(("three-set occupancy", q, best, M[3][q]))
    return {"entries": 289, "three_set_coset_bound": occupancies}


def translation_masks(n):
    q = 1 << n
    return [
        (1 << j, sum(1 << x for x in range(q) if not (x & (1 << j))))
        for j in range(n)
    ]


def translate(mask, d, masks):
    for j, (shift, low) in enumerate(masks):
        if d & (1 << j):
            mask = ((mask & low) << shift) | ((mask >> shift) & low)
    return mask


def inspect_set(mask, n, masks):
    q = 1 << n
    w = mask.bit_count()
    if w < 2:
        return None
    pairs = [0] + [(mask & translate(mask, d, masks)).bit_count() // 2 for d in range(1, q)]
    K = {0} | {d for d in range(1, q) if pairs[d] == w // 2}
    if any(a ^ b not in K for a in K for b in K):
        raise AssertionError(("maximal subspace", n, mask))
    h = len(K)
    if any(pairs[d] != pairs[d ^ k] for d in range(1, q) if d not in K for k in K):
        raise AssertionError(("coset constancy", n, mask))
    if w % 2 == 0:
        if any(translate(mask, k, masks) != mask for k in K):
            raise AssertionError(("even period", n, mask))
        if any(pairs[d] % h for d in range(1, q) if d not in K):
            raise AssertionError(("even divisibility", n, mask))
    elif h > 1:
        cosets = {frozenset(x ^ k for k in K) for x in range(q)}
        partial = [sum(bool(mask & (1 << x)) for x in C) for C in cosets]
        partial = [t for t in partial if 0 < t < h]
        if len(partial) != 1 or partial[0] not in (1, h - 1):
            raise AssertionError(("one partial coset", n, mask, partial))
        if h >= 4:
            residues = {0, w % h}
            if w % h not in (1, h - 1):
                raise AssertionError(("odd weight residue", n, mask))
            if any(pairs[d] % h not in residues for d in range(1, q) if d not in K):
                raise AssertionError(("odd pair residues", n, mask))
    return h


def verify_subspace_lemma():
    hist = {}
    masks = translation_masks(4)
    examined = 0
    for mask in range(1, 1 << 16):
        h = inspect_set(mask, 4, masks)
        if h is not None:
            examined += 1
            key = str(h)
            hist[key] = hist.get(key, 0) + 1
    rng = random.Random(20261028)
    masks5 = translation_masks(5)
    samples = set()
    for w in range(2, 33):
        for trial in range(64):
            samples.add(sum(1 << x for x in rng.sample(range(32), w)))
    for mask in sorted(samples):
        inspect_set(mask, 5, masks5)
    return {
        "dimension4_nonempty_subsets": 65535,
        "dimension4_weight_at_least2": examined,
        "dimension4_maximal_subspace_sizes": hist,
        "dimension5_reproducible_examples": len(samples),
        "seed": 20261028,
    }


def verify_spectrum_metadata(E):
    specs = E.load_spectra(IMPORTED / "data/spec32.csv")
    subspaces = E.all_subspaces()
    if len(subspaces) != 374 or len(set(subspaces)) != 374:
        raise AssertionError("wrong subspace count")
    for H in subspaces:
        if 0 not in H or any(x ^ y not in H for x in H for y in H):
            raise AssertionError("non-subspace")
    by_dimension = {
        str(r): sum(len(H) == 1 << r for H in subspaces)
        for r in range(6)
    }
    if list(by_dimension.values()) != [1, 31, 155, 155, 31, 1]:
        raise AssertionError("Gaussian-binomial count mismatch")
    ambiguous = []
    for w, hist, lo, hi in specs:
        if len(hist) != 17 or sum(hist) != 31:
            raise AssertionError(("histogram", w, hist))
        if sum(i * c for i, c in enumerate(hist)) != w * (w - 1) // 2:
            raise AssertionError(("pair total", w, hist))
        if any(hist[j] for j in range(w // 2 + 1, 17)):
            raise AssertionError(("pair maximum", w, hist))
        c = hist[w // 2]
        if (c + 1) & c:
            raise AssertionError(("maximal-subspace cardinality", w, hist))
        if lo != hi:
            ambiguous.append({"weight": w, "histogram": hist, "ranks": [lo, hi]})
    return {
        "spectra": len(specs),
        "subspaces": len(subspaces),
        "subspaces_by_dimension": by_dimension,
        "rank_intervals": ambiguous,
        "limitation": "Metadata checks do not replace complete spectrum-census enumeration.",
    }


def main():
    started = time.monotonic()
    E = load_encoder()
    report = {
        "status": "PASS",
        "scope": "Finite corroboration of hand proofs and primitive CNF assignments; not formal verification.",
        "encoder_sha256": PIN,
        "primitives": verify_primitives(E),
        "capacity": verify_capacity_table(E),
        "spectra_metadata": verify_spectrum_metadata(E),
        "maximal_subspace": verify_subspace_lemma(),
    }
    report["seconds"] = round(time.monotonic() - started, 3)
    (ROOT / "ENCODER_LEMMA_REPLAY.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
