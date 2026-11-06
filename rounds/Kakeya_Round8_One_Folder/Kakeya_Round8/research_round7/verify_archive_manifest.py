#!/usr/bin/env python3
"""Verify every delivered file against the Round7 archive manifest.

Run before replay: replay intentionally updates procedural logs and receipts.
Extra generated files do not affect the check of the delivered inventory.
"""
from pathlib import Path, PurePosixPath
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(root=ROOT):
    manifest = json.loads((root / "MANIFEST_ROUND7.json").read_text())
    if manifest["schema"] != "kakeya-complete-round7-archive-v1":
        raise ValueError("Wrong manifest schema")
    paths = [row["path"] for row in manifest["files"]]
    if len(paths) != len(set(paths)) or len(paths) != manifest["payload_files"]:
        raise ValueError("Duplicated or incomplete payload inventory")
    for row in manifest["files"]:
        name = PurePosixPath(row["path"])
        if name.is_absolute() or ".." in name.parts or "\\" in str(name):
            raise ValueError("Unsafe manifest path")
        path = root.joinpath(*name.parts)
        if not path.is_file() or path.is_symlink():
            raise ValueError("Missing or non-regular payload: " + str(name))
        if path.stat().st_size != row["bytes"] or sha(path) != row["sha256"]:
            raise ValueError("Payload differs: " + str(name))
    result = {"status": "PASS_ALL_DELIVERED_ROUND7_PAYLOAD_HASHES", "payload_files": len(paths),
              "preserved_Round6_payload_files": manifest["preserved_Round6_payload_files"],
              "monograph_words": manifest["monograph_word_count"]}
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    verify()
