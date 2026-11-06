#!/usr/bin/env python3
"""Isolated Round9: exact frozen next-frontier CNFs and certified outcomes."""
import argparse, concurrent.futures, gc, hashlib, importlib.util, json, lzma, os, shutil, sys, time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
def mod(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
N=mod('r9_frozen_next',ROOT/'research_round8/incidence/encode_next_frontier.py')
P=mod('r9_producer_tools',ROOT/'research_round7/support13/certify_support13.py')
A=P.A
def sha(p):return A.sha(p)
def dump(p,d):P.dump(p,d)
def source_hashes():
    paths=[HERE/'campaign.py',HERE/'solver_worker.py',ROOT/'research_round8/NEXT_ATTACK_QUEUE.json',ROOT/'research_round8/incidence/encode_next_frontier.py',ROOT/'research_round8/incidence/incidence_cuts.py',ROOT/'research_round8/strengthened/encode_strengthened.py',ROOT/'research_round6/encoder_audit/encode_maximal_cosets.py',ROOT/'research_round6/joint_maxima/encode_joint_maxima.py',ROOT/'research_round7/support13/rup_unit_solver.py']
    paths+=list((P.IMPORTED/'data').glob('*'))
    return {str(p.relative_to(ROOT)):sha(p) for p in paths if p.is_file()}
def compress(p):
    digest=sha(p);out=Path(str(p)+'.xz')
    with p.open('rb') as a,lzma.open(out,'wb',preset=1) as b:shutil.copyfileobj(a,b)
    with lzma.open(out,'rb') as f:
        h=hashlib.file_digest(f,'sha256').hexdigest()
    assert h==digest
    row={'raw_sha256':digest,'xz_sha256':sha(out),'raw_bytes':p.stat().st_size,'xz_bytes':out.stat().st_size};p.unlink();return row
def make(case):
    data=P.IMPORTED/'data'
    spec=N.load_spectra(data/'spec32.csv');tab=N.load_M(data/'Mtable.txt');subs=N.all_subspaces()
    return N.encode(case['support'][1:],case['maximum_interval'][0],spec,tab,subs)
def one(args):
    case,limit,tag,check_timeout=args
    folder=HERE/'cases'/(case['case_id'].replace('_pending','')+'_'+tag)
    folder.mkdir(parents=True,exist_ok=True)
    receipt=folder/'CASE_RECEIPT.json'
    if receipt.exists():return json.loads(receipt.read_text())
    pins=source_hashes();started=time.monotonic();cnf=folder/'input.cnf';proof=folder/'proof.drat'
    row={'case':case,'tag':tag,'source_hashes':pins,'status':'STARTING','exclusion_credited':False,'proof_format':'BINARY_DRAT_WITH_RUP_UNIT_PREFIX','search_limit_seconds':limit,'encoder_formalized':False}
    f=make(case);N.write_dimacs(f,cnf)
    row.update(cnf_sha256=sha(cnf),variables=f.n,clauses=len(f.cl),extension=f.r8_next_frontier_metadata,encode_seconds=time.monotonic()-started)
    del f;gc.collect()
    command=[sys.executable,str(HERE/'solver_worker.py'),str(cnf),str(proof),str(folder/'SEARCH.json'),str(ROOT/'research_round7/support13/rup_unit_solver.py')]
    result=P.run_guarded_solver(command,folder,limit,proof_byte_limit=768*1024**2,min_free_bytes=2*1024**3)
    row.update(result)
    assert sha(cnf)==row['cnf_sha256']
    if result['solver_returncode']==20:
        f=make(case);N.write_dimacs(f,folder/'regenerated.cnf');del f;gc.collect()
        assert sha(folder/'regenerated.cnf')==row['cnf_sha256'];(folder/'regenerated.cnf').unlink()
        binaries={x:HERE/'tools/bin'/x for x in ('drat-trim','lrat-check','cake_lpr')}
        row['audit']=A.check_pair(cnf,proof,folder/'audit',binaries,check_timeout,1024,256,False)
        row['exclusion_credited']=row['audit']['status']=='PASS_CNF_UNSAT_VIA_CAKEML_LRAT'
        row['status']='CERTIFIED_EXCLUSION' if row['exclusion_credited'] else 'CHECK_FAILED'
        (folder/'audit/converted.lrat').unlink(missing_ok=True)
    elif result['solver_returncode']==10:row['status']='SAT_RELAXATION_NO_RING_WITNESS'
    else:row['status']='UNKNOWN_TIMEOUT_OR_RESOURCE_STOP'
    row['storage']={'input.cnf':compress(cnf)}
    if row['exclusion_credited']:row['storage']['proof.drat']=compress(proof)
    else:proof.unlink(missing_ok=True)
    assert source_hashes()==pins
    row['seconds']=time.monotonic()-started;dump(receipt,row);return row
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=45);ap.add_argument('--jobs',type=int,default=4);ap.add_argument('--first',type=int,default=0);ap.add_argument('--tag',default='first45');ap.add_argument('--check-timeout',type=int,default=900);args=ap.parse_args()
    queue=json.loads((ROOT/'research_round8/NEXT_ATTACK_QUEUE.json').read_text())['cases']
    # Interleave the two exact maxima on each support for a balanced pilot.
    queue.sort(key=lambda c:(c['nonzero_support_mask'],c['maximum_interval'][0]))
    if args.first:queue=queue[:args.first]
    assert len({c['case_id'] for c in queue})==len(queue)
    pins=A.verify_sources();binaries,build=A.build_checkers(HERE/'tools/bin',HERE/'tools/build_logs');dump(HERE/'tools/BUILD.json',{'pins':pins,'build':build})
    import pysat,pysolvers
    dump(HERE/'SOLVER_PROVENANCE.json',{'python_sat_version':pysat.__version__,'native_extension_sha256':sha(Path(pysolvers.__file__)),'solver':'cadical195','solver_trusted':False})
    dump(HERE/'FROZEN_SOURCES.json',source_hashes())
    summary={'status':'RUNNING','expected_case_ids':[c['case_id'] for c in queue],'results':[],'new_exclusions':0,'base_round8_frontier_edited':False}
    out=HERE/('CAMPAIGN_'+args.tag+'.json');dump(out,summary)
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.jobs) as pool:
        futures=[pool.submit(one,(case,args.limit,args.tag,args.check_timeout)) for case in queue]
        for future in concurrent.futures.as_completed(futures):
            row=future.result();summary['results'].append(row);summary['new_exclusions']+=row['exclusion_credited'];dump(out,summary)
            print(row['case']['nonzero_support_mask'],row['case']['maximum_interval'],row['status'],round(row['seconds'],1),flush=True)
    summary['status']='COMPLETE_BOUNDED_CAMPAIGN';dump(out,summary)
    print('COMPLETE',len(queue),'CERTIFIED',summary['new_exclusions'],flush=True)
if __name__=='__main__':main()
