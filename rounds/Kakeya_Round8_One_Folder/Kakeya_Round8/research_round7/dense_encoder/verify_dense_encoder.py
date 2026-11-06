#!/usr/bin/env python3
"""Exhaustive local constructive validation and bounded encoder controls.

This finite replay needs only Python.  It does not trust a SAT solver and does
not assert that all global strengthened formulas are unsatisfiable.
"""
from pathlib import Path
import gc
import hashlib
import importlib.util
import itertools
import json
import random
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    out = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(out)
    return out


E = module("dense_encoder_under_test", HERE / "encode_dense_types.py")
B = module("frozen_joint_baseline", ROOT / "research_round6/joint_maxima/encode_joint_maxima.py")
DATA = ROOT / "research_round6/imported_claude_round4/data"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cnf_sha(f):
    h = hashlib.sha256(f"p cnf {f.n} {len(f.cl)}\n".encode())
    for c in f.cl:
        h.update((" ".join(map(str, c)) + " 0\n").encode())
    return h.hexdigest()


def span(points):
    out = {0}
    for p in points:
        out |= {q ^ p for q in list(out)}
    return frozenset(out)


def profile(A):
    return tuple(sum((x ^ d) in A for x in A) // 2 for d in range(1, 32))


def fixed_flat_profiles():
    H = frozenset(range(16))
    targets = {11: set(), 12: set()}
    examined = 0
    for complement_weight in [4, 5]:
        w = 16 - complement_weight
        for removed in itertools.combinations(H, complement_weight):
            removed = frozenset(removed)
            A = H - removed
            p = profile(A)
            examined += 1
            target_energy = 205 if w == 11 else 294
            if sum(x * x for x in p) == target_energy:
                if span(x ^ min(A) for x in A) != H:
                    raise AssertionError("actual set lacks stated affine rank")
                targets[w].add(p)
    assert len(targets[11]) == 168 and len(targets[12]) == 105
    return targets, examined


def labelled_models(SUBS):
    out = {11: {}, 12: {}}
    for values in itertools.combinations(range(1, 32), 5):
        xor = 0
        for v in values:
            xor ^= v
        if xor:
            continue
        C, H = frozenset(values), span(values)
        if len(H) != 16:
            raise AssertionError("five-circuit lemma failed")
        p = tuple(3 if d in C else 4 if d in H else 0 for d in range(1, 32))
        out[11][p] = (H, C)
    for H in [H for H in SUBS if len(H) == 16]:
        for J in [J for J in SUBS if len(J) == 8 and J <= H]:
            for u in sorted(J - {0}):
                p = tuple(5 if d in J and d != u else 4 if d in H else 0
                          for d in range(1, 32))
                out[12][p] = (H, (J, u))
    assert len(out[11]) == 5208 and len(out[12]) == 3255
    return out


def basis(H):
    b = []
    seen = {0}
    for x in sorted(H - {0}):
        if x not in seen:
            b.append(x)
            seen |= {t ^ x for t in list(seen)}
    return b


def transfer_models(actual, SUBS):
    transported = {11: set(), 12: set()}
    for H in [H for H in SUBS if len(H) == 16]:
        b = basis(H)
        images = []
        for d in range(16):
            x = 0
            for i, e in enumerate(b):
                if d >> i & 1:
                    x ^= e
            images.append(x)
        for w in [11, 12]:
            for p in actual[w]:
                q = [0] * 31
                for d in range(1, 16):
                    q[images[d] - 1] = p[d - 1]
                transported[w].add(tuple(q))
    return transported


def local_formula(SPEC, SUBS):
    f = E.CNF()
    indices = E.type_indices(SPEC)
    z = {(0, i): f.new() for i in indices.values()}
    y = {(0, d, k): f.new() for d in range(1, 32) for k in range(17)}
    h = {H: f.new() for H in SUBS}
    models = E.append_dense_constraints(
        f, [0], {0: list(range(1, 32))}, SPEC, SUBS, z, y, {0: h})
    return f, z, y, h, models


def make_assignment(f, y, h, models, w, p, data):
    H, shape = data
    a = [False] * (f.n + 1)
    for U, variable in h.items():
        a[variable] = U == H
    for (v, d, k), variable in y.items():
        a[variable] = p[d - 1] == k
    selected = "w11_q205" if w == 11 else "w12_q294"
    for (v, name), model in models.items():
        a[model["gate"]] = name == selected
        if name == selected:
            if w == 11:
                for d, variable in model["circuit"].items():
                    a[variable] = d in shape
            else:
                J, u = shape
                for U, variable in model["j_selectors"].items():
                    a[variable] = U == J
                for d, variable in model["u_selectors"].items():
                    a[variable] = d == u
        model["builder"].complete_assignment(a)
    return a


def failed_clauses(f, a):
    bad = []
    for i, clause in enumerate(f.cl):
        if not any(a[abs(x)] == (x > 0) for x in clause):
            bad.append(i)
    return bad


def exhaustive_local_checks(SPEC, SUBS):
    actual, complement_count = fixed_flat_profiles()
    generated = labelled_models(SUBS)
    transported = transfer_models(actual, SUBS)
    for w in [11, 12]:
        if set(generated[w]) != transported[w]:
            raise AssertionError("model differs from actual complement profiles")
    f, z, y, h, models = local_formula(SPEC, SUBS)
    examined = 0
    for w in [11, 12]:
        for p, data in sorted(generated[w].items()):
            a = make_assignment(f, y, h, models, w, p, data)
            bad = failed_clauses(f, a)
            if bad:
                raise AssertionError((w, p, bad[:10]))
            examined += 1
    # Every added clause has the type gate, including the hidden structural
    # variables.  Thus inactive types extend *any* existing assignment.
    for model in models.values():
        begin, end = model["clause_range"]
        assert all(-model["gate"] in c for c in f.cl[begin:end])
    rng = random.Random(20261028)
    for _ in range(64):
        a = [bool(rng.getrandbits(1)) for _ in range(f.n + 1)]
        for model in models.values():
            a[model["gate"]] = False
        assert not failed_clauses(f, a)
    # Falsification controls: changed incident pair values, incorrect hidden
    # circuit, wrong selected direction space, and a wrong omitted J-point.
    controls = []
    for w in [11, 12]:
        p, data = next(iter(generated[w].items()))
        a = make_assignment(f, y, h, models, w, p, data)
        active = models[0, "w11_q205" if w == 11 else "w12_q294"]
        H = data[0]
        d = min(H - {0})
        changed = list(a)
        changed[y[0, d, p[d - 1]]] = False
        changed[y[0, d, 0]] = True
        assert failed_clauses(f, changed)
        controls.append(f"w{w}_wrong_incident_pair")
        changed = list(a)
        changed[h[H]] = False
        changed[h[frozenset({0})]] = True
        active["builder"].complete_assignment(changed)
        assert failed_clauses(f, changed)
        controls.append(f"w{w}_wrong_H")
        if w == 11:
            changed = list(a)
            changed[active["circuit"][d]] = not changed[active["circuit"][d]]
            active["builder"].complete_assignment(changed)
            assert failed_clauses(f, changed)
            controls.append("w11_wrong_circuit")
        else:
            J, u = data[1]
            changed = list(a)
            changed[active["u_selectors"][u]] = False
            changed[active["u_selectors"][min(J - {0, u})]] = True
            active["builder"].complete_assignment(changed)
            assert failed_clauses(f, changed)
            controls.append("w12_wrong_omitted_point")
    return {
        "actual_complements_in_fixed_flat": complement_count,
        "weight11_actual_profiles_per_flat": len(actual[11]),
        "weight12_actual_profiles_per_flat": len(actual[12]),
        "all_labelled_weight11_profiles": len(generated[11]),
        "all_labelled_weight12_profiles": len(generated[12]),
        "all_constructive_clause_assignments_passed": examined,
        "inactive_gate_random_assignments_passed": 64,
        "all_new_clauses_have_own_type_gate": True,
        "negative_witness_controls_rejected": controls,
        "local_variables": f.n, "local_clauses": len(f.cl),
        "scope": "Complete labelled local pair-profile equality; negative controls reject specific bad witnesses, not independently arbitrary extensions."
    }


def baseline_checks(SPEC, M, SUBS):
    mask = 1022358
    T = [x for x in range(1, 32) if mask >> x & 1]
    baseline = B.encode(T, 18, SPEC, M, SUBS, hub_min=2)
    n, c, digest = baseline.n, len(baseline.cl), cnf_sha(baseline)
    del baseline
    gc.collect()
    disabled = E.encode(T, 18, SPEC, M, SUBS, hub_min=2, strengthen=False)
    if cnf_sha(disabled) != digest:
        raise AssertionError("Disabled new encoder changed baseline bytes")
    del disabled
    gc.collect()
    dense = E.encode(T, 18, SPEC, M, SUBS, hub_min=2, strengthen=True)
    # The exact original prefix is untouched, with the same original numbers.
    dense_prefix = E.CNF()
    dense_prefix.n = n
    dense_prefix.cl = dense.cl[:c]
    if cnf_sha(dense_prefix) != digest:
        raise AssertionError("Appending changed original variable/clause prefix")
    return {
        "support_mask": mask, "maximum_interval": [2, 18],
        "baseline_variables": n, "baseline_clauses": c,
        "baseline_cnf_sha256": digest,
        "disabled_identical": True, "original_prefix_unchanged": True,
        "dense_variables": dense.n, "dense_clauses": len(dense.cl),
        "extra_variables": dense.dense_extra_variables,
        "extra_clauses": dense.dense_extra_clauses,
        "dense_cnf_sha256": cnf_sha(dense),
    }


def boolean_primitive_checks():
    """Exhaust all inputs AND auxiliary bits for small primitive instances.

    Unlike witness-only controls these checks also rule out spurious
    auxiliary extensions in the examined Boolean truth tables.
    """
    rows = []
    assignments_examined = 0
    for kind, sizes in [("totalizer", range(5)),
                        ("exactly_one", range(1, 8)),
                        ("xor_zero", range(1, 6)),
                        ("or", range(5))]:
        for n in sizes:
            f = E.CNF()
            gate = f.new()
            inputs = [f.new() for _ in range(n)]
            g = E.Gated(f, gate)
            if kind == "totalizer":
                outputs = g.unary_sum(inputs)
            elif kind == "exactly_one":
                outputs = []
                g.exactly_one(inputs)
            elif kind == "xor_zero":
                outputs = []
                g.parity_zero(inputs)
            else:
                outputs = [g.or_literal(inputs)]
            projected = set()
            accepted = 0
            for mask in range(1 << (f.n - 1)):
                a = [False] * (f.n + 1)
                a[gate] = True
                for v in range(2, f.n + 1):
                    a[v] = bool(mask >> (v - 2) & 1)
                assignments_examined += 1
                satisfied = not failed_clauses(f, a)
                count = sum(a[v] for v in inputs)
                if satisfied:
                    accepted += 1
                    projected.add(tuple(a[v] for v in inputs))
                    if kind == "totalizer":
                        assert [a[v] for v in outputs] == [count >= k + 1 for k in range(n)]
                    elif kind == "exactly_one":
                        assert count == 1
                    elif kind == "xor_zero":
                        assert count % 2 == 0
                    else:
                        assert a[outputs[0]] == bool(count)
                a[gate] = False
                assert not failed_clauses(f, a)
            expected = (n if kind == "exactly_one" else
                        (1 << (n - 1)) if kind == "xor_zero" else 1 << n)
            assert len(projected) == expected
            rows.append({"kind": kind, "inputs": n, "variables": f.n,
                         "accepted_assignments": accepted,
                         "accepted_input_projections": len(projected)})
    return {"truth_table_assignments_examined": assignments_examined,
            "all_accepted_outputs_and_input_projections_correct": True,
            "all_inactive_assignments_accepted": True, "instances": rows}


def main():
    started = time.monotonic()
    SPEC = E.load_spectra(DATA / "spec32.csv")
    M = E.load_M(DATA / "Mtable.txt")
    SUBS = E.all_subspaces()
    result = {
        "status": "PASS_EXACT_DENSE_TYPE_CONSTRUCTIVE_REPLAY",
        "local": exhaustive_local_checks(SPEC, SUBS),
        "baseline": baseline_checks(SPEC, M, SUBS),
        "boolean_primitives": boolean_primitive_checks(),
        "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in [
            HERE / "encode_dense_types.py", HERE / "verify_dense_encoder.py",
            E.BASE_PATH, ROOT / "research_round6/joint_maxima/encode_joint_maxima.py",
            DATA / "spec32.csv", DATA / "Mtable.txt",
        ]},
        "proof_assistant_formalized": False,
        "seconds": round(time.monotonic() - started, 6),
    }
    (HERE / "DENSE_ENCODER_REPLAY.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
