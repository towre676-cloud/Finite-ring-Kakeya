#!/usr/bin/env python3
"""Reconstruct the complete Round9 experiment and save immutable case files.

Original raw files were lost. These are regenerated replacements. Old timing
logs cannot be reconstructed. No original-proof byte identity is asserted.
"""
from pathlib import Path
import argparse,concurrent.futures,gc,hashlib,importlib.util,json,lzma,shutil,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[1];HERE=ROOT/'research_round9'
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
N=module('recovery_next_frontier',ROOT/'research_round8/incidence/encode_next_frontier.py')
P=module('recovery_supervision',ROOT/'research_round7/support13/certify_support13.py')
A=P.A
TARGETS={12:{75737494,109144470,110453014,153184662,157376918,291627286,375492886,376013078,411130262,411134358,673786198,2187956502,2254541078},13:{75737494,109144470,153184662,157376918,291627286,375492886,376013078,411130262,411134358,673786198,675891606,1116316054,2187956502,2254541078}}
def sha(p):return A.sha(p)
def dump(p,v):P.dump(p,v)
def sources():
    files=[Path(__file__),HERE/'solver_worker.py',ROOT/'research_round8/NEXT_ATTACK_QUEUE.json',ROOT/'research_round8/incidence/encode_next_frontier.py',ROOT/'research_round8/incidence/incidence_cuts.py',ROOT/'research_round8/strengthened/encode_strengthened.py',ROOT/'research_round6/joint_maxima/encode_joint_maxima.py',ROOT/'research_round6/encoder_audit/encode_maximal_cosets.py',ROOT/'research_round7/support13/rup_unit_solver.py']
    files+=list((P.IMPORTED/'data').glob('*'))
    return {str(p.relative_to(ROOT)):sha(p) for p in files if p.is_file()}
def formula(case):
    data=P.IMPORTED/'data'
    return N.encode(case['support'][1:],case['maximum_interval'][0],N.load_spectra(data/'spec32.csv'),N.load_M(data/'Mtable.txt'),N.all_subspaces())
