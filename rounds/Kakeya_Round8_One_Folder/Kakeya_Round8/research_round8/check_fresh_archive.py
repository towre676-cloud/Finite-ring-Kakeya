#!/usr/bin/env python3
"""Verify every ZIP payload and replay after fresh extraction.

The default freshly checks all four proofs. Explicit reuse requires the
unchanged proof files and sources from a prior complete fresh-extraction replay.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "research_round8"
DESTINATION = ROOT / "Kakeya_Round8_Fresh_Extraction_Receipt.json"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def main():
    # No prior successful run may supply completion flags to an early failure.
    DESTINATION.write_text(json.dumps({"status": "RUNNING",
        "fresh_proofs_checked": 0,
        "previously_freshly_checked_unchanged_proofs_bound": 0,
        "all_payloads_preserved": False,
        "regenerated_ledger_identical": False}, indent=2) + "\n")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=ROOT / "Kakeya_Round8_One_Folder.zip")
    parser.add_argument("--reuse-checked-certificates", action="store_true")
    args = parser.parse_args()
    start = time.monotonic()
    report = {"status": "RUNNING", "archive": str(args.archive.resolve()),
              "fresh_proofs_checked": 0,
              "previously_freshly_checked_unchanged_proofs_bound": 0,
              "all_payloads_preserved": False, "regenerated_ledger_identical": False}
    DESTINATION.write_text(json.dumps(report, indent=2) + "\n")
    archive_hash = sha(args.archive)
    logs = HERE / "fresh_archive_logs"
    logs.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="kakeya_round8_fresh_") as temporary:
        temp = Path(temporary)
        with zipfile.ZipFile(args.archive) as archive:
            names = archive.namelist()
            require(len(names) == len(set(names)), "Duplicate ZIP paths")
            require({n.split("/")[0] for n in names} == {"Kakeya_Round8"}, "ZIP must have one extraction folder")
            for name in names:
                p = PurePosixPath(name)
                require(not p.is_absolute() and ".." not in p.parts and "\\" not in name, "Unsafe ZIP name")
            manifest = json.loads(archive.read("Kakeya_Round8/MANIFEST_ROUND8.json"))
            expected = {"Kakeya_Round8/" + r["path"] for r in manifest["files"]}
            require(set(names) == expected | {"Kakeya_Round8/", "Kakeya_Round8/MANIFEST_ROUND8.json"},
                    "ZIP inventory does not exactly match its manifest")
            archive.extractall(temp)
        extracted = temp / "Kakeya_Round8"
        for row in manifest["files"]:
            path = extracted / row["path"]
            require(path.is_file() and not path.is_symlink() and path.stat().st_size == row["bytes"]
                    and sha(path) == row["sha256"], "Freshly extracted payload differs: " + row["path"])
        report.update(archive_sha256=archive_hash, payload_hashes_verified=len(manifest["files"]),
                      sole_extraction_root="Kakeya_Round8", all_payloads_preserved=True)
        DESTINATION.write_text(json.dumps(report, indent=2) + "\n")
        command = [sys.executable, "VERIFY_ROUND8.py"]
        if args.reuse_checked_certificates:
            previous = extracted / "research_round8/proof_portability"
            receipt = json.loads((previous / "FULL_PROOF_PORTABILITY_RECEIPT.json").read_text())
            prior_integrated = json.loads((previous / "ROUND8_PORTABLE_REPLAY.json").read_text())
            prior_proofs = json.loads((previous / "COMPACT_CERTIFICATE_REPLAY.json").read_text())
            current_proofs = json.loads((extracted / "research_round8/strengthened/compact/COMPACT_CERTIFICATE_REPLAY.json").read_text())
            require(receipt["status"] == "PASS_FRESH_SINGLE_FOLDER_ARCHIVE_AND_ALL_NEW_PROOFS"
                    and receipt["fresh_proofs_checked"] == 4
                    and prior_integrated["status"] == "PASS_ROUND8_FRESH_ALL_NEW_CERTIFICATES_AND_FINITE_RESULTS"
                    and prior_integrated["fresh_all_four_new_proofs_replayed"] is True,
                    "No complete earlier fresh-extraction proof replay is available")
            for key in ("status", "full_inventory_replayed", "compact_manifest_sha256",
                        "source_manifest_sha256", "source_hashes"):
                require(prior_proofs[key] == current_proofs[key],
                        "Previously checked proof semantic sources differ: " + key)
            def case_binding(rows):
                require(len(rows) == 4, "Exactly four checked proof rows required")
                return {r["case_id"]: {k: r[k] for k in
                        ("status", "nonzero_support_mask", "maximum_interval", "mode",
                         "representation", "checked_proof_sha256", "exclusion_credited",
                         "regeneration")} | {"input_sha256": r["audit"]["input_sha256"],
                                            "audit_status": r["audit"]["status"]} for r in rows}
            require(case_binding(prior_proofs["cases"]) == case_binding(current_proofs["cases"]),
                    "The exact formulas or compact proofs differ from the prior fresh check")
            command.append("--reuse-checked-certificates")
            report["preceding_full_proof_extraction_receipt_sha256"] = sha(previous / "FULL_PROOF_PORTABILITY_RECEIPT.json")
            report["preceding_full_proof_archive_sha256"] = receipt["archive_sha256"]
            report["same_exact_formulas_proofs_and_sources_as_prior_full_check"] = True
        print("All fresh archive payload hashes passed; starting Round8 replay.", flush=True)
        with (logs / "stdout.txt").open("w") as output, (logs / "stderr.txt").open("w") as error:
            process = subprocess.Popen(command, cwd=extracted,
                                       stdout=subprocess.PIPE, stderr=error, text=True)
            for line in process.stdout:
                output.write(line)
                output.flush()
                print(line, end="", flush=True)
            returncode = process.wait()
        require(returncode == 0, "Freshly extracted integrated replay failed")
        replay = json.loads((extracted / "research_round8/ROUND8_PORTABLE_REPLAY.json").read_text())
        expected_status = ("PASS_ROUND8_INTEGRATION_WITH_BOUND_FULL_PROOF_RECEIPTS"
                           if args.reuse_checked_certificates
                           else "PASS_ROUND8_FRESH_ALL_NEW_CERTIFICATES_AND_FINITE_RESULTS")
        require(replay["status"] == expected_status
                and replay["fresh_all_four_new_proofs_replayed"] is not args.reuse_checked_certificates
                and replay["previous_complete_new_proof_replay_receipts_reused"] is args.reuse_checked_certificates,
                "Fresh extraction did not complete the requested proof-checking mode")
        original_ledger = next(r for r in manifest["files"] if r["path"] == "Kakeya_Research_Frontier_Round8.json")
        require(sha(extracted / original_ledger["path"]) == original_ledger["sha256"],
                "Regenerated ledger differs from the packaged current ledger")
        for name in ("ROUND8_PORTABLE_REPLAY.json", "ROUND8_MERGED_REPLAY.json"):
            (logs / name).write_bytes((extracted / "research_round8" / name).read_bytes())
        (logs / "COMPACT_CERTIFICATE_REPLAY.json").write_bytes(
            (extracted / "research_round8/strengthened/compact/COMPACT_CERTIFICATE_REPLAY.json").read_bytes())
        report.update(status="PASS_FRESH_SINGLE_FOLDER_ARCHIVE_WITH_UNCHANGED_CHECKED_PROOFS"
                      if args.reuse_checked_certificates
                      else "PASS_FRESH_SINGLE_FOLDER_ARCHIVE_AND_ALL_NEW_PROOFS",
                      fresh_replay_status=replay["status"], completed_stages=replay["completed_stages"],
                      fresh_proofs_checked=0 if args.reuse_checked_certificates else 4,
                      previously_freshly_checked_unchanged_proofs_bound=4 if args.reuse_checked_certificates else 0,
                      inherited_payloads_hash_bound=True,
                      inherited_proofs_freshly_rechecked=False, regenerated_ledger_identical=True,
                      stdout_sha256=sha(logs / "stdout.txt"), stderr_sha256=sha(logs / "stderr.txt"),
                      seconds=round(time.monotonic()-start, 6))
    require(sha(args.archive) == archive_hash, "Delivered ZIP changed during portable replay")
    DESTINATION.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    try:
        main()
    except BaseException as error:
        if isinstance(error, SystemExit) and error.code in (None, 0):
            raise
        try:
            report = json.loads(DESTINATION.read_text()) if DESTINATION.exists() else {}
            report.update(status="FAIL", error=repr(error))
            DESTINATION.write_text(json.dumps(report, indent=2) + "\n")
        except OSError:
            pass
        raise
