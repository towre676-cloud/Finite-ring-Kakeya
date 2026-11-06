"""Search and preserve joint-maxima CNFs with direct LRAT certificates.

All support-11/12 hub-marked classes are imported from the separately checked
38-case geometric bijection. The default interval 2..18 includes every smaller
maximum, with a largest fibre marked at zero and ties allowed. Solver output
is credited only after the pinned upstream CakeML checker accepts its LRAT
against the exact CNF. This is not a formal proof of the encoder semantics.
"""
from pathlib import Path
import argparse
import concurrent.futures
import importlib.util
import json
import shutil
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
IMPORTED = HERE.parent / 'imported_claude_round4'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


E = module('joint_maxima_encoder', HERE / 'encode_joint_maxima.py')
A = module('joint_maxima_pinned_audit', ROOT / 'research_round5/proof_audit/audit_certificates.py')


def dump(path, value):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2) + '\n')
    tmp.replace(path)


def inputs():
    paths = [HERE / 'encode_joint_maxima.py', IMPORTED / 'data/spec32.csv',
             IMPORTED / 'data/Mtable.txt',
             HERE.parent / 'catalogue_audit/CLAUDE_TO_ROUND5_38_CASE_MAP.json']
    return {str(p.relative_to(ROOT)): A.sha(p) for p in paths}


def cases(supports, lower, upper):
    rows = json.loads((HERE.parent / 'catalogue_audit/CLAUDE_TO_ROUND5_38_CASE_MAP.json').read_text())['cases']
    if len(rows) != 38 or len({r['case_id'] for r in rows}) != 38:
        raise ValueError('Invalid complete support catalogue')
    result = []
    for row in rows:
        if row['support_size'] not in supports:
            continue
        result.append(dict(row, geometric_case_id=row['case_id'],
                           case_id=f'm{lower}_{upper}_' + row['case_id'],
                           maximum_interval=[lower, upper]))
    return result


