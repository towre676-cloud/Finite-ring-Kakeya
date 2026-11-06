#!/usr/bin/env python3
"""Resumable one-worker production of independently checked compact DRAT cores.

The trimming program is untrusted. Every produced core is checked against
the exact ORIGINAL CNF by DRAT-trim -> LRAT -> pinned CakeML. Original
proofs are read-only provenance and never overwritten. Final manifest
publication is explicit, after the original case inventory stops growing.
"""
import argparse
from contextlib import ExitStack
import json
import os
from pathlib import Path
import shutil
import tempfile
import time

from common import (A, C, CORE_PASS, HERE, MANIFEST, ROOT, SOURCE, V,
                    check_original_row, dump, global_source_hashes,
                    safe_path, source_inventory, validate_existing_core)


def copy_checked(source, target, digest):
    A.require(not target.exists(), 'Refusing to overwrite a published file')
    shutil.copyfile(source, target)
    A.require(A.sha(target) == digest, 'Published copy differs')


def import_pilot(row, original, source_manifest_hash):
    pilot_folder = ROOT / 'research_round7/compact_pilot'
    pilot_path = pilot_folder / 'PILOT_RECEIPT.json'
    if not pilot_path.is_file():
        return None
    pilot = json.loads(pilot_path.read_text())
    if pilot.get('original_case') != str(Path(row['receipt']).parent):
        return None
    A.require(pilot['status'] == 'PASS_CORE_DRAT_VIA_CAKEML', 'Pilot was not accepted')
    A.require(pilot['cnf_sha256'] == row['cnf_sha256']
              and pilot['source_drat_sha256'] == row['proof_sha256'], 'Pilot input binding differs')
    audit = pilot['audit']
    A.require(audit['status'] == 'PASS_CNF_UNSAT_VIA_CAKEML_LRAT'
              and audit['input_sha256'] == {'cnf': row['cnf_sha256'], 'drat': pilot['core_sha256']},
              'Pilot checked different exact bytes')
    A.require(A.sha(pilot_folder / 'core.drat.xz') == pilot['core_storage']['xz_sha256'], 'Pilot compressed core changed')
    A.require(C.logical_sha(pilot_folder / 'core.drat', prefer_compressed=True) == pilot['core_sha256'], 'Pilot decoded core changed')
    destination = HERE / 'cases' / row['case_id']
    destination.mkdir(parents=True)
    copy_checked(pilot_folder / 'core.drat.xz', destination / 'core.drat.xz',
                 pilot['core_storage']['xz_sha256'])
    for path in pilot_folder.glob('*.txt'):
        copy_checked(path, destination / path.name, A.sha(path))
    storage = dict(pilot['core_storage'])
    storage.update(logical_path=str((destination / 'core.drat').relative_to(ROOT)),
                   compressed_path=str((destination / 'core.drat.xz').relative_to(ROOT)))
    result = {
        'status': CORE_PASS, 'case_id': row['case_id'], 'original_case': row,
        'source_manifest_sha256_at_production': source_manifest_hash,
        'method': 'IMPORTED_ALREADY_CHECKED_CORE_PILOT',
        'pilot_receipt': str(pilot_path.relative_to(ROOT)), 'pilot_receipt_sha256': A.sha(pilot_path),
        'cnf_sha256': row['cnf_sha256'], 'original_proof_sha256': row['proof_sha256'],
        'original_raw_bytes': pilot['source_raw_bytes'],
        'original_compressed_bytes': pilot['source_compressed_bytes'],
        'core_sha256': pilot['core_sha256'], 'core_raw_bytes': pilot['core_raw_bytes'],
        'storage': storage, 'audit': audit, 'seconds': pilot['seconds'],
        'producer_sha256': A.sha(Path(__file__).resolve()),
        'original_cnf_used_without_new_axioms': True,
        'original_proof_unchanged': True,
        'portable_replay_requires_original_drat': False,
    }
    dump(destination / 'CORE_RECEIPT.json', result)
    return validate_existing_core(row)


