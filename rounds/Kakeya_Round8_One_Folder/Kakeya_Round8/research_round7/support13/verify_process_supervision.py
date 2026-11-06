#!/usr/bin/env python3
"""Exercise nested-child stops and wrapper trace guards, without SAT search."""
from pathlib import Path
import json
import os
import sys
import tempfile
import time
import certify_support13 as P

CHILD = '''from pathlib import Path
import subprocess,sys,time
mode=sys.argv[1];work=Path(sys.argv[2])
if mode in ('writer','sleeper'):
    (work/'grandchild_pid.txt').write_text(str(__import__('os').getpid()))
    if mode=='writer':
        with (work/'search_solver.drat').open('wb') as out:
            while True:
                out.write(b'0'*262144);out.flush();time.sleep(0.03)
    else:time.sleep(60)
else:
    child=subprocess.Popen([sys.executable,__file__,'sleeper' if mode=='wall' else 'writer',str(work)])
    if mode!='orphan':time.sleep(60)
'''


def main():
    start=time.monotonic();results=[]
    for mode,limit,size,expected in [('guard',5,512*1024,'PROOF_SIZE_GUARD'),
                                     ('orphan',5,10*1024**2,None),
                                     ('wall',0.1,10*1024**2,'WALL_TIMEOUT')]:
        with tempfile.TemporaryDirectory(prefix='kakeya_group_control_') as directory:
            work=Path(directory);script=work/'nested_child.py';script.write_text(CHILD)
            r=P.run_guarded_solver([sys.executable,str(script),mode,str(work)],work,limit,
                                   proof_byte_limit=size,min_free_bytes=0)
            P.A.require(r['stop_reason']==expected,'Unexpected guard outcome')
            group=r['process_supervision']
            P.A.require(group['whole_process_group_confirmed_absent'] and
                        not P.group_exists(group['process_group_id']),'Descendant process group still exists')
            P.A.require(group['adopted_descendants_reaped'],'Control did not exercise descendant reaping')
            pid=int((work/'grandchild_pid.txt').read_text())
            try:
                os.kill(pid,0);still_present=True
            except ProcessLookupError:
                still_present=False
            P.A.require(not still_present,'Controlled grandchild is still present')
            before=P.live_drat_bytes(work)
            time.sleep(0.1)
            P.A.require(P.live_drat_bytes(work)==before,'Stopped descendant is still writing')
            results.append({'mode':mode,'status':'PASS','result':r,'proof_bytes_after_stop':before[0]})
    receipt={'status':'PASS_NESTED_PROCESS_GROUP_RESOURCE_CONTROLS','cases':results,
             'producer_sha256':P.A.sha(P.HERE/'certify_support13.py'),
             'retained_v1_producer_sha256':P.A.sha(P.HERE/'producer_snapshots/certify_support13_v1.py'),
             'seconds':round(time.monotonic()-start,6)}
    P.dump(P.HERE/'PROCESS_SUPERVISION_CONTROLS.json',receipt)
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
