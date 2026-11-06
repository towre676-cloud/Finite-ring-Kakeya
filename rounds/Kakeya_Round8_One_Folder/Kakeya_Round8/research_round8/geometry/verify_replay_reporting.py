#!/usr/bin/env python3
"""In-memory review controls for the Round8 orchestration and proof reuse.

No child program, archive extraction, SAT solver or proof checker is run.
All writes made by the reviewed scripts are redirected to memory. Only
this review's own JSON receipt is written to the geometry directory.
"""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import ast
import contextlib
import hashlib
import io
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imported_namespace(path):
    tree = ast.parse(path.read_text())
    require(isinstance(tree.body[-1], ast.If), "Expected guarded script entrypoint")
    namespace = {"__file__": str(path), "__name__": "review_import"}
    exec(compile(ast.Module(body=tree.body[:-1], type_ignores=[]), str(path), "exec"), namespace)
    return tree, namespace


def memory_paths(store):
    class MemoryFile(io.BytesIO):
        def __init__(self, key):
            super().__init__()
            self.key = key

        def close(self):
            if not self.closed:
                store[self.key] = self.getvalue()
            super().close()

    class MemoryPath:
        def __init__(self, key):
            self.key = str(key)

        def __truediv__(self, other):
            return MemoryPath(self.key + "/" + str(other))

        def __str__(self):
            return self.key

        def mkdir(self, *args, **kwargs):
            pass

        def open(self, mode):
            require(mode == "wb", "Unexpected mocked file mode")
            return MemoryFile(self.key)

        def write_text(self, data):
            store[self.key] = data.encode()
            return len(data)

        def read_text(self, errors="strict"):
            return store[self.key].decode(errors=errors)

        def read_bytes(self):
            return store[self.key]

        def exists(self):
            return self.key in store

    return MemoryPath


def guarded_call(tree, namespace, arguments):
    old_argv = sys.argv
    sys.argv = [namespace["__file__"], *arguments]
    caught = None
    namespace["__name__"] = "__main__"
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            try:
                exec(compile(ast.Module(body=[tree.body[-1]], type_ignores=[]), namespace["__file__"], "exec"), namespace)
            except BaseException as error:
                caught = repr(error)
    finally:
        sys.argv = old_argv
    return caught


def runner_trial(arguments=(), fail_at=None, raise_at=None, optimize=0, seed=None):
    store = {}
    MemoryPath = memory_paths(store)
    path = ROOT / "VERIFY_ROUND8.py"
    tree, namespace = imported_namespace(path)
    namespace["ROOT"] = MemoryPath("/mock")
    namespace["HERE"] = MemoryPath("/mock/research_round8")
    namespace["sys"] = SimpleNamespace(flags=SimpleNamespace(optimize=optimize),
                                       executable=sys.executable, stderr=io.StringIO())
    calls = []

    def mocked_run(command, **kwargs):
        number = len(calls) + 1
        calls.append(command)
        require((ROOT / command[1]).is_file(), "Missing stage entrypoint: " + command[1])
        kwargs["stdout"].write(b"mocked stdout\n")
        kwargs["stderr"].write(b"mocked stderr\n")
        if number == raise_at:
            raise RuntimeError("Mocked unexpected child exception")
        return SimpleNamespace(returncode=1 if number == fail_at else 0)

    namespace["subprocess"] = SimpleNamespace(run=mocked_run)
    key = "/mock/research_round8/ROUND8_PORTABLE_REPLAY.json"
    if seed is not None:
        store[key] = json.dumps(seed).encode()
    error = guarded_call(tree, namespace, arguments)
    result = json.loads(store[key]) if key in store else None
    return result, calls, error


