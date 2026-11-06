"""Verify every original payload hash before replays rewrite generated receipts."""
from hashlib import sha256
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent


if __name__ == '__main__':
    manifest = json.loads((ROOT/'MANIFEST_ROUND5.json').read_text())
    for name, expected in manifest['files_sha256'].items():
        path = ROOT/name
        if not path.is_file() or sha256(path.read_bytes()).hexdigest() != expected:
            raise SystemExit('Manifest mismatch: ' + name)
    print(json.dumps({'status':'PASS_ALL_ARCHIVE_PAYLOAD_HASHES',
                      'payload_files':len(manifest['files_sha256']),
                      'prior_entries_preserved':manifest['prior_archive']['entries_preserved']},indent=2))
