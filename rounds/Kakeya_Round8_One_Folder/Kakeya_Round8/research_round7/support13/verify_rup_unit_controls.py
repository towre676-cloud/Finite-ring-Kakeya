#!/usr/bin/env python3
"""Check proof-prefix plumbing, including rejection against the wrong formula.

Search preprocessing is still untrusted: the production gate remains a
checked complete refutation of the original exact CNF.
"""
from pathlib import Path
import argparse
import itertools
import json
import random
import subprocess
import tempfile
import time
import certify_support13 as P
import rup_unit_solver as U


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay',action='store_true',help='Use delivered tiny proofs; run no SAT solver')
    args=parser.parse_args()
    start=time.monotonic();out=P.HERE/'unit_controls';out.mkdir(exist_ok=True)
    rng=random.Random(20261028)
    clauses=[]
    for k in range(1,5):
        for variables in itertools.combinations(range(1,5),k):
            for signs in itertools.product((-1,1),repeat=k):
                clauses.append([x*s for x,s in zip(variables,signs)])
    tested=0;nontrivial=0
    for _ in range(1000):
        formula=rng.sample(clauses,rng.randrange(2,13))
        units,witnesses=U.derive_units(formula)
        nontrivial+=bool(units)
        for assignment in itertools.product((False,True),repeat=4):
            truth=lambda lit: assignment[abs(lit)-1] if lit>0 else not assignment[abs(lit)-1]
            if all(any(map(truth,c)) for c in formula):
                P.A.require(all(map(truth,units)),'Derived unit removes a real model')
        tested+=1
    pins=P.A.verify_sources()
    binaries,build=P.A.build_checkers(out/'bin',out/'build_logs')
    checks=[]
    with tempfile.TemporaryDirectory(prefix='kakeya_rup_controls_') as directory:
        work=Path(directory)
        original=work/'original.cnf';proof=work/'proof.drat'
        formula=[[1,2],[-1,3],[-2,3],[-3,4],[-3,-4]]
        U.write_formula(original,4,formula,[])
        if args.replay:
            for name in ('proof.drat','search_solver.drat','search_augmented.cnf',
                         'rup_unit_prefix.txt','rup_unit_preprocessing.txt'):
                (work/name).write_bytes((out/name).read_bytes())
            units,_=U.derive_units(formula)
            regenerated=work/'regenerated_augmented.cnf'
            U.write_formula(regenerated,4,formula,units)
            P.A.require(P.A.sha(regenerated)==P.A.sha(work/'search_augmented.cnf'),
                        'Delivered tiny augmented formula did not regenerate')
        else:
            run=subprocess.run([str(P.HERE/'rup_unit_solver.py'),'--no-binary','--no-witness','-t','5',str(original),str(proof)],
                               capture_output=True,text=True,timeout=10)
            P.A.require(run.returncode==20,'Control formula did not refute')
        meta=json.loads((work/'rup_unit_preprocessing.txt').read_text())
        P.A.require(3 in meta['added_units'],'Control did not exercise derived non-unit consequence')
        audit=P.A.check_pair(original,proof,work/'positive_audit',binaries,30,1024,256,False)
        P.A.require(audit['status']=='PASS_CNF_UNSAT_VIA_CAKEML_LRAT','Prefixed proof failed on originalCNF')
        checks.append({'name':'derived_unit_prefix_plus_solver_proof_checks_against_original','status':'PASS',
                       'original_cnf_sha256':P.A.sha(original),'proof_sha256':P.A.sha(proof),'audit':audit})
        # This deliberately chosen empty-only proof is valid on the
        # augmented formula by unit propagation, but invalid on the original
        # without the derived-unit prefix. A solver may redundantly emit its
        # input unit itself, so its actual raw proof need not exercise this.
        bare=work/'empty_without_prefix.drat';bare.write_text('0\n')
        augmented_audit=P.A.check_pair(work/'search_augmented.cnf',bare,work/'augmented_audit',binaries,30,1024,256,False)
        P.A.require(augmented_audit['status']=='PASS_CNF_UNSAT_VIA_CAKEML_LRAT','Chosen augmented-only proof not valid')
        bare_audit=P.A.check_pair(original,bare,work/'bare_audit',binaries,30,1024,256,False)
        P.A.require(bare_audit['status']!='PASS_CNF_UNSAT_VIA_CAKEML_LRAT','Missing-prefix empty proof accepted on original')
        checks.append({'name':'augmented_only_empty_proof_rejected_against_original','status':'PASS',
                       'augmented_audit':augmented_audit,'original_audit':bare_audit})
        sat=work/'satisfiable.cnf';wrong=work/'wrong.drat'
        U.write_formula(sat,3,[[1,2],[-1,3],[-2,3]],[])
        wrong.write_text('-3 0\n0\n')
        rejected=P.A.check_pair(sat,wrong,work/'negative_audit',binaries,30,1024,256,False)
        P.A.require(rejected['status']!='PASS_CNF_UNSAT_VIA_CAKEML_LRAT','Wrong unit refutation accepted on SATCNF')
        checks.append({'name':'wrong_preprocessing_unit_cannot_refute_satisfiable_original','status':'PASS','audit':rejected})
        for name in ('original.cnf','proof.drat','search_solver.drat','search_augmented.cnf','empty_without_prefix.drat','rup_unit_prefix.txt',
                     'rup_unit_preprocessing.txt','satisfiable.cnf','wrong.drat'):
            (out/name).write_bytes((work/name).read_bytes())
        for folder in ('positive_audit','augmented_audit','bare_audit','negative_audit'):
            target=out/folder;target.mkdir(exist_ok=True)
            for p in (work/folder).glob('*.txt'):(target/p.name).write_bytes(p.read_bytes())
    receipt={'status':'PASS_RUP_UNIT_PREPROCESSING_CONTROLS','truth_table_formulas':tested,
             'formulas_with_added_units':nontrivial,'assignments_per_formula':16,
             'checker_controls':checks,'checker_pins':pins,'checker_build':build,
             'wrapper_sha256':P.A.sha(P.HERE/'rup_unit_solver.py'),
             'new_kakeya_exclusions_proved_by_controls':0,'preprocessor_trusted':False,
             'solver_search_run':not args.replay,
             'seconds':round(time.monotonic()-start,6)}
    P.dump(P.HERE/'RUP_UNIT_CONTROLS.json',receipt)
    print(json.dumps({k:receipt[k] for k in ('status','truth_table_formulas','formulas_with_added_units','seconds')}))


if __name__=='__main__':main()
