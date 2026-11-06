#!/usr/bin/env python3
"""Read-only final950 accounting review with publications held in memory.

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
EXT_REPLAY = ROOT / "research_round8/incidence/EXTENDED_INCIDENCE_PROFILE_REPLAY.json"
EXT_SURVIVORS = ROOT / "research_round8/incidence/after_extended_incidence_survivors.txt"
EXT_CERTIFICATE = ROOT / "research_round8/incidence/EXTENDED_INCIDENCE_PROFILE_EXCLUSIONS.json"
EXT_VERIFIER = ROOT / "research_round8/incidence/verify_extended_incidence_profiles.py"
LATER = {
    "general": ROOT / "research_round8/incidence/GENERAL_INCIDENCE_PROFILE_REPLAY.json",
    "matching": ROOT / "research_round8/incidence/MATCHING_INCIDENCE_PROFILE_REPLAY.json",
    "three_direction": ROOT / "research_round8/incidence/THREE_DIRECTION_PROFILE_REPLAY.json",
}
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
        EXT_REPLAY, EXT_SURVIVORS, EXT_CERTIFICATE, EXT_VERIFIER,
        ROOT / "VERIFY_ROUND8.py", *LATER.values(),
        ROOT / "research_round8/incidence/verify_general_incidence_profiles.py",
        ROOT / "research_round8/incidence/verify_matching_incidence_profiles.py",
        ROOT / "research_round8/incidence/verify_three_direction_profiles.py",
        ROOT / "research_round8/incidence/GENERAL_INCIDENCE_PROFILE_EXCLUSIONS.json",
        ROOT / "research_round8/incidence/MATCHING_INCIDENCE_PROFILE_EXCLUSIONS.json",
        ROOT / "research_round8/incidence/THREE_DIRECTION_PROFILE_EXCLUSIONS.json",
        ROOT / "research_round8/incidence/after_general_incidence_survivors.txt",
        ROOT / "research_round8/incidence/after_matching_incidence_survivors.txt",
        ROOT / "research_round8/incidence/after_three_direction_survivors.txt",
        ROOT / "research_round8/incidence/THREE_DIRECTION_PRICE_LEMMA.md",
        ROOT / "research_round8/incidence/SUPPORT13_MAX15_HEAVY_COROLLARY.md",
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
            require(middle["remaining_weight_profiles"] == 182526 and
                    middle["round8_whole_weight_profile_exclusions"] == 950 and
                    middle["remaining_profiles_by_support"] == {"13": 84946, "14": 74039, "15": 19362, "16": 3793, "17": 386} and
                    sum(middle["remaining_profiles_by_support"].values()) == 182526,
                    "Independent profile accounting differs")
            incidence = ledger["round8_incidence_profile_exclusions"]
            history = incidence["cumulative_stage_history"]
            require([row["cumulative_exclusions"] for row in history] == [16, 128, 175, 745, 950] and
                    [row["additional_exclusions"] for row in history] == [16, 112, 47, 570, 205] and
                    incidence["excluded"] == 950 and incidence["remaining"] == 182526 and
                    incidence["matching_threshold_exclusions"] == 745 and
                    incidence["three_direction_price_exclusions"] == 488 and
                    incidence["overlap_between_matching_and_price"] == 283 and
                    incidence["price_exclusions_additional_to_matching"] == 205 and
                    incidence["by_maximum"] == {"12": 129, "13": 68, "14": 191, "15": 108,
                                                "16": 250, "17": 94, "18": 110},
                    "Cumulative stage or matching/price union accounting differs")
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
    extension = json.loads(EXT_REPLAY.read_text())
    for key, value in (
        ("status", "PASS_UNRELATED_RECEIPT"),
        ("original_profiles", 183460),
        ("intermediate_profiles", 183476),
        ("previously_excluded_profiles", 0),
        ("newly_excluded_profiles", 128),
        ("cumulative_excluded_profiles", 144),
        ("remaining_profiles", 183332),
        ("original_input_file", "research_round8/incidence/after_incidence_survivors.txt"),
        ("original_input_sha256", "0"*64),
        ("certificate_sha256", "0"*64),
        ("survivor_sha256", "0"*64),
        ("verifier_sha256", "0"*64),
        ("scope", "Only one support placement and only Z/4Z are covered."),
    ):
        data = copy.deepcopy(extension); data[key] = value
        controls.append(execute("extension_wrong_"+key, {EXT_REPLAY: json.dumps(data).encode()}, False))
    for field in ("analytic_proof_pins", "prior_stage_pins"):
        data = copy.deepcopy(extension); data[field][next(iter(data[field]))] = "0"*64
        controls.append(execute("extension_wrong_"+field, {EXT_REPLAY: json.dumps(data).encode()}, False))
        data = copy.deepcopy(extension); del data[field][next(iter(data[field]))]
        controls.append(execute("extension_missing_"+field, {EXT_REPLAY: json.dumps(data).encode()}, False))
    for key, value in (
        ("every_original_source_line_accounted_for", False),
        ("every_retained_original_line_preserved_byte_identically_and_in_order", False),
        ("direct_and_intermediate_frontier_regeneration_identical", False),
        ("prior_sixteen_semantic_artifacts_unchanged", False),
        ("inherited_energy_metadata_used_in_exclusion", True),
    ):
        data = copy.deepcopy(extension); data["coverage"][key] = value
        controls.append(execute("extension_false_flag_"+key, {EXT_REPLAY: json.dumps(data).encode()}, False))
    for key in ("excluded_original_source_lines", "previously_excluded_original_source_lines",
                "newly_excluded_original_source_lines"):
        data = copy.deepcopy(extension); data["coverage"][key][0] = 1
        controls.append(execute("extension_wrong_"+key, {EXT_REPLAY: json.dumps(data).encode()}, False))
    controls.append(execute("extension_dropped_survivor_byte", {EXT_SURVIVORS: EXT_SURVIVORS.read_bytes()[:-1]}, False))
    controls.append(execute("extension_changed_certificate_bytes", {EXT_CERTIFICATE: EXT_CERTIFICATE.read_bytes()+b"\n"}, False))
    for stage, receipt_path in LATER.items():
        original = json.loads(receipt_path.read_text())
        mutations = [("status", "PASS_UNRELATED_RECEIPT"),
                     ("scope", "Only one placement in one ring is covered."),
                     ("previously_excluded_profiles", 0),
                     ("newly_excluded_profiles", original["newly_excluded_profiles"]+1),
                     ("cumulative_excluded_profiles", original["cumulative_excluded_profiles"]+1)]
        mutations += [(field, "0"*64) for field in
                      ("original_input_sha256", "certificate_sha256", "survivor_sha256", "verifier_sha256")]
        for field, value in mutations:
            data = copy.deepcopy(original); data[field] = value
            controls.append(execute(stage+"_wrong_"+field, {receipt_path: json.dumps(data).encode()}, False))
        for field in ("analytic_proof_pins", "prior_stage_pins"):
            data = copy.deepcopy(original); data[field][next(iter(data[field]))] = "0"*64
            controls.append(execute(stage+"_wrong_"+field, {receipt_path: json.dumps(data).encode()}, False))
        for field, value in original["coverage"].items():
            if isinstance(value, bool):
                data = copy.deepcopy(original); data["coverage"][field] = not value
                controls.append(execute(stage+"_false_"+field, {receipt_path: json.dumps(data).encode()}, False))
        for field in ("excluded_original_source_lines", "previously_excluded_original_source_lines",
                      "newly_excluded_original_source_lines"):
            data = copy.deepcopy(original); data["coverage"][field][0] = 1
            controls.append(execute(stage+"_wrong_"+field, {receipt_path: json.dumps(data).encode()}, False))
        data = copy.deepcopy(original); data["by_support"]["13"]["remaining"] += 1
        controls.append(execute(stage+"_wrong_support_aggregate", {receipt_path: json.dumps(data).encode()}, False))
        data = copy.deepcopy(original); data["by_maximum"]["12"]["cumulative_excluded"] += 1
        controls.append(execute(stage+"_wrong_maximum_aggregate", {receipt_path: json.dumps(data).encode()}, False))
    final_receipt = LATER["three_direction"]
    original = json.loads(final_receipt.read_text())
    for field, value in (("cube_tables_sha256", "0"*64), ("local_cube_subsets_total", 275)):
        data = copy.deepcopy(original); data[field] = value
        controls.append(execute("final_wrong_"+field, {final_receipt: json.dumps(data).encode()}, False))
    data = copy.deepcopy(original); data["local_cube_subset_counts"]["3"] = 255
    controls.append(execute("final_wrong_dimension3_cube_count", {final_receipt: json.dumps(data).encode()}, False))
    data = copy.deepcopy(original); data["E_k_for_weights0_through32"]["3"][18] += 1
    controls.append(execute("final_wrong_E3_at18", {final_receipt: json.dumps(data).encode()}, False))
    final_survivors = ROOT / original["survivor_file"]
    controls.append(execute("final_dropped_survivor_byte", {final_survivors: final_survivors.read_bytes()[:-1]}, False))
    require(all(sha(ROOT / p) == expected for p, expected in pins.items()), "Reviewed inputs changed during review")
    result = {"status": "PASS_READ_ONLY_ROUND8_FINAL950_MERGE_AND_THEOREM_REVIEW",
              "reviewer": "/root/support13_certification",
              "source_sha256": pins, "control_count": len(controls), "controls": controls,
              "whole_class_result": {"new_marked_roles": 4, "new_affine_classes": [109, 110, 111],
                                     "remaining_affine_classes": 42, "combined_direct_marked_coverage": "39 of 55",
                                     "full_support13_maximum11_closure_uses_inherited_reduction": True},
              "separate_whole_profile_result": {"excluded": 950, "remaining": 182526, "all_prior_stages_included_once": True, "stage_counts": [16,128,175,745,950],
                                                "sat_role_exclusions_used": False},
              "theorem_note_review": "Scope, common-ring carry translation, conditional inherited encoder/census trust, four new versus 39 combined marked cases, and separation of 950 cumulative whole-profile exclusions, with 745 matching plus 488 price exclusions and overlap 283 are accurate.",
              "blocking_issues": [], "fresh_sat_or_certificate_replays_run": False,
              "compact_inventory_bytes_and_sources_validated_once": True,
              "all_merge_writes_were_redirected_in_memory": True,
              "inherited_sources_and_other_agent_artifacts_written": False}
    destination = HERE / "ROUND8_FINAL_INTEGRATION_REVIEW.json"
    destination.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({"status": result["status"], "control_count": len(controls),
                      "receipt": str(destination.relative_to(ROOT)), "merge_sha256": pins[str(MERGE.relative_to(ROOT))]}, indent=2))


if __name__ == "__main__":
    main()
