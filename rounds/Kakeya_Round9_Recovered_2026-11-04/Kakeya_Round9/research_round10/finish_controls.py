#!/usr/bin/env python3
"""Finish the incomplete sweep plus explicit controls of the hardest support."""
import concurrent.futures,json
from pathlib import Path
import finish_campaign as F
C=F.C;HERE=Path(__file__).resolve().parent
prior_sources=C.sources

def sources():
 return {**prior_sources(),str(Path(__file__).relative_to(HERE.parent)):C.R.sha(Path(__file__))}
C.sources=sources
queue=json.loads((HERE.parent/'research_round9/REMAINING_CASES.json').read_text())['cases'];args=[]
for row in queue:
 name=row['case']['case_id'].replace('_incidence_pending','')+'_projected'
 if not (HERE/'cases'/name/'RECEIPT.json').exists():args.append((row,'projected',90))
for row in queue:
 if row['case']['nonzero_support_mask']==411136406:
  name=row['case']['case_id'].replace('_incidence_pending','')+'_baseline'
  if not (HERE/'cases'/name/'RECEIPT.json').exists():args.append((row,'baseline',180))
if __name__=='__main__':
 print('FINAL BATCH',len(args),flush=True)
 with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
  for r in pool.map(C.one,args):print(r['case']['nonzero_support_mask'],r['case']['maximum_interval'][0],r['variant'],r['status'],r['solve_seconds'],flush=True)
