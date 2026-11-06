#!/usr/bin/env python3
"""Build one ordinary ZIP and verify its complete single-folder payload.

The sealed Round6 archive supplies every inherited byte. Only Round7
payloads come from the current working tree, so replay-updated historical
logs cannot silently overwrite the earlier checkpoint.
"""
from pathlib import Path, PurePosixPath
import errno
import hashlib
import json
import os
import shutil
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "research_round7"
BASE = ROOT / "Kakeya_Round6_One_Folder.zip"
BASE_SHA = "d6ee0e5cdeda3376abf5be65d32b0bfd534b4be04532f466368f21691a742896"
OUTPUT = ROOT / "Kakeya_Round7_One_Folder.zip"
PREFIX = "Kakeya_Round7/"
BASE_PREFIX = "Kakeya_Round6/"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read(relative):
    return json.loads((ROOT / relative).read_text())


def selected_files():
    selected = {}
    def add(path):
        path = Path(path)
        require(path.is_file() and not path.is_symlink(), "Missing or non-regular payload: " + str(path))
        relative = str(path.relative_to(ROOT))
        selected[relative] = path
    for name in ("README_Round7.txt", "VERIFY_ROUND7.py", "Kakeya_Research_Frontier_Round7.json"):
        add(ROOT / name)
    ordinary = {".py", ".cpp", ".c", ".h", ".lean", ".md", ".txt", ".json", ".jsonl", ".csv", ".pdf", ".log"}
    ignored = {"__pycache__", "bin", "replay_bin", "compact_pilot"}
    for path in HERE.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(HERE)
        if any(part in ignored or part.startswith(".") for part in relative.parts):
            continue
        if path.suffix in ordinary:
            add(path)
    # Tiny positive/negative proof-prefix controls are actual replay inputs.
    for path in (HERE / "support13/unit_controls").iterdir():
        if path.is_file() and path.suffix in {".cnf", ".drat", ".lrat"}:
            add(path)
    # Exact-ring proofs are already small; retain their complete originals.
    for directory in ("exact_ring", "exact_shape", "support13/four_pair_cut"):
        for path in (HERE / directory / "cases").rglob("*.xz"):
            add(path)
    # All56 dimension4 exact formulas are retained, including timeouts.
    for path in (HERE / "dimension4/cases").glob("*/input.cnf.xz"):
        add(path)
    n4 = read("research_round7/dimension4_compact/COMPACT_DIMENSION4_MANIFEST.json")
    for row in n4["cases"]:
        if row["representation"] == "COMPACT_DRAT":
            path = HERE / "dimension4_compact/cases" / row["case_id"] / "core.drat.xz"
            require(sha(path) == row["core_xz_sha256"], "Changed dimension4 compact proof")
            add(path)
    # The final48-case S13 inventory selects original CNFs and replacement
    # cores explicitly. The inherited CNF/LRAT is already in the base ZIP.
    support = read("research_round7/compact_support13/COMPACT_SUPPORT13_MANIFEST.json")
    for row in support["cases"]:
        old = row["original_case"]
        if old["inherited"]:
            continue
        cnf = ROOT / (old["cnf"] + ".xz")
        require(sha(cnf) == old["cnf_xz_sha256"], "Changed support13 original CNF")
        add(cnf)
        proof = ROOT / (row["core_proof"] + ".xz")
        require(sha(proof) == row["core_xz_sha256"], "Changed support13 compact proof")
        add(proof)
    qa = read("research_round7/MONOGRAPH_PDF_QA.json")
    require(qa["status"] == "PASS_FINAL_PDF_VISUAL_AND_TEXT_QA"
            and qa["source_whitespace_words"] == qa["pdf_body_whitespace_words"] == 1500,
            "Monograph is not the verified1500-word artifact")
    require(sha(HERE / qa["source"]) == qa["source_sha256"] and sha(HERE / qa["pdf"]) == qa["pdf_sha256"], "Monograph changed")
    return selected


def safe_name(name):
    path = PurePosixPath(name)
    require(not path.is_absolute() and ".." not in path.parts and "\\" not in name, "Unsafe ZIP path")
    return str(path)


