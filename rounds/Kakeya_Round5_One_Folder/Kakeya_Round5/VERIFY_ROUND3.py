"""Portable exact replay of the Kakeya round3 checkpoint and its inputs."""
from pathlib import Path
import hashlib
import json
import os
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent
if sys.flags.optimize:
    raise SystemExit('Assertions are required; run without -O or PYTHONOPTIMIZE.')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest_path=ROOT/'MANIFEST_ROUND3.json'
manifest=json.loads(manifest_path.read_text())
for item in manifest['files']:
    p=ROOT/item['path']
    if not p.is_file() or p.stat().st_size!=item['bytes'] or sha(p)!=item['sha256']:
        raise SystemExit('Payload hash mismatch: '+item['path'])
print('Initial payload hashes PASS: '+str(len(manifest['files']))+' files',flush=True)
frontier_initial=(ROOT/'Kakeya_Research_Frontier_Round3.json').read_bytes()
assert len((ROOT/'Kakeya_Research_Round3_Report.txt').read_text().split())==1500

steps=[
 ('inherited_round2_complete_replay','VERIFY_ALL.py'),
 ('caught_up_compatibility_package','research_round3/catchup/energy_compatibility/Kakeya_Energy_and_Compatibility_2026-10-27/verify_package.py'),
 ('shared_period_and_rooted_rank_controls','research_round3/root/verify_shared_geometry.py'),
 ('full_hub_outer_twelve_controls','research_round3/root/verify_full_hub_twelve.py'),
 ('m11_support17_assignment_duals','research_round3/m11/verify_s17_envelope_duals.py'),
 ('m11_support17_remaining_placements','research_round3/m11/verify_remaining_s17_placements.py'),
 ('m11_support16_six_classes','research_round3/m11/s16/verify_s16_checkpoint.py'),
 ('middle_complete_support18_exclusion','research_round3/middle/verify_support18_completion.py'),
 ('m19_common_rank_modes','research_round3/m19/verify_common_shape_certificates.py'),
 ('m19_deleted_direction','research_round3/m19/verify_deleted_direction_profile.py'),
 ('m19_common_periodic_modes','research_round3/m19/verify_own_periodic_certificates.py'),
 ('m19_normalized_support_roles','research_round3/m19/verify_unique_edge_roles.py'),
 ('independent_m19_role_review','research_round3/reviews/review_m19_role_certificates.py'),
 ('m19_disjoint_stage_accounting','research_round3/m19/build_m19_round3_manifest.py'),
 ('consolidated_round3_frontier','research_round3/root/build_round3_frontier.py'),
]
logs=ROOT/'verification_logs_round3'
logs.mkdir(exist_ok=True)
receipt={
 'status':'RUNNING','scope':'All credited round3 finite exclusions and controls, plus the included complete round2 replay. Analytic proofs are separately supplied and reviewed; inherited earlier full results are anchored to prior checkpoints.',
 'initial_manifest_sha256':sha(manifest_path),
 'initial_payload_files_verified':len(manifest['files']),
 'python_version':platform.python_version(),
 'steps':[],
}
target=ROOT/'VERIFICATION_RECEIPT_ROUND3.json'
env=dict(os.environ)
env.pop('PYTHONOPTIMIZE',None)
env['PYTHONDONTWRITEBYTECODE']='1'
started=time.monotonic()
for i,(name,relative) in enumerate(steps,1):
    print(f'[{i}/{len(steps)}] {name}',flush=True)
    log=logs/(name+'.txt')
    begin=time.monotonic()
    with log.open('w') as stream:
        result=subprocess.run([sys.executable,str(ROOT/relative)],cwd=ROOT,env=env,
                              stdout=stream,stderr=subprocess.STDOUT)
    row={'name':name,'script':relative,'status':'PASS' if result.returncode==0 else 'FAIL',
         'returncode':result.returncode,'seconds':round(time.monotonic()-begin,3),
         'log':str(log.relative_to(ROOT)),'log_sha256':sha(log)}
    receipt['steps'].append(row)
    receipt['seconds']=round(time.monotonic()-started,3)
    if result.returncode:
        receipt['status']='FAIL'
        target.write_text(json.dumps(receipt,indent=2)+'\n')
        print(log.read_text()[-12000:],file=sys.stderr)
        raise SystemExit('Verification failed: '+name)
    target.write_text(json.dumps(receipt,indent=2)+'\n')
    print('  PASS ('+str(row['seconds'])+' seconds)',flush=True)

assert (ROOT/'Kakeya_Research_Frontier_Round3.json').read_bytes()==frontier_initial
f=json.loads(frontier_initial)
receipt.update(status='PASS_ALL_ROUND3_REPLAY_STEPS',seconds=round(time.monotonic()-started,3),
               report_word_count=1500,regenerated_frontier_sha256=sha(ROOT/'Kakeya_Research_Frontier_Round3.json'),
               final_frontier={
                   'unrestricted_dimension5_theorem':f['unrestricted_dimension5_theorem'],
                   'm11_support_upper_bound':16,'m11_remaining_affine_classes':46,
                   'middle_support_upper_bound':17,'middle_support18_survivors':0,
                   'm19_round3_exclusions':26673,'m19_remaining_profiles':3798,
                   'full_hub_outer_cap12_theorem':'n>=6,sharp3*2^n-2,star equality',
               })
target.write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'status':receipt['status'],'seconds':receipt['seconds'],
                  'frontier':receipt['final_frontier']},indent=2),flush=True)
