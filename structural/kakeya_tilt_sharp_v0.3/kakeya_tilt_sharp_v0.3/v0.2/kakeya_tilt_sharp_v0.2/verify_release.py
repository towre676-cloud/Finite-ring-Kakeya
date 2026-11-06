"""Verify the delivered mathematics with standard-library exact arithmetic."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--full',action='store_true',help='also replay the complete arithmetic census and finite n=3 proofs')
    args=ap.parse_args()
    root=Path(__file__).resolve().parent
    out=root/'verification_results'
    out.mkdir(exist_ok=True)
    started=time.perf_counter()
    results=[]
    manifest=root/'MANIFEST.sha256'
    if manifest.exists():
        checked=0
        for line in manifest.read_text().splitlines():
            digest,relative=line.split('  ',1)
            p=root/relative
            actual=hashlib.sha256(p.read_bytes()).hexdigest()
            if actual!=digest: raise AssertionError('File changed: '+relative)
            checked+=1
        results.append({'name':'file_integrity','status':'passed','files':checked})
    with tempfile.TemporaryDirectory(prefix='kakeya_v02_verify_') as temp:
        stage=Path(temp)/'package'
        shutil.copytree(root,stage,ignore=shutil.ignore_patterns('verification_results','__pycache__','*.pyc'))
        jobs=[
            ('spectral_theory',['extension/theory/verify_theory.py']),
            ('carry_transfer',['extension/gauge/carry_transfer.py']),
            ('independent_plane_and_local_census',['extension/solver/audit_replay.py']),
            ('shared_period_capacity',['extension/solver/period_replay.py']),
            ('nonfull_24_point_family',['extension/solver/nonfull_family_replay.py']),
            ('trace_laws',['extension/trace/trace_law.py','--profile','standard' if args.full else 'quick']),
        ]
        proof_code="from pathlib import Path; from certified_sat import verify_drat; import json; print(json.dumps({r:verify_drat(Path('proof_'+r+'_n2_m9.cnf'),Path('proof_'+r+'_n2_m9.drat')) for r in ('Z4','D2')},indent=2))"
        jobs.append(('stored_sat_refutations',['-c',proof_code],'extension/solver'))
        if args.full:
            jobs.extend([
                ('n3_lower_bound',['extension/solver/finite_certificate.py','--ub','21','--nodes','2000000','--output','finite_lower_check.json']),
                ('n3_equality_profile',['extension/solver/finite_certificate.py','--ub','22','--exclude-star','--nodes','2000000','--output','finite_equality_check.json']),
            ])
            source=stage/'extension/solver/finite_n3_nonfull_23_period.json'
            if source.exists() and json.loads(source.read_text()).get('status')=='INFEASIBLE':
                jobs.append(('n3_nonfull_gap',['extension/solver/finite_certificate.py','--ub','23','--cap','7','--period','--nodes','1000000','--output','finite_nonfull_check.json']))
        for job in jobs:
            name,argv=job[:2]
            cwd=stage/job[2] if len(job)>2 else stage
            print('Checking '+name+' ...',flush=True)
            t=time.perf_counter()
            result=subprocess.run([sys.executable,*argv],cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            (out/(name+'.log')).write_text(result.stdout)
            if result.returncode:
                raise RuntimeError(name+' failed; see '+str(out/(name+'.log')))
            if name.startswith('n3_'):
                parsed=json.loads(result.stdout)
                if parsed.get('status')!='INFEASIBLE':
                    raise AssertionError(name+' did not finish a proof: '+parsed.get('status','missing'))
            results.append({'name':name,'status':'passed','seconds':round(time.perf_counter()-t,4)})
    summary={'release':'0.2','profile':'full' if args.full else 'standard-library quick',
             'status':'passed','checks':results,'seconds':round(time.perf_counter()-started,4)}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
