#!/usr/bin/env python3
"""Finite controls for Round8's explicit heavy and edge-capacity extension."""
from pathlib import Path
import gc
import hashlib
import itertools
import json
import sys
import tempfile
import time

sys.dont_write_bytecode = True
import encode_strengthened as X

HERE, ROOT = X.HERE, X.ROOT
MASKS = [377850134, 411136406, 671697334, 2185856310]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def satisfied(formula, assignment):
    return all(any(assignment[abs(literal)] == (literal > 0) for literal in clause)
               for clause in formula.cl)


class RecordedCNF(X.E.CNF):
    def __init__(self):
        super().__init__()
        self.merges = []

    def unary_sum(self, literals):
        outputs = super().unary_sum(literals)
        if len(literals) > 1:
            self.merges.append((list(literals), outputs))
        return outputs

    def extend_totals(self, assignment):
        for inputs, outputs in self.merges:
            count = sum(assignment[variable] for variable in inputs)
            for threshold, variable in enumerate(outputs, 1):
                assignment[variable] = count >= threshold


def heavy_controls():
    checks = []
    for upper, required in [(11, 9), (13, 9), (14, 8), (18, 8)]:
        formula = RecordedCNF()
        formula.z = {(v, i): formula.new() for v in range(13) for i in range(2)}
        for v in range(13):
            formula.exactly_one([formula.z[v, 0], formula.z[v, 1]])
        metadata = X.add_heavy_cardinality(formula, range(13), [(3,), (upper,)])
        require(metadata["required_heavy_vertices"] == required, "Wrong domain-sensitive threshold")
        for mask in range(1 << 13):
            assignment = {}
            for v in range(13):
                bit = bool(mask >> v & 1)
                assignment.update({formula.z[v, 0]: not bit, formula.z[v, 1]: bit,
                                   formula.r8_heavy[v]: bit})
            formula.extend_totals(assignment)
            require(satisfied(formula, assignment) == (mask.bit_count() >= required),
                    "Heavy indicator/counter rejects or accepts the wrong Boolean pattern")
        checks.append({"largest_domain_weight": upper, "minimum_heavy": required,
                       "all_boolean_patterns_checked": 1 << 13})
    invalid = 0
    for size, weights in [(12, [(3,), (11,)]), (13, [(1,), (11,)]), (13, [(3,), (19,)])]:
        formula = RecordedCNF()
        formula.z = {(v, i): formula.new() for v in range(size) for i in range(2)}
        try:
            X.add_heavy_cardinality(formula, range(size), weights)
        except ValueError:
            invalid += 1
        else:
            raise AssertionError("Invalid heavy theorem scope accepted")
    return {"threshold_cases": checks, "invalid_scopes_rejected": invalid}


def edge_formula(table, a=0, b=1, formula=None):
    formula = RecordedCNF() if formula is None else formula
    if not hasattr(formula, "y"):
        formula.y = {}
    d = a ^ b
    for v in (a, b):
        for p in range(6):
            formula.y[v, d, p] = formula.new()
        formula.exactly_one([formula.y[v, d, p] for p in range(6)])
    ta, tb = formula.new(), formula.new()
    bits = X.add_edge_capacity(formula, a, b, d, table, ta, tb)
    return formula, ta, tb, bits


def set_edge(assignment, formula, a, b, ta, tb, bits, p, q, flag_a, flag_b, capacity):
    d = a ^ b
    assignment.update({formula.y[a, d, j]: j == p for j in range(6)})
    assignment.update({formula.y[b, d, j]: j == q for j in range(6)})
    assignment.update({ta: flag_a, tb: flag_b})
    assignment.update({variable: capacity >= j for j, variable in enumerate(bits, 1)})


def capacity_controls(table):
    formula, ta, tb, bits = edge_formula(table)
    cases = rejected = 0
    for p, q, flag_a, flag_b, capacity in itertools.product(
            range(6), range(6), (False, True), (False, True), range(17)):
        assignment = {}
        set_edge(assignment, formula, 0, 1, ta, tb, bits, p, q, flag_a, flag_b, capacity)
        cap = table[p][q]
        if flag_a and flag_b and p == q == 4:
            cap = min(cap, 14)
        expected = capacity <= cap
        require(satisfied(formula, assignment) == expected, "Explicit unary edge cap has wrong gate or index")
        cases += 1
        rejected += not expected
    # A genuine multiple-edge direction: the flagged 4x4 edge may supply14
    # while a second edge supplies2. It must not be prohibited outright.
    f, ta1, tb1, bits1 = edge_formula(table)
    f, ta2, tb2, bits2 = edge_formula(table, 2, 3, f)
    outputs = f.unary_sum(bits1 + bits2)
    f.add([outputs[15]])
    multi = accepted = 0
    for c1, c2 in itertools.product(range(17), repeat=2):
        assignment = {}
        set_edge(assignment, f, 0, 1, ta1, tb1, bits1, 4, 4, True, True, c1)
        set_edge(assignment, f, 2, 3, ta2, tb2, bits2, 1, 2, False, False, c2)
        f.extend_totals(assignment)
        expected = c1 <= 14 and c2 <= 2 and c1 + c2 >= 16
        require(satisfied(f, assignment) == expected, "Multiple-edge direction capacity is encoded incorrectly")
        multi += 1
        accepted += expected
    require(accepted == 1, "The14+2 witness was not accepted exactly")
    assignment = {}
    set_edge(assignment, formula, 0, 1, ta, tb, bits, 4, 4, False, False, 16)
    assignment[bits[0]] = False
    require(not satisfied(formula, assignment), "Nonmonotone capacity bits were accepted")
    return {"edge_truth_table_assignments": cases, "rejected_over_capacity_assignments": rejected,
            "two_edge_direction_assignments": multi, "fourteen_plus_two_witness_accepted": True,
            "nonmonotone_capacity_rejected": True}


