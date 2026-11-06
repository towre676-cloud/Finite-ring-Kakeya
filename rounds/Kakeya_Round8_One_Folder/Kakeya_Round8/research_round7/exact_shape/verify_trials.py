#!/usr/bin/env python3
"""Regenerate every bounded exact-shape trial and recheck completed proofs."""
import gc
import json
from pathlib import Path
import re
import shutil
import tempfile
import time

from produce_trials import A, C, ACCEPTED, HERE, QUEUE, ROOT, dump, source_hashes
from encode_exact_shape import encode_support, write_dimacs


def main():
    output = HERE / 'EXACT_SHAPE_CERTIFICATE_REPLAY.json'
    start = time.monotonic()
    receipt = {'status': 'RUNNING', 'cases': [], 'accepted_proofs': 0,
               'whole_support_exclusions_inferred': False}
    dump(output, receipt)
    try:
        queue = {row['nonzero_support_mask']: row for row in json.loads(QUEUE.read_text())['cases']}
        rows = []
        reports = sorted(HERE.glob('*_TRIALS.json'))
        A.require(bool(reports), 'No bounded trial reports are present')
        declared_ids = []
        for report_path in reports:
            report = json.loads(report_path.read_text())
            A.require(report['status'] == 'COMPLETED_BOUNDED_EXACT_SHAPE_TRIALS', 'A producer is still running or incomplete')
            for row in report['cases']:
                declared_ids.append(row['case_id'])
                saved = json.loads((HERE / 'cases' / row['case_id'] / 'CASE_RECEIPT.json').read_text())
                A.require(row == saved, 'Producer report and immutable case receipt differ')
                rows.append(row)
        A.require(len(declared_ids) == len(set(declared_ids)), 'Duplicate case identifiers')
        actual_ids = {p.parent.name for p in (HERE / 'cases').glob('*/CASE_RECEIPT.json')}
        A.require(actual_ids == set(declared_ids), 'Trial inventory is incomplete')
        expected_pins = source_hashes()
        for row in rows:
            A.require(re.fullmatch(r'[A-Za-z0-9_]+', row['case_id']) is not None, 'Unsafe case id')
            A.require(row['semantic_input_hashes'] == expected_pins, 'Producer source/input pin changed')
            A.require(row['support'] == queue[row['nonzero_support_mask']]['support'], 'Support differs from complete catalogue')
            A.require(row['total_upper_bound'] == 93 and row['distinguished_hub'] == 0, 'Scope changed')
            lower, upper = row['maximum_interval']
            A.require(2 <= lower <= upper <= 18, 'Wrong interval')
            A.require(row['spectrum_census_used'] is False, 'Unexpected census dependency')
        checker_pins = A.verify_sources()
        with tempfile.TemporaryDirectory(prefix='kakeya_exact_shape_replay_') as name:
            temp = Path(name)
            binaries, build = A.build_checkers(temp / 'bin', HERE / 'replay_build_logs')
            receipt.update(checker_pins=checker_pins, checker_build=build,
                           producer_source_hashes=expected_pins,
                           expected_case_ids=declared_ids)
            dump(output, receipt)
            for row in rows:
                case_start = time.monotonic()
                destination = HERE / 'cases' / row['case_id']
                work = temp / row['case_id']
                work.mkdir()
                lower, upper = row['maximum_interval']
                formula = encode_support(row['support'], upper, hub_min=lower, total=93)
                # JSON stringifies integer direction keys in the saved map.
                regenerated_metadata = json.loads(json.dumps(formula.exact_shape_metadata))
                A.require(regenerated_metadata == row['formula'], 'Regenerated formula metadata differs')
                regenerated = work / 'regenerated.cnf'
                write_dimacs(formula, regenerated)
                del formula
                gc.collect()
                A.require(A.sha(regenerated) == row['cnf_sha256'], 'Exact CNF regeneration mismatch')
                for logical_name, metadata in row['storage'].items():
                    stored = destination / (logical_name + '.xz')
                    A.require(A.sha(stored) == metadata['xz_sha256'], 'Compressed stored file changed')
                with C.materialized(destination / 'input.cnf', row['cnf_sha256'], work,
                                    prefer_compressed=True) as cnf:
                    result = {'case_id': row['case_id'], 'support': row['support'],
                              'maximum_interval': row['maximum_interval'],
                              'cnf_regeneration': 'BYTE_IDENTICAL',
                              'producer_status': row['status']}
                    if row['status'] == ACCEPTED:
                        with C.materialized(destination / 'proof.drat', row['drat_sha256'], work,
                                            prefer_compressed=True) as drat:
                            audit = A.check_pair(cnf, drat, work / 'audit', binaries, 900, 1024, 256, False)
                            A.require(audit['status'] == 'PASS_CNF_UNSAT_VIA_CAKEML_LRAT', 'CakeML did not accept')
                            A.require(audit['input_sha256'] == {'cnf': row['cnf_sha256'], 'drat': row['drat_sha256']},
                                      'Checker inputs differ from frozen hashes')
                            result.update(status='PASS_FRESH_EXACT_SHAPE_CAKEML_REPLAY', proof_check=audit)
                            receipt['accepted_proofs'] += 1
                    else:
                        A.require('proof.drat' not in row['storage'], 'Unaccepted trace was incorrectly published as certificate')
                        result.update(status='PASS_REGENERATION_ONLY_NO_EXCLUSION', exclusion_credited=False)
                A.require(C.logical_sha(destination / 'input.cnf', prefer_compressed=True) == row['cnf_sha256'],
                          'Persisted CNF changed during replay')
                if row['status'] == ACCEPTED:
                    A.require(C.logical_sha(destination / 'proof.drat', prefer_compressed=True) == row['drat_sha256'],
                              'Persisted DRAT changed during replay')
                log_path = HERE / 'replay_logs' / row['case_id']
                log_path.mkdir(parents=True, exist_ok=True)
                for path in (work / 'audit').glob('*.txt'):
                    shutil.copyfile(path, log_path / path.name)
                result['seconds'] = round(time.monotonic() - case_start, 6)
                dump(log_path / 'CASE_REPLAY.json', result)
                receipt['cases'].append(result)
                dump(output, receipt)
                print(row['case_id'], result['status'], flush=True)
                shutil.rmtree(work)
        A.require(source_hashes() == expected_pins, 'Source changed during replay')
        receipt.update(status='PASS_ALL_EXACT_SHAPE_TRIAL_REGENERATIONS_AND_COMPLETED_PROOFS',
                       checked_cases=len(rows),
                       uncertified_cases=sum(row['status'] != ACCEPTED for row in rows),
                       seconds=round(time.monotonic() - start, 6))
        dump(output, receipt)
        print(json.dumps({k: receipt[k] for k in ('status', 'checked_cases', 'accepted_proofs',
                                                'uncertified_cases', 'seconds')}, indent=2))
    except Exception as error:
        receipt.update(status='FAIL', error=repr(error), seconds=round(time.monotonic() - start, 6))
        dump(output, receipt)
        raise


if __name__ == '__main__':
    main()
