"""Build the complete Round4 archive while preserving every Round3 entry.

The original Kakeya_Research_Round3_Proofs.zip must be beside VERIFY_ROUND4.py.
All inherited members are read from that pinned archive, never from possibly
regenerated workspace receipts. New research_round4 source and human-readable
artifacts are included by an explicit extension allowlist. No compiler, Lean
runtime, executable, bytecode, or build cache is added by the Round4 layer.

Run this only after all new source, reports, and frontier files are finalized.
It does not replay the proof checkers. VERIFY_ROUND4.py is the replay entry point.
"""

from pathlib import Path, PurePosixPath
import copy
import hashlib
import json
import os
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[2]
SOURCE_ARCHIVE = ROOT / 'Kakeya_Research_Round3_Proofs.zip'
SOURCE_SHA256 = '44c8663dc9a0a3343196c51fe284f7f09e84f2489cde4d837cbc8c3b95040d05'
SOURCE_ENTRIES = 396
OUTPUT = ROOT / 'Kakeya_Complete_Round4.zip'
MANIFEST = ROOT / 'MANIFEST_ROUND4.json'
NEW_ROOT_FILES = (
    'VERIFY_ROUND4.py',
    'Kakeya_Round3_Portable_Replay_Receipt.json',
    'Kakeya_Research_Frontier_Round4.json',
    'Kakeya_Research_Round4_Report.txt',
    'README_Round4.txt',
)
OPTIONAL_ROOT_FILES = ('Kakeya_Round4_Portable_Replay_Receipt.json',)
EXTENSIONS = {'.py', '.cpp', '.json', '.jsonl', '.txt', '.md', '.lean', '.toml'}
EXCLUDED_DIRECTORIES = {
    '__pycache__', '.lake', '.git', '.cache', '.pytest_cache', '.mypy_cache',
    'node_modules', 'runtime', 'runtimes', 'cache', 'caches',
}
NEW_TIMESTAMP = (2026, 10, 28, 0, 0, 0)


def digest_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def valid_archive_name(name):
    p = PurePosixPath(name)
    return (bool(name) and not p.is_absolute() and '..' not in p.parts
            and '\\' not in name and name == str(p))


def new_info(name):
    info = zipfile.ZipInfo(name, date_time=NEW_TIMESTAMP)
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    return info


def copy_and_hash(source, destination):
    digest, size = hashlib.sha256(), 0
    while True:
        block = source.read(1024 * 1024)
        if not block:
            break
        destination.write(block)
        digest.update(block)
        size += len(block)
    return {'bytes': size, 'sha256': digest.hexdigest()}


