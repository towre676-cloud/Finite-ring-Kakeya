#!/usr/bin/env python3
"""Bounded support-13 searches with exact-CNF, mandatory CakeML certificates.

Search is untrusted. An accepted row needs DRAT-trim reconstruction and the
pinned CakeML checker on the exact regenerated CNF. Partial traces confer no
exclusion. All live files are private temporary files; only stopped, hashed,
checked artifacts are published. Earlier rounds are read-only dependencies.
"""
from pathlib import Path
import argparse
import ctypes
import gc
import importlib.util
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
R6 = ROOT / 'research_round6'
IMPORTED = R6 / 'imported_claude_round4'
QUEUE = R6 / 'next_frontier/SUPPORT13_CASE_QUEUE.json'
DEFAULT_SOLVER = '/tmp/kakeya_lean_round4/lean-4.24.0-linux/bin/cadical'
ENCODER_HASH = '776af5c5699f5e153990cdfb8b0897d690202c9895dd95134eec9b8df295feba'
CATALOGUE_HASH = '2532528fed96455f714acf83cb53ba66c4b0b97dc48d541a02718dae1910f1dc'
ACCEPTED = 'PASS_EXACT_CNF_DRAT_TO_CAKEML'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


A = module('r7_s13_audit', ROOT / 'research_round5/proof_audit/audit_certificates.py')
C = module('r7_s13_storage', R6 / 'certificate_storage.py')
E = module('r7_s13_baseline', R6 / 'joint_maxima/encode_joint_maxima.py')


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', prefix='publish_',
                                     suffix='.json', dir=path.parent, delete=False) as out:
        temporary = Path(out.name)
        json.dump(value, out, indent=2)
        out.write('\n')
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def semantics():
    paths = [R6/'joint_maxima/encode_joint_maxima.py', IMPORTED/'data/spec32.csv',
             IMPORTED/'data/Mtable.txt', IMPORTED/'data/orbits_all.txt', QUEUE]
    return {str(p.relative_to(ROOT)): A.sha(p) for p in paths}


def universe():
    A.require(A.sha(R6/'joint_maxima/encode_joint_maxima.py') == ENCODER_HASH,
              'Frozen baseline encoder changed')
    A.require(A.sha(IMPORTED/'data/orbits_all.txt') == CATALOGUE_HASH,
              'Frozen orbit catalogue changed')
    source = json.loads(QUEUE.read_text())
    masks = {mask for k, mask, stab, cover in
             (map(int, line.split()) for line in (IMPORTED/'data/orbits_all.txt').read_text().splitlines())
             if k == 12 and cover == 1}
    cases = source['cases']
    A.require(len(cases) == len(masks) == 55, 'Expected complete 55-case support13 catalogue')
    A.require({c['nonzero_support_mask'] for c in cases} == masks, 'Queue/catalogue mismatch')
    for c in cases:
        mask = c['nonzero_support_mask']
        support = [0] + [x for x in range(1, 32) if (mask >> x) & 1]
        A.require(len(support) == 13 and support == c['support'] and c['distinguished_hub'] == 0,
                  'Malformed marked support')
        A.require({a ^ b for a in support for b in support} == set(range(32)),
                  'Noncovering support in catalogue')
    return cases


def publish_copy(source, target, expected):
    target = Path(target)
    A.require(not target.exists(), 'Refusing to overwrite existing artifact')
    temporary = target.with_suffix(target.suffix + '.publishing')
    shutil.copyfile(source, temporary)
    A.require(A.sha(temporary) == expected, 'Publication hash changed')
    os.replace(temporary, target)


def enable_child_subreaper():
    """Adopt/reap wrapper descendants after a forced process-group stop."""
    if not sys.platform.startswith('linux'):
        raise RuntimeError('Bounded search supervision requires Linux; proof replay remains separate.')
    libc=ctypes.CDLL(None,use_errno=True)
    libc.prctl.argtypes=[ctypes.c_int,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_ulong,ctypes.c_ulong]
    libc.prctl.restype=ctypes.c_int
    if libc.prctl(36,1,0,0,0)!=0:  # Linux PR_SET_CHILD_SUBREAPER
        raise OSError(ctypes.get_errno(),'Could not enable child subreaper')


def group_exists(group):
    try:
        os.killpg(group,0)
        return True
    except ProcessLookupError:
        return False


def stop_and_join_group(process,kill=False):
    """Require the entire session's process group to be absent before return."""
    group=process.pid;signals_sent=0;adopted=[]
    if kill and group_exists(group):
        try:os.killpg(group,signal.SIGKILL);signals_sent+=1
        except ProcessLookupError:pass
    process.wait(timeout=5)
    deadline=time.monotonic()+5
    while True:
        # Direct child was joined above. Any orphaned wrapper descendants
        # have become our children because this producer is a subreaper.
        while True:
            try:pid,status=os.waitpid(-group,os.WNOHANG)
            except ChildProcessError:break
            if pid==0:break
            adopted.append({'pid':pid,'wait_status':status})
        if not group_exists(group):
            return {'process_group_id':group,'whole_process_group_confirmed_absent':True,
                    'kill_signals_sent':signals_sent,'adopted_descendants_reaped':adopted}
        if time.monotonic()>deadline:
            raise RuntimeError('Could not stop/reap every solver process-group member')
        try:os.killpg(group,signal.SIGKILL);signals_sent+=1
        except ProcessLookupError:pass
        time.sleep(0.05)


