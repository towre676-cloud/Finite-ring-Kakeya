"""Root exact hub-stage audit: integer duals and independent stage accounting."""
import json,sys,hashlib
from pathlib import Path
from itertools import combinations
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from common_pair_bounds import read_profile,maximum_sumset
WORK=ROOT/'research_round2/geometric';R=ROOT/'research_round2/root'
hists={int(w):sorted(tuple(x['hist']) for x in rr) for w,rr in json.loads((WORK/'PAIR_SPECTRUM_CENSUS.json').read_text())['weights'].items()}
bounds={};dual_count=0;ineq=0
for line in (WORK/'HUB_COUPLED_MATCHING_DUAL_CERTIFICATES.jsonl').read_text().splitlines():
 c=json.loads(line);w,f,ell=c['weight'],c['flag'],c['cutoff'];qs=tuple(c['neighbors']);key=w,f,ell,qs
 assert key not in bounds and f in(-1,0,1)
 eligible={i for i,h in enumerate(hists[w]) if f==-1 or ((h[0]>0) if f==0 else (h[0]<31))}
 assert {d['index'] for d in c['spectra']}==eligible
 vals=[]
 for d in c['spectra']:
  ps=[p for p,n in enumerate(hists[w][d['index']]) for _ in range(n)];lam,mu=d['lambda'],d['mu']
  assert len(ps)==31 and len(mu)==31 and len(lam)==len(qs)+(f>=0) and min(mu)>=0
  assert all(isinstance(x,int) for x in lam+mu)
  for i,q in enumerate(qs):
   for j,p in enumerate(ps):
    assert lam[i]+mu[j]>=2*maximum_sumset(p,q)-ell*p;ineq+=1
  if f>=0:
   for j,p in enumerate(ps):
    if (p==0)==(f==0):
     assert lam[-1]+mu[j]>=2*maximum_sumset(p,9)-ell*p;ineq+=1
  val=sum(lam)+sum(mu);assert val==d['bound'];vals.append(val);dual_count+=1
 b=ell*w*(w-1)//2+max(vals);assert b==c['upper_doubled'];bounds[key]=b
out={'status':'PASS','method':'all integer matching duals, including nonzero own-slot reward, verified without assignment solver','dual_keys':len(bounds),'spectrum_duals':dual_count,'integer_inequalities':ineq,'supports':{}}
prev_out=json.loads((R/'ROOT_VERIFIED_OUTSIDE_SUPPORT_STAGE.json').read_text());prev_block=json.loads((R/'ROOT_VERIFIED_PAIRED_BLOCK_STAGE.json').read_text())
for s in (11,12):
 inputs={}
 for line in (R/f's{s}_after_spectrum.txt').read_text().splitlines():
  pid,z,rows=read_profile(list(map(int,line.split())));inputs[pid]=(z,rows)
 prior=set(prev_out['supports'][str(s)]['excluded_parent_ids'])|set(prev_block['supports'][str(s)]['excluded_parent_ids'])
 inputs={p:v for p,v in inputs.items() if p not in prior};cuts=set();gaps=[];examples=[]
 for line in (WORK/f'S{s}_HUB_COUPLED_CANDIDATES.jsonl').read_text().splitlines():
  c=json.loads(line);pid=c['parent_id'];assert pid in inputs and pid not in cuts;z,rows=inputs[pid]
  ell=c['cutoff'];assert 0<=ell<=8 and c['required_capacity']==496 and c['support']==s
  hs=tuple(sorted(w//2 for f,w in rows if w//2>ell));hubns=tuple(sorted(w//2 for f,w in rows if f and w//2>ell))
  hubbase=sum(maximum_sumset(9,q) for q in hubns);hh=2*hubbase+2*sum(maximum_sumset(a,b) for a,b in combinations(hs,2))
  light=[];loss=[]
  for f,w in rows:
   cap=w//2
   if cap<=ell:light.append(bounds[w,f,ell,hs])
   else:
    other=list(hs);other.remove(cap);other=tuple(other)
    b=bounds[w,f,0,other];assert b%2==0
    l=f*maximum_sumset(cap,9)+sum(maximum_sumset(cap,q) for q in other)-b//2;assert l>=0;loss.append(l)
  b=bounds[19,-1,0,hubns];assert b%2==0
  l=hubbase-b//2;assert l>=0;loss.append(l)
  plain=hh+sum(light);corr=2*max(max(loss,default=0),(sum(loss)+1)//2);upper=plain-corr
  assert (plain,corr,upper,light,loss)==(c['hub_plain_doubled'],c['heavy_correction_doubled'],c['upper_doubled'],c['light_bounds'],c['heavy_losses'])
  assert upper<992;cuts.add(pid);gaps.append(992-upper)
  if len(examples)<2:examples.append({'parent_id':pid,'rows':rows,'cutoff':ell,'heavy_caps':hs,'hub_heavy_neighbor_caps':hubns,'heavy_baseline_doubled':hh,'light_bounds':light,'heavy_losses':loss,'upper_doubled':upper})
 out['supports'][str(s)]={'input_count':len(inputs),'new_exclusions':len(cuts),'remaining':len(inputs)-len(cuts),'excluded_parent_ids':sorted(cuts),'minimum_doubled_gap':min(gaps),'examples':examples,'certificate_sha256':hashlib.sha256((WORK/f'S{s}_HUB_COUPLED_CANDIDATES.jsonl').read_bytes()).hexdigest()}
out['total_exclusions']=sum(x['new_exclusions'] for x in out['supports'].values());out['remaining_selected_profiles']=sum(x['remaining'] for x in out['supports'].values())
(R/'ROOT_VERIFIED_HUB_COUPLED_STAGE.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({**{k:v for k,v in out.items() if k!='supports'},'supports':{s:{k:v for k,v in x.items() if k not in ('excluded_parent_ids','examples')} for s,x in out['supports'].items()}},indent=2))