def main():
    require(SOURCE_ARCHIVE.is_file(), 'Missing original Round3 archive')
    require(digest_file(SOURCE_ARCHIVE) == SOURCE_SHA256,
            'Original Round3 archive does not match the pinned SHA256')
    for name in NEW_ROOT_FILES:
        require((ROOT / name).is_file(), 'Missing finalized root artifact: ' + name)
    monograph = ROOT / 'research_round4/Kakeya_Round4_Monograph.txt'
    require(len(monograph.read_text(encoding='utf-8').split()) == 1500,
            'Monograph must have exactly 1500 whitespace-delimited words')
    frontier = json.loads((ROOT / 'Kakeya_Research_Frontier_Round4.json')
                          .read_text(encoding='utf-8'))
    require(frontier['unrestricted_dimension5_theorem'] == 'OPEN',
            'The unrestricted dimension-five theorem must remain OPEN')
    require(frontier['dimension5_strata']['maximum12_through18']
            ['remaining_weight_profiles'] == 275755,
            'Unexpected final middle frontier count')
    require(frontier['middle_weight_inventory']['empty_cells']
            == [{'support': 17, 'maximum': 18}],
            'Unexpected final closed middle cells')

    added = {name: ROOT / name for name in NEW_ROOT_FILES}
    for name in OPTIONAL_ROOT_FILES:
        if (ROOT / name).is_file():
            replay = json.loads((ROOT / name).read_text(encoding='utf-8'))
            require(replay['status'] == 'PASS_ALL_ROUND4_FINITE_REPLAY_STEPS',
                    'Optional portable replay receipt is not PASS: ' + name)
            added[name] = ROOT / name
    excluded = []
    for source in sorted((ROOT / 'research_round4').rglob('*')):
        if not source.is_file():
            continue
        name = source.relative_to(ROOT).as_posix()
        relative = source.relative_to(ROOT / 'research_round4')
        if (any(part in EXCLUDED_DIRECTORIES for part in relative.parts[:-1])
                or (source.suffix not in EXTENSIONS and source.name != 'lean-toolchain')):
            excluded.append(name)
            continue
        require(not source.is_symlink(), 'Symlink is not an archive payload: ' + name)
        added[name] = source
    new_hashes = {name: {'bytes': source.stat().st_size, 'sha256': digest_file(source)}
                  for name, source in added.items()}

    temp_fd, temp_name = tempfile.mkstemp(prefix='kakeya_round4_', suffix='.zip.tmp',
                                         dir=ROOT)
    os.close(temp_fd)
    temp_path = Path(temp_name)
    try:
        with zipfile.ZipFile(SOURCE_ARCHIVE, 'r') as inherited:
            original = inherited.infolist()
            require(len(original) == SOURCE_ENTRIES,
                    'Unexpected number of original Round3 archive entries')
            require(len({info.filename for info in original}) == SOURCE_ENTRIES,
                    'Duplicate original archive member')
            require(all(not info.is_dir() and valid_archive_name(info.filename)
                        for info in original), 'Unsafe or directory member in original archive')
            require(not ({info.filename for info in original} & set(added)),
                    'A Round4 addition would overwrite an inherited Round3 entry')
            require(MANIFEST.name not in added
                    and MANIFEST.name not in inherited.namelist(),
                    'The new manifest must not appear in its own payload')
            old_manifest_bytes = inherited.read('MANIFEST_ROUND3.json')
            old_manifest = json.loads(old_manifest_bytes)
            expected_old = {row['path']: row for row in old_manifest['files']}
            require(len(expected_old) == 395, 'Unexpected original Round3 payload count')
            rows = []
            with zipfile.ZipFile(temp_path, 'w', compression=zipfile.ZIP_DEFLATED,
                                 compresslevel=9, allowZip64=True) as output:
                for original_info in original:
                    info = copy.copy(original_info)
                    with inherited.open(original_info, 'r') as source:
                        with output.open(info, 'w', force_zip64=True) as destination:
                            result = copy_and_hash(source, destination)
                    name = original_info.filename
                    require(result['bytes'] == original_info.file_size,
                            'Inherited archive member size changed: ' + name)
                    if name != 'MANIFEST_ROUND3.json':
                        require(name in expected_old and result['bytes'] == expected_old[name]['bytes']
                                and result['sha256'] == expected_old[name]['sha256'],
                                'Inherited member disagrees with its original manifest: ' + name)
                    rows.append({'path': name, **result})
                for name, source_path in sorted(added.items()):
                    require(valid_archive_name(name), 'Unsafe new archive member: ' + name)
                    with source_path.open('rb') as source:
                        with output.open(new_info(name), 'w', force_zip64=True) as destination:
                            result = copy_and_hash(source, destination)
                    require(result == new_hashes[name],
                            'Source changed during packaging: ' + name)
                    rows.append({'path': name, **result})
                rows.sort(key=lambda row: row['path'])
                manifest = {
                    'title': 'Complete Kakeya Round4 research and reproducibility checkpoint',
                    'version': 1,
                    'entry_point': 'VERIFY_ROUND4.py',
                    'scope': ('Complete inherited Round3 archive plus Round4 analytic proofs, '
                              'finite inventories and certificates, bounded Lean module, '
                              'explanatory reports, and reproducible source. The unrestricted '
                              'Kakeya theorem remains open.'),
                    'inherited_round3_archive': {
                        'filename': SOURCE_ARCHIVE.name,
                        'bytes': SOURCE_ARCHIVE.stat().st_size,
                        'sha256': SOURCE_SHA256,
                        'members_preserved_byte_identically': SOURCE_ENTRIES,
                        'manifest_sha256': hashlib.sha256(old_manifest_bytes).hexdigest(),
                    },
                    'round4_added_payload_files': len(added),
                    'round4_file_policy': {
                        'extensions': sorted(EXTENSIONS),
                        'additional_basename': 'lean-toolchain',
                        'excluded_directory_names': sorted(EXCLUDED_DIRECTORIES),
                        'excluded_workspace_files': excluded,
                        'inherited_members': 'All original members preserved regardless of extension.',
                    },
                    'replay_scope': {
                        'default': 'Round4 finite checks with fresh quota enumeration; no Lean or network.',
                        'with_round3': 'Complete Round3 replay runs first when --with-round3 is specified.',
                        'lean': 'Separate pinned compilation receipt included; portable runner does not rerun Lean.',
                    },
                    'payload_count': len(rows),
                    'payload_bytes': sum(row['bytes'] for row in rows),
                    'files': rows,
                }
                manifest_bytes = (json.dumps(manifest, indent=2) + '\n').encode('utf-8')
                output.writestr(new_info(MANIFEST.name), manifest_bytes, compresslevel=9)
            with zipfile.ZipFile(temp_path, 'r') as built:
                require(len(built.infolist()) == len(rows) + 1,
                        'Completed archive entry count mismatch')
                require(built.read(MANIFEST.name) == manifest_bytes,
                        'Completed archive manifest mismatch')
                require(built.testzip() is None, 'Completed archive CRC validation failed')
        temp_path.replace(OUTPUT)
        MANIFEST.write_bytes(manifest_bytes)
    finally:
        if temp_path.exists():
            temp_path.unlink()
    print(json.dumps({
        'status': 'PASS_PACKAGE_BUILD_AND_BYTE_PRESERVATION',
        'archive': OUTPUT.name, 'bytes': OUTPUT.stat().st_size,
        'sha256': digest_file(OUTPUT),
        'archive_entries': len(rows) + 1,
        'payload_files': len(rows), 'inherited_entries': SOURCE_ENTRIES,
        'round4_added_payload_files': len(added),
        'manifest_sha256': digest_file(MANIFEST),
        'replay': 'Extract freshly and run python3 VERIFY_ROUND4.py.',
        'scope_limit': 'Package construction is not proof replay; full theorem remains open.',
    }, indent=2), flush=True)


if __name__ == '__main__':
    main()