def runner_controls():
    failures, exceptions, successes = [], [], []
    for reuse in (False, True):
        arguments = ["--reuse-checked-certificates"] if reuse else []
        result, calls, error = runner_trial(arguments)
        require(error is None and result["status"].startswith("PASS_"), "Valid mocked integration failed")
        require(len(calls) == result["completed_stages"], "Completed stage count differs")
        require(result["fresh_all_four_new_proofs_replayed"] is (not reuse), "Fresh completion mode differs")
        require(result["previous_complete_new_proof_replay_receipts_reused"] is reuse, "Reuse completion mode differs")
        require(result["fresh_all_four_new_proofs_requested"] is (not reuse), "Fresh request flag differs")
        require(result["previous_complete_new_proof_replay_receipt_reuse_requested"] is reuse, "Reuse request flag differs")
        names = [row["stage"] for row in result["stages"]]
        require(len(set(names)) == len(names), "Repeated integration stage name")
        for suffix in ("verify_incidence_profile_exclusions.py", "verify_extended_incidence_profiles.py",
                       "verify_general_incidence_profiles.py", "verify_matching_threshold.py",
                       "verify_matching_incidence_profiles.py", "verify_three_direction_profiles.py"):
            require(any(command[1].endswith(suffix) for command in calls), "Missing cumulative incidence stage")
        proof = next((i for i, command in enumerate(calls, 1)
                      if command[1].endswith("compact_certificates.py")), None)
        merge = next(i for i, command in enumerate(calls, 1) if command[1].endswith("merge_round8.py"))
        require((proof is None) is reuse, "Proof stage inclusion differs from requested mode")
        if proof is not None:
            require(calls[proof-1][2:] == ["--replay"], "Unexpected compact proof stage CLI")
        successes.append({"reuse": reuse, "stage_count": len(calls), "stages": names,
                          "all_stage_paths_exist": True})
        for position in range(1, len(calls)+1):
            failed, attempted, _ = runner_trial(arguments, fail_at=position)
            require(failed["status"] == "FAIL" and len(attempted) == position, "Failed child did not halt integration")
            require(failed["fresh_all_four_new_proofs_replayed"] is bool(proof and position > proof),
                    "Fresh completion flag advanced before proof success")
            require(failed["previous_complete_new_proof_replay_receipts_reused"] is bool(reuse and position > merge),
                    "Reuse completion flag advanced before binding success")
            failures.append({"reuse": reuse, "stage": names[position-1], "flags_correct": True})
        for position in (1, len(calls)):
            failed, attempted, _ = runner_trial(arguments, raise_at=position)
            require(failed["status"] == "FAIL" and len(attempted) == position, "Unexpected child exception not recorded")
            require(failed["fresh_all_four_new_proofs_replayed"] is bool(proof and position > proof), "Fresh exception flag differs")
            require(failed["previous_complete_new_proof_replay_receipts_reused"] is bool(reuse and position > merge), "Reuse exception flag differs")
            exceptions.append({"reuse": reuse, "stage": names[position-1], "flags_correct": True})
    seed = {"status": "PASS_OLD", "fresh_all_four_new_proofs_replayed": True,
            "previous_complete_new_proof_replay_receipts_reused": True}
    startup = []
    for label, arguments, optimize in (("invalid_CLI", ["--invalid-argument"], 0), ("Python_O_rejected", [], 1)):
        failed, calls, _ = runner_trial(arguments, optimize=optimize, seed=seed)
        require(failed["status"] == "FAIL" and not calls, "Startup error did not fail before children")
        for key in ("fresh_all_four_new_proofs_requested", "previous_complete_new_proof_replay_receipt_reuse_requested",
                    "fresh_all_four_new_proofs_replayed", "previous_complete_new_proof_replay_receipts_reused"):
            require(failed[key] is False, "Prior-run flag leaked into startup failure")
        startup.append({"control": label, "old_completion_flags_cleared": True})
    result, calls, error = runner_trial(["--inherited-archive", "/tmp/review_only_round7.zip", "--reuse-checked-certificates"])
    require(error is None and calls[0][2:] == ["--archive", "/tmp/review_only_round7.zip"], "Inherited archive argument not forwarded")
    return {"successful_modes": successes, "nonzero_child_returns": failures,
            "unexpected_child_exceptions": exceptions, "startup_controls": startup,
            "optional_inherited_archive_CLI_forwarding": True}