def pack(source,dest):
    info={'raw_sha256':sha(source),'raw_bytes':source.stat().st_size}
    with source.open('rb') as a,lzma.open(dest,'wb',preset=1) as b:shutil.copyfileobj(a,b)
    with lzma.open(dest,'rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==info['raw_sha256']
    info.update(xz_sha256=sha(dest),xz_bytes=dest.stat().st_size);return info
def unpack(source,dest,info):
    assert sha(source)==info['xz_sha256']
    with lzma.open(source,'rb') as a,dest.open('wb') as b:shutil.copyfileobj(a,b)
    assert sha(dest)==info['raw_sha256']
def case_dir(case):return HERE/'cases'/case['case_id'].replace('_pending','_recovered')
def produce(args):
    case,limit=args;dest=case_dir(case)
    if (dest/'CASE.json').exists():return json.loads((dest/'CASE.json').read_text())
    pins=sources();started=time.monotonic();dest.mkdir(parents=True,exist_ok=True)
    row={'case':case,'source_hashes':pins,'provenance':'REGENERATED_AFTER_WORKSPACE_MAINTENANCE','original_proof_byte_identity':'UNAVAILABLE_FOR_COMPARISON','limit_seconds':limit,'exclusion_credited':False}
    with tempfile.TemporaryDirectory(prefix='kakeya_reconstruct_') as temp:
        work=Path(temp);cnf=work/'input.cnf';proof=work/'proof.drat'
        f=formula(case);N.write_dimacs(f,cnf)
        row.update(cnf_sha256=sha(cnf),variables=f.n,clauses=len(f.cl),extension=f.r8_next_frontier_metadata)
        assert A.cnf_header(cnf)=={'variables':f.n,'clauses':len(f.cl)}
        del f;gc.collect()
        command=[sys.executable,str(HERE/'solver_worker.py'),str(cnf),str(proof),str(work/'SEARCH.json'),str(ROOT/'research_round7/support13/rup_unit_solver.py')]
        row.update(P.run_guarded_solver(command,work,limit,proof_byte_limit=768*1024**2,min_free_bytes=2*1024**3))
        assert sha(cnf)==row['cnf_sha256']
        if row['solver_returncode']==20:
            f=formula(case);N.write_dimacs(f,work/'regenerated.cnf');del f;gc.collect()
            assert sha(work/'regenerated.cnf')==row['cnf_sha256']
            binaries={k:HERE/'tools/bin'/k for k in ('drat-trim','lrat-check','cake_lpr')}
            row['audit']=A.check_pair(cnf,proof,work/'audit',binaries,900,1024,256,False)
            row['exclusion_credited']=row['audit']['status']=='PASS_CNF_UNSAT_VIA_CAKEML_LRAT'
            row['status']='CERTIFIED_EXCLUSION' if row['exclusion_credited'] else 'UNCERTIFIED_CHECK_FAILURE'
        elif row['solver_returncode']==10:row['status']='SAT_RELAXATION_NO_RING_WITNESS'
        else:row['status']='UNKNOWN_TIMEOUT'
        row['storage']={'input.cnf':pack(cnf,dest/'input.cnf.xz')}
        if row['exclusion_credited']:row['storage']['proof.drat']=pack(proof,dest/'proof.drat.xz')
        for p in list(work.glob('*.txt'))+list(work.glob('*.json'))+list((work/'audit').glob('*.txt')):
            target=dest/(('audit_' if p.parent.name=='audit' else '')+p.name);shutil.copy2(p,target)
        assert sources()==pins
        row['seconds']=time.monotonic()-started;dump(dest/'CASE.json',row)
    return row
def transport_check(groups):
    count=0
    for group in groups:
        support=group['representative_support'];roles=group['all_thirteen_hub_choices'];seen=set()
        assert len(support)==len(set(support))==13
        assert {r['largest_vertex_in_representative'] for r in roles}==set(support)
        for role in roles:
            cols=role['linear_columns_after_translation'];assert len(cols)==5
            def lin(x):
                out=0
                for i,c in enumerate(cols):
                    if x>>i&1:out^=c
                return out
            assert len({lin(x) for x in range(32)})==32
            points={lin(x^role['largest_vertex_in_representative']) for x in support}
            mask=sum(1<<x for x in points if x);assert mask==role['target_marked_nonzero_mask'] and 0 in points
            seen.add(mask);count+=1
        assert seen==set(group['marked_nonzero_masks'])
    return count
def merge(rows,verified=False):
    oldpath=ROOT/'Kakeya_Research_Frontier_Round8.json';old=json.loads(oldpath.read_text());inherited=set(old['support13_partial_coverage']['complete_masks']);assert len(inherited)==28
    groups=json.loads((ROOT/'research_round7/geometry/SUPPORT13_MARKING_MAP.json').read_text())['groups'];transports=transport_check(groups)
    new={m:{r['case']['nonzero_support_mask'] for r in rows if r['case']['maximum_interval']==[m,m] and r['exclusion_credited']} for m in (12,13)}
    return {'status':'FRESH_REPLAY_COMPLETE' if verified else 'PARTIAL_RECOVERY_CHECKPOINT','cases_accounted_for':len(rows),'certified_cases':sum(len(x) for x in new.values()),'prior_27_targets_reestablished':all(TARGETS[m]<=new[m] for m in TARGETS),'inherited_marked_coverage_per_maximum':28,'inherited_proofs_freshly_replayed':False,'coverage_of55':{m:len(inherited|new[m]) for m in new},'complete_affine_classes':{m:[g['unmarked_affine_orbit_id'] for g in groups if set(g['marked_nonzero_masks'])<=inherited|new[m]] for m in new},'remaining_prior_targets':{m:sorted(TARGETS[m]-new[m]) for m in new},'transports_checked':transports,'round8_frontier_sha256':sha(oldpath),'whole_weight_profiles_removed':0,'middle_profiles':182526,'maximum11_affine_classes':42,'full_n5_theorem':'OPEN','original_timing_logs':'LOST; new timing logs retained','original_proof_bytes':'LOST; checked regenerated replacements retained'}
def run(jobs,limit,only_targets=False):
    A.verify_sources();bins,build=A.build_checkers(HERE/'tools/bin',HERE/'tools/logs');dump(HERE/'CHECKER_BUILD.json',{'pins':A.verify_sources(),'build':build})
    import pysat,pysolvers
    dump(HERE/'SOLVER.json',{'python_sat':pysat.__version__,'native_sha256':sha(Path(pysolvers.__file__)),'solver':'cadical195','trusted':False})
    queue=json.loads((ROOT/'research_round8/NEXT_ATTACK_QUEUE.json').read_text())['cases'];assert len(queue)==54 and len({c['case_id'] for c in queue})==54
    if only_targets:queue=[c for c in queue if c['nonzero_support_mask'] in TARGETS[c['maximum_interval'][0]]]
    queue.sort(key=lambda c:(c['nonzero_support_mask'] not in TARGETS[c['maximum_interval'][0]],c['nonzero_support_mask'],c['maximum_interval'][0]))
    rows=[];errors=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as pool:
        futures={pool.submit(produce,(case,limit)):case for case in queue}
        for future in concurrent.futures.as_completed(futures):
            try:
                row=future.result();rows.append(row);print(row['case']['nonzero_support_mask'],row['case']['maximum_interval'],row['status'],flush=True)
            except Exception as error:errors.append({'case':futures[future],'error':repr(error)});print('ERROR',repr(error),flush=True)
            summary=merge(rows);summary.update(errors=errors,results=rows);dump(HERE/'RECOVERY_PROGRESS.json',summary)
    summary=merge(rows);summary.update(status='PRODUCTION_COMPLETE',errors=errors,results=rows);dump(HERE/'RECOVERY_PROGRESS.json',summary)
    assert not errors
    print('COMPLETE',len(rows),'CERTIFIED',summary['certified_cases'],flush=True)
def replay_one(case):
    folder=case_dir(case);row=json.loads((folder/'CASE.json').read_text());assert row['case']==case and row['source_hashes']==sources()
    with tempfile.TemporaryDirectory(prefix='kakeya_independent_replay_') as temp:
        temp=Path(temp);unpack(folder/'input.cnf.xz',temp/'input.cnf',row['storage']['input.cnf'])
        f=formula(case);N.write_dimacs(f,temp/'regenerated.cnf');assert f.n==row['variables'] and len(f.cl)==row['clauses'] and f.r8_next_frontier_metadata==row['extension'];del f;gc.collect()
        assert sha(temp/'input.cnf')==sha(temp/'regenerated.cnf')==row['cnf_sha256']
        if row['exclusion_credited']:
            unpack(folder/'proof.drat.xz',temp/'proof.drat',row['storage']['proof.drat'])
            assert row['status']=='CERTIFIED_EXCLUSION' and row['audit']['status']=='PASS_CNF_UNSAT_VIA_CAKEML_LRAT'
            bins={k:HERE/'replay_tools/bin'/k for k in ('drat-trim','lrat-check','cake_lpr')}
            audit=A.check_pair(temp/'input.cnf',temp/'proof.drat',temp/'audit',bins,900,1024,256,False)
            assert audit['status']=='PASS_CNF_UNSAT_VIA_CAKEML_LRAT'
            audit['case_id']=case['case_id'];dump(HERE/'fresh_replay'/ (case['case_id']+'.json'),audit)
    return row
def replay(jobs):
    A.verify_sources();bins,build=A.build_checkers(HERE/'replay_tools/bin',HERE/'replay_tools/logs');dump(HERE/'FRESH_CHECKER_BUILD.json',build)
    queue=json.loads((ROOT/'research_round8/NEXT_ATTACK_QUEUE.json').read_text())['cases'];assert len(queue)==54
    rows=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as pool:
        for row in pool.map(replay_one,queue):rows.append(row);print('REPLAY',len(rows),row['status'],flush=True)
    summary=merge(rows,verified=True);assert summary['prior_27_targets_reestablished'] and len(rows)==54;summary['source_hashes']=sources();summary['fresh_cnf_count']=54;summary['fresh_proof_count']=sum(r['exclusion_credited'] for r in rows);dump(HERE/'VERIFIED_FRONTIER.json',summary);print(json.dumps(summary,indent=2),flush=True)
def main():
    if sys.flags.optimize:raise SystemExit('Run without -O.')
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['run','replay']);ap.add_argument('--jobs',type=int,default=4);ap.add_argument('--limit',type=int,default=45);ap.add_argument('--targets-only',action='store_true');a=ap.parse_args()
    if a.mode=='run':run(a.jobs,a.limit,a.targets_only)
    else:replay(a.jobs)
if __name__=='__main__':main()
