"""Compile the pinned coordinate/line soundness bridge and audit its axioms."""
from pathlib import Path
from hashlib import sha256
import argparse,json,os,re,shutil,subprocess,time

HERE=Path(__file__).resolve().parent
COMMIT='f897ebcf72cd16f89ab4577d0c826cd14afaafc7'
THEOREMS={
 'encode_injective','encode_lt_four','z4_add_encoding','z4_mul_encoding','z4_line_encoding',
 'coordinate_corners','linePoint_zero','linePoint_nilpotent','linePoint_one',
 'linePoint_one_add_nilpotent','lineContained_iff_two_pairs',
 'vxor_eq_self_forces_zero','primitive_pair_distinct','endpoint_involution',
 'line_exists_iff_pair_sum',
}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--mathlib',type=Path)
    parser.add_argument('--lean-bin',type=Path)
    args=parser.parse_args();start=time.monotonic()
    work=args.mathlib.resolve() if args.mathlib else HERE
    library=work if args.mathlib else HERE/'.lake/packages/mathlib'
    env=dict(os.environ)
    if args.lean_bin:
        binary=args.lean_bin.resolve();lake=str(binary/'lake');lean=str(binary/'lean')
        env['PATH']=str(binary)+os.pathsep+env.get('PATH','')
    else:
        lake=shutil.which('lake');lean='lean'
        if not lake:raise SystemExit('Install the pinned Lean toolchain and dependencies first.')
    commit=subprocess.run(['git','rev-parse','HEAD'],cwd=library,check=True,capture_output=True,text=True).stdout.strip()
    assert commit==COMMIT,commit
    version=subprocess.run([lake,'env',lean,'--version'],cwd=work,env=env,check=True,capture_output=True,text=True).stdout.strip()
    assert 'version 4.24.0,' in version,version
    source=HERE/'CarryBridge.lean';body=source.read_text()
    assert not re.search(r'\b(sorry|admit|native_decide)\b',body)
    assert not re.search(r'^\s*axiom\s',body,re.MULTILINE)
    run=subprocess.run([lake,'env',lean,str(source)],cwd=work,env=env,capture_output=True,text=True)
    log=run.stdout+run.stderr
    (HERE/'CARRY_LEAN_COMPILE_LOG.txt').write_text(log)
    if run.returncode:
        print(log,end='');raise SystemExit(run.returncode)
    assert 'sorryAx' not in log and 'error:' not in log
    audits={}
    for name,raw in re.findall(r"'KakeyaRound5\.([^']+)' depends on axioms: \[([^\]]*)\]",log):
        values=[s.strip() for s in raw.split(',') if s.strip()]
        assert name not in audits and set(values)<={'propext','Quot.sound','Classical.choice'}
        audits[name]=values
    for name in re.findall(r"'KakeyaRound5\.([^']+)' does not depend on any axioms",log):
        assert name not in audits;audits[name]=[]
    assert set(audits)==THEOREMS,(set(audits),THEOREMS)
    receipt={'status':'PASS_PINNED_LEAN_COORDINATE_AND_LINE_BRIDGE','lean_version':version,
        'mathlib_commit':commit,'theorem_count':len(audits),'axiom_audits':audits,
        'formalized':[
          'Injective canonical encoding of Bool pairs into the four natural residues.',
          'Z/4 coefficient addition, multiplication, and line arithmetic agree with literal arithmetic modulo4.',
          'For both coordinate ring models, four coefficient choices give the two tangent pairs with the correctcarry.',
          'For any index type, full line containment iff the two tangent pairs exist; primitive pair points are distinct.',
          'For any index type, line existence iff a carry-shifted pair-sum witness exists.',
        ],
        'not_formalized':[
          'A full abstract Ring instance/isomorphism for the dual-number coordinate carrier.',
          'Quotient-label cardinality, pair-count energy, or support-orbit completeness.',
          'Affine support normalization over the rings.',
          'Claudes unavailable conditionsA-E, the actual CNF encoder, DRATchecker, or maximum19closure.',
        ],
        'source_sha256':sha256(source.read_bytes()).hexdigest(),
        'log_sha256':sha256(log.encode()).hexdigest(),
        'seconds':round(time.monotonic()-start,6)}
    (HERE/'CARRY_LEAN_REPLAY.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ['status','lean_version','mathlib_commit','theorem_count','seconds']},indent=2))

if __name__=='__main__':main()
