"""Check exact distributed payload bytes before procedural replays rewrite logs."""
from pathlib import Path, PurePosixPath
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def main():
    manifest = json.loads((ROOT / 'MANIFEST_ROUND6.json').read_text())
    rows = manifest['files']
    seen = set()
    for row in rows:
        name = PurePosixPath(row['path'])
        if name.is_absolute() or '..' in name.parts or str(name) in seen:
            raise ValueError('Unsafe or duplicated manifest path')
        seen.add(str(name))
        path = ROOT.joinpath(*name.parts)
        if not path.is_file() or path.stat().st_size != row['bytes'] or sha(path) != row['sha256']:
            raise ValueError('Payload mismatch: ' + str(name))
    if len(rows) != manifest['payload_files']:
        raise ValueError('Wrong payload count')
    print(json.dumps({'status': 'PASS_ALL_ROUND6_DISTRIBUTED_PAYLOAD_HASHES',
                      'checked_files': len(rows)}))


if __name__ == '__main__':
    main()
