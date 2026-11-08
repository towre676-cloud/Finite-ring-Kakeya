#!/usr/bin/env python3
"""Replay retained certificates with no SAT solver or network required."""
import argparse,gc,importlib.util,json,sys,tempfile
from pathlib import Path
import encode_projected as E
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
spec=importlib.util.spec_from_file_location('round10_replay_recovery',ROOT/'research_round9/recover.py')
R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R)

def require(ok,message):
    if not ok:raise ValueError(message)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--case',help='Exact case folder name; omitted means all retained runs');a=ap.parse_args()
    R.A.verify_sources()
    bins,build=R.A.build_checkers(HERE/'replay_tools/bin',HERE/'replay_tools/logs')
    originals={r['case']['case_id']:r for r in json.loads((ROOT/'research_round9/REMAINING_CASES.json').read_text())['cases']}
    folders=sorted((HERE/'cases').iterdir())
    if a.case:folders=[p for p in folders if p.name==a.case]
    require(bool(folders),'No matching retained cases')
    output=[]
    for folder in folders:
        row=json.loads((folder/'RECEIPT.json').read_text());case=row['case'];old=originals[case['case_id']]
        require(case==old['case'],'Case scope differs from historical queue')
        require(row['baseline_expected_sha256']==old['cnf_sha256'],'Wrong baseline pin')
        require(row['variant'] in ('baseline','projected'),'Unknown encoder variant')
        for path,digest in row['source_hashes'].items():
            require(R.sha(ROOT/path)==digest,'Source changed: '+path)
        with tempfile.TemporaryDirectory(prefix='r10_replay_') as tmp:
            work=Path(tmp);f=R.formula(case);E.N.write_dimacs(f,work/'baseline.cnf')
            require(R.sha(work/'baseline.cnf')==old['cnf_sha256'],'Regenerated baseline differs')
            meta=E.append_projection(f,case['support'],case['maximum_interval'][0],enabled=row['variant']=='projected')
            require(meta==row['projection'],'Projection metadata differs')
            require((f.n,len(f.cl))==(row['variables'],row['clauses']),'Formula size differs')
            E.N.write_dimacs(f,work/'regenerated.cnf');del f;gc.collect()
            R.unpack(folder/'input.cnf.xz',work/'input.cnf',row['storage']['input.cnf'])
            require(R.sha(work/'input.cnf')==R.sha(work/'regenerated.cnf')==row['cnf_sha256'],'Exact input differs')
            receipt={'case_id':case['case_id'],'variant':row['variant'],'cnf_sha256':row['cnf_sha256'],'regeneration':'PASS','exclusion_credited':False}
            if row['exclusion_credited']:
                require(row['status']=='CERTIFIED_EXCLUSION','Credit/status mismatch')
                R.unpack(folder/'proof.drat.xz',work/'proof.drat',row['storage']['proof.drat'])
                check=R.A.check_pair(work/'input.cnf',work/'proof.drat',work/'audit',bins,300,512,128,False)
                require(check['status']=='PASS_CNF_UNSAT_VIA_CAKEML_LRAT','Independent checker rejected proof')
                receipt.update(audit=check,exclusion_credited=True)
            output.append(receipt);print('REPLAY',folder.name,receipt['exclusion_credited'],flush=True)
    R.dump(HERE/'REPLAY.json',{'status':'PASS','checker_build':build,'runs':output})
if __name__=='__main__':
    if sys.flags.optimize:raise SystemExit('Run without -O')
    main()
