"""Compile the pinned Lean module and record its explicit formal scope."""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

HERE=Path(__file__).resolve().parent
MATHLIB_COMMIT='f897ebcf72cd16f89ab4577d0c826cd14afaafc7'
THEOREMS=[
 'pair_capacity_energy','weighted_pair_capacity_energy','sum_injective_resource',
 'remaining_energy_budget','cube_incidence_count','cube_edge_budget',
 'cube_other_surplus_row','small_surplus_table','surplus_zero_of_ge_five',
 'cube_master_bound','critical_profile_arithmetic','six_boundary_arithmetic',
 'critical_profile_exclusion',
]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--mathlib',type=Path)
    parser.add_argument('--lean-bin',type=Path)
    args=parser.parse_args()
    started=time.monotonic()
    work=args.mathlib.resolve() if args.mathlib else HERE
    library=work if args.mathlib else HERE/'.lake/packages/mathlib'
    env=dict(os.environ)
    if args.lean_bin:
        binary=args.lean_bin.resolve()
        lake=str(binary/'lake');lean=str(binary/'lean')
        env['PATH']=str(binary)+os.pathsep+env.get('PATH','')
    else:
        lake=shutil.which('lake')
        if not lake:raise SystemExit('Lake is not on PATH; install the pinned toolchain first.')
        lean='lean'
    commit=subprocess.run(['git','rev-parse','HEAD'],cwd=library,check=True,
                          capture_output=True,text=True).stdout.strip()
    assert commit==MATHLIB_COMMIT,('Wrong Mathlib commit',commit)
    version=subprocess.run([lake,'env',lean,'--version'],cwd=work,env=env,
                           check=True,capture_output=True,text=True).stdout.strip()
    assert 'version 4.24.0,' in version,version
    source=HERE/'CubeMaster.lean'
    text=source.read_text()
    # These checks supplement, and do not replace, the subsequent compiler run.
    assert not re.search(r'\b(sorry|admit|native_decide)\b',text)
    assert not re.search(r'^\s*axiom\s',text,re.MULTILINE)
    command=[lake,'env',lean,str(source)]
    result=subprocess.run(command,cwd=work,env=env,capture_output=True,text=True)
    log=result.stdout+result.stderr
    (HERE/'LEAN_COMPILE_LOG.txt').write_text(log)
    if result.returncode:
        print(log,end='')
        raise SystemExit(result.returncode)
    assert 'sorryAx' not in log and 'error:' not in log
    audits={}
    for name,body in re.findall(r"'KakeyaRound4\.([^']+)' depends on axioms: \[([^\]]*)\]",log):
        assert name not in audits
        axioms=[a.strip() for a in body.split(',') if a.strip()]
        assert set(axioms)<={'propext','Classical.choice','Quot.sound'},(name,axioms)
        audits[name]=axioms
    assert set(audits)==set(THEOREMS),(sorted(audits),THEOREMS)
    receipt={
      'status':'PASS_PINNED_LEAN_KERNEL_COMPILATION',
      'lean_version':version,'mathlib_commit':commit,
      'theorem_count':len(audits),'theorem_axiom_audits':audits,
      'main_theorem':'KakeyaRound4.cube_master_bound',
      'main_conclusion':'2*total_capacity<=remaining_energy+77*number_of_cubes+10*expensive_edge_bound+sum_cross_gains',
      'formalized':[
        'Finite injective resource accounting and disjoint remaining-endpoint energy.',
        'Seven slots per cube imply the doubled-edge incidence budget.',
        'Summation of cheap/expensive cube-edge and cross-edge inequalities.',
        'Ordinary and weighted AM-GM algebra; cube cross-edge surplus algebra.',
        'The general cube master aggregation theorem and all six boundary arithmetic inequalities.',
      ],
      'not_formalized':[
        'Actual binary sets, pair counting, affine planes, and the Q identity.',
        'The twelve-point energy theorem.',
        'Geometric construction of incidence injections, quotient capacities, triangle geometry, and Mantel.',
        'Profile-specific energy/gain bounds, exhaustive support reductions, and unrestricted Kakeya.',
      ],
      'source_sha256':sha256(source.read_bytes()).hexdigest(),
      'log_sha256':sha256(log.encode()).hexdigest(),
      'standard_axioms_only':True,
      'seconds':round(time.monotonic()-started,6),
    }
    (HERE/'LEAN_REPLAY_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('status','lean_version','mathlib_commit','theorem_count','standard_axioms_only','seconds')},indent=2))

if __name__=='__main__':main()
