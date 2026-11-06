#!/usr/bin/env python3
"""Bounded proof-logged tests of the census-free exact-shape relaxation."""
import argparse
import gc
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

from encode_exact_shape import encode_support, write_dimacs

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
QUEUE = ROOT / 'research_round6/next_frontier/SUPPORT13_CASE_QUEUE.json'
SOLVER = Path('/tmp/kakeya_lean_round4/lean-4.24.0-linux/bin/cadical')
ACCEPTED = 'PASS_EXACT_SHAPE_CNF_DRAT_CAKEML'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


A = module('exact_shape_audit', ROOT / 'research_round5/proof_audit/audit_certificates.py')
C = module('exact_shape_storage', ROOT / 'research_round6/certificate_storage.py')


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.publishing')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    os.replace(temporary, path)


def source_hashes():
    paths = [Path(__file__).resolve(), HERE / 'encode_exact_shape.py', QUEUE,
             ROOT / 'research_round5/proof_audit/audit_certificates.py',
             ROOT / 'research_round6/certificate_storage.py']
    return {str(path.relative_to(ROOT)): A.sha(path) for path in paths}


def copy_verified(source, target, digest):
    A.require(not target.exists(), 'Refusing to overwrite published trial input')
    temporary = target.with_suffix(target.suffix + '.publishing')
    shutil.copyfile(source, temporary)
    A.require(A.sha(temporary) == digest, 'Copy changed accepted bytes')
    os.replace(temporary, target)


