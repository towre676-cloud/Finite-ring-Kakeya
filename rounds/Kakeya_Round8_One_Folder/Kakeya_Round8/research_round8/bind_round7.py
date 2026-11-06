#!/usr/bin/env python3
"""Bind the immutable inherited checkpoint without rerunning old producers."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SHA = "7646c5f0c2664a9206666cdbf1ff9ae7b920af0badeb952c3ae0aa00e19d9ae9"
ARCHIVE_SHA = "f935db84b72b7561403017c7c436995a96b291959650fc478a88d3b27d14759d"


def digest(stream):
    h, size = hashlib.sha256(), 0
    for block in iter(lambda: stream.read(1024*1024), b""):
        h.update(block)
        size += len(block)
    return h.hexdigest(), size


def check_name(name):
    p = PurePosixPath(name)
    if p.is_absolute() or ".." in p.parts or "\\" in name:
        raise ValueError("Unsafe inherited payload path")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    start = time.monotonic()
    raw = (ROOT / "MANIFEST_ROUND7.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != MANIFEST_SHA:
        raise ValueError("Inherited Round7 manifest changed")
    manifest = json.loads(raw)
    rows = manifest["files"]
    if len(rows) != 4958 or len({r["path"] for r in rows}) != len(rows):
        raise ValueError("Inherited inventory is not the complete sealed checkpoint")
    total = 0
    if args.archive:
        with args.archive.open("rb") as source:
            if digest(source)[0] != ARCHIVE_SHA:
                raise ValueError("The inherited archive is not the sealed Round7 ZIP")
        with zipfile.ZipFile(args.archive) as archive:
            if archive.read("Kakeya_Round7/MANIFEST_ROUND7.json") != raw:
                raise ValueError("Inherited archive manifest differs")
            for row in rows:
                check_name(row["path"])
                with archive.open("Kakeya_Round7/" + row["path"]) as source:
                    h, size = digest(source)
                if h != row["sha256"] or size != row["bytes"]:
                    raise ValueError("Inherited archive payload changed: " + row["path"])
                total += size
        route = "SEALED_ROUND7_ARCHIVE"
    else:
        for row in rows:
            check_name(row["path"])
            path = ROOT / row["path"]
            if path.is_symlink() or not path.is_file():
                raise ValueError("Missing regular inherited payload: " + row["path"])
            with path.open("rb") as source:
                h, size = digest(source)
            if h != row["sha256"] or size != row["bytes"]:
                raise ValueError("Inherited payload changed: " + row["path"])
            total += size
        route = "EXTRACTED_ROUND7_PAYLOADS"
    result = {"status": "PASS_IMMUTABLE_INHERITED_CHECKPOINT_BINDING", "route": route,
              "payload_files": len(rows), "payload_bytes": total,
              "manifest_sha256": MANIFEST_SHA, "source_archive_sha256": ARCHIVE_SHA,
              "fresh_inherited_proof_replay": False,
              "meaning": "All inherited bytes are bound to the prior completed checkpoint; no old producer or checker was rerun.",
              "seconds": round(time.monotonic()-start, 6)}
    (ROOT / "research_round8/INHERITED_ROUND7_BINDING.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