def live_drat_bytes(work):
    """Count both wrapper search traces and the final prefixed DRAT output."""
    sizes={}
    for path in Path(work).glob('*.drat'):
        try:sizes[path.name]=path.stat().st_size
        except FileNotFoundError:pass
    return sum(sizes.values()),sizes


def run_guarded_solver(command,work,limit,proof_byte_limit=1536*1024**2,min_free_bytes=2*1024**3):
    enable_child_subreaper()
    work=Path(work);start=time.monotonic();reason=None;observed={}
    with (work/'solver.stdout.txt').open('wb') as out,(work/'solver.stderr.txt').open('wb') as err:
        process=subprocess.Popen(command,stdout=out,stderr=err,start_new_session=True)
        try:
            while process.poll() is None:
                byte_count,observed=live_drat_bytes(work)
                if time.monotonic()-start>limit+2:reason='WALL_TIMEOUT'
                elif byte_count>proof_byte_limit:reason='PROOF_SIZE_GUARD'
                elif shutil.disk_usage('/tmp').free<min_free_bytes:reason='DISK_GUARD'
                if reason:break
                time.sleep(0.2)
        finally:
            group=stop_and_join_group(process,kill=(reason is not None or process.poll() is None))
    return {'solver_returncode':process.returncode,'stop_reason':reason,
            'solve_seconds':round(time.monotonic()-start,6),'process_supervision':group,
            'last_observed_live_drat_bytes':observed,
            'proof_size_guard_counts_all_live_drat_files':True}


