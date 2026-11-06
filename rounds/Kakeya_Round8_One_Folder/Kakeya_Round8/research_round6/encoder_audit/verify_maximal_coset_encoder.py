#!/usr/bin/env python3
"""Test the optional strengthening against actual fibres and the exact baseline."""
from pathlib import Path
import gc
import hashlib
import importlib.util
import itertools
import json
import random
import time

ROOT = Path(__file__).resolve().parent
IMPORTED = ROOT.parent / "imported_claude_round4"


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    out = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(out)
    return out


def cnf_digest(f):
    h = hashlib.sha256()
    h.update(f"p cnf {f.n} {len(f.cl)}\n".encode())
    for cl in f.cl:
        h.update((" ".join(map(str, cl)) + " 0\n").encode())
    return h.hexdigest()


def affine_direction_space(A):
    a0 = min(A)
    H = {0}
    for x in sorted(A):
        d = x ^ a0
        H |= {h ^ d for h in H}
    return frozenset(H)


def actual_assignment(A, E, SUBS):
    """Build just the extra clause family, then assign it from an actual set."""
    f = E.CNF()
    H = affine_direction_space(A)
    p = {d: sum((x ^ d) in A for x in A) // 2 for d in range(1, 32)}
    K = frozenset({0} | {d for d, value in p.items() if value == len(A) // 2})
    y = {(0, d, k): f.new() for d in range(1, 32) for k in range(17)}
    hs = {U: f.new() for U in SUBS}
    ks = {U: f.new() for U in SUBS}
    mem = E.append_maximal_subspace_constraints(
        f, [0], {0: list(range(1, 32))}, y, {0: hs}, {0: ks}, SUBS
    )
    assignment = {}
    for (v, d, k), lit in y.items():
        assignment[lit] = p[d] == k
    for U, lit in hs.items():
        assignment[lit] = U == H
    for U, lit in ks.items():
        assignment[lit] = U == K
    for (v, r), lit in mem.items():
        assignment[lit] = r in K
    if len(assignment) != f.n:
        raise AssertionError("not every auxiliary assigned")
    return f, assignment, y, hs, ks, mem, H, K


def fails(f, a):
    return [
        i for i, cl in enumerate(f.cl)
        if not any(a[abs(x)] == (x > 0) for x in cl)
    ]


def check_actual_shapes(E, SUBS):
    shapes = {frozenset(H) for H in SUBS if len(H) >= 2}
    shapes |= {frozenset(H - {0}) for H in SUBS if len(H) >= 4}
    rng = random.Random(20261028)
    for w in range(2, 33):
        for trial in range(3):
            shapes.add(frozenset(rng.sample(range(32), w)))
    examined = 0
    for A in sorted(shapes, key=lambda x: (len(x), sorted(x))):
        f, a, *_ = actual_assignment(A, E, SUBS)
        bad = fails(f, a)
        if bad:
            raise AssertionError(("real fibre rejected", sorted(A), bad[:5]))
        examined += 1

    # Make three deliberate inconsistencies, each rejected by the NEW rows.
    f, a, y, hs, ks, mem, H, K = actual_assignment(set(range(8)), E, SUBS)
    wrong_coset = dict(a)
    wrong_coset[y[0, 8, 0]] = False
    wrong_coset[y[0, 8, 1]] = True
    if not fails(f, wrong_coset):
        raise AssertionError("unequal coset values not detected")
    wrong_H = dict(a)
    wrong_H[hs[H]] = False
    wrong_H[hs[frozenset({0})]] = True
    if not fails(f, wrong_H):
        raise AssertionError("K not contained in H was not detected")
    wrong_member = dict(a)
    wrong_member[mem[0, 1]] = False
    if not fails(f, wrong_member):
        raise AssertionError("wrong membership bit not detected")
    return {"actual_shapes": examined, "negative_controls_rejected": 3}


def check_baseline_identity(E, B, SUBS):
    SPEC = E.load_spectra(IMPORTED / "data/spec32.csv")
    M = E.load_M(IMPORTED / "data/Mtable.txt")
    mask = next(
        int(line.split()[1])
        for line in (IMPORTED / "data/orbits_all.txt").read_text().splitlines()
        if int(line.split()[0]) == 10 and int(line.split()[3]) == 1
    )
    T = [x for x in range(1, 32) if (mask >> x) & 1]
    b = B.encode(T, 18, SPEC, M, SUBS, hub_min=2)
    baseline_n = b.n
    baseline_clauses = len(b.cl)
    baseline_hash = cnf_digest(b)
    del b
    gc.collect()
    disabled = E.encode(T, 18, SPEC, M, SUBS, hub_min=2, strengthen=False)
    if cnf_digest(disabled) != baseline_hash:
        raise AssertionError("disabled strengthening changed exact baseline")
    before = len(disabled.cl)
    disabled.membership = E.append_maximal_subspace_constraints(
        disabled, [0] + T, {v: [v ^ b for b in [0] + T if b != v] for v in [0] + T},
        disabled.y, disabled.h_selectors, disabled.k_selectors, SUBS
    )
    expected_n = baseline_n + 31 * (len(T) + 1)
    if disabled.n != expected_n:
        raise AssertionError("unexpected number of membership variables")
    strong_hash = cnf_digest(disabled)
    extra_clauses = len(disabled.cl) - before
    del disabled
    gc.collect()
    enabled = E.encode(T, 18, SPEC, M, SUBS, hub_min=2, strengthen=True)
    if cnf_digest(enabled) != strong_hash:
        raise AssertionError("integrated strengthening differs from append-only route")
    return {
        "support_mask": mask,
        "support_size": len(T) + 1,
        "hub_interval": [2, 18],
        "baseline_variables": baseline_n,
        "baseline_clauses": baseline_clauses,
        "baseline_cnf_sha256": baseline_hash,
        "strong_variables": enabled.n,
        "strong_clauses": len(enabled.cl),
        "extra_variables": 31 * (len(T) + 1),
        "extra_clauses": extra_clauses,
        "strong_cnf_sha256": strong_hash,
    }


def main():
    started = time.monotonic()
    ep = ROOT / "encode_maximal_cosets.py"
    bp = ROOT.parent / "joint_maxima/encode_joint_maxima.py"
    E = module(ep, "strong_maximal_cosets")
    B = module(bp, "baseline_joint_maxima")
    SUBS = E.all_subspaces()
    result = {
        "status": "PASS",
        "scope": "Constructive tests of new necessary clauses; no SAT exclusion is claimed here.",
        "strong_encoder_sha256": hashlib.sha256(ep.read_bytes()).hexdigest(),
        "baseline_encoder_sha256": hashlib.sha256(bp.read_bytes()).hexdigest(),
        "actual_fibres": check_actual_shapes(E, SUBS),
        "baseline_identity": check_baseline_identity(E, B, SUBS),
        "seconds": round(time.monotonic() - started, 3),
    }
    (ROOT / "MAXIMAL_COSET_ENCODER_REPLAY.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