def run_one(case, lower, upper, limit, tag, binaries):
    case_id = f's13_T{case["nonzero_support_mask"]}_m{lower}_{upper}_exactshape_{tag}'
    destination = HERE / 'cases' / case_id
    A.require(not destination.exists(), 'Trial paths are immutable; choose another tag')
    pins = source_hashes()
    start = time.monotonic()
    result = {'case_id': case_id, 'support': case['support'],
              'nonzero_support_mask': case['nonzero_support_mask'],
              'maximum_interval': [lower, upper], 'total_upper_bound': 93,
              'distinguished_hub': 0, 'ring_scope': 'common_cardinality_relaxation_both_rings',
              'spectrum_census_used': False, 'semantic_input_hashes': pins,
              'solver_sha256': A.sha(SOLVER), 'wall_limit_seconds': limit,
              'status': 'STARTING', 'storage': {}}
    A.require(shutil.disk_usage('/tmp').free > 3 * 1024**3, 'Temporary disk guard')
    with tempfile.TemporaryDirectory(prefix='kakeya_exact_shape_') as name:
        work = Path(name)
        cnf, proof = work / 'input.cnf', work / 'proof.drat'
        formula = encode_support(case['support'], upper, hub_min=lower, total=93)
        write_dimacs(formula, cnf)
        result.update(formula=formula.exact_shape_metadata, cnf_sha256=A.sha(cnf),
                      cnf_bytes=cnf.stat().st_size,
                      encode_seconds=round(time.monotonic() - start, 6))
        del formula
        gc.collect()
        command = [str(SOLVER), '--no-binary', '--no-witness', '-t', str(limit), str(cnf), str(proof)]
        reason = None
        solve_start = time.monotonic()
        with (work / 'solver.stdout.txt').open('wb') as out, (work / 'solver.stderr.txt').open('wb') as err:
            process = subprocess.Popen(command, stdout=out, stderr=err)
            try:
                while process.poll() is None:
                    if time.monotonic() - solve_start > limit + 2:
                        reason = 'WALL_TIMEOUT'
                    elif proof.exists() and proof.stat().st_size > 1024**3:
                        reason = 'PROOF_SIZE_GUARD'
                    elif shutil.disk_usage('/tmp').free < 2 * 1024**3:
                        reason = 'DISK_GUARD'
                    if reason:
                        process.kill()
                        break
                    time.sleep(0.2)
                code = process.wait()
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait()
        result.update(solve_seconds=round(time.monotonic() - solve_start, 6),
                      solver_returncode=code, stop_reason=reason, solver_command=command)
        if proof.exists():
            result.update(drat_sha256=A.sha(proof), drat_bytes=proof.stat().st_size)
        accepted = False
        if code == 20 and 's UNSATISFIABLE' in (work / 'solver.stdout.txt').read_text():
            audit = A.check_pair(cnf, proof, work / 'audit', binaries, 900, 1024, 256, False)
            result['audit'] = audit
            A.require(audit['input_sha256'] == {'cnf': result['cnf_sha256'], 'drat': result['drat_sha256']},
                      'Checker input hashes differ')
            accepted = audit['status'] == 'PASS_CNF_UNSAT_VIA_CAKEML_LRAT'
        result['status'] = ACCEPTED if accepted else ('SAT_RELAXATION_NOT_A_KAKEYA_SET' if code == 10 else
                            'TIMEOUT_UNCERTIFIED' if reason or code == 0 else 'UNACCEPTED_UNCERTIFIED')
        A.require(source_hashes() == pins, 'Frozen source changed during trial')
        destination.mkdir(parents=True)
        for raw in [cnf] + ([proof] if accepted else []):
            digest = result['cnf_sha256'] if raw == cnf else result['drat_sha256']
            metadata = C.compress_verified(raw, digest, preset=1, remove_raw=True)
            stored = Path(str(raw) + '.xz')
            copy_verified(stored, destination / stored.name, metadata['xz_sha256'])
            A.require(C.logical_sha(destination / raw.name, prefer_compressed=True) == digest,
                      'Published decoded bytes changed')
            result['storage'][raw.name] = metadata
        if not accepted and proof.exists():
            result['discarded_unaccepted_drat'] = {
                'sha256': result['drat_sha256'], 'bytes': result['drat_bytes'],
                'mathematical_credit': 'None: incomplete or unaccepted trace.'}
        for path in list(work.glob('*.txt')) + list((work / 'audit').glob('*.txt')):
            copy_verified(path, destination / path.name, A.sha(path))
        result.update(seconds=round(time.monotonic() - start, 6),
                      reconstructed_lrat_retained=False, unfinished_proof_retained=False)
        dump(destination / 'CASE_RECEIPT.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mask', type=int, required=True)
    parser.add_argument('--lower', type=int, default=2)
    parser.add_argument('--upper', type=int, default=18)
    parser.add_argument('--limit', type=int, default=60)
    parser.add_argument('--tag', required=True)
    parser.add_argument('--fallback-exact18', action='store_true')
    args = parser.parse_args()
    A.require(2 <= args.lower <= args.upper <= 18 and args.limit > 0, 'Bad interval or limit')
    A.require(args.tag.replace('_', '').isalnum(), 'Bad tag')
    cases = {row['nonzero_support_mask']: row for row in json.loads(QUEUE.read_text())['cases']}
    A.require(args.mask in cases, 'Unknown marked support')
    pins = A.verify_sources()
    binaries, build = A.build_checkers(HERE / 'bin', HERE / 'build_logs')
    dump(HERE / 'CHECKER_BUILD_RECEIPT.json', {'pins': pins, 'build': build})
    report = {'status': 'RUNNING', 'cases': [], 'performance_caveat':
              'Bounded single runs in a shared environment; no general speed claim.'}
    path = HERE / f'{args.tag}_TRIALS.json'
    dump(path, report)
    row = run_one(cases[args.mask], args.lower, args.upper, args.limit, args.tag, binaries)
    report['cases'].append(row)
    dump(path, report)
    print(json.dumps({k: row.get(k) for k in ['case_id', 'status', 'solve_seconds', 'drat_bytes', 'seconds']}), flush=True)
    if args.fallback_exact18 and row['status'] != ACCEPTED and (args.lower, args.upper) != (18, 18):
        row = run_one(cases[args.mask], 18, 18, args.limit, args.tag, binaries)
        report['cases'].append(row)
        dump(path, report)
        print(json.dumps({k: row.get(k) for k in ['case_id', 'status', 'solve_seconds', 'drat_bytes', 'seconds']}), flush=True)
    report['status'] = 'COMPLETED_BOUNDED_EXACT_SHAPE_TRIALS'
    dump(path, report)


if __name__ == '__main__':
    main()