def main():
    require(sha(BASE) == BASE_SHA, "Sealed Round6 checkpoint changed")
    integration = read("research_round7/ROUND7_PORTABLE_REPLAY.json")
    require(integration["status"] in {"PASS_ROUND7_INTEGRATION_WITH_BOUND_FULL_REPLAY_RECEIPTS", "PASS_ROUND7_FRESH_ALL_NEW_CERTIFICATE_REPLAY"},
            "Complete integrated verification is required before packaging")
    require(read("research_round7/ROUND7_MERGED_REPLAY.json")["status"] == "PASS_EXACT_ROUND7_FRONTIER_ACCOUNTING", "Ledger has not passed")
    selected = selected_files()
    rows, originals = [], []
    with zipfile.ZipFile(BASE) as baseline:
        for item in baseline.infolist():
            if item.is_dir():
                continue
            require(item.filename.startswith(BASE_PREFIX), "Unexpected inherited extraction root")
            name = safe_name(item.filename[len(BASE_PREFIX):])
            require(name not in selected, "Round7 would overwrite an inherited payload")
            digest, size = hashlib.sha256(), 0
            with baseline.open(item) as stream:
                for block in iter(lambda: stream.read(1024*1024), b""):
                    digest.update(block); size += len(block)
            rows.append({"path": name, "bytes": size, "sha256": digest.hexdigest(), "source": "unchanged_Round6"})
            originals.append((name, item.filename))
    for name, path in sorted(selected.items()):
        rows.append({"path": safe_name(name), "bytes": path.stat().st_size, "sha256": sha(path), "source": "Round7"})
    require(len(rows) == len({row["path"] for row in rows}), "Duplicated archive payload")
    manifest = {
        "schema": "kakeya-complete-round7-archive-v1", "top_level_folder": "Kakeya_Round7",
        "payload_files": len(rows), "preserved_Round6_payload_files": len(originals),
        "source_Round6_archive_sha256": BASE_SHA, "monograph_word_count": 1500,
        "new_complete_theorem": "k_R(3)=22 in both rings; elementary proof plus10 exact ring-specific refutations",
        "dimension4_status": "OPEN;14checked refutations and42uncredited timeouts",
        "dimension5_status": "OPEN;183476middle profiles and45maximum11 affine classes remain",
        "new_support13_certificate_rows": 48, "new_support13_DRAT_cores": 47,
        "new_whole_weight_profile_exclusions": 3006,
        "proof_storage": "Exact original CNFs plus separately checked compact DRATs for new S13/n4; complete original exact-ring DRATs. Mandatory regenerated-LRAT CakeML replay.",
        "omitted_intermediates": "Original untrimmed Round7 S13/n4 DRAT streams, unfinished proof traces, compiled binaries/caches, pilot scratch, and uncertified generic-variant/S13 survey CNFs. Their required source parameters, exact hashes and completed provenance remain; replay does not require omitted streams.",
        "files": rows}
    manifest_path = ROOT / "MANIFEST_ROUND7.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    with tempfile.TemporaryDirectory(prefix="kakeya_round7_zip_") as temporary:
        staged = Path(temporary) / OUTPUT.name
        with zipfile.ZipFile(staged, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
            archive.writestr(PREFIX, b"")
            with zipfile.ZipFile(BASE) as baseline:
                for name, original_name in originals:
                    info = zipfile.ZipInfo(PREFIX + name, date_time=(2026, 10, 28, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_STORED if name.endswith((".xz", ".zip")) else zipfile.ZIP_DEFLATED
                    info.external_attr = 0o100644 << 16
                    with baseline.open(original_name) as source, archive.open(info, "w", force_zip64=True) as destination:
                        shutil.copyfileobj(source, destination, 1024*1024)
            for name, path in sorted(selected.items()):
                kind = zipfile.ZIP_STORED if path.suffix in {".xz", ".zip"} else zipfile.ZIP_DEFLATED
                archive.write(path, PREFIX + name, compress_type=kind)
            archive.write(manifest_path, PREFIX + manifest_path.name)
        expected = {row["path"]: row for row in rows}
        with zipfile.ZipFile(staged) as archive:
            names = archive.namelist()
            require(len(names) == len(set(names)) and {name.split("/")[0] for name in names} == {"Kakeya_Round7"}, "ZIP does not have one unique root")
            actual = {name[len(PREFIX):] for name in names if name not in {PREFIX, PREFIX + manifest_path.name}}
            require(actual == set(expected), "ZIP payload inventory differs")
            for name, row in expected.items():
                digest, size = hashlib.sha256(), 0
                with archive.open(PREFIX + name) as stream:
                    for block in iter(lambda: stream.read(1024*1024), b""):
                        digest.update(block); size += len(block)
                require(size == row["bytes"] and digest.hexdigest() == row["sha256"], "ZIP changed a payload: " + name)
            require(json.loads(archive.read(PREFIX + manifest_path.name)) == manifest, "ZIP manifest differs")
        digest = sha(staged)
        try:
            os.replace(staged, OUTPUT)
        except OSError as error:
            if error.errno != errno.EXDEV:
                raise
            pending = OUTPUT.with_suffix(".zip.publishing")
            shutil.copyfile(staged, pending)
            require(sha(pending) == digest, "Archive copy changed")
            pending.replace(OUTPUT)
        require(sha(OUTPUT) == digest, "Published archive changed")
    receipt = {"status": "PASS_COMPLETE_SINGLE_FOLDER_ROUND7_ARCHIVE", "path": str(OUTPUT),
               "bytes": OUTPUT.stat().st_size, "sha256": digest, "payload_files": len(rows),
               "preserved_Round6_files": len(originals), "all_payload_hashes_verified": True,
               "sole_extraction_root": PREFIX, "monograph_words": 1500}
    (ROOT / "Kakeya_Round7_Archive_Receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2), flush=True)


if __name__ == "__main__":
    main()
