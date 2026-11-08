#!/usr/bin/env python3
"""Compose a new ledger without rewriting any recovered historical record."""
from pathlib import Path
from collections import Counter
import json
from campaign import R
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
old=json.loads((ROOT/'research_round9/REMAINING_CASES.json').read_text())['cases']
runs=[json.loads(p.read_text()) for p in sorted((HERE/'cases').glob('*/RECEIPT.json'))]
projected={r['case']['case_id']:r for r in runs if r['variant']=='projected'}
if set(projected)!={r['case']['case_id'] for r in old}:raise ValueError('The 25-case sweep is incomplete')
accepted=set()
for path in sorted((HERE/'cases').glob('*/RECEIPT.json')):
 r=json.loads(path.read_text())
 if r['exclusion_credited']:
  if r['status']!='CERTIFIED_EXCLUSION' or r['audit']['status']!='PASS_CNF_UNSAT_VIA_CAKEML_LRAT':raise ValueError('Unverified credit')
  if r['audit']['input_sha256']!={'cnf':r['cnf_sha256'],'drat':r['storage']['proof.drat']['raw_sha256']}:raise ValueError('Input hash binding')
  if (path.parent/'audit_cake_lpr.stdout.txt').read_text()!='s VERIFIED UNSAT\n':raise ValueError('Missing checker acceptance')
  for step in ['drat_trim','cake_lpr']:
   for suffix in ['stdout','stderr']:
    if R.sha(path.parent/f'audit_{step}.{suffix}.txt')!=r['audit'][step][suffix+'_sha256']:raise ValueError('Checker log hash')
  accepted.add(r['case']['case_id'])
rows=[]
for p in sorted((ROOT/'research_round9/cases').glob('*/CASE.json')):
 r=json.loads(p.read_text())
 if r['case']['case_id'] in accepted:r['exclusion_credited']=True
 rows.append(r)
frontier=R.merge(rows)
frontier.update(status='ROUND10_NEW_CERTIFICATES_COMPOSED_WITH_HISTORICAL_LEDGER',historical_29_proofs_freshly_replayed=False,
                new_exclusions_credited=len(accepted),new_proof_streams_checked=sum(r['exclusion_credited'] for r in runs),
                combined_recovered_cases_certified=29+len(accepted))
bymax=Counter(r['case']['maximum_interval'][0] for r in old if r['case']['case_id'] in accepted)
remaining=Counter(r['case']['maximum_interval'][0] for r in old if r['case']['case_id'] not in accepted)
queue=[]
for original in old:
 c=original['case'];run=projected[c['case_id']]
 queue.append({'case_id':c['case_id'],'support':c['support'],'nonzero_support_mask':c['nonzero_support_mask'],
  'unmarked_affine_class':c['unmarked_affine_class'],'distinguished_hub':0,'maximum_interval':c['maximum_interval'],
  'total_upper_bound':93,'ring_scope':c['ring_scope'],'original_cnf_sha256':original['cnf_sha256'],
  'candidate_cuts_already_in_original':c['new_available_cuts'],'round10_search_performed':True,
  'projected_cnf_sha256':run['cnf_sha256'],'status':'CERTIFIED_EXCLUSION' if c['case_id'] in accepted else run['status'],
  'projected_search_status':run['status'],'projected_stop_reason':run['stop_reason'],
  'accepted_variants':[{'variant':r['variant'],'cnf_sha256':r['cnf_sha256']} for r in runs if r['case']['case_id']==c['case_id'] and r['exclusion_credited']],
  'exclusion_credited':c['case_id'] in accepted})
report={'base_commit':'de29e4473bfe4c46a90ccb85a33ad44b7a203caa','newly_excluded_cases':len(accepted),
 'new_by_maximum':dict(bymax),'remaining_cases':25-len(accepted),'remaining_by_maximum':dict(remaining),
 'search_limit_seconds_other_cases':90,'target_comparison_limit_seconds':120,
 'baseline_control_limits_seconds':sorted({r['limit_seconds'] for r in runs if r['variant']=='baseline'}),
 'frontier':frontier,'cases':queue,'full_n5_theorem':'OPEN','all_dimensional_law':'OPEN',
 'historical_queue_correction':'The four candidate cuts and proof search were already applied to every recovered Round9 formula; nested pending fields are historical snapshots.',
 'search_speed_claim':'No general speedup established. Target baseline was faster than projection in the paired run.'}
R.dump(HERE/'RESULTS.json',report)
print(json.dumps({k:report[k] for k in ['newly_excluded_cases','new_by_maximum','remaining_cases','remaining_by_maximum']},indent=2))
