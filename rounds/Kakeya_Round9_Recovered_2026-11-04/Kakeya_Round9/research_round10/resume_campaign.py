#!/usr/bin/env python3
"""Retry disk-stopped searches with a guard on the actual work filesystem.

The historical supervisor hard-codes /tmp. This wrapper leaves it frozen,
uses the same process-group cleanup, and checks the supplied work directory.
Use TMPDIR=/dev/shm/<private-directory> when the disk volume is constrained.
"""
import argparse,concurrent.futures,json,shutil,subprocess,time
from pathlib import Path
import campaign as C
HERE=Path(__file__).resolve().parent
original_sources=C.sources

def sources():
    return {**original_sources(),str(Path(__file__).relative_to(HERE.parent)):C.R.sha(Path(__file__))}
C.sources=sources

def supervise(command,work,limit,proof_byte_limit=256*1024**2,min_free_bytes=512*1024**2):
    P=C.R.P;P.enable_child_subreaper();work=Path(work);start=time.monotonic();reason=None;observed={}
    initial_free=shutil.disk_usage(work).free
    with (work/'solver.stdout.txt').open('wb') as out,(work/'solver.stderr.txt').open('wb') as err:
        process=subprocess.Popen(command,stdout=out,stderr=err,start_new_session=True)
        try:
            while process.poll() is None:
                byte_count,observed=P.live_drat_bytes(work)
                if time.monotonic()-start>limit+2:reason='WALL_TIMEOUT'
                elif byte_count>proof_byte_limit:reason='PROOF_SIZE_GUARD'
                elif shutil.disk_usage(work).free<min_free_bytes:reason='DISK_GUARD'
                if reason:break
                time.sleep(.2)
        finally:
            group=P.stop_and_join_group(process,kill=reason is not None or process.poll() is None)
    return {'solver_returncode':process.returncode,'stop_reason':reason,
            'solve_seconds':round(time.monotonic()-start,6),'process_supervision':group,
            'last_observed_live_drat_bytes':observed,
            'disk_guard_target':'actual_work_directory','initial_work_free_bytes':initial_free,
            'proof_size_guard_counts_all_live_drat_files':True}
C.R.P.run_guarded_solver=supervise

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--jobs',type=int,default=2);ap.add_argument('--limit',type=int,default=90);a=ap.parse_args()
    queue=json.loads((HERE.parent/'research_round9/REMAINING_CASES.json').read_text())['cases']
    old={r['case']['case_id']:r for r in queue};args=[]
    for p in sorted((HERE/'cases').glob('*/RECEIPT.json')):
        r=json.loads(p.read_text())
        if r['stop_reason']=='DISK_GUARD':
            archive=HERE/'attempts/hardcoded_tmp_guard'/p.parent.name
            archive.parent.mkdir(parents=True,exist_ok=True)
            if archive.exists():raise ValueError('Retry archive already exists')
            p.parent.rename(archive)
            args.append((old[r['case']['case_id']],r['variant'],120 if r['variant']=='baseline' else a.limit))
    print('RETRYING',len(args),flush=True)
    with concurrent.futures.ProcessPoolExecutor(max_workers=a.jobs) as pool:
        for r in pool.map(C.one,args):
            print(r['case']['nonzero_support_mask'],r['case']['maximum_interval'][0],r['variant'],r['status'],round(r['solve_seconds'],2),flush=True)
if __name__=='__main__':main()
