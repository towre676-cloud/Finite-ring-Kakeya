"""Replay the complete joint-maximum exclusions without new SAT search.

Requires Python3, gcc, Linux x86_64. Proofs may be plain or losslessly stored
as sibling .xz files; only one case is materialized at a time. Every declared
support and maximum interval is bound to a deterministic CNF regeneration.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
IMPORTED = HERE.parent / 'imported_claude_round4'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


A = module('joint_replay_audit', ROOT / 'research_round5/proof_audit/audit_certificates.py')
E = module('joint_replay_encoder', HERE / 'encode_joint_maxima.py')
C = module('joint_certificate_storage', HERE.parent / 'certificate_storage.py')
M = module('joint_support_mapper', ROOT / 'research_round5/encoding_bridge/map_marked_case.py')


def universe():
    source = json.loads((HERE.parent / 'catalogue_audit/CLAUDE_TO_ROUND5_38_CASE_MAP.json').read_text())
    rows = source['cases']
    expected = json.loads((ROOT / 'research_round5/encoding_bridge/M19_MARKED_CASE_CONTRACT.json').read_text())['cases']
    expected_ids = {r['case_id'] for r in expected}
    if len(rows) != 38 or {r['case_id'] for r in rows} != expected_ids:
        raise ValueError('Incomplete geometric 13+25 support universe')
    for row in rows:
        actual = M.map_marked_support(row['source_support'], 0)
        if actual['case_id'] != row['case_id'] or actual['affine_map_to_contract'] != row['affine_map_to_contract']:
            raise ValueError('Incorrect explicit support transport')
    return rows


def finalize():
    """Freeze a complete manifest only after all exact-byte gates pass."""
    records = []
    provenance = {str(p.relative_to(ROOT)): A.sha(p) for p in
                  [HERE / 'encode_joint_maxima.py', IMPORTED / 'data/spec32.csv',
                   IMPORTED / 'data/Mtable.txt',
                   HERE.parent / 'catalogue_audit/CLAUDE_TO_ROUND5_38_CASE_MAP.json']}
    for row in universe():
        cid = 'm2_18_' + row['case_id']
        folder = HERE / 'cases' / cid
        receipt = json.loads((folder / 'CASE_RECEIPT.json').read_text())
        A.require(receipt['status'] == 'PASS_CNF_UNSAT_VIA_CAKEML_LRAT', 'Unaccepted case: ' + cid)
        A.require(receipt['maximum_interval'] == [2, 18], 'Wrong joint maximum interval')
        A.require(receipt['semantic_input_hashes'] == provenance, 'Encoder/data changed after certification')
        A.require(receipt['marked_support']['support'] == row['source_support'], 'Wrong support')
        A.require(receipt['marked_support']['distinguished_hub'] == 0, 'Wrong marked hub')
        A.require(receipt['marked_support']['affine_map_to_contract'] == row['affine_map_to_contract'], 'Wrong transport')
        for name, digest in [('input.cnf', receipt['cnf_sha256']), ('proof.lrat', receipt['lrat_sha256'])]:
            A.require(C.logical_sha(folder / name) == digest, 'Certificate bytes changed: ' + cid + '/' + name)
        check = receipt['cake_lpr']
        A.require(check['accepted'], 'No authoritative acceptance')
        A.require(A.sha(folder / check['stdout_file']) == check['stdout_sha256'], 'Acceptance log changed')
        A.require(A.sha(folder / check['stderr_file']) == check['stderr_sha256'], 'Error log changed')
        A.require((folder / check['stdout_file']).read_bytes().strip() == b's VERIFIED UNSAT', 'Wrong acceptance marker')
        A.require((folder / check['stderr_file']).stat().st_size == 0, 'Checker stderr is not empty')
        records.append({'case_id': cid, 'geometric_case_id': row['case_id'],
                        'support_size': row['support_size'], 'maximum_interval': [2, 18],
                        'total_upper_bound': 93, 'marked_support': receipt['marked_support'],
                        'cnf': str((folder / 'input.cnf').relative_to(HERE)),
                        'cnf_sha256': receipt['cnf_sha256'],
                        'lrat': str((folder / 'proof.lrat').relative_to(HERE)),
                        'lrat_sha256': receipt['lrat_sha256'],
                        'case_receipt_sha256': A.sha(folder / 'CASE_RECEIPT.json')})
    manifest = {'schema': 'kakeya-joint-maximum-certificate-v1',
                'status': 'PASS_COMPLETE_38_CASE_INVENTORY_AND_ACCEPTED_FILE_HASHES',
                'maximum_interval': [2, 18], 'total_upper_bound': 93,
                'ring_scope': 'common_necessary_relaxation_both_rings',
                'support_counts': {'11': 13, '12': 25},
                'expected_case_ids': sorted(r['case_id'] for r in records),
                'semantic_input_hashes': provenance, 'cases': records,
                'logical_file_storage': 'Plain path or exactly equivalent sibling PATH.xz',
                'encoder_formally_verified': False}
    A.dump(HERE / 'JOINT_CERTIFICATE_MANIFEST.json', manifest)
    print('PASS_COMPLETE_38_CASE_INVENTORY_AND_ACCEPTED_FILE_HASHES', flush=True)
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--finalize', action='store_true')
    parser.add_argument('--inventory-only', action='store_true')
    parser.add_argument('--quick', action='store_true')
    parser.add_argument('--prefer-compressed', action='store_true')
    parser.add_argument('--timeout', type=int, default=1200)
    parser.add_argument('--heap-mb', type=int, default=1024)
    args = parser.parse_args()
    if args.finalize:
        finalize()
        if args.inventory_only:
            return
    manifest = json.loads((HERE / 'JOINT_CERTIFICATE_MANIFEST.json').read_text())
    expected = {'m2_18_' + r['case_id']: r for r in universe()}
    rows = manifest['cases']
    A.require(len(rows) == 38 and {r['case_id'] for r in rows} == set(expected), 'Incomplete certificate inventory')
    A.require(manifest['expected_case_ids'] == sorted(expected), 'Wrong expected case set')
    A.require(manifest['maximum_interval'] == [2, 18] and manifest['total_upper_bound'] == 93, 'Wrong declared theorem')
    for path, digest in manifest['semantic_input_hashes'].items():
        A.require(A.sha(ROOT / path) == digest, 'Changed semantic input: ' + path)
    selected = rows
    if args.quick:
        selected = [next(r for r in rows if r['support_size'] == s) for s in (11, 12)]
    output = HERE / 'fresh_replay'
    output.mkdir(exist_ok=True)
    target = HERE / 'JOINT_FRESH_REPLAY.json'
    receipt = {'status': 'RUNNING', 'quick': args.quick, 'checked_cases': 0, 'cases': [],
               'encoder_formally_verified': False, 'prefer_compressed': args.prefer_compressed}
    A.dump(target, receipt)
    started = time.monotonic()
    try:
        A.verify_sources()
        spectra = E.load_spectra(IMPORTED / 'data/spec32.csv')
        capacities = E.load_M(IMPORTED / 'data/Mtable.txt')
        subspaces = E.all_subspaces()
        with tempfile.TemporaryDirectory(prefix='kakeya_joint_replay_') as temporary:
            temp = Path(temporary)
            bins, build = A.build_checkers(temp / 'bin', output / 'build_logs')
            receipt['build'] = build
            for number, row in enumerate(selected, 1):
                cid = row['case_id']
                geometric = expected[cid]
                A.require(row['maximum_interval'] == [2, 18] and row['total_upper_bound'] == 93, 'Changed case parameters')
                A.require(row['marked_support']['support'] == geometric['source_support'], 'Changed support')
                A.require(row['marked_support']['distinguished_hub'] == 0, 'Changed hub')
                A.require(row['marked_support']['affine_map_to_contract'] == geometric['affine_map_to_contract'], 'Changed affine transport')
                formula = E.encode([x for x in geometric['source_support'] if x], 18,
                                   spectra, capacities, subspaces, outtotal=93, hub_min=2)
                regenerated = temp / 'regenerated.cnf'
                E.write_dimacs(formula, regenerated)
                del formula
                A.require(A.sha(regenerated) == row['cnf_sha256'], 'CNF regeneration differs: ' + cid)
                folder = output / cid
                folder.mkdir(exist_ok=True)
                with C.materialized(HERE / row['cnf'], row['cnf_sha256'], temp,
                                    prefer_compressed=args.prefer_compressed) as cnf:
                    A.cnf_header(cnf)
                    with C.materialized(HERE / row['lrat'], row['lrat_sha256'], temp,
                                        prefer_compressed=args.prefer_compressed) as proof:
                        check = A.run_checker([bins['cake_lpr'], '--CML_HEAP_SIZE=' + str(args.heap_mb),
                                               '--CML_STACK_SIZE=256', cnf, proof], folder,
                                              'cake_lpr', args.timeout, 's VERIFIED UNSAT', True)
                        A.require(check['accepted'], 'CakeML rejected: ' + cid)
                        A.require(A.sha(cnf) == row['cnf_sha256'] and A.sha(proof) == row['lrat_sha256'], 'Inputs changed during verification')
                receipt['cases'].append({'case_id': cid, 'cnf_regeneration': 'BYTE_IDENTICAL',
                                         'cnf_sha256': row['cnf_sha256'], 'lrat_sha256': row['lrat_sha256'],
                                         'cake_lpr': check})
                receipt.update(checked_cases=len(receipt['cases']), seconds=round(time.monotonic() - started, 6))
                A.dump(target, receipt)
                print(f'[{number}/{len(selected)}] {cid}: BYTE_IDENTICAL_CNF + CAKEML_ACCEPTED', flush=True)
        receipt.update(status='PASS_QUICK_TWO_CASES_ONLY' if args.quick else 'PASS_ALL_38_EXACT_CNF_REGENERATIONS_AND_CAKEML_CERTIFICATES',
                       seconds=round(time.monotonic() - started, 6))
        A.dump(target, receipt)
        print(receipt['status'], flush=True)
    except Exception as error:
        receipt.update(status='FAIL', error=repr(error), seconds=round(time.monotonic() - started, 6))
        A.dump(target, receipt)
        raise


if __name__ == '__main__':
    main()
