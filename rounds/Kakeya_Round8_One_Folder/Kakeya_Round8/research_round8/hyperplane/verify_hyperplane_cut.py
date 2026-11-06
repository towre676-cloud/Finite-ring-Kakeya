#!/usr/bin/env python3
"""Independent finite controls for the elementary crossing-pair extension."""
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


E = module("hyperplane_base", ROOT / "research_round6/joint_maxima/encode_joint_maxima.py")
C = module("hyperplane_cut", HERE / "hyperplane_cut.py")
DATA = ROOT / "research_round6/imported_claude_round4/data/spec32.csv"
SPEC = E.load_spectra(DATA)


def counts(points, n):
    result = [0] * (1 << n)
    for a, b in itertools.combinations(points, 2):
        result[a ^ b] += 1
    return result


def rank(points):
    base = points[0]
    span = {0}
    for point in points[1:]:
        delta = point ^ base
        span |= {x ^ delta for x in span}
    return len(span).bit_length() - 1


def local_formula(directions):
    f = E.CNF()
    f.z = {(0, i): f.new() for i, sp in enumerate(SPEC) if 2 <= sp[0] <= 11}
    f.y = {(0, d, k): f.new() for d in directions for k in range(6)}
    C.append_hyperplane_cuts(f, [0], SPEC)
    return f


def assign(f, index, pair_counts):
    a = {z: i == index for (v, i), z in f.z.items()}
    a.update({z: pair_counts[d] == k for (v, d, k), z in f.y.items()})
    C.complete_assignment(f, a)
    return a


def failed(f, assignment):
    return [i for i, clause in enumerate(f.cl)
            if not any(assignment[abs(x)] == (x > 0) for x in clause)]


def main():
    started = time.monotonic()
    # All subsets of F2^4: the identity and bound for all fifteen functionals.
    hyperplane_masks = {u: sum(1 << x for x in range(16) if C.dot(u, x))
                        for u in range(1, 16)}
    identity_checks = 0
    for mask in range(1 << 16):
        points = [x for x in range(16) if mask >> x & 1]
        p = counts(points, 4)
        w = len(points)
        for u, side in hyperplane_masks.items():
            b = (mask & side).bit_count()
            actual = sum(p[d] for d in range(1, 16) if C.dot(u, d))
            assert actual == b * (w - b)
            assert actual <= C.crossing_budget(w)
            identity_checks += 1

    directions = [x for x in range(1, 32) if 377850134 >> x & 1]
    f = local_formula(directions)
    rng = random.Random(80102026)
    witness_checks = 0
    for w in range(2, 12):
        for repetition in range(12):
            points = sorted(rng.sample(range(32), w))
            p = counts(points, 5)
            hist = [p[1:].count(k) for k in range(17)]
            r = rank(points)
            choices = [i for i, sp in enumerate(SPEC)
                       if sp[0] == w and sp[1] == hist and sp[2] <= r <= sp[3]]
            assert len(choices) == 1
            assignment = assign(f, choices[0], p)
            assert not failed(f, assignment)
            witness_checks += 1

    # A locally baseline-admissible near-cube histogram arranged incorrectly.
    # Its seven p=3 directions are not required to form a space by the old K
    # rule, because its actual maximum possible count floor(8/2)=4 never occurs.
    subs = [s for s in E.all_subspaces() if len(s) == 16]
    candidates = [(H, u, [d for d in directions if d in H and C.dot(u, d)])
                  for H in subs for u in range(1, 32)]
    H, u, high = next(x for x in candidates if len(x[2]) >= 6)
    high = high[:6]
    high.append(next(d for d in H if d and d not in high))
    omitted = next(d for d in H if d and d not in high)
    p = [0] * 32
    for d in H:
        if d and d != omitted:
            p[d] = 3 if d in high else 1
    index = next(i for i, sp in enumerate(SPEC)
                 if sp[0] == 8 and sum(k*k*c for k, c in enumerate(sp[1])) == 70)
    assert [p[1:].count(k) for k in range(17)] == SPEC[index][1]
    assert SPEC[index][2:] == (4, 4)
    assert p.count(4) == 0
    assert all(p[d] == 0 for d in range(1, 32) if d not in H)
    bad = assign(f, index, p)
    bad_crossing_sum = sum(p[d] for d in directions if C.dot(u, d))
    violations = failed(f, bad)
    assert violations
    # With all spectrum gates off, the same counter assignment is permitted.
    for literal in f.z.values():
        bad[literal] = False
    assert not failed(f, bad)

    # Disabling the append function preserves an arbitrary formula exactly.
    disabled = E.CNF()
    x, y = disabled.new(), disabled.new()
    disabled.add([x, -y])
    original = (disabled.n, [list(c) for c in disabled.cl])
    C.append_hyperplane_cuts(disabled, [], SPEC, enabled=False)
    assert original == (disabled.n, disabled.cl)

    # The recurrence is independent of histogram values: compare it with
    # direct counts on every assignment to five one-hot 0..4 directions.
    mini = local_formula([1, 2, 4, 8, 16])
    counter_checks = 0
    for selected in itertools.product(range(5), repeat=5):
        p = [0] * 32
        for d, k in zip([1, 2, 4, 8, 16], selected):
            p[d] = k
        assignment = assign(mini, -1, p)
        assert not failed(mini, assignment)
        counter_checks += 1

    sources = [Path(__file__), HERE / "hyperplane_cut.py",
               HERE / "HYPERPLANE_CROSSING_LEMMA.txt", DATA,
               ROOT / "research_round6/joint_maxima/encode_joint_maxima.py"]
    receipt = {
        "status": "PASS", "seconds": round(time.monotonic() - started, 3),
        "complete_F2_4_identity_checks": identity_checks,
        "actual_F2_5_fibre_assignments": witness_checks,
        "complete_small_counter_assignments": counter_checks,
        "invalid_histogram_arrangement_rejected": {
            "spectrum_index": index, "direction_space": sorted(H),
            "linear_functional": u, "observed_crossing_pairs":
                bad_crossing_sum,
            "permitted_budget": 16, "violated_clauses": len(violations)},
        "gate_off_control": "PASS", "disabled_identity": "PASS",
        "local_formula_statistics": f.hyperplane_cut_statistics,
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sources},
        "scope": "Local mathematical and encoder controls only; no support exclusion."
    }
    target = HERE / "HYPERPLANE_CUT_REPLAY.json"
    target.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
