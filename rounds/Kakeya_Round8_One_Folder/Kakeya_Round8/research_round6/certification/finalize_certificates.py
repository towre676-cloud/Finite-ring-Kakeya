"""Bind all 38 freshly checked formula/proof pairs to the complete support contract.

This does not redo checking: it validates all recorded hashes, checker transcripts,
and the exact inventory from completed per-case checks. Use verify_m19_certificates.py
for a fresh checker replay and deterministic CNF regeneration.
"""
from pathlib import Path
import importlib.util,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
IMPORT=ROOT/'research_round6/imported_claude_round4'
def mod(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
A=mod('round6_finalize_audit',ROOT/'research_round5/proof_audit/audit_certificates.py')
STORE=mod('round6_finalize_storage',HERE.parent/'certificate_storage.py')

def main():
 universe=json.loads((HERE/'CASE_UNIVERSE.json').read_text())
 case_ids=sorted(r['case_id'] for r in universe)
 manifest={'schema':'kakeya-proof-audit-v1','label':'Fresh exact packaged Claude Round4 CNFs: maximum19 support11/12, Round6 authoritative recertification','expected_case_ids':case_ids,'coverage_scope':'All 13 distinguished-hub support11 and all 25 distinguished-hub support12 classes at maximum fibre19; common necessary-condition relaxation for both rings; total at most93.','encoder_soundness_status':'A separate mathematical/code review is needed; the proof checker alone establishes exact CNF unsatisfiability.','orbit_catalogue_completeness_status':'Round5 complete normalized enumeration and Round6 exact bijection to imported catalogue.','coverage_contract':{'path':'../../research_round5/encoding_bridge/M19_MARKED_CASE_CONTRACT.json','sha256':A.M19_CONTRACT_SHA256,'ring_scope':'common_relaxation_both_rings'},'cases':[],'semantic_reference_files':[]}
 for relative in ['src/encode_cnf2.py','data/spec32.csv','data/Mtable.txt','data/orbits_all.txt','docs/SUPPORT_ORBIT_METHOD.md']:
  manifest['semantic_reference_files'].append({'path':'../imported_claude_round4/'+relative,'sha256':A.sha(IMPORT/relative)})
 summaries=[]
 for row in sorted(universe,key=lambda r:r['case_id']):
  case_id=row['case_id'];folder=HERE/'cases'/case_id
  r=json.loads((folder/'CASE_RECEIPT.json').read_text())
  A.require(r['status']=='PASS_CNF_UNSAT_VIA_CAKEML_LRAT','Not accepted: '+case_id)
  A.require(r['encoder_sha256']==A.sha(IMPORT/'src/encode_cnf2.py'),'Encoder changed')
  audit=r['audit'];A.require(audit['status']=='PASS_CNF_UNSAT_VIA_CAKEML_LRAT','Bad audit status')
  for field,name in [('cnf','input.cnf'),('proof','proof.drat')]:
   A.require(STORE.logical_sha(folder/name)==r[field+'_sha256'],'Changed case input '+case_id+'/'+name)
  A.require(STORE.logical_sha(folder/'audit/converted.lrat')==audit['lrat_sha256'],'Changed LRAT '+case_id)
  for name,check in [('drat_trim',audit['drat_trim']),('cake_lpr',audit['cake_lpr'])]:
   A.require(check['accepted'] and check['returncode']==0 and not check['timed_out'],'Recorded checker did not accept')
   for typ in ('stdout','stderr'):
    p=folder/'audit'/check[typ+'_file'];A.require(A.sha(p)==check[typ+'_sha256'],'Changed checker log')
  A.require((folder/'audit/cake_lpr.stdout.txt').read_text().strip()=='s VERIFIED UNSAT' and (folder/'audit/cake_lpr.stderr.txt').stat().st_size==0,'CakeML transcript mismatch')
  A.require(any(s.strip()=='s VERIFIED' for s in (folder/'audit/drat_trim.stdout.txt').read_text().splitlines()),'DRAT-trim marker absent')
  case={'case_id':case_id,'cnf':'cases/'+case_id+'/input.cnf','proof':'cases/'+case_id+'/proof.drat','cnf_sha256':r['cnf_sha256'],'proof_sha256':r['proof_sha256'],'lrat':'cases/'+case_id+'/audit/converted.lrat','lrat_sha256':audit['lrat_sha256'],'marked_support':r['marked_support'],'metadata':{'m':19,'total_upper_bound':93,'source_T_bitmask':r['T'],'support_size':r['support_size'],'encoder_sha256':r['encoder_sha256'],'original_solver_case_id':'claude_T_'+str(r['T']),'historical_CNF_sha256':r['historical_cnf_sha256'],'historical_proof_bytes_checked':False,'scope':'Fresh exact packaged encoder; no old-revision equivalence assumption.'}}
  manifest['cases'].append(case)
  summaries.append({'case_id':case_id,'support_size':r['support_size'],'T':r['T'],'cnf_sha256':r['cnf_sha256'],'proof_sha256':r['proof_sha256'],'lrat_sha256':audit['lrat_sha256'],'solve_seconds':r['solve_seconds'],'drat_trim_seconds':audit['drat_trim']['seconds'],'cake_lpr_seconds':audit['cake_lpr']['seconds'],'total_seconds':r['seconds'],'cnf_bytes':r['cnf_bytes'],'proof_bytes':r['proof_bytes'],'lrat_bytes':audit['lrat_bytes']})
 p=HERE/'M19_CERTIFICATE_MANIFEST.json';A.dump(p,manifest)
 REPLAY=mod('round6_finalize_loader',HERE/'verify_m19_certificates.py')
 checked,cases,refs=REPLAY.load_manifest_metadata(p)
 contract=A.check_marked_contract(checked,cases,p)
 receipt={'status':'PASS_ALL_38_FRESH_PACKAGED_ENCODER_CNF_CERTIFICATES','checked_cases':len(cases),'counts_by_support':{str(s):sum(r['support_size']==s for r in summaries) for s in (11,12)},'contract_check':contract,'manifest_sha256':A.sha(p),'encoder_soundness_proved_by_this_script':False,'proofs_regenerated_from_packaged_encoder':True,'historical_encoder_equivalence_assumed':False,'historical_proof_files_checked':False,'acceptance':'Each original DRAT converted by pinned DRAT-trim and each resulting LRAT accepted by pinned CakeML artifact against the same original CNF. This script audits stored evidence; verify_m19_certificates.py replays fresh.','cases':summaries,'totals':{k:sum(r[k] for r in summaries) for k in ('solve_seconds','drat_trim_seconds','cake_lpr_seconds','cnf_bytes','proof_bytes','lrat_bytes')}}
 A.dump(HERE/'M19_COMPLETE_CERTIFICATION_RECEIPT.json',receipt)
 print(json.dumps({k:receipt[k] for k in ('status','checked_cases','counts_by_support','totals')},indent=2))
if __name__=='__main__':main()
