"""Root audit: exact matching dual inequalities; no assignment solver trusted."""
import json, sys, hashlib
from pathlib import Path
from itertools import combinations
from collections import Counter
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from common_pair_bounds import read_profile, maximum_sumset
WORK=ROOT/'research_round2/geometric'
C=json.loads((WORK/'PAIR_SPECTRUM_CENSUS.json').read_text())
H={int(w):sorted(tuple(r['hist']) for r in rs) for w,rs in C['weights'].items()}
bounds={}; inequalities=0; dual_count=0
for line in (WORK/'SPECTRUM_MATCHING_DUAL_CERTIFICATES.jsonl').read_text().splitlines():
 c=json.loads(line); w,f,ell=c['weight'],c['flag'],c['cutoff']; qs=tuple(c['neighbors']); key=(w,f,ell,qs)
 assert key not in bounds
 eligible={i for i,h in enumerate(H[w]) if f<0 or (h[0]>0 if f==0 else h[0]<31)}
 assert {x['index'] for x in c['spectra']}==eligible
 vals=[]
 for dual in c['spectra']:
  dual_count+=1
  ps=[p for p,num in enumerate(H[w][dual['index']]) for _ in range(num)]
  lam,mu=dual['lambda'],dual['mu']
  assert len(mu)==31 and len(lam)==len(qs)+(f>=0)
  assert all(isinstance(x,int) for x in lam+mu) and min(mu)>=0
  for i,q in enumerate(qs):
   for j,p in enumerate(ps):
    assert lam[i]+mu[j]>=2*maximum_sumset(p,q)-ell*p, (key,dual['index'],i,j)
    inequalities+=1
  if f>=0:
   for j,p in enumerate(ps):
    if (p==0)==(f==0):
     assert lam[-1]+mu[j]>=-ell*p
     inequalities+=1
  value=sum(lam)+sum(mu)
  assert value==dual['bound']
  vals.append(value)
 b=ell*w*(w-1)//2+max(vals)
 assert b==c['upper_doubled']
 bounds[key]=b
summary={'status':'PASS','method':'all integer matching dual inequalities verified without Hungarian algorithm','dual_keys':len(bounds),'spectrum_duals':dual_count,'integer_inequalities':inequalities,'supports':{}}
for s in (11,12):
 inputs={}
 for line in (WORK/f's{s}_remaining_input.txt').read_text().splitlines():
  pid,z,rows=read_profile(list(map(int,line.split())));inputs[pid]=(z,rows)
 # Check exact input provenance against old current list minus all four prior verified stages.
 prior=set()
 for fn,key in [('ROOT_VERIFIED_M19_PROFILE_EXCLUSIONS.json','excluded_parent_ids'),('ROOT_VERIFIED_M19_HEAVY_BUDGET_EXCLUSIONS.json','additional_excluded_parent_ids'),('ROOT_VERIFIED_M19_PRICE_EXCLUSIONS.json','additional_excluded_parent_ids'),('ROOT_VERIFIED_M19_QUOTA_EXCLUSIONS.json','additional_excluded_parent_ids')]:
  j=json.loads((ROOT/fn).read_text());prior.update(j['supports'][str(s)][key])
 old={}
 for line in (ROOT/f'research_external/m19/s{s}_current.txt').read_text().splitlines():
  pid,z,rows=read_profile(list(map(int,line.split())));old[pid]=(z,rows)
 assert inputs=={p:v for p,v in old.items() if p not in prior}
 cuts=set();gaps=[];examples=[]
 for line in (WORK/f'S{s}_SPECTRUM_CANDIDATES.jsonl').read_text().splitlines():
  c=json.loads(line);pid,ell=c['parent_id'],c['cutoff'];assert pid in inputs and pid not in cuts
  z,rows=inputs[pid];assert len(rows)+1==s
  u=sum(f==1 and w<=3 for f,w in rows);need=16*z+7*u+max(0,u-3)
  assert c['required_capacity']==need
  hs=tuple(sorted(w//2 for f,w in rows if w//2>ell))
  hh=2*sum(maximum_sumset(a,b) for a,b in combinations(hs,2))
  light=[];loss=[]
  for f,w in rows:
   cap=w//2
   if cap<=ell:light.append(bounds[(w,f,ell,hs)])
   else:
    other=list(hs);other.remove(cap);other=tuple(other)
    b=bounds[(w,f,0,other)];assert b%2==0
    q=sum(maximum_sumset(cap,h) for h in other)-b//2;assert q>=0;loss.append(q)
  plain=hh+sum(light);correction=2*max(max(loss,default=0),(sum(loss)+1)//2);upper=plain-correction
  assert (plain,correction,upper,light,loss)==(c['spectrum_plain_doubled'],c['heavy_correction_doubled'],c['upper_doubled'],c['light_bounds'],c['heavy_losses'])
  assert upper<2*need
  gaps.append(2*need-upper);cuts.add(pid)
  if len(examples)<2:examples.append({'parent_id':pid,'rows':rows,'demand':need,'cutoff':ell,'heavy_caps':hs,'heavy_heavy_doubled':hh,'light_terms':light,'heavy_losses':loss,'upper_doubled':upper})
 summary['supports'][str(s)]={'input_count':len(inputs),'new_exclusions':len(cuts),'remaining':len(inputs)-len(cuts),'minimum_doubled_gap':min(gaps),'excluded_parent_ids':sorted(cuts),'examples':examples,'certificate_sha256':hashlib.sha256((WORK/f'S{s}_SPECTRUM_CANDIDATES.jsonl').read_bytes()).hexdigest()}
summary['total_exclusions']=sum(x['new_exclusions'] for x in summary['supports'].values())
summary['remaining_selected_profiles']=sum(x['remaining'] for x in summary['supports'].values())
(ROOT/'research_round2/root/ROOT_VERIFIED_SPECTRUM_STAGE.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({**{k:v for k,v in summary.items() if k!='supports'},'supports':{s:{k:v for k,v in x.items() if k not in ('excluded_parent_ids','examples')} for s,x in summary['supports'].items()}},indent=2))
