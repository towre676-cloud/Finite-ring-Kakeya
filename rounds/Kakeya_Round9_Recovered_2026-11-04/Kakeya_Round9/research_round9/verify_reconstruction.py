#!/usr/bin/env python3
"""Freshly check all 54 recovered inputs and every accepted refutation.

Can run while reconstruction is completing. Incomplete case folders are
never read; publication is gated by the atomic CASE.json receipt.
"""
import concurrent.futures,json,time,sys
from pathlib import Path
import recover as R

def ready(case):
    deadline=time.monotonic()+1800
    while not (R.case_dir(case)/'CASE.json').exists():
        if time.monotonic()>deadline:raise RuntimeError('Case publication did not complete: '+case['case_id'])
        time.sleep(1)
    return R.replay_one(case)

def main():
    if sys.flags.optimize:raise SystemExit('Run without -O.')
    R.A.verify_sources();binaries,build=R.A.build_checkers(R.HERE/'replay_tools/bin',R.HERE/'replay_tools/logs');R.dump(R.HERE/'FRESH_CHECKER_BUILD.json',build)
    queue=json.loads((R.ROOT/'research_round8/NEXT_ATTACK_QUEUE.json').read_text())['cases'];assert len(queue)==54
    queue.sort(key=lambda c:(c['nonzero_support_mask'] not in R.TARGETS[c['maximum_interval'][0]],c['nonzero_support_mask'],c['maximum_interval'][0]))
    rows=[];started=time.monotonic()
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
        futures={pool.submit(ready,case):case for case in queue}
        for future in concurrent.futures.as_completed(futures):
            row=future.result();rows.append(row)
            R.dump(R.HERE/'VERIFICATION_PROGRESS.json',{'status':'RUNNING','checked_cases':len(rows),'checked_proofs':sum(r['exclusion_credited'] for r in rows),'case_ids':[r['case']['case_id'] for r in rows]})
            print('FRESH',len(rows),row['case']['case_id'],row['status'],flush=True)
    assert {r['case']['case_id'] for r in rows}=={c['case_id'] for c in queue}
    summary=R.merge(rows,verified=True);assert summary['prior_27_targets_reestablished']
    summary.update(source_hashes=R.sources(),fresh_cnf_count=54,fresh_proof_count=sum(r['exclusion_credited'] for r in rows),verification_driver_sha256=R.sha(Path(__file__)),seconds=time.monotonic()-started)
    R.dump(R.HERE/'VERIFIED_FRONTIER.json',summary);print(json.dumps(summary,indent=2),flush=True)
if __name__=='__main__':main()
