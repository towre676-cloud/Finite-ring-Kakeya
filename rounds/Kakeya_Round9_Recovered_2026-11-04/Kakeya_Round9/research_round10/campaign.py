#!/usr/bin/env python3
"""Bounded exact-formula search; credit requires DRAT -> pinned CakeML LRAT."""
import argparse, concurrent.futures, gc, importlib.util, json, lzma, shutil, sys, tempfile, time
from pathlib import Path
import encode_projected as E
import pysat, pysolvers
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
spec=importlib.util.spec_from_file_location('round10_recovery',ROOT/'research_round9/recover.py')
R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R)

def sources():
    return {**R.sources(), **{str(p.relative_to(ROOT)):R.sha(p) for p in
            [Path(__file__),HERE/'encode_projected.py']}}

def one(args):
    old, variant, limit = args
    case=old['case']; dest=HERE/'cases'/(case['case_id'].replace('_incidence_pending','')+'_'+variant)
    if (dest/'RECEIPT.json').exists(): return json.loads((dest/'RECEIPT.json').read_text())
    dest.mkdir(parents=True,exist_ok=True); start=time.monotonic(); pins=sources()
    row={'case':case,'variant':variant,'baseline_expected_sha256':old['cnf_sha256'],
         'source_hashes':pins,'limit_seconds':limit,'exclusion_credited':False,
         'solver':{'python_sat':pysat.__version__,'native_sha256':R.sha(Path(pysolvers.__file__)),'engine':'cadical195','trusted':False}}
    with tempfile.TemporaryDirectory(prefix='r10_') as tmp:
        work=Path(tmp);cnf=work/'input.cnf';proof=work/'proof.drat'
        f=R.formula(case); E.N.write_dimacs(f,cnf)
        if R.sha(cnf)!=old['cnf_sha256']: raise ValueError('Baseline hash mismatch')
        row['baseline_regenerated']=True
        row['baseline_variables']=f.n;row['baseline_clauses']=len(f.cl)
        row['projection']=E.append_projection(f,case['support'],case['maximum_interval'][0],enabled=variant=='projected')
        E.N.write_dimacs(f,cnf);row.update(cnf_sha256=R.sha(cnf),variables=f.n,clauses=len(f.cl));del f;gc.collect()
        command=[sys.executable,str(ROOT/'research_round9/solver_worker.py'),str(cnf),str(proof),str(work/'SEARCH.json'),str(ROOT/'research_round7/support13/rup_unit_solver.py')]
        row.update(R.P.run_guarded_solver(command,work,limit,proof_byte_limit=256*1024**2,min_free_bytes=512*1024**2))
        if R.sha(cnf)!=row['cnf_sha256']: raise ValueError('Formula changed during search')
        if row['solver_returncode']==20:
            f=R.formula(case);E.append_projection(f,case['support'],case['maximum_interval'][0],enabled=variant=='projected');E.N.write_dimacs(f,work/'regenerated.cnf');del f;gc.collect()
            if R.sha(work/'regenerated.cnf')!=row['cnf_sha256']:raise ValueError('Post-search formula mismatch')
            bins={k:HERE/'tools/bin'/k for k in ('drat-trim','lrat-check','cake_lpr')}
            row['audit']=R.A.check_pair(cnf,proof,work/'audit',bins,120,512,128,False)
            row['exclusion_credited']=row['audit']['status']=='PASS_CNF_UNSAT_VIA_CAKEML_LRAT'
            row['status']='CERTIFIED_EXCLUSION' if row['exclusion_credited'] else 'UNCERTIFIED_CHECK_FAILURE'
        elif row['solver_returncode']==10:row['status']='SAT_RELAXATION_NO_RING_WITNESS'
        elif row['stop_reason']:row['status']='UNKNOWN_RESOURCE_LIMIT'
        else:row['status']='SEARCH_ERROR'
        row['storage']={'input.cnf':R.pack(cnf,dest/'input.cnf.xz')}
        if row['exclusion_credited']:row['storage']['proof.drat']=R.pack(proof,dest/'proof.drat.xz')
        for p in list(work.glob('*.json'))+list(work.glob('*.txt'))+list((work/'audit').glob('*.txt')):
            shutil.copy2(p,dest/(('audit_' if p.parent.name=='audit' else '')+p.name))
        if sources()!=pins:raise ValueError('Source changed during search')
    row['seconds']=round(time.monotonic()-start,6);R.dump(dest/'RECEIPT.json',row)
    return row

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--target',action='store_true');ap.add_argument('--variant',choices=['baseline','projected','both'],default='projected');ap.add_argument('--jobs',type=int,default=2);ap.add_argument('--limit',type=int,default=90);a=ap.parse_args()
    R.A.verify_sources()
    queue=json.loads((ROOT/'research_round9/REMAINING_CASES.json').read_text())['cases']
    if a.target:queue=queue[:1]
    variants=['baseline','projected'] if a.variant=='both' else [a.variant]
    args=[(row,v,a.limit) for row in queue for v in variants]
    with concurrent.futures.ProcessPoolExecutor(max_workers=a.jobs) as pool:
        for row in pool.map(one,args):
            print(row['case']['nonzero_support_mask'],row['case']['maximum_interval'][0],row['variant'],row['status'],round(row['solve_seconds'],2),flush=True)
    rows=[json.loads(p.read_text()) for p in sorted((HERE/'cases').glob('*/RECEIPT.json'))]
    accepted={r['case']['case_id'] for r in rows if r['exclusion_credited']}
    original=json.loads((ROOT/'research_round9/REMAINING_CASES.json').read_text())['cases']
    report={'newly_excluded_cases':len(accepted),'remaining_cases':len(original)-len(accepted),'accepted_case_ids':sorted(accepted),'remaining_case_ids':[r['case']['case_id'] for r in original if r['case']['case_id'] not in accepted],'runs':[{k:r[k] for k in ['case','variant','status','cnf_sha256','solve_seconds','exclusion_credited']} for r in rows], 'full_n5_theorem':'OPEN','all_dimensional_law':'OPEN'}
    R.dump(HERE/'CAMPAIGN.json',report);print('TOTAL NEWLY EXCLUDED',len(accepted),flush=True)
if __name__=='__main__':
    if sys.flags.optimize:raise SystemExit('Run without -O')
    main()
