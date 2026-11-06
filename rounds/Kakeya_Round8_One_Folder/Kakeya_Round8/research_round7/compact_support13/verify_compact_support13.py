#!/usr/bin/env python3
"""Portable original-CNF replay using compact support13 proofs only.

No original Round7 DRAT is opened or required. Exact original CNFs are
regenerated, compact proofs are decoded and hashed, DRAT-trim rebuilds
LRAT in private temporary storage, and pinned CakeML must accept. The
one inherited Round6 LRAT remains in the base checkpoint and is checked.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import ExitStack
import json
from pathlib import Path
import shutil
import tempfile
import time

from common import (A, C, CORE_PASS, HERE, MANIFEST, ROOT, SOURCE, V,
                    check_original_row, dump, global_source_hashes,
                    safe_path, source_inventory, validate_existing_core)


def load_compact_inventory():
    compact = json.loads(MANIFEST.read_text())
    A.require(compact['schema'] == 'kakeya-compact-support13-v1', 'Wrong compact schema')
    A.require(compact['original_drat_payloads_required_for_replay'] is False,
              'Unexpected original-proof dependency')
    source, catalogue, digest = source_inventory()
    A.require(compact['source_manifest'] == str(SOURCE.relative_to(ROOT))
              and compact['source_manifest_sha256'] == digest, 'Final original inventory changed')
    snapshot = safe_path(compact['source_manifest_snapshot'])
    A.require(A.sha(snapshot) == digest and json.loads(snapshot.read_text()) == source,
              'Frozen source snapshot differs')
    A.require(compact['semantic_and_replay_source_hashes'] == global_source_hashes(source),
              'A semantic/replay source changed')
    rows = compact['cases']
    A.require(compact['case_ids'] == source['case_ids']
              == [row['case_id'] for row in rows], 'Compact collection is incomplete or reordered')
    A.require(len(rows) == len({row['case_id'] for row in rows}), 'Duplicate compact case')
    for row, original in zip(rows, source['cases']):
        A.require(row['original_case'] == original, 'Compact mathematical scope differs from source case')
        check_original_row(original)
        cnf = safe_path(original['cnf'])
        A.require(A.sha(Path(str(cnf) + '.xz')) == original['cnf_xz_sha256'],
                  'Original exact compressed CNF changed')
        if original['inherited']:
            A.require(row['representation'] == 'INHERITED_LRAT' and original['proof_kind'] == 'lrat',
                      'Inherited representation differs')
            A.require(A.sha(Path(str(safe_path(original['proof'])) + '.xz')) == original['proof_xz_sha256'],
                      'Inherited LRAT changed')
        else:
            A.require(row['representation'] == 'COMPACT_DRAT' and original['proof_kind'] == 'drat',
                      'Expected a compact replacement DRAT')
            receipt = safe_path(row['core_receipt'])
            A.require(A.sha(receipt) == row['core_receipt_sha256'], 'Compact production receipt changed')
            produced = validate_existing_core(original)
            A.require(produced['core_sha256'] == row['core_sha256']
                      and produced['storage']['xz_sha256'] == row['core_xz_sha256'],
                      'Compact proof binding differs')
            expected = HERE / 'cases' / row['case_id'] / 'core.drat'
            A.require(safe_path(row['core_proof']) == expected, 'Unexpected compact proof path')
            A.require(A.sha(Path(str(expected) + '.xz')) == row['core_xz_sha256'], 'Compressed core changed')
    A.require(compact['inventory_coverage'] == source['inventory_coverage']
              == V.coverage(source['cases'], catalogue), 'Coverage arithmetic differs')
    return compact, source, catalogue


def replay_one(row, binaries, temporary_root, timeout):
    start = time.monotonic()
    original = row['original_case']
    result = {'case_id': row['case_id'], 'status': 'RUNNING',
              'nonzero_support_mask': original['nonzero_support_mask'],
              'maximum_interval': original['maximum_interval'],
              'representation': row['representation'],
              'original_round7_drat_read': False}
    logs = HERE / 'replay_logs' / row['case_id']
    logs.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix='case_', dir=temporary_root) as name:
            work = Path(name)
            result['formula_regeneration'] = V.regenerate_formula(original, work / 'regenerated.cnf')
            if row['representation'] == 'COMPACT_DRAT':
                proof_path, proof_hash = safe_path(row['core_proof']), row['core_sha256']
            else:
                proof_path, proof_hash = safe_path(original['proof']), original['proof_sha256']
            with ExitStack() as stack:
                cnf = stack.enter_context(C.materialized(safe_path(original['cnf']), original['cnf_sha256'],
                                                        work, prefer_compressed=True))
                proof = stack.enter_context(C.materialized(proof_path, proof_hash, work,
                                                          prefer_compressed=True))
                if row['representation'] == 'COMPACT_DRAT':
                    audit = A.check_pair(cnf, proof, work / 'audit', binaries, timeout, 1024, 256, False)
                    A.require(audit['status'] == 'PASS_CNF_UNSAT_VIA_CAKEML_LRAT', 'Compact proof rejected')
                    A.require(audit['input_sha256'] == {'cnf': original['cnf_sha256'], 'drat': proof_hash},
                              'Checker used different exact inputs')
                else:
                    (work / 'audit').mkdir()
                    audit = A.run_checker([binaries['cake_lpr'], '--CML_HEAP_SIZE=1024', '--CML_STACK_SIZE=256',
                                           cnf, proof], work / 'audit', 'cake_lpr', timeout,
                                          's VERIFIED UNSAT', True)
                    A.require(audit['accepted'], 'Inherited LRAT rejected')
                A.require(A.sha(cnf) == original['cnf_sha256'] and A.sha(proof) == proof_hash,
                          'Materialized certificate changed during checking')
                for path in (work / 'audit').glob('*.txt'):
                    shutil.copyfile(path, logs / path.name)
                A.require(C.logical_sha(safe_path(original['cnf']), prefer_compressed=True) == original['cnf_sha256'],
                          'Persisted original CNF changed during checking')
                A.require(C.logical_sha(proof_path, prefer_compressed=True) == proof_hash,
                          'Persisted replacement proof changed during checking')
                result.update(status='PASS_EXACT_ORIGINAL_CNF_AND_PORTABLE_CAKEML_PROOF',
                              cnf_sha256=original['cnf_sha256'], checked_proof_sha256=proof_hash,
                              audit=audit)
    except Exception as error:
        result.update(status='FAIL', error=repr(error))
    result['seconds'] = round(time.monotonic() - start, 6)
    dump(logs / 'CORE_REPLAY.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quick', action='store_true')
    parser.add_argument('--timeout', type=int, default=900)
    parser.add_argument('--jobs', type=int, choices=(1, 2), default=1)
    args = parser.parse_args()
    A.require(args.timeout > 0, 'Positive checker timeout required')
    output = HERE / ('COMPACT_SUPPORT13_QUICK_REPLAY.json' if args.quick else 'COMPACT_SUPPORT13_REPLAY.json')
    start = time.monotonic()
    receipt = {'status': 'RUNNING', 'quick': args.quick, 'jobs': args.jobs, 'cases': [],
               'original_round7_drat_required': False, 'original_round7_drat_read': False,
               'full_original_inventory_replayed': False}
    dump(output, receipt)
    try:
        compact, source, catalogue = load_compact_inventory()
        rows = compact['cases']
        if args.quick:
            selected = []
            for representation, variant in [('INHERITED_LRAT', False), ('COMPACT_DRAT', False),
                                            ('COMPACT_DRAT', True)]:
                match = next((row for row in rows if row['representation'] == representation
                              and bool(row['original_case'].get('encoder_kind')) == variant), None)
                if match is not None and match not in selected:
                    selected.append(match)
            rows = selected
        receipt.update(compact_manifest_sha256=A.sha(MANIFEST),
                       source_manifest_sha256=compact['source_manifest_sha256'],
                       expected_case_ids=compact['case_ids'],
                       requested_case_ids=[row['case_id'] for row in rows],
                       checker_pins=A.verify_sources(),
                       source_inventory_coverage=compact['inventory_coverage'])
        with tempfile.TemporaryDirectory(prefix='kakeya_s13_portable_') as name:
            temporary = Path(name)
            binaries, build = A.build_checkers(temporary / 'bin', HERE / 'replay_build_logs')
            receipt['checker_build'] = build
            dump(output, receipt)
            with ProcessPoolExecutor(args.jobs) as pool:
                futures = [pool.submit(replay_one, row, binaries, temporary, args.timeout)
                           for row in rows]
                for future in as_completed(futures):
                    result = future.result()
                    receipt['cases'].append(result)
                    receipt['seconds'] = round(time.monotonic() - start, 6)
                    dump(output, receipt)
                    print(f"[{len(receipt['cases'])}/{len(rows)}] {result['case_id']}: {result['status']} "
                          f"({result['seconds']:.1f}s)", flush=True)
        A.require(len(receipt['cases']) == len(rows)
                  and all(row['status'] == 'PASS_EXACT_ORIGINAL_CNF_AND_PORTABLE_CAKEML_PROOF'
                          for row in receipt['cases']), 'One or more portable proofs failed')
        # Repeat only the small binding/coverage checks; no old DRAT is read.
        fresh_source, fresh_catalogue, fresh_digest = source_inventory()
        A.require(fresh_digest == compact['source_manifest_sha256']
                  and global_source_hashes(fresh_source) == compact['semantic_and_replay_source_hashes'],
                  'Source inventory changed during replay')
        if not args.quick:
            A.require({row['case_id'] for row in receipt['cases']} == set(compact['case_ids']),
                      'Final original proof inventory is incomplete')
            receipt['certified_inventory_coverage'] = V.coverage(fresh_source['cases'], fresh_catalogue)
        receipt.update(status='PASS_QUICK_COMPACT_SUPPORT13_SAMPLE_ONLY' if args.quick else
                       'PASS_ALL_ORIGINAL_SUPPORT13_CASES_VIA_COMPACT_CAKEML_PROOFS',
                       full_original_inventory_replayed=not args.quick,
                       checked_cases=len(rows), seconds=round(time.monotonic() - start, 6))
        dump(output, receipt)
        print(receipt['status'], flush=True)
    except Exception as error:
        receipt.update(status='FAIL', error=repr(error), seconds=round(time.monotonic() - start, 6))
        dump(output, receipt)
        raise


if __name__ == '__main__':
    main()