def produce_one(row, source_manifest_hash, binaries, timeout):
    A.require(not row['inherited'] and row['proof_kind'] == 'drat', 'Only new DRAT cases are trimmed')
    original = check_original_row(row)
    destination = HERE / 'cases' / row['case_id']
    if destination.exists():
        return validate_existing_core(row)
    imported = import_pilot(row, original, source_manifest_hash)
    if imported is not None:
        return imported
    start = time.monotonic()
    A.require(shutil.disk_usage('/tmp').free > 3 * 1024**3, 'Temporary disk guard')
    with tempfile.TemporaryDirectory(prefix='kakeya_s13_core_') as name:
        work = Path(name)
        regenerated = work / 'regenerated.cnf'
        regenerated_metadata = V.regenerate_formula(row, regenerated)
        for kind in ('cnf', 'proof'):
            A.require(A.sha(Path(str(safe_path(row[kind])) + '.xz')) == row[kind + '_xz_sha256'],
                      'Original compressed bytes changed before trimming')
        with ExitStack() as stack:
            cnf = stack.enter_context(C.materialized(safe_path(row['cnf']), row['cnf_sha256'], work,
                                                    prefer_compressed=True))
            drat = stack.enter_context(C.materialized(safe_path(row['proof']), row['proof_sha256'], work,
                                                     prefer_compressed=True))
            core = work / 'core.drat'
            trim = A.run_checker([binaries['drat-trim'], cnf, drat, '-l', core], work,
                                 'trim', timeout, 's VERIFIED', False)
            A.require(trim['accepted'] and core.is_file(), 'Trimming failed')
            digest = A.sha(core)
            core_bytes = core.stat().st_size
            audit = A.check_pair(cnf, core, work / 'audit', binaries, timeout, 1024, 256, False)
            A.require(audit['status'] == 'PASS_CNF_UNSAT_VIA_CAKEML_LRAT', 'New core failed mandatory CakeML check')
            A.require(audit['input_sha256'] == {'cnf': row['cnf_sha256'], 'drat': digest},
                      'Core was checked against different exact bytes')
            A.require(A.sha(cnf) == row['cnf_sha256'] and A.sha(drat) == row['proof_sha256'],
                      'Materialized originals changed during core production')
        # Only fully checked immutable output crosses into the checkpoint.
        storage = C.compress_verified(core, digest, preset=3, remove_raw=True)
        destination.mkdir(parents=True)
        copy_checked(Path(str(core) + '.xz'), destination / 'core.drat.xz', storage['xz_sha256'])
        A.require(C.logical_sha(destination / 'core.drat', prefer_compressed=True) == digest,
                  'Published decoded core differs')
        for path in list(work.glob('*.txt')) + list((work / 'audit').glob('*.txt')):
            copy_checked(path, destination / path.name, A.sha(path))
        for kind in ('cnf', 'proof'):
            A.require(A.sha(Path(str(safe_path(row[kind])) + '.xz')) == row[kind + '_xz_sha256'],
                      'Persisted original changed during core production')
        storage.update(logical_path=str((destination / 'core.drat').relative_to(ROOT)),
                       compressed_path=str((destination / 'core.drat.xz').relative_to(ROOT)))
        result = {
            'status': CORE_PASS, 'case_id': row['case_id'], 'original_case': row,
            'source_manifest_sha256_at_production': source_manifest_hash,
            'method': 'DRAT_TRIM_CORE_THEN_FRESH_ORIGINAL_CNF_CAKEML',
            'cnf_sha256': row['cnf_sha256'], 'original_proof_sha256': row['proof_sha256'],
            'original_raw_bytes': original.get('proof_bytes', original.get('drat_bytes')),
            'original_compressed_bytes': Path(str(safe_path(row['proof'])) + '.xz').stat().st_size,
            'core_sha256': digest, 'core_raw_bytes': core_bytes,
            'storage': storage, 'trim': trim, 'audit': audit,
            'regenerated_formula': regenerated_metadata,
            'seconds': round(time.monotonic() - start, 6),
            'producer_sha256': A.sha(Path(__file__).resolve()),
            'original_cnf_used_without_new_axioms': True,
            'original_proof_unchanged': True,
            'portable_replay_requires_original_drat': False,
        }
        dump(destination / 'CORE_RECEIPT.json', result)
    return validate_existing_core(row)


