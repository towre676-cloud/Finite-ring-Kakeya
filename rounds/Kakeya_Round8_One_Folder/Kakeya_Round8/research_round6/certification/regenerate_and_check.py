"""Regenerate exact imported m19 CNFs and preserve independently checked proofs.

CaDiCaL is an untrusted search tool. Mandatory acceptance is through the pinned
Round5 DRAT-trim -> CakeML path. This does not prove encoder soundness.
"""
from pathlib import Path
import argparse, concurrent.futures, hashlib, importlib.util, json, os, subprocess, time
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
IMPORT=ROOT/'research_round6/imported_claude_round4'

def module(name,path):
 s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
E=module('round6_exact_encoder',IMPORT/'src/encode_cnf2.py')
A=module('round6_pinned_audit',ROOT/'research_round5/proof_audit/audit_certificates.py')
MAP=module('round6_case_mapper',ROOT/'research_round5/encoding_bridge/map_marked_case.py')

def dump(path,value):
 path=Path(path); tmp=path.with_suffix(path.suffix+'.tmp'); tmp.write_text(json.dumps(value,indent=2)+'\n'); tmp.replace(path)

def cases():
 result=[]
 old={r['T']:r for r in map(json.loads,(IMPORT/'results/m19_s11_12.jsonl').read_text().splitlines())}
 for line in (IMPORT/'data/orbits_all.txt').read_text().splitlines():
  k,mask,stab,cover=map(int,line.split())
  if cover and k+1 in (11,12):
   support=[0]+[x for x in range(1,32) if mask>>x&1]
   row=MAP.map_marked_support(support,0)
   row.update(m=19,T=mask,stabilizer=stab,historical_log=old[mask])
   result.append(row)
 assert len(result)==len({r['case_id'] for r in result})==38
 return result

def one(task):
 row,solver,timeout,heap=task
 folder=HERE/'cases'/row['case_id']; folder.mkdir(parents=True,exist_ok=True)
 receipt=folder/'CASE_RECEIPT.json'
 cnf,proof=folder/'input.cnf',folder/'proof.drat'
 # Resume only from already accepted exact files, with recorded hashes checked.
 if receipt.exists():
  prior=json.loads(receipt.read_text())
  if prior.get('status')=='PASS_CNF_UNSAT_VIA_CAKEML_LRAT' and cnf.exists() and proof.exists():
   if A.sha(cnf)==prior['cnf_sha256'] and A.sha(proof)==prior['proof_sha256'] and A.sha(folder/'audit/converted.lrat')==prior['audit']['lrat_sha256']:
    return prior
 start=time.monotonic()
 record={'status':'ENCODING','case_id':row['case_id'],'m':19,'support_size':row['support_size'],'T':row['T'],'marked_support':{'support':row['source_support'],'distinguished_hub':0,'affine_map_to_contract':row['affine_map_to_contract']},'encoder_sha256':A.sha(IMPORT/'src/encode_cnf2.py'),'historical_cnf_sha256':row['historical_log']['cnf_sha256'],'solver_path':solver}
 dump(receipt,record)
 try:
  SPEC=E.load_spectra(IMPORT/'data/spec32.csv'); M=E.load_M(IMPORT/'data/Mtable.txt'); SUBS=E.all_subspaces()
  f=E.encode([x for x in row['source_support'] if x],19,SPEC,M,SUBS)
  E.write_dimacs(f,cnf)
  record.update(cnf_sha256=A.sha(cnf),cnf_bytes=cnf.stat().st_size,variables=f.n,clauses=len(f.cl),encode_seconds=round(time.monotonic()-start,6),status='SOLVING')
  del f
  dump(receipt,record)
  solve_start=time.monotonic()
  command=[solver,'--no-binary','--no-witness','-t',str(timeout),str(cnf),str(proof)]
  with (folder/'solver.stdout.txt').open('wb') as out,(folder/'solver.stderr.txt').open('wb') as err:
   try:
    r=subprocess.run(command,stdout=out,stderr=err,timeout=timeout+30)
    code=r.returncode
   except subprocess.TimeoutExpired:
    code=None
  record.update(solver_returncode=code,solve_seconds=round(time.monotonic()-solve_start,6),solver_command=command)
  if code!=20 or 's UNSATISFIABLE' not in (folder/'solver.stdout.txt').read_text():
   record.update(status='UNACCEPTED_SOLVER_RESULT',seconds=round(time.monotonic()-start,6)); dump(receipt,record); return record
  record.update(status='CHECKING',proof_sha256=A.sha(proof),proof_bytes=proof.stat().st_size)
  dump(receipt,record)
  binaries={name:HERE/'bin'/name for name in ('drat-trim','lrat-check','cake_lpr')}
  audit=A.check_pair(cnf,proof,folder/'audit',binaries,timeout,heap,256,False)
  record.update(status=audit['status'],audit=audit,seconds=round(time.monotonic()-start,6))
  dump(receipt,record)
 except Exception as error:
  record.update(status='ERROR',error=repr(error),seconds=round(time.monotonic()-start,6)); dump(receipt,record)
 return record

