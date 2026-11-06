#!/usr/bin/env python3
"""Run one half of an explicit immutable two-worker compact-proof partition."""
import argparse
import json
from pathlib import Path
import tempfile
import time

import produce_cores as P
from common import A, HERE, ROOT, check_original_row, dump, safe_path, source_inventory, validate_existing_core


def make_split(path):
    A.require(not path.exists(), 'A worker split is immutable; choose a new filename')
    source, catalogue, digest = source_inventory()
    pending, finished = [], []
    for row in source['cases']:
        if row['inherited']:
            continue
        folder = HERE / 'cases' / row['case_id']
        if folder.exists():
            validate_existing_core(row)
            finished.append(row['case_id'])
        else:
            pending.append(row)
    pending.sort(key=lambda row: Path(str(safe_path(row['proof'])) + '.xz').stat().st_size, reverse=True)
    workers = {'0': [], '1': []}
    bytes_by_worker = {'0': 0, '1': 0}
    for row in pending:
        worker = min(bytes_by_worker, key=lambda key: (bytes_by_worker[key], key))
        workers[worker].append(row['case_id'])
        bytes_by_worker[worker] += Path(str(safe_path(row['proof'])) + '.xz').stat().st_size
    flat = workers['0'] + workers['1']
    A.require(len(flat) == len(set(flat)) == len(pending), 'Worker assignment overlaps or omits a case')
    split = {'status': 'FROZEN_DISJOINT_TWO_WORKER_SPLIT', 'source_manifest_sha256': digest,
             'workers': workers, 'estimated_original_compressed_bytes': bytes_by_worker,
             'source_rows': {row['case_id']: row for row in pending},
             'already_completed_case_ids': finished}
    dump(path, split)
    print(json.dumps({'workers': {key: len(values) for key, values in workers.items()},
                      'estimated_bytes': bytes_by_worker, 'already_completed': len(finished)}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--split', required=True)
    parser.add_argument('--make-split', action='store_true')
    parser.add_argument('--worker', choices=('0', '1'))
    parser.add_argument('--timeout', type=int, default=900)
    args = parser.parse_args()
    path = Path(args.split).resolve()
    A.require(path.is_relative_to(HERE), 'Split must belong to compact checkpoint')
    if args.make_split:
        make_split(path)
        return
    A.require(args.worker is not None and args.timeout > 0, 'Choose a worker and positive timeout')
    split = json.loads(path.read_text())
    A.require(split['status'] == 'FROZEN_DISJOINT_TWO_WORKER_SPLIT', 'Wrong split schema')
    source, catalogue, source_hash = source_inventory()
    available = {row['case_id']: row for row in source['cases']}
    all_ids = split['workers']['0'] + split['workers']['1']
    A.require(len(all_ids) == len(set(all_ids)), 'Worker partitions overlap')
    for case_id in all_ids:
        A.require(available.get(case_id) == split['source_rows'][case_id], 'A frozen original case changed')
    selected = split['workers'][args.worker]
    progress = HERE / f"{path.stem}_WORKER_{args.worker}_PROGRESS.json"
    report = {'status': 'RUNNING', 'worker': args.worker, 'split_sha256': A.sha(path),
              'requested_case_ids': selected, 'cases': [], 'producer_sha256': A.sha(P.__file__),
              'worker_source_sha256': A.sha(Path(__file__).resolve()),
              'worker_partition_disjoint': True}
    dump(progress, report)
    start = time.monotonic()
    try:
        with tempfile.TemporaryDirectory(prefix=f'kakeya_s13_core_worker{args.worker}_') as name:
            binaries, build = A.build_checkers(Path(name) / 'bin',
                                               HERE / f'worker_{args.worker}_build_logs')
            report.update(checker_pins=A.verify_sources(), checker_build=build)
            dump(progress, report)
            for case_id in selected:
                row = available[case_id]
                core = P.produce_one(row, source_hash, binaries, args.timeout)
                summary = {'case_id': case_id, 'status': core['status'],
                           'old_compressed_bytes': core['original_compressed_bytes'],
                           'core_compressed_bytes': core['storage']['xz_bytes'],
                           'production_seconds': core['seconds']}
                report['cases'].append(summary)
                report['seconds'] = round(time.monotonic() - start, 6)
                dump(progress, report)
                print(json.dumps(summary), flush=True)
        report.update(status='PASS_ALL_DISJOINT_WORKER_CORES',
                      seconds=round(time.monotonic() - start, 6))
        dump(progress, report)
    except BaseException as error:
        report.update(status='FAIL_OR_INTERRUPTED', error=repr(error),
                      seconds=round(time.monotonic() - start, 6))
        dump(progress, report)
        raise


if __name__ == '__main__':
    main()
