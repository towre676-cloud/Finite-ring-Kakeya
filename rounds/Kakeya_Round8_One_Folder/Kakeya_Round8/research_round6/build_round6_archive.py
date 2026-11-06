"""Build and verify one ordinary ZIP with one top-level Kakeya_Round6 folder.

The earlier Round5 payload is copied byte-for-byte from its sealed archive.
New proof payloads are selected explicitly: exact CNFs and complete DRAT
refutations, replayed through reconstructed LRAT and the pinned CakeML checker.
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
HERE = ROOT / 'research_round6'
BASE = ROOT / 'Kakeya_Complete_Round5.zip'
BASE_SHA = 'b5b11afa1b59574f9521f2c959606ba7dc1552ce1f5e99b78b2a71f1084336da'
OUTPUT = ROOT / 'Kakeya_Round6_One_Folder.zip'
PREFIX = 'Kakeya_Round6/'


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text())


def new_files():
    selected = {str(p.relative_to(ROOT)): p for p in
                [ROOT / 'README_Round6.txt', ROOT / 'VERIFY_ROUND6.py',
                 ROOT / 'Kakeya_Research_Frontier_Round6.json']}
    ignored = {'__pycache__', 'bin', 'replay_bin', 'pilot_s11', 'pilot_s11_m2_18',
               'direct_lrat_pilot', 'compression_pilot'}
    ordinary = {'.py', '.cpp', '.md', '.txt', '.json', '.jsonl', '.csv', '.log', '.pdf'}
    for path in HERE.rglob('*'):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if any(part in ignored or part.startswith('.') for part in relative.parts):
            continue
        if path.suffix in ordinary:
            selected[str(relative)] = path
    # The supplied archive is a preserved input, not another user download.
    path = HERE / 'input/Claude_Round4_Handoff.zip'
    selected[str(path.relative_to(ROOT))] = path
    # Maximum19: original exact DRAT proofs and formulas, both losslessly XZ.
    m19 = read(HERE / 'certification/M19_CERTIFICATE_MANIFEST.json')
    require(len(m19['cases']) == 38, 'Wrong maximum19 certificate count')
    compact_m19 = read(HERE / 'compact_m19/COMPACT_M19_MANIFEST.json')
    require(compact_m19['representation'] == 'ORIGINAL_CNF_AND_DRAT_ONLY'
            and compact_m19['original_manifest_sha256'] == sha(HERE / 'certification/M19_CERTIFICATE_MANIFEST.json')
            and {r['case_id'] for r in compact_m19['cases']} == {r['case_id'] for r in m19['cases']},
            'Maximum19 compact representation differs from the accepted inventory')
    for row in m19['cases']:
        for key in ['cnf', 'proof']:
            path = HERE / 'certification' / (row[key] + '.xz')
            require(path.is_file(), 'Missing compressed maximum19 payload: ' + str(path))
            selected[str(path.relative_to(ROOT))] = path
    # Joint domains: original exact CNF bytes and complete compact DRAT proofs.
    joint = read(HERE / 'joint_maxima/JOINT_CERTIFICATE_MANIFEST.json')
    require(joint['status'] == 'PASS_COMPLETE_38_CASE_INVENTORY_AND_ACCEPTED_FILE_HASHES', 'Incomplete joint collection')
    for row in joint['cases']:
        path = HERE / 'joint_maxima' / row['cnf']
        require(path.is_file() and sha(path) == row['cnf_sha256'], 'Changed joint formula')
        selected[str(path.relative_to(ROOT))] = path
    compact = read(HERE / 'compact_certificates/COMPACT_CERTIFICATE_MANIFEST.json')
    require(compact['status'] == 'PASS_COMPLETE_38_COMPACT_DRAT_CERTIFICATES'
            and compact['schema'] == 'kakeya-compact-drat-v1' and len(compact['cases']) == 38,
            'Complete accepted joint compact collection is required')
    require({r['case_id'] for r in compact['cases']} == {r['case_id'] for r in joint['cases']},
            'Compact/joint inventory mismatch')
    for row in compact['cases']:
        expected_proof = 'cases/' + row['case_id'] + '/proof.drat.xz'
        require(row['proof'] == expected_proof, 'Unexpected compact certificate path')
        path = HERE / 'compact_certificates' / row['proof']
        require(path.is_file() and path.stat().st_size == row['compressed_bytes']
                and sha(path) == row['compressed_sha256'], 'Changed compressed DRAT proof')
        selected[str(path.relative_to(ROOT))] = path
    # Preserve exactly the completed support13 diagnostic payload list.
    trial_manifest = HERE / 'strengthened_trials/STRENGTHENED_TRIAL_FILES.json'
    trials = read(trial_manifest)
    for row in trials['files']:
        path = HERE / 'strengthened_trials' / row['path']
        require(path.is_file(), 'Missing completed diagnostic payload')
        # A procedural replay can update timing/log receipts. Preserve the
        # actual current package bytes, while theorem inputs retain their own
        # independently checked, immutable semantic hashes.
        row.update(bytes=path.stat().st_size, sha256=sha(path))
        selected[str(path.relative_to(ROOT))] = path
    trial_manifest.write_text(json.dumps(trials, indent=2) + '\n')
    selected[str(trial_manifest.relative_to(ROOT))] = trial_manifest
    require(len((HERE / 'Kakeya_Round6_Monograph.txt').read_text().split()) == 1500,
            'Monograph must contain exactly1500 whitespace words')
    require((HERE / 'Kakeya_Round6_Monograph.pdf').is_file(),
            'The formatted monograph PDF must be complete before packaging')
    pdf_qa = read(HERE / 'MONOGRAPH_PDF_QA.json')
    require(pdf_qa['status'] == 'PASS_FINAL_PDF_VISUAL_AND_TEXT_QA'
            and pdf_qa['source_whitespace_words'] == pdf_qa['pdf_body_whitespace_words'] == 1500
            and sha(HERE / pdf_qa['source']) == pdf_qa['source_sha256']
            and sha(HERE / pdf_qa['pdf']) == pdf_qa['pdf_sha256'],
            'Monograph source/PDF differs from its completed visual and text checks')
    return selected


def main():
    require(sha(BASE) == BASE_SHA, 'Earlier complete Round5 archive changed')
    replay = read(HERE / 'ROUND6_PORTABLE_REPLAY.json')
    require(replay['status'] == 'PASS_ALL_ROUND6_FINITE_AND_CERTIFICATE_REPLAYS'
            and replay['full_main_certificate_replay'], 'Full portable replay has not passed')
    selected = new_files()
    rows = []
    base_names = []
    with zipfile.ZipFile(BASE) as baseline:
        for item in baseline.infolist():
            if item.is_dir():
                continue
            name = PurePosixPath(item.filename)
            require(not name.is_absolute() and '..' not in name.parts, 'Unsafe base path')
            require(str(name) not in selected, 'New file would overwrite a preserved earlier payload')
            data = baseline.read(item)
            rows.append({'path': str(name), 'bytes': len(data),
                         'sha256': hashlib.sha256(data).hexdigest(), 'source': 'unchanged_Round5'})
            base_names.append(str(name))
    for name, path in sorted(selected.items()):
        rows.append({'path': name, 'bytes': path.stat().st_size,
                     'sha256': sha(path), 'source': 'Round6'})
    require(len(rows) == len({r['path'] for r in rows}), 'Duplicate archive payload')
    manifest = {'schema': 'kakeya-complete-round6-archive-v1',
                'top_level_folder': 'Kakeya_Round6', 'payload_files': len(rows),
                'preserved_Round5_payload_files': len(base_names),
                'source_Round5_archive_sha256': BASE_SHA,
                'source_Claude_archive_sha256': read(HERE / 'input/SOURCE_ARCHIVE_RECEIPT.json')['source_archive_sha256'],
                'main_CNF_refutations': 76, 'additional_S13_CNF_refutations': 2,
                'monograph_word_count': 1500,
                'proof_storage': 'All76 main exact CNFs and complete DRAT refutations, with mandatory reconstructed-LRAT CakeML replay; both S13 diagnostics retain accepted LRAT. Standard XZ for large proof payloads.',
                'omitted_intermediates': 'Larger intermediate LRAT streams and superseded joint proof-core streams; hashes/provenance retained.',
                'files': rows}
    manifest_path = ROOT / 'MANIFEST_ROUND6.json'
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    with tempfile.TemporaryDirectory(prefix='kakeya_round6_zip_') as temporary:
        staged = Path(temporary) / OUTPUT.name
        with zipfile.ZipFile(staged, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
            archive.writestr(PREFIX, b'')
            with zipfile.ZipFile(BASE) as baseline:
                for name in base_names:
                    archive.writestr(PREFIX + name, baseline.read(name))
            for name, path in sorted(selected.items()):
                compression = zipfile.ZIP_STORED if path.suffix in ('.xz', '.zip') else zipfile.ZIP_DEFLATED
                archive.write(path, PREFIX + name, compress_type=compression)
            archive.write(manifest_path, PREFIX + 'MANIFEST_ROUND6.json')
        # Verify every payload and the sole root folder from the finished ZIP.
        expected = {r['path']: r for r in rows}
        with zipfile.ZipFile(staged) as archive:
            names = archive.namelist()
            require({n.split('/')[0] for n in names} == {'Kakeya_Round6'}, 'More than one extraction root')
            payload_names = {n[len(PREFIX):] for n in names if n != PREFIX and n != PREFIX + 'MANIFEST_ROUND6.json'}
            require(payload_names == set(expected), 'Archive inventory mismatch')
            for name, row in expected.items():
                digest = hashlib.sha256()
                total = 0
                with archive.open(PREFIX + name) as stream:
                    for block in iter(lambda: stream.read(1024 * 1024), b''):
                        total += len(block)
                        digest.update(block)
                require(total == row['bytes'] and digest.hexdigest() == row['sha256'], 'Archived payload changed: ' + name)
            require(json.loads(archive.read(PREFIX + 'MANIFEST_ROUND6.json')) == manifest, 'Archived manifest changed')
        digest = sha(staged)
        try:
            os.replace(staged, OUTPUT)
        except OSError as error:
            if error.errno != errno.EXDEV:
                raise
            publication = OUTPUT.with_suffix('.zip.publishing')
            shutil.copyfile(staged, publication)
            require(sha(publication) == digest, 'Completed archive copy changed')
            publication.replace(OUTPUT)
        require(sha(OUTPUT) == digest, 'Published archive differs')
    receipt = {'status': 'PASS_COMPLETE_SINGLE_FOLDER_ROUND6_ARCHIVE',
               'path': str(OUTPUT), 'bytes': OUTPUT.stat().st_size, 'sha256': digest,
               'payload_files': len(rows), 'zip_entries': len(rows) + 2,
               'preserved_Round5_files': len(base_names), 'all_payload_hashes_verified': True,
               'sole_extraction_root': 'Kakeya_Round6/', 'monograph_words': 1500}
    (ROOT / 'Kakeya_Round6_Archive_Receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2), flush=True)


if __name__ == '__main__':
    main()
