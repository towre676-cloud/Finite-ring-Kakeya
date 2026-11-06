"""Independent recursive resource replay for the outside-support budget stage."""
from collections import Counter
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from common_pair_bounds import read_profile, maximum_sumset
WORK=ROOT/'research_round2/root'
def quota(w):
 return (w&-w)-1 if w%2==0 else max((w-1)&-(w-1),(w+1)&-(w+1))-1
@lru_cache(None)
def allocate(neighbours,cap,budget,slots,ell):
 if not neighbours or budget==0:return 0
 q,rest=neighbours[0],neighbours[1:]
 return max(2*maximum_sumset(p,q)-ell*p+allocate(rest,cap,budget-p,slots-(p==cap),ell)
            for p in range(min(cap,budget)+1) if slots>0 or p<cap)
def compute(rows,ell):
 hs=tuple(sorted(w//2 for f,w in rows if w//2>ell))
 hh=2*sum(maximum_sumset(a,b) for a,b in combinations(hs,2));light=[];loss=[]
 for f,w in rows:
  cap=w//2;budget=(w-f)*(w-f-1)//2;r=quota(w)
  if cap<=ell:
   val=ell*budget+allocate(hs,cap,budget,r,ell)
   light.append({'flag':f,'weight':w,'budget':budget,'upper_doubled':val})
  else:
   other=list(hs);other.remove(cap);other=tuple(other)
   b=allocate(other,cap,budget,r,0);assert b%2==0
   q=sum(maximum_sumset(cap,h) for h in other)-b//2;assert q>=0;loss.append(q)
 plain=hh+sum(x['upper_doubled'] for x in light);corr=2*max(max(loss,default=0),(sum(loss)+1)//2)
 return {'heavy_caps':hs,'heavy_heavy_doubled':hh,'light_terms':light,'outside_plain_doubled':plain,'heavy_losses':loss,'heavy_correction_doubled':corr,'upper_doubled':plain-corr}
summary={'status':'PASS','scope':'entire weight/own-direction profiles, both rings, after full spectrum stage','supports':{}}
previous=json.loads((WORK/'ROOT_VERIFIED_SPECTRUM_STAGE.json').read_text())
for s in (11,12):
 inputs={}
 for line in (WORK/f's{s}_after_spectrum.txt').read_text().splitlines():
  pid,z,rows=read_profile(list(map(int,line.split())));inputs[pid]=(z,rows)
 before={}
 for line in (ROOT/f'research_round2/geometric/s{s}_remaining_input.txt').read_text().splitlines():
  pid,z,rows=read_profile(list(map(int,line.split())));before[pid]=(z,rows)
 prior=set(previous['supports'][str(s)]['excluded_parent_ids'])
 assert inputs=={p:v for p,v in before.items() if p not in prior}
 cuts=set();gaps=[];examples=[];ell_counts=Counter()
 for line in (WORK/f'S{s}_OUTSIDE_SUPPORT_CANDIDATES.jsonl').read_text().splitlines():
  c=json.loads(line);pid=c['parent_id'];assert pid in inputs and pid not in cuts
  z,rows=inputs[pid];assert len(rows)+1==s
  need=16*(32-s);assert need==c['required_capacity']
  result=compute(rows,c['cutoff'])
  for k in ('outside_plain_doubled','heavy_losses','heavy_correction_doubled','upper_doubled'):assert c[k]==result[k]
  assert result['upper_doubled']<2*need
  cuts.add(pid);gaps.append(2*need-result['upper_doubled']);ell_counts[c['cutoff']]+=1
  if len(examples)<4:examples.append({'parent_id':pid,'rows':rows,'demand':need,'cutoff':c['cutoff'],**result})
 summary['supports'][str(s)]={'input_count':len(inputs),'new_exclusions':len(cuts),'remaining':len(inputs)-len(cuts),'excluded_parent_ids':sorted(cuts),'minimum_doubled_gap':min(gaps),'cutoff_histogram':dict(sorted(ell_counts.items())),'examples':examples,'certificate_sha256':sha256((WORK/f'S{s}_OUTSIDE_SUPPORT_CANDIDATES.jsonl').read_bytes()).hexdigest()}
summary['total_exclusions']=sum(x['new_exclusions'] for x in summary['supports'].values())
summary['remaining_selected_profiles']=sum(x['remaining'] for x in summary['supports'].values())
(WORK/'ROOT_VERIFIED_OUTSIDE_SUPPORT_STAGE.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({**{k:v for k,v in summary.items() if k!='supports'},'supports':{s:{k:v for k,v in x.items() if k not in ('excluded_parent_ids','examples')} for s,x in summary['supports'].items()}},indent=2))
