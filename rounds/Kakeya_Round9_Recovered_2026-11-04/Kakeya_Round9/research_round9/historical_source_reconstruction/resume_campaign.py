#!/usr/bin/env python3
"""Complete the frozen 54-case queue; failures remain explicit, uncredited."""
import concurrent.futures,json,time,traceback
from pathlib import Path
import campaign as C

def main():
    queue=json.loads((C.ROOT/'research_round8/NEXT_ATTACK_QUEUE.json').read_text())['cases']
    queue.sort(key=lambda c:(c['nonzero_support_mask'],c['maximum_interval'][0]))
    assert len(queue)==54 and len({c['case_id'] for c in queue})==54
    summary={'status':'RUNNING','queue_sha256':C.sha(C.ROOT/'research_round8/NEXT_ATTACK_QUEUE.json'),'driver_sha256':C.sha(Path(__file__)),'source_hashes':C.source_hashes(),'expected_case_ids':[c['case_id'] for c in queue],'results':[],'errors':[],'new_exclusions':0,'base_round8_frontier_edited':False,'limit_seconds':45}
    out=C.HERE/'COMPLETE_QUEUE_CAMPAIGN.json';C.dump(out,summary)
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(C.one,(case,45,'pilot45',900)):case for case in queue}
        for future in concurrent.futures.as_completed(futures):
            case=futures[future]
            try:
                row=future.result();summary['results'].append(row);summary['new_exclusions']+=bool(row['exclusion_credited'])
                print(case['nonzero_support_mask'],case['maximum_interval'],row['status'],flush=True)
            except Exception as error:
                summary['errors'].append({'case':case,'status':'UNACCEPTED_ERROR','error':repr(error),'exclusion_credited':False})
                print('ERROR',case['case_id'],repr(error),flush=True)
            C.dump(out,summary)
    summary['status']='COMPLETE_ALL_QUEUE_CASES_ACCOUNTED_FOR';C.dump(out,summary)
    print('COMPLETE',len(summary['results']),'ERRORS',len(summary['errors']),'CERTIFIED',summary['new_exclusions'],flush=True)
if __name__=='__main__':main()
