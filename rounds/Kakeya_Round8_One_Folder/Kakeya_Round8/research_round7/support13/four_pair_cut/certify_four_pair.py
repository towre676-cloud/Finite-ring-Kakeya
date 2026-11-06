#!/usr/bin/env python3
"""Two bounded proof-producing trials of the new unique-edge geometric cut."""
from pathlib import Path
import gc
import json
import sys
import tempfile
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent))
import certify_support13 as P
import encode_four_pair as X

ACCEPTED='PASS_FOUR_PAIR_CNF_DRAT_CAKEML'


def semantic_hashes():
    result=P.semantics()
    for path in (HERE/'encode_four_pair.py',HERE/'FOUR_PAIR_CAPACITY_LEMMA.txt',HERE/'ENCODER_SOUNDNESS.txt'):
        result[str(path.relative_to(ROOT))]=P.A.sha(path)
    return result


def make_formula(case,lower,upper,SPEC,M,SUBS):
    return X.encode(case['support'][1:],upper,SPEC,M,SUBS,outtotal=93,hub_min=lower,enabled=True)


def one(case,binaries,SPEC,M,SUBS):
    mask=case['nonzero_support_mask'];cid=f's13_T{mask}_m11_11_four_pair_unique_t45'
    destination=HERE/'cases'/cid
    P.A.require(not destination.exists(),'Refusing to overwrite a finished trial')
    start=time.monotonic();pins=semantic_hashes()
    record={'case_id':cid,'status':'STARTING','encoder_kind':'four_pair_unique',
            'support':case['support'],'nonzero_support_mask':mask,'distinguished_hub':0,
            'maximum_interval':[11,11],'total_upper_bound':93,
            'ring_scope':'common_necessary_relaxation_both_rings','semantic_input_hashes':pins,
            'producer_sha256':P.A.sha(__file__),'search_wrapper_sha256':P.A.sha(HERE.parent/'rup_unit_solver.py'),
            'solver_limit_seconds':45,'encoder_formalized':False,'storage':{}}
    with tempfile.TemporaryDirectory(prefix='kakeya_four_pair_trial_') as directory:
        work=Path(directory);cnf=work/'input.cnf';proof=work/'proof.drat'
        f=make_formula(case,11,11,SPEC,M,SUBS)
        X.write_dimacs(f,cnf)
        record.update(variables=f.n,clauses=len(f.cl),cnf_sha256=P.A.sha(cnf),
                      cnf_bytes=cnf.stat().st_size,four_pair_extension=f.four_pair_metadata,
                      encode_seconds=round(time.monotonic()-start,6))
        del f;gc.collect()
        command=[str(HERE.parent/'rup_unit_solver.py'),'--no-binary','--no-witness','-t','45',str(cnf),str(proof)]
        supervised=P.run_guarded_solver(command,work,45)
        record.update(supervised,solver_command=command)
        code=supervised['solver_returncode']
        if proof.exists():record.update(proof_sha256=P.A.sha(proof),proof_bytes=proof.stat().st_size)
        unsat=code==20 and 's UNSATISFIABLE' in (work/'solver.stdout.txt').read_text()
        accepted=False
        if unsat:
            audit=P.A.check_pair(cnf,proof,work/'audit',binaries,900,1024,256,False)
            record['audit']=audit
            P.A.require(audit['input_sha256']=={'cnf':record['cnf_sha256'],'drat':record['proof_sha256']},
                        'Checker did not receive the exact new formula/proof')
            accepted=audit['status']=='PASS_CNF_UNSAT_VIA_CAKEML_LRAT'
        record['status']=ACCEPTED if accepted else 'TIMEOUT_OR_UNACCEPTED_UNCERTIFIED'
        P.A.require(semantic_hashes()==pins,'Semantic sources changed during trial')
        destination.mkdir(parents=True)
        for raw in [cnf]+([proof] if accepted else []):
            expected=record['cnf_sha256'] if raw==cnf else record['proof_sha256']
            meta=P.C.compress_verified(raw,expected,preset=1,remove_raw=True)
            compressed=Path(str(raw)+'.xz')
            P.publish_copy(compressed,destination/compressed.name,meta['xz_sha256'])
            P.A.require(P.C.logical_sha(destination/raw.name,prefer_compressed=True)==expected,'Published decoded bytes differ')
            record['storage'][raw.name]=meta
        if not accepted and proof.exists():
            record['discarded_unaccepted_proof']={'sha256':record['proof_sha256'],'bytes':record['proof_bytes']}
        for source in list(work.glob('*.txt'))+list((work/'audit').glob('*.txt')):
            P.publish_copy(source,destination/source.name,P.A.sha(source))
        record.update(seconds=round(time.monotonic()-start,6),original_baseline_CNF_claimed_refuted=False,
                      scope='This checks the NEW geometric-extension CNF; the one-way lemma supplies its Kakeya meaning.',
                      unfinished_proof_retained=False,reconstructed_lrat_retained=False)
        P.dump(destination/'CASE_RECEIPT.json',record)
    return record


def main():
    P.A.require(P.A.sha(X.BASE)==P.ENCODER_HASH,'Frozen baseline changed')
    wanted=[377850134,411136406]
    universe={c['nonzero_support_mask']:c for c in P.universe()}
    pins=P.A.verify_sources();binaries,build=P.A.build_checkers(HERE/'bin',HERE/'build_logs')
    P.dump(HERE/'BUILD_RECEIPT.json',{'pins':pins,'build':build,'semantic_input_hashes':semantic_hashes()})
    data=P.IMPORTED/'data';SPEC=X.load_spectra(data/'spec32.csv');M=X.load_M(data/'Mtable.txt');SUBS=X.all_subspaces()
    report={'status':'RUNNING','requested_masks':wanted,'maximum_interval':[11,11],'cases':[],
            'performance_caveat':'Two bounded trials in a shared environment; no general speed claim.'}
    for mask in wanted:
        row=one(universe[mask],binaries,SPEC,M,SUBS)
        report['cases'].append(row);P.dump(HERE/'FOUR_PAIR_TRIALS.json',report)
        print(json.dumps({k:row.get(k) for k in ('case_id','status','solve_seconds','proof_bytes','seconds')}),flush=True)
    report.update(status='COMPLETED_TWO_BOUNDED_FOUR_PAIR_TRIALS',
                  accepted_trials=sum(r['status']==ACCEPTED for r in report['cases']))
    P.dump(HERE/'FOUR_PAIR_TRIALS.json',report)


if __name__=='__main__':main()
