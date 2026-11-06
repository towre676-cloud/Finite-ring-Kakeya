#!/usr/bin/env python3
"""Read-only accounting review with all merge publications held in memory.

The frozen compact inventory is validated once.  This is a review of the
merger's bindings and coverage arithmetic, not a new proof-checking run.
No inherited or other-agent artifact is written by this script.
"""
import copy
import hashlib
import importlib.abc
import importlib.util
import io
import json
from pathlib import Path
import sys
from contextlib import redirect_stdout
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MERGE = ROOT / "research_round8/merge_round8.py"
THEOREM = ROOT / "research_round8/SUPPORT13_MAXIMUM11_THEOREM.txt"
COMPACT = HERE / "compact/compact_certificates.py"
PROOF_REPLAY = HERE / "compact/COMPACT_CERTIFICATE_REPLAY.json"
PROFILE_REPLAY = ROOT / "research_round8/incidence/INCIDENCE_PROFILE_EXCLUSIONS_REPLAY.json"
SURVIVORS = ROOT / "research_round8/incidence/after_incidence_survivors.txt"
LEDGER = ROOT / "Kakeya_Research_Frontier_Round8.json"
REPORT = ROOT / "research_round8/ROUND8_MERGED_REPLAY.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    pins = {str(p.relative_to(ROOT)): sha(p) for p in (
        MERGE, THEOREM, COMPACT, PROOF_REPLAY, PROFILE_REPLAY, SURVIVORS,
        ROOT / "MANIFEST_ROUND7.json",
        HERE / "compact/COMPACT_CERTIFICATE_MANIFEST.json",
        ROOT / "research_round8/incidence/verify_incidence_profile_exclusions.py",
        ROOT / "research_round8/incidence/INCIDENCE_PROFILE_EXCLUSIONS.json",
    )}
    spec = importlib.util.spec_from_file_location("round8_review_actual_compact", COMPACT)
    actual = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = actual
    spec.loader.exec_module(actual)
    validated = actual.load()
    code = MERGE.read_text()
    original_open = Path.open
    original_spec = importlib.util.spec_from_file_location

    class CachedInventoryLoader(importlib.abc.Loader):
        def create_module(self, spec):
            return None

        def exec_module(self, module):
            module.load = lambda: copy.deepcopy(validated)
            module.MANIFEST = actual.MANIFEST
            module.V = actual.V

    def use_validated_inventory(name, path, *args, **kwargs):
        if Path(path).resolve() == COMPACT:
            return importlib.util.spec_from_loader(name, CachedInventoryLoader())
        return original_spec(name, path, *args, **kwargs)

    def execute(label, overrides, expected_success):
        memory = {REPORT: b'{"status":"PASS_OLD_RECEIPT_CONTROL"}\n', **overrides}
        writes = []

        def virtual_open(path, mode="r", buffering=-1, encoding=None, errors=None, newline=None):
            path = Path(path).resolve()
            require(not any(c in mode for c in "wax+"), "Unexpected file-opening write during review")
            if path in memory:
                if "b" in mode:
                    return io.BytesIO(memory[path])
                selected_encoding = "utf-8" if encoding in (None, "locale") else encoding
                return io.StringIO(memory[path].decode(selected_encoding, errors or "strict"))
            return original_open(path, mode, buffering, encoding, errors, newline)

        def virtual_write_bytes(path, data):
            path = Path(path).resolve()
            require(path in (LEDGER, REPORT), "Merge attempted an unauthorized artifact write")
            memory[path] = bytes(data)
            writes.append({"path": str(path.relative_to(ROOT)),
                           "status": json.loads(data).get("status")})
            return len(data)

        def virtual_write_text(path, data, encoding=None, errors=None, newline=None):
            selected_encoding = "utf-8" if encoding in (None, "locale") else encoding
            virtual_write_bytes(path, data.encode(selected_encoding, errors or "strict"))
            return len(data)

        def forbidden_mutation(*args, **kwargs):
            raise AssertionError("Unexpected filesystem mutation during read-only merge review")

        error = None
        with patch.object(Path, "open", virtual_open), \
             patch.object(Path, "write_text", virtual_write_text), \
             patch.object(Path, "write_bytes", virtual_write_bytes), \
             patch.object(Path, "replace", forbidden_mutation), \
             patch.object(Path, "rename", forbidden_mutation), \
             patch.object(Path, "unlink", forbidden_mutation), \
             patch.object(importlib.util, "spec_from_file_location", use_validated_inventory), \
             redirect_stdout(io.StringIO()):
            try:
                exec(compile(code, str(MERGE), "exec"),
                     {"__name__": "__main__", "__file__": str(MERGE)})
            except BaseException as caught:
                error = caught
        result = json.loads(memory[REPORT])
        require(writes and writes[0]["status"] == "RUNNING", "Prior PASS was not invalidated before preflight")
        if expected_success:
            require(error is None and result["status"] == "PASS_EXACT_ROUND8_FRONTIER_ACCOUNTING",
                    "Unmodified merge failed: " + repr(error))
            ledger = json.loads(memory[LEDGER])
            maximum = ledger["dimension5_strata"]["maximum11"]
            middle = ledger["dimension5_strata"]["maximum12_through18"]
            require(maximum["remaining_affine_support_classes"] == 42 and
                    maximum["remaining_counts_by_support"] == {"13": 0, "14": 9, "15": 16, "16": 17},
                    "Whole affine-class accounting differs")
            require(ledger["round8_main_result"]["complete_direct_exact11_marked_coverage"] ==
                    {"closed": 39, "catalogue": 55} and
                    ledger["round8_main_result"]["middle_weight_profiles_removed_by_these_four_sat_cases"] == 0,
                    "Marked cases were conflated with whole profiles")
            require(middle["remaining_weight_profiles"] == 183460 and
                    middle["round8_whole_weight_profile_exclusions"] == 16 and
                    middle["remaining_profiles_by_support"]["13"] == 85324 and
                    sum(middle["remaining_profiles_by_support"].values()) == 183460,
                    "Independent profile accounting differs")
            require(ledger["dimension4"]["status"] == "OPEN" and
                    ledger["unrestricted_dimension5_theorem"] is False,
                    "An unrelated open theorem was promoted")
        else:
            require(error is not None and result["status"] == "FAIL", "Corrupted input left success credit: " + label)
            require(LEDGER not in memory, "Rejected input published a new ledger: " + label)
        return {"control": label, "expected_success": expected_success,
                "status": result["status"], "exception": repr(error) if error else None,
                "publications_redirected_in_memory": True, "begins_with_running": True}

    controls = [execute("valid_complete_merge", {}, True)]
    controls.append(execute("inherited_manifest_changed", {
        ROOT / "MANIFEST_ROUND7.json": b"{}\n"}, False))
    proof = json.loads(PROOF_REPLAY.read_text())
    cases = [
        ("wrong_case_status", "status", "TIMEOUT_UNCERTIFIED"),
        ("wrong_marked_role", "nonzero_support_mask", 0),
        ("wrong_maximum_interval", "maximum_interval", [10, 11]),
        ("wrong_mode", "mode", "baseline"),
        ("wrong_representation", "representation", "UNCERTIFIED_CNF_ONLY"),
        ("wrong_checked_proof_hash", "checked_proof_sha256", "0"*64),
        ("missing_exclusion_credit", "exclusion_credited", False),
    ]
    for label, key, value in cases:
        data = copy.deepcopy(proof); data["cases"][0][key] = value
        controls.append(execute(label, {PROOF_REPLAY: json.dumps(data).encode()}, False))
    for label, modify in (
        ("wrong_checked_case_id", lambda d: d["cases"][0].update(case_id="unknown_case")),
        ("duplicate_checked_case", lambda d: d["cases"].__setitem__(0, copy.deepcopy(d["cases"][1]))),
        ("incomplete_checked_inventory", lambda d: d["cases"].pop()),
        ("wrong_exact_cnf_binding", lambda d: d["cases"][0]["audit"]["input_sha256"].update(cnf="0"*64)),
        ("incomplete_full_replay", lambda d: d.update(full_inventory_replayed=False)),
    ):
        data = copy.deepcopy(proof); modify(data)
        controls.append(execute(label, {PROOF_REPLAY: json.dumps(data).encode()}, False))
    profile = json.loads(PROFILE_REPLAY.read_text())
    for key, value in (
        ("status", "PASS_UNRELATED_RECEIPT"),
        ("input_sha256", "0"*64),
        ("certificate_sha256", "0"*64),
        ("survivor_sha256", "0"*64),
        ("verifier_sha256", "0"*64),
        ("whole_profiles_excluded", 17),
    ):
        data = copy.deepcopy(profile); data[key] = value
        controls.append(execute("profile_wrong_"+key, {PROFILE_REPLAY: json.dumps(data).encode()}, False))
    data = copy.deepcopy(profile); data["coverage"]["excluded_source_lines"][0] = 1
    controls.append(execute("profile_wrong_source_line", {PROFILE_REPLAY: json.dumps(data).encode()}, False))
    data = copy.deepcopy(profile); data["analytic_proof_pins"][next(iter(data["analytic_proof_pins"]))] = "0"*64
    controls.append(execute("profile_wrong_analytic_pin", {PROFILE_REPLAY: json.dumps(data).encode()}, False))
    controls.append(execute("dropped_surviving_profile_byte", {SURVIVORS: SURVIVORS.read_bytes()[:-1]}, False))
    require(all(sha(ROOT / p) == expected for p, expected in pins.items()), "Reviewed inputs changed during review")
    result = {"status": "PASS_READ_ONLY_ROUND8_MERGE_AND_THEOREM_REVIEW",
              "reviewer": "/root/support13_certification",
              "source_sha256": pins, "control_count": len(controls), "controls": controls,
              "whole_class_result": {"new_marked_roles": 4, "new_affine_classes": [109, 110, 111],
                                     "remaining_affine_classes": 42, "combined_direct_marked_coverage": "39 of55",
                                     "full_support13_maximum11_closure_uses_inherited_reduction": True},
              "separate_whole_profile_result": {"excluded": 16, "remaining": 183460,
                                                "sat_role_exclusions_used": False},
              "theorem_note_review": "Scope, common-ring carry translation, conditional inherited encoder/census trust, four new versus39 combined marked cases, and separation of16 whole-profile exclusions are accurate.",
              "blocking_issues": [], "fresh_sat_or_certificate_replays_run": False,
              "compact_inventory_bytes_and_sources_validated_once": True,
              "all_merge_writes_were_redirected_in_memory": True,
              "inherited_sources_and_other_agent_artifacts_written": False}
    destination = HERE / "ROUND8_INTEGRATION_REVIEW.json"
    destination.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({"status": result["status"], "control_count": len(controls),
                      "receipt": str(destination.relative_to(ROOT)), "merge_sha256": pins[str(MERGE.relative_to(ROOT))]}, indent=2))


if __name__ == "__main__":
    main()