def one(case, lower, upper, limit, solver, binaries, SPEC, M, SUBS, tag, check_timeout):
    mask = case['nonzero_support_mask']
    cid = f's13_T{mask}_m{lower}_{upper}_{tag}'
    destination = HERE/'cases'/cid
    if destination.exists():
        receipt = json.loads((destination/'CASE_RECEIPT.json').read_text())
        A.require(receipt['case_id'] == cid, 'Existing case identifier differs')
        for name, info in receipt.get('storage', {}).items():
            path = destination / (name + '.xz')
            A.require(A.sha(path) == info['xz_sha256'], 'Existing stored bytes changed')
            A.require(C.logical_sha(destination/name, prefer_compressed=True) == info['raw_sha256'],
                      'Existing decoded bytes changed')
        return receipt
    started = time.monotonic()
    record = {'case_id': cid, 'status': 'STARTING', 'support': case['support'],
              'nonzero_support_mask': mask, 'distinguished_hub': 0,
              'maximum_interval': [lower, upper], 'total_upper_bound': 93,
              'ring_scope': 'common_necessary_relaxation_both_rings',
              'encoder': 'research_round6/joint_maxima/encode_joint_maxima.py',
              'semantic_input_hashes': semantics(), 'solver_limit_seconds': limit,
              'solver_sha256': A.sha(solver), 'producer_sha256': A.sha(__file__),
              'encoder_soundness_formalized': False, 'storage': {}}
    A.require(shutil.disk_usage('/tmp').free >= 3*1024**3, 'Less than3GiB temporary disk free')
    with tempfile.TemporaryDirectory(prefix=f'kakeya_r7_s13_{mask}_') as temporary:
        work = Path(temporary)
        cnf, proof = work/'input.cnf', work/'proof.drat'
        f = E.encode(case['support'][1:], upper, SPEC, M, SUBS, outtotal=93, hub_min=lower)
        E.write_dimacs(f, cnf)
        record.update(variables=f.n, clauses=len(f.cl), cnf_sha256=A.sha(cnf),
                      cnf_bytes=cnf.stat().st_size, encode_seconds=round(time.monotonic()-started, 6))
        del f
        gc.collect()
        command = [solver, '--no-binary', '--no-witness', '-t', str(limit), str(cnf), str(proof)]
        supervision=run_guarded_solver(command,work,limit)
        record.update(supervision,solver_command=command)
        code,reason=supervision['solver_returncode'],supervision['stop_reason']
        unsat = code == 20 and 's UNSATISFIABLE' in (work/'solver.stdout.txt').read_text()
        if proof.exists():
            record.update(proof_sha256=A.sha(proof), proof_bytes=proof.stat().st_size)
        accepted = False
        if unsat:
            audit = A.check_pair(cnf, proof, work/'audit', binaries, check_timeout, 1024, 256, False)
            record['audit'] = audit
            accepted = audit['status'] == 'PASS_CNF_UNSAT_VIA_CAKEML_LRAT'
            A.require(audit['input_sha256'] == {'cnf': record['cnf_sha256'], 'drat': record['proof_sha256']},
                      'Audit inputs differ from encoded/solved inputs')
            record['status'] = ACCEPTED if accepted else 'CHECKER_REJECTED_UNCERTIFIED'
        else:
            record['status'] = 'TIMEOUT_OR_RESOURCE_UNCERTIFIED' if reason or code == 0 else 'UNACCEPTED_SOLVER_RESULT'
        destination.mkdir(parents=True)
        for raw in [cnf] + ([proof] if accepted else []):
            expected = record['cnf_sha256'] if raw == cnf else record['proof_sha256']
            meta = C.compress_verified(raw, expected, preset=1, remove_raw=True)
            compressed = Path(str(raw)+'.xz')
            publish_copy(compressed, destination/compressed.name, meta['xz_sha256'])
            A.require(C.logical_sha(destination/raw.name, prefer_compressed=True) == expected,
                      'Published decoded artifact differs')
            meta.update(logical_path=raw.name, compressed_path=compressed.name)
            record['storage'][raw.name] = meta
        if not accepted and proof.exists():
            record['discarded_unaccepted_proof'] = {'sha256': record['proof_sha256'],
                'bytes': record['proof_bytes'], 'reason': 'No mandatory checked refutation; no exclusion credit.'}
            proof.unlink()
        for source in list(work.glob('*.txt')) + list((work/'audit').glob('*.txt')):
            publish_copy(source, destination/source.name, A.sha(source))
        record.update(seconds=round(time.monotonic()-started, 6), reconstructed_lrat_retained=False,
                      incomplete_proof_retained=False)
        dump(destination/'CASE_RECEIPT.json', record)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, default=30)
    parser.add_argument('--check-timeout', type=int, default=600)
    parser.add_argument('--lower', type=int, default=2)
    parser.add_argument('--upper', type=int, default=18)
    parser.add_argument('--mask', action='append', type=int)
    parser.add_argument('--skip', action='append', type=int, default=[])
    parser.add_argument('--take', type=int)
    parser.add_argument('--tag', default='baseline_t30')
    parser.add_argument('--worker', default='main', help='Unique tool-build namespace for concurrent disjoint batches')
    parser.add_argument('--solver', default=DEFAULT_SOLVER)
    args = parser.parse_args()
    A.require(2 <= args.lower <= args.upper <= 18 and args.limit > 0 and args.check_timeout > 0,
              'Invalid domain or resource limits')
    A.require(args.tag.replace('_','').isalnum(), 'Unsafe tag')
    A.require(args.worker.replace('_','').isalnum(), 'Unsafe worker namespace')
    all_cases = universe()
    selected = [c for c in all_cases if c['nonzero_support_mask'] != 37848950
                and c['nonzero_support_mask'] not in set(args.skip)
                and (args.mask is None or c['nonzero_support_mask'] in set(args.mask))]
    if args.mask is not None:
        A.require(set(args.mask) <= {c['nonzero_support_mask'] for c in all_cases}, 'Unknown requested mask')
    if args.take is not None:
        selected = selected[:args.take]
    dump(HERE/'CASE_UNIVERSE.json', {'source_queue_sha256': A.sha(QUEUE),
         'catalogue_sha256': CATALOGUE_HASH, 'complete_marked_case_count': 55,
         'cases': all_cases, 'inherited_certified_mask': 37848950,
         'scope': '55 marked support classes, not55 unmarked affine supports or weight profiles.'})
    pins = A.verify_sources()
    tool_root=HERE/'worker_tools'/args.worker
    binaries, build = A.build_checkers(tool_root/'bin',tool_root/'build_logs')
    dump(tool_root/'BUILD_RECEIPT.json', {'pins': pins, 'build': build,
         'solver_binary_sha256': A.sha(args.solver), 'semantic_input_hashes': semantics()})
    SPEC = E.load_spectra(IMPORTED/'data/spec32.csv')
    M = E.load_M(IMPORTED/'data/Mtable.txt')
    SUBS = E.all_subspaces()
    summary_path = HERE/f'{args.tag}_m{args.lower}_{args.upper}_SWEEP.json'
    record = {'status': 'RUNNING', 'scope': 'Bounded proof-producing search; incomplete rows give no exclusion.',
              'requested_masks': [c['nonzero_support_mask'] for c in selected],
              'maximum_interval': [args.lower, args.upper], 'worker':args.worker,
              'cases': [], 'full_55_case_coverage': False}
    dump(summary_path, record)
    start = time.monotonic()
    for case in selected:
        if (HERE/'STOP_REQUESTED').exists():
            record['stop_requested'] = True
            break
        result = one(case, args.lower, args.upper, args.limit, args.solver, binaries,
                     SPEC, M, SUBS, args.tag, args.check_timeout)
        record['cases'].append(result)
        record['seconds'] = round(time.monotonic()-start, 6)
        dump(summary_path, record)
        print(json.dumps({k: result.get(k) for k in ['case_id','status','solve_seconds','proof_bytes','seconds']}), flush=True)
    record.update(status='COMPLETED_BOUNDED_SEARCH', accepted_attempts=sum(r['status']==ACCEPTED for r in record['cases']),
                  seconds=round(time.monotonic()-start, 6))
    dump(summary_path, record)
    print(json.dumps({k: record[k] for k in ['status','accepted_attempts','seconds']}), flush=True)


if __name__ == '__main__':
    main()
