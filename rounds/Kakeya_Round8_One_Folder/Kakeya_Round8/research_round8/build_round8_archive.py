#!/usr/bin/env python3
"""Preserve the sealed history and publish one verified single-folder ZIP."""
from pathlib import Path, PurePosixPath
import errno
import hashlib
import json
import os
import shutil
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "research_round8"
BASE = ROOT / "Kakeya_Round7_One_Folder.zip"
BASE_SHA = "f935db84b72b7561403017c7c436995a96b291959650fc478a88d3b27d14759d"
OUTPUT = ROOT / "Kakeya_Round8_One_Folder.zip"
PREFIX = "Kakeya_Round8/"
BASE_PREFIX = "Kakeya_Round7/"


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads((ROOT / path).read_text())


def safe_name(name):
    p = PurePosixPath(name)
    require(not p.is_absolute() and ".." not in p.parts and "\\" not in name,
            "Unsafe payload path")
    return str(p)


def selected_files():
    files = {}

    def add(path):
        require(path.is_file() and not path.is_symlink(), "Missing regular payload: " + str(path))
        files[str(path.relative_to(ROOT))] = path

    for name in ("README_Round8.txt", "VERIFY_ROUND8.py", "Kakeya_Research_Frontier_Round8.json"):
        add(ROOT / name)
    ordinary = {".py", ".cpp", ".c", ".h", ".lean", ".md", ".txt", ".json", ".jsonl", ".csv", ".pdf", ".log"}
    # Final extraction logs are external receipts for this ZIP; including
    # them would package a previous extraction under a misleading current name.
    ignored = {"__pycache__", "bin", "replay_bin", "fresh_archive_logs"}
    for path in HERE.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(HERE)
        if any(part in ignored or part.startswith(".") for part in relative.parts):
            continue
        if path.suffix in ordinary:
            add(path)
    compact = read("research_round8/strengthened/compact/COMPACT_CERTIFICATE_MANIFEST.json")
    require(len(compact["cases"]) == 4, "Exactly four compact new proofs required")
    for row in compact["cases"]:
        original = row["original_case"]
        require(row["representation"] == "COMPACT_DRAT", "A new case lacks its checked compact proof")
        cnf = HERE / "strengthened/cases" / row["case_id"] / "input.cnf.xz"
        core = HERE / "strengthened/compact/cases" / row["case_id"] / "core.drat.xz"
        require(digest(cnf) == original["storage"]["input.cnf"]["xz_sha256"], "Original new CNF changed")
        require(digest(core) == row["core_xz_sha256"], "New compact proof changed")
        add(cnf)
        add(core)
    require(not any(name.endswith("proof.drat.xz") for name in files),
            "Large original Round8 proofs should not be duplicated in the portable ZIP")
    return files