def flag_controls(spectra):
    eligible = [i for i, spectrum in enumerate(spectra) if X.nonplanar_four_pair_type(spectrum)]
    require(len(eligible) == 2 and {spectra[i][0] for i in eligible} == {8, 11},
            "Changed or overbroad nonplanar spectrum flags")
    for i in eligible:
        changed = list(spectra[i])
        changed[3] = 5
        require(not X.nonplanar_four_pair_type(changed), "Rank5 interval incorrectly flagged")
    controls = 0
    for chosen_a, chosen_b in itertools.product(range(len(spectra)), repeat=2):
        # No synthetic SAT solve: the OR definitions must match precisely
        # the selected spectrum, for both positive and negative examples.
        if spectra[chosen_a][0] not in (8, 11) or spectra[chosen_b][0] not in (8, 11):
            continue
        f = X.E.CNF()
        z = [f.new() for _ in spectra]
        flag = X.disjunction(f, [z[i] for i in eligible])
        for selected in (chosen_a, chosen_b):
            assignment = {variable: i == selected for i, variable in enumerate(z)}
            expected = selected in eligible
            assignment[flag] = expected
            require(satisfied(f, assignment), "Correct spectrum flag violates its defining clauses")
            assignment[flag] = not expected
            require(not satisfied(f, assignment), "Incorrect spectrum flag satisfies its defining clauses")
            controls += 1
    return {"eligible_spectrum_indices": eligible, "exact_rank_interval_required": True,
            "selected_type_flag_checks": controls}


def identity_controls(spectra, table, subspaces):
    queue = json.loads((ROOT / "research_round6/next_frontier/SUPPORT13_CASE_QUEUE.json").read_text())
    universe = {c["nonzero_support_mask"]: c for c in queue["cases"]}
    records = []
    with tempfile.TemporaryDirectory(prefix="kakeya_r8_identity_") as temporary:
        directory = Path(temporary)
        for mask in MASKS:
            support = universe[mask]["support"]
            baseline = X.E.encode(support[1:], 11, spectra, table, subspaces, outtotal=93, hub_min=11)
            X.write_dimacs(baseline, directory / "baseline.cnf")
            disabled = X.encode(support[1:], 11, spectra, table, subspaces, enabled=False)
            X.write_dimacs(disabled, directory / "disabled.cnf")
            require(sha(directory / "baseline.cnf") == sha(directory / "disabled.cnf"),
                    "Disabled wrapper or selector-export baseline changed original bytes")
            del disabled
            enabled = X.encode(support[1:], 11, spectra, table, subspaces)
            require(enabled.cl[:len(baseline.cl)] == baseline.cl, "Extension altered a baseline clause")
            require(set(enabled.h_selectors) == set(support) and set(enabled.k_selectors) == set(support),
                    "Explicit direction/maximal-subspace selector API is incomplete")
            require(len(enabled.r8_edge_capacity) == 78 and
                    sum(map(len, enabled.r8_direction_edges.values())) == 78,
                    "Explicit capacity map lost or duplicated an edge")
            require(all(len(bits) == 16 and all(literal > baseline.n for literal in bits)
                        for bits in enabled.r8_edge_capacity.values()), "Capacity bits alias baseline variables")
            X.write_dimacs(enabled, directory / "enabled.cnf")
            records.append({"support_mask": mask, "baseline_sha256": sha(directory / "baseline.cnf"),
                            "disabled_sha256": sha(directory / "disabled.cnf"),
                            "enabled_sha256": sha(directory / "enabled.cnf"),
                            "base_variables": baseline.n, "base_clauses": len(baseline.cl),
                            "variables": enabled.n, "clauses": len(enabled.cl),
                            "extension": enabled.r8_strengthened_metadata})
            del baseline, enabled
            gc.collect()
    return records


def main():
    started = time.monotonic()
    output = HERE / "STRENGTHENED_FINITE_REPLAY.json"
    report = {"status": "RUNNING", "SAT_solver_invoked": False, "exclusions_credited": 0}
    output.write_text(json.dumps(report) + "\n")
    try:
        data = ROOT / "research_round6/imported_claude_round4/data"
        spectra, table, subspaces = X.load_spectra(data / "spec32.csv"), X.load_M(data / "Mtable.txt"), X.all_subspaces()
        report.update(heavy=heavy_controls(), capacities=capacity_controls(table), flags=flag_controls(spectra),
                      actual_case_identity=identity_controls(spectra, table, subspaces))
        report.update(status="PASS_ROUND8_STRENGTHENED_FINITE_CONTROLS", source_hashes={
            str(path.relative_to(ROOT)): sha(path) for path in (
                HERE / "encode_strengthened.py", HERE / "ONE_WAY_SOUNDNESS.txt", Path(__file__), X.BASE, X.EXPOSED_BASE)},
                      seconds=round(time.monotonic() - started, 6))
        output.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({k: report[k] for k in ("status", "seconds", "SAT_solver_invoked", "exclusions_credited")}))
    except BaseException as error:
        report.update(status="FAIL", error=repr(error), seconds=round(time.monotonic() - started, 6))
        output.write_text(json.dumps(report, indent=2) + "\n")
        raise


if __name__ == "__main__":
    main()