def freeze_final_manifest():
    source, catalogue, source_hash = source_inventory()
    rows = []
    for row in source['cases']:
        check_original_row(row)
        if row['inherited']:
            rows.append({'case_id': row['case_id'], 'representation': 'INHERITED_LRAT',
                         'original_case': row})
            continue
        core = validate_existing_core(row)
        folder = HERE / 'cases' / row['case_id']
        rows.append({'case_id': row['case_id'], 'representation': 'COMPACT_DRAT',
                     'original_case': row,
                     'core_proof': str((folder / 'core.drat').relative_to(ROOT)),
                     'core_sha256': core['core_sha256'],
                     'core_xz_sha256': core['storage']['xz_sha256'],
                     'core_xz_bytes': core['storage']['xz_bytes'],
                     'core_receipt': str((folder / 'CORE_RECEIPT.json').relative_to(ROOT)),
                     'core_receipt_sha256': A.sha(folder / 'CORE_RECEIPT.json')})
    A.require([row['case_id'] for row in rows] == source['case_ids'], 'Incomplete compact inventory')
    snapshot = HERE / 'SOURCE_SUPPORT13_MANIFEST.json'
    if snapshot.exists():
        A.require(A.sha(snapshot) == source_hash, 'A final source snapshot already exists with different bytes')
    else:
        shutil.copyfile(SOURCE, snapshot)
    A.require(A.sha(snapshot) == source_hash == A.sha(SOURCE), 'Final source snapshot changed')
    result = {
        'schema': 'kakeya-compact-support13-v1',
        'status': 'COMPLETE_COMPACT_INVENTORY_PENDING_FRESH_PORTABLE_REPLAY',
        'source_manifest': str(SOURCE.relative_to(ROOT)),
        'source_manifest_snapshot': str(snapshot.relative_to(ROOT)),
        'source_manifest_sha256': source_hash,
        'semantic_and_replay_source_hashes': global_source_hashes(source),
        'original_drat_payloads_required_for_replay': False,
        'original_cnf_payloads_required': True,
        'scope': 'Exactly the original accepted S13 case inventory; compact proofs add no theorem cases.',
        'case_ids': source['case_ids'],
        'cases': rows,
        'inventory_coverage': source['inventory_coverage'],
        'compact_drat_cases': sum(row['representation'] == 'COMPACT_DRAT' for row in rows),
        'inherited_lrat_cases': sum(row['representation'] == 'INHERITED_LRAT' for row in rows),
        'compact_drat_bytes': sum(row.get('core_xz_bytes', 0) for row in rows),
    }
    dump(MANIFEST, result)
    print(json.dumps({key: result[key] for key in ('status', 'compact_drat_cases',
                                                   'inherited_lrat_cases', 'compact_drat_bytes')}),
          flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--take', type=int)
    parser.add_argument('--case', action='append')
    parser.add_argument('--timeout', type=int, default=900)
    parser.add_argument('--freeze-only', action='store_true')
    args = parser.parse_args()
    A.require(args.timeout > 0, 'Positive timeout required')
    if args.freeze_only:
        freeze_final_manifest()
        return
    source, catalogue, source_hash = source_inventory()
    selected = [row for row in source['cases'] if not row['inherited']
                and (args.case is None or row['case_id'] in args.case)]
    if args.case:
        A.require(set(args.case) <= {row['case_id'] for row in selected}, 'Unknown requested case')
    selected.sort(key=lambda row: Path(str(safe_path(row['proof'])) + '.xz').stat().st_size, reverse=True)
    if args.take is not None:
        selected = selected[:args.take]
    receipt_path = HERE / 'CORE_PRODUCTION_PROGRESS.json'
    report = {'status': 'RUNNING', 'source_manifest_sha256_at_start': source_hash,
              'requested_case_ids': [row['case_id'] for row in selected], 'cases': [],
              'one_worker': True, 'originals_unchanged': True}
    dump(receipt_path, report)
    start = time.monotonic()
    try:
        pins = A.verify_sources()
        with tempfile.TemporaryDirectory(prefix='kakeya_s13_core_tools_') as tools:
            binaries, build = A.build_checkers(Path(tools) / 'bin', HERE / 'build_logs')
            report.update(checker_pins=pins, checker_build=build)
            dump(receipt_path, report)
            for row in selected:
                core = produce_one(row, source_hash, binaries, args.timeout)
                summary = {'case_id': row['case_id'], 'status': core['status'],
                           'old_compressed_bytes': core['original_compressed_bytes'],
                           'core_compressed_bytes': core['storage']['xz_bytes'],
                           'production_seconds': core['seconds']}
                report['cases'].append(summary)
                report['seconds'] = round(time.monotonic() - start, 6)
                dump(receipt_path, report)
                print(json.dumps(summary), flush=True)
        report.update(status='PASS_ALL_REQUESTED_CORE_PRODUCTIONS',
                      seconds=round(time.monotonic() - start, 6),
                      final_source_inventory_frozen=False)
        dump(receipt_path, report)
    except Exception as error:
        report.update(status='FAIL', error=repr(error), seconds=round(time.monotonic() - start, 6))
        dump(receipt_path, report)
        raise


if __name__ == '__main__':
    main()
