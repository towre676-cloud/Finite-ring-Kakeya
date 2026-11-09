#!/usr/bin/env python3
"""Resume only incomplete scopes in bounded batches, retaining prior receipts."""
import argparse,concurrent.futures,json
from pathlib import Path
import resume_campaign as W
C=W.C;HERE=Path(__file__).resolve().parent
prior_sources=C.sources

def sources():
 return {**prior_sources(),str(Path(__file__).relative_to(HERE.parent)):C.R.sha(Path(__file__))}
C.sources=sources

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--count',type=int,default=4);a=ap.parse_args()
 queue=json.loads((HERE.parent/'research_round9/REMAINING_CASES.json').read_text())['cases'];args=[]
 for row in queue:
  case=row['case'];name=case['case_id'].replace('_incidence_pending','')+'_projected'
  if not (HERE/'cases'/name/'RECEIPT.json').exists():args.append((row,'projected',90))
 for row in queue:
  if row['case']['nonzero_support_mask']==411136406 and row['case']['maximum_interval']==[12,12]:
   name=row['case']['case_id'].replace('_incidence_pending','')+'_baseline'
   if not (HERE/'cases'/name/'RECEIPT.json').exists():args.append((row,'baseline',120))
 print('BATCH',len(args[:a.count]),'INCOMPLETE',len(args),flush=True)
 with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
  for r in pool.map(C.one,args[:a.count]):print(r['case']['nonzero_support_mask'],r['case']['maximum_interval'][0],r['variant'],r['status'],r['solve_seconds'],flush=True)
if __name__=='__main__':main()
