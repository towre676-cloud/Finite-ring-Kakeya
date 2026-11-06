"""Verify this package with the Python standard library, without changing it.

The complete archived SAT-encoder audit can additionally be repeated with
the optional dependency documented in compute/README.md. This entry point
checks the saved cases and the included finite mathematical controls.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main():
    if sys.flags.optimize:
        raise SystemExit('Run without -O or -OO: verification uses assertions.')
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / 'MANIFEST.json').read_text())
    for relative, expected in manifest['sha256'].items():
        path = root / relative
        if not path.is_file():
            raise SystemExit('Missing package file: ' + relative)
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit('SHA256 mismatch: ' + relative)
    scripts = [
        'analytic/check_three_images.py',
        'analytic/check_image_structure.py',
        'energy/finite_energy.py',
        'compute/verify_completion_results.py',
        'review/verify_independent.py',
    ]
    results = []
    # The component scripts regenerate receipts next to themselves. Isolate
    # those writes so archive integrity survives repeated verification.
    with tempfile.TemporaryDirectory(prefix='kakeya_verify_') as temp:
        copy = Path(temp) / 'package'
        shutil.copytree(root, copy, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        for script in scripts:
            print('Checking ' + script, flush=True)
            result = subprocess.run([sys.executable, '-B', str(copy / script)],
                                    cwd=copy, capture_output=True, text=True)
            if result.returncode:
                print(result.stdout, end='')
                print(result.stderr, end='', file=sys.stderr)
                raise SystemExit(result.returncode)
            results.append({'script': script, 'status': 'PASS'})
    print(json.dumps({
        'status': 'PASS',
        'manifest_files_checked': len(manifest['sha256']),
        'checks': results,
        'scope': 'Included finite controls and fixed-shape certificates; no unrestricted n5 theorem',
        'package_modified': False,
    }, indent=2))


if __name__ == '__main__':
    main()
