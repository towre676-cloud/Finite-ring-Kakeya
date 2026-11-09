#!/usr/bin/env python3
"""Restore the exact Round 10 evidence from its reviewed archive."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / "EVIDENCE_MANIFEST.json").read_text())
    if digest(args.archive) != manifest["archive_sha256"]:
        raise ValueError("The review archive SHA-256 does not match")
    with zipfile.ZipFile(args.archive) as archive:
        for name, expected in manifest["files"]:
            relative = Path(name)
            target = root / relative
            if relative.is_absolute() or ".." in relative.parts or not target.resolve().is_relative_to(root):
                raise ValueError(f"Invalid evidence path: {name}")
            if target.exists():
                if digest(target) != expected:
                    raise ValueError(f"Existing file differs: {name}")
                continue
            data = archive.read(manifest["archive_prefix"] + name)
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError(f"Archive member hash differs: {name}")
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as stream:
                temporary = Path(stream.name)
            try:
                temporary.write_bytes(data)
                temporary.replace(target)
            finally:
                temporary.unlink(missing_ok=True)
    print(f"Verified {len(manifest['files'])} Round 10 evidence files.")


if __name__ == "__main__":
    main()
