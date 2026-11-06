"""Shared bindings for compact support-thirteen certificate delivery."""
from pathlib import Path
import importlib.util
import json
import os
import re
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'research_round7/support13/SUPPORT13_CERTIFICATE_MANIFEST.json'
MANIFEST = HERE / 'COMPACT_SUPPORT13_MANIFEST.json'
sys.path.insert(0, str(ROOT / 'research_round7/support13'))
import verify_support13 as V

A, C = V.A, V.C
CORE_PASS = 'PASS_CORE_DRAT_CHECKED_AGAINST_EXACT_ORIGINAL_CNF'


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


def safe_path(relative):
    path = Path(relative)
    result = (ROOT / path).resolve()
    A.require(not path.is_absolute() and result.is_relative_to(ROOT), 'Unsafe relative path')
    return result


def source_inventory():
    digest = A.sha(SOURCE)
    manifest, catalogue = V.load_manifest(check_artifact_bytes=False)
    A.require(A.sha(SOURCE) == digest, 'Source manifest changed while read')
    return manifest, catalogue, digest


def check_original_row(row):
    """Check immutable production evidence without reading its old proof."""
    A.require(re.fullmatch(r'[A-Za-z0-9_]+', row['case_id']) is not None, 'Unsafe case id')
    path = safe_path(row['receipt'])
    A.require(A.sha(path) == row['receipt_sha256'], 'Original production receipt changed')
    receipt = json.loads(path.read_text())
    if row['inherited']:
        expected_status = 'PASS_CNF_UNSAT_VIA_CAKEML_LRAT'
    elif row.get('encoder_kind') == 'audited_common_variant':
        expected_status = 'PASS_EXACT_VARIANT_CNF_DRAT_CAKEML'
    else:
        expected_status = 'PASS_EXACT_CNF_DRAT_TO_CAKEML'
    A.require(receipt['status'] == expected_status, 'Original case was not accepted')
    A.require(receipt['cnf_sha256'] == row['cnf_sha256'], 'Original CNF binding differs')
    if not row['inherited']:
        proof_hash = receipt.get('proof_sha256', receipt.get('drat_sha256'))
        A.require(proof_hash == row['proof_sha256'], 'Original DRAT binding differs')
        A.require(receipt['support'] == row['support']
                  and receipt['maximum_interval'] == row['maximum_interval'],
                  'Original mathematical scope differs')
    return receipt


def validate_existing_core(row):
    folder = HERE / 'cases' / row['case_id']
    path = folder / 'CORE_RECEIPT.json'
    A.require(path.is_file(), 'Missing compact production receipt')
    result = json.loads(path.read_text())
    A.require(result['status'] == CORE_PASS and result['original_case'] == row,
              'Compact receipt does not bind the exact original case')
    A.require(result['audit']['status'] == 'PASS_CNF_UNSAT_VIA_CAKEML_LRAT', 'Core lacked CakeML acceptance')
    A.require(result['audit']['input_sha256'] == {'cnf': row['cnf_sha256'], 'drat': result['core_sha256']},
              'Core checker used different bytes')
    stored = folder / 'core.drat.xz'
    A.require(A.sha(stored) == result['storage']['xz_sha256'], 'Stored core changed')
    A.require(C.logical_sha(folder / 'core.drat', prefer_compressed=True) == result['core_sha256'],
              'Decoded stored core changed')
    return result


def global_source_hashes(source_manifest):
    paths = {HERE / name for name in ('common.py', 'produce_cores.py', 'verify_compact_support13.py',
                                    'run_disjoint_worker.py')}
    paths |= {
        ROOT / 'research_round7/support13/verify_support13.py',
        ROOT / 'research_round7/support13/certify_support13.py',
        ROOT / 'research_round5/proof_audit/audit_certificates.py',
        ROOT / 'research_round6/certificate_storage.py',
    }
    paths |= {ROOT / relative for relative in source_manifest['semantic_input_hashes']}
    paths.add(ROOT / source_manifest['geometry_mapping']['path'])
    if 'inherited_frontier' in source_manifest:
        paths.add(ROOT / source_manifest['inherited_frontier']['path'])
    for row in source_manifest['cases']:
        paths |= {ROOT / relative for relative in row.get('variant_semantic_input_hashes', {})}
    return {str(path.relative_to(ROOT)): A.sha(path) for path in sorted(paths)}