def archive_controls():
    path = ROOT / "research_round8/check_fresh_archive.py"
    tree, namespace = imported_namespace(path)
    main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main")
    block = next(node for node in ast.walk(main) if isinstance(node, ast.If) and
                 isinstance(node.test, ast.Attribute) and node.test.attr == "reuse_checked_certificates")
    compiled = compile(ast.Module(body=block.body, type_ignores=[]), str(path), "exec")
    files = {
        "receipt": ROOT / "research_round8/proof_portability/FULL_PROOF_PORTABILITY_RECEIPT.json",
        "integrated": ROOT / "research_round8/proof_portability/ROUND8_PORTABLE_REPLAY.json",
        "prior": ROOT / "research_round8/proof_portability/COMPACT_CERTIFICATE_REPLAY.json",
        "current": ROOT / "research_round8/strengthened/compact/COMPACT_CERTIFICATE_REPLAY.json",
    }
    texts = {key: p.read_text() for key, p in files.items()}
    require(len(set(texts.values())) == len(texts), "JSON override controls need distinct receipt bytes")
    base = {key: json.loads(value) for key, value in texts.items()}

    def accepts(change=None):
        values = deepcopy(base)
        if change:
            change(values)
        lookup = {texts[key]: values[key] for key in values}
        local = dict(namespace, extracted=ROOT, command=["python", "VERIFY_ROUND8.py"], report={})
        local["json"] = SimpleNamespace(loads=lambda text: deepcopy(lookup[text]) if text in lookup else json.loads(text))
        try:
            exec(compiled, local)
        except ValueError:
            return False
        require(local["command"][-1] == "--reuse-checked-certificates", "Reuse flag missing")
        require(local["report"]["same_exact_formulas_proofs_and_sources_as_prior_full_check"] is True, "Reuse binding missing")
        return True

    require(accepts(), "Valid preserved proof replay rejected")
    negatives = []

    def reject(label, change):
        require(not accepts(change), "Invalid proof reuse accepted: " + label)
        negatives.append(label)

    for key, value in (("status", "FAIL"), ("fresh_proofs_checked", 0)):
        reject("prior_extraction_" + key, lambda values, k=key, v=value: values["receipt"].__setitem__(k, v))
    for key, value in (("status", "FAIL"), ("fresh_all_four_new_proofs_replayed", False)):
        reject("prior_integrated_" + key, lambda values, k=key, v=value: values["integrated"].__setitem__(k, v))
    for key in ("status", "full_inventory_replayed", "compact_manifest_sha256", "source_manifest_sha256", "source_hashes"):
        reject("proof_" + key, lambda values, k=key: values["prior"].__setitem__(k, "changed"))
    for key in ("status", "nonzero_support_mask", "maximum_interval", "mode", "representation", "checked_proof_sha256", "exclusion_credited", "regeneration"):
        reject("case_" + key, lambda values, k=key: values["prior"]["cases"][0].__setitem__(k, "changed"))
    for key in ("input_sha256", "status"):
        reject("audit_" + key, lambda values, k=key: values["prior"]["cases"][0]["audit"].__setitem__(k, "changed"))
    reject("only_three_cases", lambda values: values["prior"]["cases"].pop())
    reject("duplicate_case_id", lambda values: values["prior"]["cases"][0].__setitem__("case_id", values["prior"]["cases"][1]["case_id"]))
    store = {}
    MemoryPath = memory_paths(store)
    _, early = imported_namespace(path)
    destination = MemoryPath("/mock/archive_receipt.json")
    early["DESTINATION"] = destination
    store[destination.key] = json.dumps({"status": "PASS_OLD", "fresh_proofs_checked": 4,
                                        "previously_freshly_checked_unchanged_proofs_bound": 4,
                                        "all_payloads_preserved": True, "regenerated_ledger_identical": True}).encode()
    guarded_call(tree, early, ["--invalid-argument"])
    failed = json.loads(store[destination.key])
    require(failed["status"] == "FAIL" and failed["fresh_proofs_checked"] == 0 and
            failed["previously_freshly_checked_unchanged_proofs_bound"] == 0 and
            failed["all_payloads_preserved"] is False and failed["regenerated_ledger_identical"] is False,
            "Archive startup failure retained prior success claims")
    return {"valid_prior_full_replay_bound": True, "negative_controls": negatives,
            "invalid_CLI_clears_prior_success_claims": True,
            "preserved_receipt_hashes": {str(p.relative_to(ROOT)): sha(p) for p in files.values()}}


def main():
    runner = runner_controls()
    archive = archive_controls()
    paths = [Path(__file__), ROOT / "VERIFY_ROUND8.py", ROOT / "research_round8/check_fresh_archive.py"]
    report = {
        "status": "PASS_REPLAY_REPORTING_AND_EXPLICIT_PROOF_REUSE_REVIEW",
        "reviewer": "Separate model agent /root/support13_geometry; not independent human review or proof-assistant formalization",
        "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in paths},
        "runner_controls": runner, "archive_reuse_controls": archive,
        "read_only_source_findings": [
            "Fresh and reused proof completion flags start false, are separate from requests, and become true only after the corresponding successful stage.",
            "All stage entrypoint paths exist; the complete16,128,175,745,950 profile chain and separate matching-lemma controls are included in order.",
            "The fresh archive checker verifies a single extraction root, safe and unique ZIP names, exact manifest inventory, every extracted payload size/hash, and unchanged archive bytes.",
            "Explicit proof reuse binds the prior complete fresh-extraction status, semantic source/manifest hashes, all four exact cases, regenerated CNF hashes, proof hashes and audit input pairs.",
            "The integrated merge separately binds the current replay to the actual compact manifests, immutable source files and proof/CNF payload hashes, and requires four unique expected cases.",
            "Successful reuse reports zero newly checked proofs and four bound prior fresh checks; this review performs neither operation."
        ],
        "child_programs_run": 0, "archives_extracted": 0, "SAT_or_proof_checkers_run": 0,
        "reviewed_script_writes_redirected_to_memory": True,
        "only_actual_output": "research_round8/geometry/REPLAY_REPORTING_REVIEW.json",
        "blocking_issues_found": [],
    }
    output = HERE / "REPLAY_REPORTING_REVIEW.json"
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "nonzero_stage_returns": len(runner["nonzero_child_returns"]),
                      "unexpected_child_exceptions": len(runner["unexpected_child_exceptions"]),
                      "reuse_negative_controls": len(archive["negative_controls"]),
                      "review_receipt_sha256": sha(output)}, indent=2))


if __name__ == "__main__":
    main()