def main():
 p=argparse.ArgumentParser(); p.add_argument('--solver',default='/tmp/kakeya_lean_round4/lean-4.24.0-linux/bin/cadical');p.add_argument('--jobs',type=int,default=2);p.add_argument('--timeout',type=int,default=1800);p.add_argument('--heap-mb',type=int,default=1024);p.add_argument('--pilot',action='store_true');p.add_argument('--case-id',action='append',default=[]);args=p.parse_args()
 if not 1<=args.jobs<=2:raise ValueError('Use one or two solver workers')
 rows=cases();dump(HERE/'CASE_UNIVERSE.json',rows)
 pins=A.verify_sources();binaries,build=A.build_checkers(HERE/'bin',HERE/'build_logs')
 version=subprocess.run([args.solver,'--version'],capture_output=True,text=True,check=True).stdout.strip()
 dump(HERE/'BUILD_RECEIPT.json',{'pins':pins,'build':build,'solver_version':version,'solver_binary_sha256':A.sha(args.solver),'encoder_sha256':A.sha(IMPORT/'src/encode_cnf2.py')})
 if args.pilot:
  rows=[min((r for r in rows if r['support_size']==s),key=lambda r:r['historical_log']['solve_sec']) for s in (11,12)]
 if args.case_id:rows=[r for r in rows if r['case_id'] in args.case_id]
 # Expensive historical cases first once pilot established resource behavior.
 rows.sort(key=lambda r:r['historical_log']['solve_sec'],reverse=True)
 started=time.monotonic();results=[]
 with concurrent.futures.ProcessPoolExecutor(args.jobs) as pool:
  futures={pool.submit(one,(row,args.solver,args.timeout,args.heap_mb)):row for row in rows}
  for future in concurrent.futures.as_completed(futures):
   r=future.result();results.append(r)
   print(json.dumps({k:r.get(k) for k in ('case_id','status','encode_seconds','solve_seconds','seconds','proof_bytes')}),flush=True)
   dump(HERE/('PILOT_RECEIPT.json' if args.pilot else ('SELECTED_REGENERATION_RECEIPT.json' if args.case_id else 'REGENERATION_RECEIPT.json')),{'status':'RUNNING','requested_cases':len(rows),'completed_cases':len(results),'cases':results,'seconds':round(time.monotonic()-started,6)})
 good=all(r['status']=='PASS_CNF_UNSAT_VIA_CAKEML_LRAT' for r in results)
 dump(HERE/('PILOT_RECEIPT.json' if args.pilot else ('SELECTED_REGENERATION_RECEIPT.json' if args.case_id else 'REGENERATION_RECEIPT.json')),{'status':'PASS_ALL_REQUESTED_CNF_CERTIFICATES' if good else 'INCOMPLETE_OR_FAILED','requested_cases':len(rows),'completed_cases':len(results),'cases':results,'seconds':round(time.monotonic()-started,6),'encoder_soundness_proved_by_this_run':False,'historical_proof_bytes_checked':False})
 print('ALL_REQUESTED_PASS' if good else 'INCOMPLETE_OR_FAILED',flush=True)

if __name__=='__main__':main()
