#!/usr/bin/env python3
"""Finite and exact-encoding controls for the next-frontier incidence cuts.

No SAT solver is run. All outputs belong to Round8. This checks the general
theorem's gate separately from the stronger scope-specific consequences.
"""
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import gc
import hashlib
import json
import random
import tempfile
import time

import incidence_cuts as I
import encode_next_frontier as N

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
S13 = [0, 1, 2, 4, 8, 11, 15, 16, 18, 23, 25, 26, 28]
S14 = [0, 1, 2, 3, 4, 5, 7, 8, 10, 11, 16, 19, 28, 31]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def differences(points):
    return {a ^ b for a, b in combinations(points, 2)}


def truth(values, literal):
    return values[literal] if literal > 0 else not values[-literal]


def mathematical_controls():
    planes = {frozenset((0, a, b, a ^ b)) for a, b in combinations(range(1, 32), 2)}
    require(len(planes) == 155, "Two-space inventory differs")
    for plane in planes:
        cosets = {frozenset(x ^ p for p in plane) for x in range(32)}
        require(len(cosets) == 8 and all(len(C) == 4 for C in cosets), "Plane coset count differs")
        require(set().union(*cosets) == set(range(32)), "Plane cosets do not partition ambient space")
    light_count = 0
    for weight in (2, 3):
        for A in combinations(range(32), weight):
            D = differences(A)
            require(len(D) == (1 if weight == 2 else 3), "Light pair-direction count differs")
            if weight == 3:
                require(frozenset({0} | D) in planes, "Three-point pair directions are not a plane")
            light_count += 1
    matching_count = 0
    for P in range(1, 17):
        r = (16+P-1)//P
        require(P*(r-1) < 16 <= P*r, "Integer incidence threshold differs")
        for mixed in range(15):
            for light_light in range(8):
                active = mixed+2*light_light
                if active > 14:
                    continue
                capacity = P*mixed+light_light
                require(capacity <= P*active, "Light incidence overpays incorrectly")
                if active < r:
                    require(capacity < 16, "Too few active lights can cover sixteen")
                matching_count += 1
    scopes = []
    algebra_count = 0
    for s, P in ((13, 6), (14, 5)):
        r = (16+P-1)//P
        gaps = []
        for h in range(8):
            gap = 16*(31-h*(h-1)//2)-3*P*(s-h)
            require(gap > 0, "Small-heavy scalar screen failed")
            gaps.append(gap)
        require(96 > 3*P*(s-8), "Eight-heavy screen failed")
        require(3*r > 2*(s-9), "Nine-heavy incidence screen failed")
        require((2*(s-10))//r <= 2 and P*(s-11) < 16, "Next-frontier consequences failed")
        for h in range(s+1):
            for n3 in range(s-h+1):
                n2 = s-h-n3
                for missing in range(32):
                    left = r*missing <= n2+2*n3
                    right = r*missing+h+(s-n3) <= 2*s
                    require(left == right, "Boolean budget algebra differs")
                    algebra_count += 1
        scopes.append({"support_size": s, "P": P, "r": r, "small_heavy_strict_gaps": gaps,
                       "eight_heavy_available": 3*P*(s-8), "eight_heavy_required": 96,
                       "minimum_heavy": 10, "minimum_heavy_differences": 29,
                       "eleven_heavy_missing_direction_capacity_upper_bound": P*(s-11)})
    return {"all_two_spaces_checked": len(planes), "actual_light_fibres_checked": light_count,
            "matching_capacity_combinations_checked": matching_count,
            "budget_identity_cases_checked": algebra_count, "scope_controls": scopes}


def primitive_controls():
    count = 0
    for kind in ("or", "and"):
        for n in range(4):
            f = N.B.CNF(); inputs = [f.new() for _ in range(n)]; records = []
            out = (I._or if kind == "or" else I._and)(f, inputs, records)
            for bits in product((False, True), repeat=n+1):
                values = [False]+list(bits)
                satisfies = all(any(truth(values, x) for x in clause) for clause in f.cl)
                expected = values[out] == (any(bits[:n]) if kind == "or" else all(bits[:n]))
                require(satisfies == expected, "Gate equivalence failed")
                count += 1
    f = N.B.CNF(); a, b = f.new(), f.new()
    outputs = f.unary_sum([a, a, b])
    # Exhaust every auxiliary truth assignment of this duplicated-input
    # counter, not merely its canonical extension.
    counter_count = 0
    for bits in product((False, True), repeat=f.n):
        values = [False]+list(bits)
        if all(any(truth(values, x) for x in clause) for clause in f.cl):
            expected = 2*values[a]+values[b]
            require(all(values[out] == (expected >= j+1) for j, out in enumerate(outputs)),
                    "Weighted repeated-literal totalizer is not exact")
        counter_count += 1
    return {"gate_input_and_auxiliary_assignments": count,
            "weighted_counter_all_input_and_auxiliary_assignments": counter_count}


class RecordedFormula(N.B.CNF):
    def __init__(self):
        super().__init__(); self.totalizer_records = []
    def unary_sum(self, literals):
        outputs = super().unary_sum(literals)
        if len(literals) >= 2:
            self.totalizer_records.append(("counter", tuple(outputs), tuple(literals)))
        return outputs


def tiny_formula(S, maximum, *, general=False, propagate=True):
    spectra = [(2,), (3,), (4,), (maximum,)]
    f = RecordedFormula(); f.z = {}; f.y = {}
    for v in S:
        for i in range(4):
            f.z[v, i] = f.new()
        f.exactly_one([f.z[v, i] for i in range(4)])
        for b in S:
            if b != v:
                for p in range(maximum//2+1):
                    f.y[v, v ^ b, p] = f.new()
    f.cut_start = len(f.cl)
    metadata = (I.add_incidence_budget if general else I.append_next_frontier_cuts)(
        f, S, spectra, **({} if general else {"propagate": propagate}))
    f.test_spectra = spectra
    operations = [row for row in f.r8_incidence["construction_records"] if row[0] != "counter"] + f.totalizer_records
    operations.sort(key=lambda row: row[1][0] if row[0] == "counter" else row[1])
    f.test_operations = operations
    return f, metadata


def assignment(f, weights, pair_counts=None):
    pair_counts = pair_counts or {}
    values = [False]*(f.n+1)
    for v, weight in weights.items():
        selected = next(i for i, row in enumerate(f.test_spectra) if row[0] == weight)
        values[f.z[v, selected]] = True
    for (v, d, p), variable in f.y.items():
        values[variable] = p == pair_counts.get((v, d), 0)
    for kind, output, inputs in f.test_operations:
        arguments = [truth(values, x) for x in inputs]
        if kind == "counter":
            total = sum(arguments)
            for j, variable in enumerate(output):
                values[variable] = total >= j+1
        else:
            values[output] = any(arguments) if kind == "or" else all(arguments)
    return values


def accepts(f, values):
    return all(any(truth(values, x) for x in clause) for clause in f.cl[f.cut_start:])


def expected_predicate(S, maximum, weights, pair_counts, *, general, propagate):
    H = {v for v in S if weights[v] >= 4}
    missing = set(range(1, 32))-differences(H)
    h, P, s = len(H), maximum//2, len(S)
    r = (16+P-1)//P
    budget = r*len(missing)+h+sum(weights[v] != 3 for v in S) <= 2*s
    if general:
        return h < 9 or budget
    if h < 10 or len(missing) > 2 or (h >= s-r+1 and missing) or not budget:
        return False
    if propagate and s-10 == r and h == 10:
        light = set(S)-H
        if len(missing) == 2 and any(weights[v] != 3 for v in light):
            return False
        for a in light:
            for d in missing:
                b = a ^ d
                if b not in H or pair_counts.get((a, d), 0) != 1 or pair_counts.get((b, d), 0) < 16-P*(r-1):
                    return False
    return True


def boolean_controls():
    rng = random.Random(20261029)
    cases = []; negative = []; checked = 0
    for S, maximum in ((S13, 13), (S14, 11)):
        f, metadata = tiny_formula(S, maximum, propagate=True)
        samples = []
        # Every possible heavy count and varied light2/light3 assignments.
        for h in range(len(S)+1):
            for _ in range(3):
                H = set(rng.sample(S, h))
                samples.append({v: maximum if v in H else rng.choice((2, 3)) for v in S})
        for weights in samples:
            expected = expected_predicate(S, maximum, weights, {}, general=False, propagate=True)
            require(accepts(f, assignment(f, weights)) == expected, "Scope-specific Boolean predicate differs")
            checked += 1
        # Exercise a real support pattern with exactly two missing heavy
        # directions and all missing-direction light neighbours present.
        chosen = None
        for Htuple in combinations(S, 10):
            H = set(Htuple); light = set(S)-H; missing = set(range(1, 32))-differences(H)
            if len(missing) == 2 and all(a ^ d in H for a in light for d in missing):
                chosen = H, light, missing; break
        require(chosen is not None, "Missing active propagation control")
        H, light, missing = chosen
        weights = {v: maximum if v in H else 3 for v in S}
        P, r = maximum//2, (16+maximum//2-1)//(maximum//2)
        rho = 16-P*(r-1)
        pair_counts = {}
        for a in light:
            for d in missing:
                pair_counts[a, d] = 1
                pair_counts[a ^ d, d] = rho
        values = assignment(f, weights, pair_counts)
        require(expected_predicate(S, maximum, weights, pair_counts, general=False, propagate=True) and accepts(f, values),
                "Valid active propagation control rejected")
        a, d = min(light), min(missing)
        for label, location, wrong in (("inactive_light_pair", (a, d), 0),
                                        ("insufficient_heavy_partner", (a ^ d, d), rho-1)):
            bad = dict(pair_counts); bad[location] = wrong
            require(not accepts(f, assignment(f, weights, bad)), "Active pair propagation failed to reject")
            negative.append({"support_size": len(S), "control": label, "rejected": True})
        for label, variable in (("false_missing_flag", f.r8_incidence["missing"][d]),
                                ("false_heavy_edge_AND", next(iter(f.r8_incidence["heavy_edge_AND"].values())))):
            bad = list(values); bad[variable] = not bad[variable]
            require(not accepts(f, bad), "Incorrect auxiliary flag accepted")
            negative.append({"support_size": len(S), "control": label, "rejected": True})
        all_heavy = {v: maximum for v in S}
        require(accepts(f, assignment(f, all_heavy)), "Inactive h10 propagation gate imposed a pair requirement")
        no_prop, _ = tiny_formula(S, maximum, propagate=False)
        require(accepts(no_prop, assignment(no_prop, weights)), "Disabled pair propagation still constrained y")
        cases.append({"support_size": len(S), "maximum": maximum, "metadata": metadata,
                      "active_propagation_heavy_residues": sorted(H), "active_missing_directions": sorted(missing),
                      "heavy_partner_pair_lower_bound": rho,
                      "inactive_h10_gate_accepts_arbitrary_pair_counts": True,
                      "disabled_pair_propagation_accepts_arbitrary_pair_counts": True})
        del f, no_prop; gc.collect()
    general, general_metadata = tiny_formula(S13, 13, general=True)
    for h, should_pass in ((8, True), (9, False)):
        weights = {v: 13 if i < h else 3 for i, v in enumerate(S13)}
        H = set(S13[:h]); missing = set(range(1, 32))-differences(H)
        require(3*len(missing)+2*h > 26, "Gate control failed to violate ungated bound")
        require(accepts(general, assignment(general, weights)) == should_pass, "At-least-nine-heavy gate is incorrect")
    return {"canonical_scope_assignments_checked": checked, "cases": cases, "negative_controls": negative,
            "general_budget_gate": {"eight_heavy_inactive_accepts": True, "nine_heavy_active_rejects": True,
                                    "metadata": general_metadata}}


def real_encoder_controls():
    data = ROOT / "research_round6/imported_claude_round4/data"
    spectra, table, subspaces = N.load_spectra(data / "spec32.csv"), N.load_M(data / "Mtable.txt"), N.all_subspaces()
    rows = []
    with tempfile.TemporaryDirectory(prefix="kakeya_r8_incidence_identity_") as temporary:
        work = Path(temporary)
        for S, maximum in ((S13, 12), (S13, 13), (S14, 11)):
            baseline = N.B.encode(S[1:], maximum, spectra, table, subspaces, outtotal=93, hub_min=maximum, strengthen=False)
            N.write_dimacs(baseline, work / "baseline.cnf")
            before = baseline.n, len(baseline.cl)
            I.append_next_frontier_cuts(baseline, S, spectra, enabled=False)
            N.write_dimacs(baseline, work / "direct_disabled.cnf")
            require(sha(work / "baseline.cnf") == sha(work / "direct_disabled.cnf"), "Disabled direct cuts change bytes")
            disabled = N.encode(S[1:], maximum, spectra, table, subspaces, enabled=False)
            N.write_dimacs(disabled, work / "disabled.cnf")
            require(sha(work / "baseline.cnf") == sha(work / "disabled.cnf"), "Disabled convenience encoder changes baseline bytes")
            del disabled; gc.collect()
            enabled = N.encode(S[1:], maximum, spectra, table, subspaces, enabled=True, tetrahedral=True, propagate=True)
            require(enabled.cl[:before[1]] == baseline.cl and enabled.z == baseline.z and enabled.y == baseline.y,
                    "Enabled next-frontier encoder altered the baseline prefix or named inputs")
            N.write_dimacs(enabled, work / "enabled.cnf")
            rows.append({"support": S, "exact_maximum": maximum,
                         "disabled_byte_identity": True, "enabled_baseline_prefix_unchanged": True,
                         "baseline_variables": before[0], "baseline_clauses": before[1],
                         "enabled_variables": enabled.n, "enabled_clauses": len(enabled.cl),
                         "baseline_cnf_sha256": sha(work / "baseline.cnf"),
                         "enabled_cnf_sha256": sha(work / "enabled.cnf"),
                         "metadata": enabled.r8_next_frontier_metadata})
            del baseline, enabled; gc.collect()
    rejected = []
    for label, T, m, total, hub in (("wrong_S13_maximum", S13[1:], 11, 93, None),
                                   ("wrong_S14_maximum", S14[1:], 12, 93, None),
                                   ("wrong_total", S13[1:], 12, 94, None),
                                   ("nonexact_hub", S13[1:], 12, 93, 11)):
        try:
            N.encode(T, m, spectra, table, subspaces, total=total, hub_min=hub)
        except ValueError:
            rejected.append(label)
        else:
            raise ValueError("Convenience encoder accepted invalid scope: " + label)
    return {"cases": rows, "invalid_scopes_rejected": rejected, "SAT_solver_called": False}


def main():
    started = time.monotonic()
    output = HERE / "INCIDENCE_BUDGET_REPLAY.json"
    report = {"status": "RUNNING"}; output.write_text(json.dumps(report)+"\n")
    try:
        report.update(mathematical_controls=mathematical_controls(), primitive_controls=primitive_controls(),
                      boolean_controls=boolean_controls(), real_encoder_controls=real_encoder_controls())
        paths = [Path(__file__), HERE / "incidence_cuts.py", HERE / "encode_next_frontier.py",
                 HERE / "MISSING_DIRECTION_INCIDENCE.md", N.STRENGTHENED, N.X.EXPOSED_BASE, N.X.BASE,
                 ROOT / "research_round7/dense_encoder/NINE_POINT_DIFFERENCE_ANALYTIC_PROOF.md"]
        report.update(status="PASS_MISSING_DIRECTION_INCIDENCE_THEOREM_AND_NEXT_FRONTIER_ENCODER",
                      source_hashes={str(path.relative_to(ROOT)): sha(path) for path in paths},
                      SAT_solver_called=False, new_exclusions_claimed=0,
                      seconds=round(time.monotonic()-started, 6))
        output.write_text(json.dumps(report, indent=2)+"\n")
        print(json.dumps({"status": report["status"], "gate_assignments": report["primitive_controls"],
                          "real_encoder_scopes": len(report["real_encoder_controls"]["cases"]),
                          "seconds": report["seconds"]}, indent=2))
    except BaseException as error:
        report.update(status="FAIL", error=repr(error)); output.write_text(json.dumps(report, indent=2)+"\n")
        raise


if __name__ == "__main__":
    main()