def main():
    require(digest(BASE) == BASE_SHA, "Sealed inherited archive changed")
    integration = read("research_round8/ROUND8_PORTABLE_REPLAY.json")
    require(integration["status"] in {"PASS_ROUND8_INTEGRATION_WITH_BOUND_FULL_PROOF_RECEIPTS",
                                      "PASS_ROUND8_FRESH_ALL_NEW_CERTIFICATES_AND_FINITE_RESULTS"},
            "Integrated Round8 verification must pass before packaging")
    merged = read("research_round8/ROUND8_MERGED_REPLAY.json")
    require(merged["status"] == "PASS_EXACT_ROUND8_FRONTIER_ACCOUNTING"
            and merged["ledger_sha256"] == digest(ROOT / "Kakeya_Research_Frontier_Round8.json")
            and merged["source_code_sha256"] == digest(HERE / "merge_round8.py"), "Ledger binding changed")
    qa = read("research_round8/MONOGRAPH_PDF_QA.json")
    require(qa["status"] == "PASS_EXACT_1500_WORD_TEXT_AND_THREE_PAGE_VISUAL_QA"
            and qa["rendered_words_including_title"] == 1500
            and digest(ROOT / qa["source"]) == qa["source_sha256"]
            and digest(ROOT / qa["pdf"]) == qa["pdf_sha256"], "Monograph is not the checked final artifact")
    selected = selected_files()
    rows, inherited = [], []
    with zipfile.ZipFile(BASE) as archive:
        for item in archive.infolist():
            if item.is_dir():
                continue
            require(item.filename.startswith(BASE_PREFIX), "Unexpected inherited root")
            name = safe_name(item.filename[len(BASE_PREFIX):])
            require(name not in selected, "A new file would overwrite an inherited file")
            h, size = hashlib.sha256(), 0
            with archive.open(item) as stream:
                for block in iter(lambda: stream.read(1024*1024), b""):
                    h.update(block)
                    size += len(block)
            rows.append({"path": name, "bytes": size, "sha256": h.hexdigest(), "source": "unchanged_Round7"})
            inherited.append((name, item.filename))
    for name, path in sorted(selected.items()):
        rows.append({"path": safe_name(name), "bytes": path.stat().st_size,
                     "sha256": digest(path), "source": "Round8"})
    require(len(rows) == len({r["path"] for r in rows}), "Duplicate payload path")
    manifest = {"schema": "kakeya-complete-round8-archive-v1", "top_level_folder": "Kakeya_Round8",
                "payload_files": len(rows), "preserved_Round7_payload_files": len(inherited),
                "source_Round7_archive_sha256": BASE_SHA, "monograph_word_count": 1500,
                "new_branch_theorem": "Exact maximum11 and support13 excluded in dimension5 in both rings, with inherited reductions and reviewed encoding.",
                "new_checked_refutations": 4, "new_whole_affine_support_classes_closed": [109, 110, 111],
                "remaining_maximum11_affine_classes": 42, "new_whole_middle_profiles_excluded": 950,
                "remaining_middle_profiles": 182526,
                "dimension4_status": "OPEN", "unrestricted_dimension5_status": "OPEN",
                "proof_storage": "All exact new original CNFs plus four separately checked compact DRATs; mandatory regenerated-LRAT CakeML replay.",
                "omitted_new_intermediates": "Four large untrimmed Round8 DRAT streams, reconstructed temporary LRAT files, compiled executables, caches and scratch renders. Original hashes/receipts and exact compact replacements are retained.",
                "inherited_payloads_modified": False, "files": rows}
    manifest_path = ROOT / "MANIFEST_ROUND8.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    with tempfile.TemporaryDirectory(prefix="kakeya_round8_zip_") as temporary:
        staged = Path(temporary) / OUTPUT.name
        with zipfile.ZipFile(staged, "w", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=6, allowZip64=True) as archive:
            archive.writestr(PREFIX, b"")
            with zipfile.ZipFile(BASE) as baseline:
                for name, original in inherited:
                    info = zipfile.ZipInfo(PREFIX + name, date_time=(2026, 10, 28, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_STORED if name.endswith((".xz", ".zip")) else zipfile.ZIP_DEFLATED
                    info.external_attr = 0o100644 << 16
                    with baseline.open(original) as source, archive.open(info, "w", force_zip64=True) as destination:
                        shutil.copyfileobj(source, destination, 1024*1024)
            for name, path in sorted(selected.items()):
                kind = zipfile.ZIP_STORED if path.suffix in {".xz", ".zip"} else zipfile.ZIP_DEFLATED
                archive.write(path, PREFIX + name, compress_type=kind)
            archive.write(manifest_path, PREFIX + manifest_path.name)
        expected = {r["path"]: r for r in rows}
        with zipfile.ZipFile(staged) as archive:
            names = archive.namelist()
            require(len(names) == len(set(names)) and {n.split("/")[0] for n in names} == {"Kakeya_Round8"},
                    "Archive must have exactly one extraction root and unique paths")
            actual = {n[len(PREFIX):] for n in names if n not in (PREFIX, PREFIX + manifest_path.name)}
            require(actual == set(expected), "Archive inventory differs")
            for name, row in expected.items():
                h, size = hashlib.sha256(), 0
                with archive.open(PREFIX + name) as stream:
                    for block in iter(lambda: stream.read(1024*1024), b""):
                        h.update(block)
                        size += len(block)
                require(h.hexdigest() == row["sha256"] and size == row["bytes"], "Archive payload changed: " + name)
            require(json.loads(archive.read(PREFIX + manifest_path.name)) == manifest, "Packed manifest differs")
        result_hash = digest(staged)
        try:
            os.replace(staged, OUTPUT)
        except OSError as error:
            if error.errno != errno.EXDEV:
                raise
            pending = OUTPUT.with_suffix(".zip.publishing")
            shutil.copyfile(staged, pending)
            require(digest(pending) == result_hash, "Published archive copy changed")
            pending.replace(OUTPUT)
        require(digest(OUTPUT) == result_hash, "Final archive differs from its checked bytes")
    result = {"status": "PASS_COMPLETE_SINGLE_FOLDER_ROUND8_ARCHIVE", "path": str(OUTPUT),
              "bytes": OUTPUT.stat().st_size, "sha256": result_hash,
              "payload_files": len(rows), "preserved_Round7_files": len(inherited),
              "all_payload_hashes_verified": True, "sole_extraction_root": PREFIX,
              "new_checked_refutations": 4, "new_whole_profile_exclusions": 950,
              "monograph_words_including_title": 1500}
    (ROOT / "Kakeya_Round8_Archive_Receipt.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
