"""Check explicit CNF/DRAT pairs through DRAT-to-LRAT and CakeML checking.

This verifies UNSAT for the supplied CNF bytes. It does not prove the encoder
soundness, ring interpretation, symmetry reduction, or case catalogue complete.
The original Claude JSONL schema was unavailable; this script accepts only the
documented explicit manifest, rather than guessing fields or trusting statuses.
The optional C LRAT checker is diagnostic only: this pinned implementation
accepts a known false certificate on a satisfiable formula. CakeML acceptance
is mandatory; the C checker's success can never substitute for it.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
PINS = {
    'drat-trim': '2e3b2dc0ecf938addbd779d42877b6ed69d9a985',
    'cake_lpr': 'a36874a8b750b43fe4b385b8ddbf5b033e46a3fa',
}
ASSEMBLY_SHA256 = '2f3af32d55083839b3fa0e693afd817679c0b8944bef41def05a8b0ec72b7d4a'
M19_CONTRACT_SHA256 = '8d6b60a180c3cefe124e8de47b3c308f840bad9b1b3d1b8b55764ff9f19a5118'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def verify_sources():
    pins = {}
    for name, expected_commit in PINS.items():
        folder = HERE / 'vendor' / name
        pin = json.loads((folder / 'PIN.json').read_text())
        require(pin['commit'] == expected_commit, 'Unexpected checker commit: ' + name)
        for filename, digest in pin['source_files_sha256'].items():
            require(sha(folder / filename) == digest, 'Changed checker source: ' + name + '/' + filename)
        pins[name] = pin
    assembly = HERE / 'vendor/cake_lpr/cake_lpr.S'
    require(sha(assembly) == ASSEMBLY_SHA256, 'CakeML assembly differs from its published hash')
    return pins


def build_checkers(destination, logs):
    require(platform.machine().lower() in ('x86_64', 'amd64'),
            'This bundled CakeML assembly targets x86_64; use the upstream ARM artifact on ARM.')
    compiler = shutil.which('gcc') or shutil.which('cc')
    require(compiler is not None, 'A C compiler is required (tested with gcc on Linux x86_64).')
    destination, logs = Path(destination), Path(logs)
    destination.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    sources = HERE / 'vendor'
    commands = {
        'drat-trim': [compiler, '-O2', '-std=c99', str(sources/'drat-trim/drat-trim.c')],
        'lrat-check': [compiler, '-O2', '-std=c99', '-DLONGTYPE', str(sources/'drat-trim/lrat-check.c')],
        'cake_lpr': [compiler, '-O2', '-std=c99', str(sources/'cake_lpr/basis_ffi.c'), str(sources/'cake_lpr/cake_lpr.S')],
    }
    binaries, records = {}, {}
    for name, command in commands.items():
        executable = destination / name
        command = command + ['-o', str(executable)]
        result = subprocess.run(command, capture_output=True, text=True)
        log = logs / (name + '_compile.txt')
        log.write_text(result.stdout + result.stderr)
        require(result.returncode == 0, 'Checker compilation failed; see ' + str(log))
        binaries[name] = executable
        records[name] = {'binary_sha256': sha(executable), 'compile_returncode': result.returncode,
                         'compile_log_sha256': sha(log), 'compile_arguments': command[1:-2]}
    version = subprocess.run([compiler, '--version'], check=True, capture_output=True, text=True)
    return binaries, {'compiler': version.stdout.splitlines()[0], 'platform': platform.platform(),
                      'machine': platform.machine(), 'checkers': records}


def cnf_header(path):
    """Check DIMACS header, literal range and clause count without rewriting bytes."""
    variables = declared = None
    clauses = pending = 0
    with Path(path).open(encoding='ascii') as stream:
        for number, line in enumerate(stream, 1):
            line = line.strip()
            if not line or line.startswith('c'):
                continue
            words = line.split()
            if words[0] == 'p':
                require(variables is None and clauses == 0 and pending == 0,
                        'Repeated or late DIMACS header')
                require(len(words) == 4 and words[1] == 'cnf', 'Expected p cnf header')
                variables, declared = map(int, words[2:])
                require(variables >= 0 and declared >= 0, 'Negative DIMACS size')
                continue
            require(variables is not None, 'DIMACS clause before header')
            for word in words:
                literal = int(word)
                if literal == 0:
                    clauses += 1
                    pending = 0
                else:
                    require(abs(literal) <= variables, 'Literal exceeds declared variable bound')
                    pending += 1
    require(variables is not None and pending == 0, 'Missing header or unterminated clause')
    require(clauses == declared, 'DIMACS clause count mismatch')
    return {'variables': variables, 'clauses': clauses}


def run_checker(command, folder, name, timeout, expected_line, exact_stdout=False):
    folder = Path(folder)
    stdout, stderr = folder/(name+'.stdout.txt'), folder/(name+'.stderr.txt')
    started = time.monotonic()
    timed_out = False
    with stdout.open('wb') as out, stderr.open('wb') as err:
        try:
            result = subprocess.run([str(x) for x in command], stdout=out, stderr=err, timeout=timeout)
            returncode = result.returncode
        except subprocess.TimeoutExpired:
            returncode, timed_out = None, True
    output = stdout.read_bytes()
    if exact_stdout:
        marker = output.strip() == expected_line.encode('ascii') and stderr.stat().st_size == 0
    else:
        marker = any(line.strip() == expected_line.encode('ascii') for line in output.splitlines())
    return {'accepted': returncode == 0 and marker and not timed_out,
            'returncode': returncode, 'timed_out': timed_out, 'success_marker_present': marker,
            'seconds': round(time.monotonic()-started, 6),
            'stdout_file': stdout.name, 'stdout_sha256': sha(stdout),
            'stderr_file': stderr.name, 'stderr_sha256': sha(stderr)}


def check_pair(cnf, proof, folder, binaries, timeout=3600, heap_mb=1024, stack_mb=256,
               c_diagnostic=False):
    cnf, proof, folder = Path(cnf), Path(proof), Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    lrat = folder/'converted.lrat'
    require(cnf.resolve() != lrat.resolve() and proof.resolve() != lrat.resolve(),
            'An output path would overwrite an input certificate')
    lrat.unlink(missing_ok=True)
    original_hashes = {'cnf': sha(cnf), 'drat': sha(proof)}
    result = {'status': 'FAIL', 'cnf_header': cnf_header(cnf), 'input_sha256': original_hashes,
              'drat_trim': run_checker([binaries['drat-trim'], cnf, proof, '-L', lrat],
                                      folder, 'drat_trim', timeout, 's VERIFIED')}
    if not result['drat_trim']['accepted'] or not lrat.is_file():
        return result
    result['lrat_sha256'] = sha(lrat)
    result['lrat_bytes'] = lrat.stat().st_size
    if c_diagnostic:
        result['lrat_check_c'] = run_checker([binaries['lrat-check'], cnf, lrat], folder,
                                           'lrat_check_c', timeout, 'c VERIFIED')
        result['lrat_check_c']['role'] = 'DIAGNOSTIC_ONLY_KNOWN_FALSE_POSITIVE'
    else:
        result['lrat_check_c'] = {'status':'NOT_RUN_DIAGNOSTIC_ONLY_KNOWN_FALSE_POSITIVE'}
    result['cake_lpr'] = run_checker([binaries['cake_lpr'], '--CML_HEAP_SIZE='+str(heap_mb),
                                     '--CML_STACK_SIZE='+str(stack_mb), cnf, lrat],
                                    folder, 'cake_lpr', timeout, 's VERIFIED UNSAT', True)
    require({'cnf': sha(cnf), 'drat': sha(proof)} == original_hashes,
            'Input files changed during proof checking')
    require(sha(lrat) == result['lrat_sha256'], 'Converted LRAT changed during proof checking')
    if result['cake_lpr']['accepted']:
        result['status'] = 'PASS_CNF_UNSAT_VIA_CAKEML_LRAT'
    return result


def check_marked_contract(manifest, cases, manifest_path):
    """Check exact declared case coverage and explicit F_2^5 transport witnesses.

    This verifies metadata against a hashed catalogue. It does not prove that
    the CNF encodes that metadata, or that the catalogue is mathematically complete.
    """
    reference = manifest.get('coverage_contract')
    if reference is None:
        return {'status': 'NOT_REQUESTED'}
    contract_path = Path(reference['path'])
    if not contract_path.is_absolute():
        contract_path = Path(manifest_path).parent/contract_path
    contract_path = contract_path.resolve()
    require(contract_path.is_file(), 'Missing coverage contract')
    require(sha(contract_path) == reference['sha256'] == M19_CONTRACT_SHA256,
            'Coverage-contract hash mismatch')
    contract = json.loads(contract_path.read_text())
    require(contract['schema'] == 'maximum19-marked-support-contract-v1',
            'Unsupported coverage contract schema')
    ring_scope = reference['ring_scope']
    require(ring_scope in ('common_relaxation_both_rings', 'z4', 'dual'),
            'Declare common_relaxation_both_rings, z4, or dual for a 38-case manifest')
    entries = contract['cases']
    inventory = {entry['case_id']: entry for entry in entries}
    require(len(entries) == len(inventory) == contract['case_count'] == 38,
            'Expected exactly 38 distinct maximum-19 marked support cases')
    require(set(manifest['expected_case_ids']) == set(inventory),
            'Expected case ids do not exactly match the 38-case coverage contract')
    require(len(cases) == 38 and {case['case_id'] for case in cases} == set(inventory),
            'Actual cases do not exactly match the 38-case coverage contract')
    counts = {11: 0, 12: 0}
    for case in cases:
        entry = inventory[case['case_id']]
        target = entry['hub_zero_support']
        require(len(set(target)) == entry['support_size'] in counts and 0 in target,
                'Malformed contract representative')
        marked = case['marked_support']
        support, hub = marked['support'], marked['distinguished_hub']
        require(isinstance(support, list) and len(set(support)) == len(support),
                'Marked support must be a list of distinct points')
        require(all(type(x) is int and 0 <= x < 32 for x in support)
                and type(hub) is int and hub in support,
                'Marked support and hub must be points of F_2^5')
        affine = marked['affine_map_to_contract']
        require(isinstance(affine, list) and len(affine) == 6
                and all(type(x) is int and 0 <= x < 32 for x in affine),
                'An affine transport must contain offset followed by five columns')
        def transport(x):
            y = affine[0]
            for bit in range(5):
                if x & (1 << bit):
                    y ^= affine[bit + 1]
            return y
        require(len({transport(x) for x in range(32)}) == 32,
                'Marked-support transport is not invertible')
        require(transport(hub) == 0 and {transport(x) for x in support} == set(target),
                'Marked support does not transport to its named contract representative')
        counts[len(target)] += 1
    require(counts == {11: 13, 12: 25}, 'Unexpected marked support counts')
    return {'status': 'PASS_EXACT_HASHED_CONTRACT_AND_TRANSPORT_WITNESSES',
            'contract_sha256': sha(contract_path), 'contract_schema': contract['schema'],
            'case_count': len(inventory), 'counts_by_support': counts,
            'declared_ring_scope': ring_scope, 'ring_scope_soundness_checked': False,
            'CNF_to_declared_support_link_checked': False,
            'catalogue_completeness_proved_by_this_check': False}


def load_manifest(path):
    path = Path(path).resolve()
    manifest = json.loads(path.read_text())
    require(manifest['schema'] == 'kakeya-proof-audit-v1', 'Unsupported manifest schema')
    expected = manifest['expected_case_ids']
    require(isinstance(expected, list) and expected and len(expected) == len(set(expected)),
            'Expected case ids must be a nonempty list without duplicates')
    ids, cases = [], []
    for saved in manifest['cases']:
        case = dict(saved)
        case_id = case['case_id']
        require(isinstance(case_id, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', case_id),
                'Case ids must be safe unique filenames')
        ids.append(case_id)
        for name in ('cnf', 'proof'):
            filename = case[name]
            require(isinstance(filename, str) and not any(c in filename for c in '\x00\r\n'),
                    'Invalid certificate path')
            source = Path(filename)
            if not source.is_absolute():
                source = path.parent/source
            source = source.resolve()
            require(source.is_file(), 'Missing certificate: ' + str(source))
            digest = case[name+'_sha256']
            require(re.fullmatch(r'[0-9a-f]{64}', digest or '') is not None,
                    'A literal SHA256 is required for every input')
            require(sha(source) == digest, 'Input hash mismatch: ' + str(source))
            case[name+'_resolved'] = source
        cases.append(case)
    require(len(ids) == len(set(ids)) and set(ids) == set(expected),
            'Actual cases do not equal the declared expected case inventory')
    references = []
    for reference in manifest.get('semantic_reference_files', []):
        source = Path(reference['path'])
        if not source.is_absolute():
            source = path.parent/source
        require(source.is_file() and sha(source) == reference['sha256'],
                'Semantic-reference file is missing or has changed')
        references.append(reference)
    return manifest, cases, references


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--timeout', type=int, default=3600, help='Maximum seconds per checker process')
    parser.add_argument('--heap-mb', type=int, default=1024)
    parser.add_argument('--stack-mb', type=int, default=256)
    parser.add_argument('--c-diagnostic', action='store_true',
                        help='Also run the ordinary C LRAT checker as a diagnostic; its known false positive prevents using it as the acceptance gate.')
    args = parser.parse_args()
    require(min(args.timeout, args.heap_mb, args.stack_mb) > 0, 'Positive resource limits are required')
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    # Replace a previous receipt before validation, so an invalid input cannot
    # leave an older successful receipt masquerading as the current run.
    receipt = {'status': 'RUNNING', 'manifest_path': str(args.manifest.resolve()), 'cases': []}
    dump(output/'AUDIT_RECEIPT.json', receipt)
    started = time.monotonic()
    try:
        manifest, cases, references = load_manifest(args.manifest)
        contract_check = check_marked_contract(manifest, cases, args.manifest.resolve())
        pins = verify_sources()
        receipt.update({
        'manifest_sha256': sha(args.manifest),
        'label': manifest.get('label', ''), 'coverage_scope': manifest.get('coverage_scope', ''),
        'declared_expected_case_ids': manifest['expected_case_ids'],
        'encoder_soundness_checked_by_this_run': False,
        'orbit_catalogue_completeness_checked_by_this_run': False,
        'claimed_encoder_status': manifest.get('encoder_soundness_status', 'UNSPECIFIED'),
        'claimed_orbit_catalogue_status': manifest.get('orbit_catalogue_completeness_status', 'UNSPECIFIED'),
        'semantic_reference_hashes_verified': references,
        'marked_support_contract_check': contract_check,
        'checker_pins': pins,
        'required_acceptance_path':'DRAT-trim conversion and mandatory CakeML LPR acceptance on the same CNF bytes.',
        'C_LRAT_checker_role':'Optional diagnostic only; a false acceptance on a satisfiable formula is reproduced in verify_pipeline.py.',
        'upstream_HOL4_CakeML_proofs_rebuilt_here': False,
        'scope': 'UNSAT of the exact supplied CNF bytes, with exact manifest-case coverage. The mathematical encoding and case-catalogue completeness are separate obligations.',
        'cases': [],
        })
        with tempfile.TemporaryDirectory(prefix='kakeya_proof_checkers_') as tmp:
            binaries, build = build_checkers(tmp, output/'build_logs')
            receipt['build'] = build
            dump(output/'AUDIT_RECEIPT.json', receipt)
            for index, case in enumerate(cases, 1):
                print(f"[{index}/{len(cases)}] {case['case_id']}", flush=True)
                result = check_pair(case['cnf_resolved'], case['proof_resolved'],
                                    output/case['case_id'], binaries, args.timeout,
                                    args.heap_mb, args.stack_mb, args.c_diagnostic)
                result.update(case_id=case['case_id'], metadata=case.get('metadata', {}),
                              declared_cnf_sha256=case['cnf_sha256'],
                              declared_proof_sha256=case['proof_sha256'])
                receipt['cases'].append(result)
                receipt['seconds'] = round(time.monotonic()-started, 6)
                dump(output/'AUDIT_RECEIPT.json', receipt)
                require(result['input_sha256'] == {'cnf':case['cnf_sha256'], 'drat':case['proof_sha256']},
                        'Input file differs from its declared manifest hash during checking')
                require(result['status'] == 'PASS_CNF_UNSAT_VIA_CAKEML_LRAT',
                        'Proof check failed: ' + case['case_id'])
        receipt['status'] = 'PASS_ALL_DECLARED_CNF_CERTIFICATES'
        receipt['checked_cases'] = len(cases)
        receipt['declared_case_inventory_exactly_covered'] = True
        receipt['seconds'] = round(time.monotonic()-started, 6)
        dump(output/'AUDIT_RECEIPT.json', receipt)
    except Exception as error:
        receipt['status'], receipt['error'] = 'FAIL', str(error)
        receipt['seconds'] = round(time.monotonic()-started, 6)
        dump(output/'AUDIT_RECEIPT.json', receipt)
        raise
    print(json.dumps({k: receipt[k] for k in ('status', 'checked_cases', 'seconds',
                      'encoder_soundness_checked_by_this_run',
                      'orbit_catalogue_completeness_checked_by_this_run')}, indent=2))


if __name__ == '__main__':
    main()