def one(task):
    row, solver, solve_timeout, check_timeout, heap_mb, provenance = task
    folder = HERE / 'cases' / row['case_id']
    folder.mkdir(parents=True, exist_ok=True)
    receipt = folder / 'CASE_RECEIPT.json'
    cnf, proof = folder / 'input.cnf', folder / 'proof.lrat'
    if receipt.exists():
        prior = json.loads(receipt.read_text())
        if (prior.get('status') == 'PASS_CNF_UNSAT_VIA_CAKEML_LRAT'
                and prior.get('semantic_input_hashes') == provenance
                and cnf.is_file() and proof.is_file()
                and A.sha(cnf) == prior['cnf_sha256'] and A.sha(proof) == prior['lrat_sha256']):
            return prior
    started = time.monotonic()
    record = {'status': 'ENCODING', 'case_id': row['case_id'],
              'geometric_case_id': row['geometric_case_id'],
              'maximum_interval': row['maximum_interval'],
              'support_size': row['support_size'], 'source_mask': row['source_mask'],
              'marked_support': {'support': row['source_support'], 'distinguished_hub': 0,
                                 'affine_map_to_contract': row['affine_map_to_contract']},
              'semantic_input_hashes': provenance,
              'mathematical_scope': 'Common necessary-condition relaxation for both rings; encoder soundness is a separate obligation.'}
    dump(receipt, record)
    try:
        lower, upper = row['maximum_interval']
        spectra = E.load_spectra(IMPORTED / 'data/spec32.csv')
        capacities = E.load_M(IMPORTED / 'data/Mtable.txt')
        subspaces = E.all_subspaces()
        formula = E.encode([x for x in row['source_support'] if x], upper, spectra,
                           capacities, subspaces, outtotal=93, hub_min=lower)
        E.write_dimacs(formula, cnf)
        record.update(cnf_sha256=A.sha(cnf), cnf_bytes=cnf.stat().st_size,
                      variables=formula.n, clauses=len(formula.cl),
                      encode_seconds=round(time.monotonic() - started, 6), status='SOLVING')
        del formula
        dump(receipt, record)
        command = [solver, '--lrat', '--no-binary', '--no-witness', '-t', str(solve_timeout),
                   str(cnf), str(proof)]
        t = time.monotonic()
        with (folder / 'solver.stdout.txt').open('wb') as stdout, (folder / 'solver.stderr.txt').open('wb') as stderr:
            try:
                solved = subprocess.run(command, stdout=stdout, stderr=stderr, timeout=solve_timeout + 30)
                code = solved.returncode
            except subprocess.TimeoutExpired:
                code = None
        record.update(solver_returncode=code, solver_command=command,
                      solve_seconds=round(time.monotonic() - t, 6))
        if code != 20 or 's UNSATISFIABLE' not in (folder / 'solver.stdout.txt').read_text():
            record.update(status='UNACCEPTED_SOLVER_RESULT', seconds=round(time.monotonic() - started, 6))
            dump(receipt, record)
            return record
        record.update(status='CHECKING', lrat_sha256=A.sha(proof), lrat_bytes=proof.stat().st_size,
                      cnf_header=A.cnf_header(cnf))
        dump(receipt, record)
        accepted = A.run_checker([HERE / 'bin/cake_lpr', '--CML_HEAP_SIZE=' + str(heap_mb),
                                  '--CML_STACK_SIZE=256', cnf, proof], folder,
                                 'cake_lpr', check_timeout, 's VERIFIED UNSAT', True)
        unchanged = A.sha(cnf) == record['cnf_sha256'] and A.sha(proof) == record['lrat_sha256']
        record.update(cake_lpr=accepted, inputs_unchanged=unchanged,
                      seconds=round(time.monotonic() - started, 6),
                      status='PASS_CNF_UNSAT_VIA_CAKEML_LRAT' if accepted['accepted'] and unchanged else 'CHECK_FAILED')
        dump(receipt, record)
    except Exception as error:
        record.update(status='ERROR', error=repr(error), seconds=round(time.monotonic() - started, 6))
        dump(receipt, record)
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--solver', default=shutil.which('cadical') or '/tmp/kakeya_lean_round4/lean-4.24.0-linux/bin/cadical')
    parser.add_argument('--jobs', type=int, default=2)
    parser.add_argument('--solve-timeout', type=int, default=300)
    parser.add_argument('--check-timeout', type=int, default=600)
    parser.add_argument('--heap-mb', type=int, default=1024)
    parser.add_argument('--lower', type=int, default=2)
    parser.add_argument('--upper', type=int, default=18)
    parser.add_argument('--supports', type=int, nargs='+', default=[11, 12])
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.jobs <= 2 or not 2 <= args.lower <= args.upper <= 32:
        raise ValueError('Unsupported worker count or maximum interval')
    if not set(args.supports) <= {11, 12}:
        raise ValueError('This complete marked-support catalogue covers only supports11 and12')
    provenance = inputs()
    rows = sorted(cases(set(args.supports), args.lower, args.upper),
                  key=lambda r: (r['support_size'], r['source_mask']))
    if args.pilot:
        rows = rows[:1]
    pins = A.verify_sources()
    binaries, build = A.build_checkers(HERE / 'bin', HERE / 'build_logs')
    version = subprocess.run([args.solver, '--version'], capture_output=True, text=True, check=True).stdout.strip()
    dump(HERE / 'BUILD_RECEIPT.json', {'pins': pins, 'build': build,
                                      'solver_version': version, 'solver_sha256': A.sha(args.solver),
                                      'semantic_input_hashes': provenance})
    dump(HERE / ('PILOT_UNIVERSE.json' if args.pilot else 'CASE_UNIVERSE.json'), rows)
    target = HERE / ('PILOT_RECEIPT.json' if args.pilot else 'CERTIFICATION_RECEIPT.json')
    results = []
    started = time.monotonic()
    report = {'status': 'RUNNING', 'maximum_interval': [args.lower, args.upper],
              'requested_supports': args.supports, 'requested_cases': len(rows),
              'scope_complete': not args.pilot, 'completed_cases': 0, 'cases': []}
    dump(target, report)
    with concurrent.futures.ProcessPoolExecutor(args.jobs) as pool:
        futures = [pool.submit(one, (row, args.solver, args.solve_timeout, args.check_timeout,
                                    args.heap_mb, provenance)) for row in rows]
        for future in concurrent.futures.as_completed(futures):
            r = future.result()
            results.append(r)
            print(json.dumps({k: r.get(k) for k in ['case_id', 'status', 'solve_seconds', 'seconds', 'lrat_bytes']}), flush=True)
            report.update(completed_cases=len(results), cases=results,
                          seconds=round(time.monotonic() - started, 6))
            dump(target, report)
    good = bool(results) and all(r['status'] == 'PASS_CNF_UNSAT_VIA_CAKEML_LRAT' for r in results)
    report['status'] = 'PASS_ALL_REQUESTED_CNF_CERTIFICATES' if good else 'INCOMPLETE_OR_FAILED'
    report['encoder_formally_verified'] = False
    report['solver_trusted_for_unsat'] = False
    report['by_support'] = {str(s): {'expected': sum(r['support_size'] == s for r in rows),
                                    'accepted': sum(r['support_size'] == s and r['status'] == 'PASS_CNF_UNSAT_VIA_CAKEML_LRAT' for r in results)}
                            for s in sorted(set(args.supports))}
    dump(target, report)
    print(report['status'], flush=True)
    return 0 if good else 1


if __name__ == '__main__':
    raise SystemExit(main())
