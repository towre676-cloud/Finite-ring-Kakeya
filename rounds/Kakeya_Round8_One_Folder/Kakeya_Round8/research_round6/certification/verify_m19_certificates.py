"""Replay all38 exact packaged-encoder CNFs against preserved CakeML certificates.

No SAT search, no PySAT, no network. Requires Python3, gcc, Linux x86_64.
Logical input.cnf/proof.drat/converted.lrat paths accept lossless .xz siblings.
By default, regenerate each CNF exactly and check its preserved LRAT directly.
Use --compressed-only to exercise compressed storage even while raw files exist.
Use --convert-drat to repeat DRAT-trim conversion, requiring extra disk space.
"""
from pathlib import Path
from contextlib import ExitStack
import argparse,importlib.util,json,re,tempfile,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
IMPORT=ROOT/'research_round6/imported_claude_round4'
def mod(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
A=mod('round6_replay_audit',ROOT/'research_round5/proof_audit/audit_certificates.py')
E=mod('round6_replay_encoder',IMPORT/'src/encode_cnf2.py')
STORE=mod('round6_replay_storage',HERE.parent/'certificate_storage.py')

def load_manifest_metadata(path):
 """Validate exact inventory and source pins; large blob hashes are checked per case.

 This retains the strict original manifest semantics while avoiding simultaneous
 decompression of every large certificate. No formula is credited before its own
 original CNF/DRAT/LRAT hashes and mandatory CakeML proof have all been checked.
 """
 path=Path(path).resolve();manifest=json.loads(path.read_text())
 A.require(manifest['schema']=='kakeya-proof-audit-v1','Unsupported manifest schema')
 expected=manifest['expected_case_ids']
 A.require(isinstance(expected,list) and expected and len(expected)==len(set(expected)),'Bad expected case inventory')
 cases=[];ids=[]
 for saved in manifest['cases']:
  case=dict(saved);cid=case['case_id'];ids.append(cid)
  A.require(isinstance(cid,str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*',cid),'Unsafe case identifier')
  for key in ('cnf','proof','lrat'):
   filename=case[key];digest=case[key+'_sha256']
   A.require(isinstance(filename,str) and not any(c in filename for c in '\x00\r\n'),'Invalid certificate path')
   A.require(isinstance(digest,str) and re.fullmatch(r'[0-9a-f]{64}',digest),'Expected literal SHA256')
   source=Path(filename)
   if not source.is_absolute():source=path.parent/source
   case[key+'_logical']=source.resolve()
  cases.append(case)
 A.require(len(ids)==len(set(ids)) and set(ids)==set(expected),'Actual case inventory differs from expected')
 refs=[]
 for reference in manifest.get('semantic_reference_files',[]):
  source=Path(reference['path'])
  if not source.is_absolute():source=path.parent/source
  A.require(source.is_file() and A.sha(source)==reference['sha256'],'Semantic source missing or changed')
  refs.append(reference)
 return manifest,cases,refs

def main():
 p=argparse.ArgumentParser();p.add_argument('--convert-drat',action='store_true');p.add_argument('--compressed-only',action='store_true');p.add_argument('--lrat-only',action='store_true',help='Replay CNF/LRAT certificates; retain original DRAT hash only as provenance, without requiring its search trace.');p.add_argument('--timeout',type=int,default=1800);p.add_argument('--heap-mb',type=int,default=1024);p.add_argument('--quick',action='store_true');args=p.parse_args()
 A.require(not(args.convert_drat and args.lrat_only),'--convert-drat and --lrat-only are incompatible')
 output=HERE/'fresh_replay';output.mkdir(exist_ok=True)
 receipt={'status':'RUNNING','cases':[]};A.dump(HERE/'M19_FRESH_REPLAY.json',receipt)
 started=time.monotonic()
 try:
  manifest,cases,refs=load_manifest_metadata(HERE/'M19_CERTIFICATE_MANIFEST.json')
  contract=A.check_marked_contract(manifest,cases,HERE/'M19_CERTIFICATE_MANIFEST.json')
  pins=A.verify_sources();receipt.update(manifest_sha256=A.sha(HERE/'M19_CERTIFICATE_MANIFEST.json'),contract_check=contract,checker_pins=pins,quick=args.quick,compressed_only=args.compressed_only,lrat_only=args.lrat_only,semantic_source_hashes_verified=refs,encoder_soundness_proved_by_this_run=False)
  selected=cases
  if args.quick:selected=[next(r for r in cases if len(r['marked_support']['support'])==s) for s in (11,12)]
  SPEC=E.load_spectra(IMPORT/'data/spec32.csv');M=E.load_M(IMPORT/'data/Mtable.txt');SUBS=E.all_subspaces()
  with tempfile.TemporaryDirectory(prefix='kakeya_round6_m19_replay_') as tmpname:
   tmp=Path(tmpname);bins,build=A.build_checkers(tmp/'bin',output/'build_logs');receipt['build']=build
   for index,case in enumerate(selected,1):
    cid=case['case_id'];folder=output/cid;folder.mkdir(exist_ok=True)
    support=case['marked_support']['support'];T=[x for x in support if x!=0]
    A.require(case['marked_support']['distinguished_hub']==0,'Encoder assumes hub zero')
    A.require(case['metadata']['m']==19 and case['metadata']['total_upper_bound']==93,'Wrong parameter metadata')
    A.require(case['metadata']['source_T_bitmask']==sum(1<<x for x in T),'Support bitmask metadata differs')
    f=E.encode(T,19,SPEC,M,SUBS);regen=tmp/'regenerated.cnf';E.write_dimacs(f,regen);del f
    A.require(A.sha(regen)==case['cnf_sha256'],'Deterministic CNF regeneration mismatch: '+cid)
    if args.compressed_only:
     for key in (('cnf','lrat') if args.lrat_only else ('cnf','proof','lrat')):A.require(Path(str(case[key+'_logical'])+'.xz').is_file(),'Missing required compressed blob')
    if not args.lrat_only:
     A.require(STORE.logical_sha(case['proof_logical'],prefer_compressed=args.compressed_only)==case['proof_sha256'],'Original DRAT bytes changed: '+cid)
    with ExitStack() as stack:
     cnf=stack.enter_context(STORE.materialized(case['cnf_logical'],case['cnf_sha256'],tmp,prefer_compressed=args.compressed_only))
     lrat=stack.enter_context(STORE.materialized(case['lrat_logical'],case['lrat_sha256'],tmp,prefer_compressed=args.compressed_only))
     header=A.cnf_header(cnf)
     if args.convert_drat:
      drat=stack.enter_context(STORE.materialized(case['proof_logical'],case['proof_sha256'],tmp,prefer_compressed=args.compressed_only))
      check=A.check_pair(cnf,drat,folder,bins,args.timeout,args.heap_mb,256,False)
      A.require(check['status']=='PASS_CNF_UNSAT_VIA_CAKEML_LRAT','Certificate replay failed: '+cid)
     else:
      check=A.run_checker([bins['cake_lpr'],'--CML_HEAP_SIZE='+str(args.heap_mb),'--CML_STACK_SIZE=256',cnf,lrat],folder,'cake_lpr',args.timeout,'s VERIFIED UNSAT',True)
      A.require(check['accepted'],'CakeML did not accept: '+cid)
     A.require(A.sha(cnf)==case['cnf_sha256'] and A.sha(lrat)==case['lrat_sha256'],'Checked bytes changed during replay')
    receipt['cases'].append({'case_id':cid,'cnf_regeneration':'BYTE_IDENTICAL','cnf_header':header,'cnf_sha256':case['cnf_sha256'],'original_drat_sha256':case['proof_sha256'],'preserved_lrat_sha256':case['lrat_sha256'],'all_three_original_byte_hashes_checked':not args.lrat_only,'original_drat_role':('PROVENANCE_HASH_ONLY_NOT_REPLAYED' if args.lrat_only else 'ORIGINAL_BYTES_HASH_VERIFIED'),'compressed_source_required':args.compressed_only,'check':check})
    receipt['seconds']=round(time.monotonic()-started,6);A.dump(HERE/'M19_FRESH_REPLAY.json',receipt)
    print(f'[{index}/{len(selected)}] {cid}: BYTE_IDENTICAL_CNF + CAKEML_ACCEPTED',flush=True)
  receipt.update(status='PASS_QUICK_TWO_CASES_ONLY' if args.quick else 'PASS_ALL_38_EXACT_CNF_REGENERATIONS_AND_CAKEML_CERTIFICATES',checked_cases=len(selected),seconds=round(time.monotonic()-started,6))
  A.dump(HERE/'M19_FRESH_REPLAY.json',receipt)
  print(receipt['status'],flush=True)
 except Exception as error:
  receipt.update(status='FAIL',error=repr(error),seconds=round(time.monotonic()-started,6));A.dump(HERE/'M19_FRESH_REPLAY.json',receipt);raise
if __name__=='__main__':main()
