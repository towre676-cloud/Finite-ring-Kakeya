"""Root replay of paired-block dual certificates, using root-audited census."""
import json,sys,hashlib
from pathlib import Path
from itertools import combinations
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from common_pair_bounds import read_profile,maximum_sumset
WORK=ROOT/'research_round2/geometric';R=ROOT/'research_round2/root'
assert json.loads((R/'ROOT_VERIFIED_BLOCK_CENSUS.json').read_text())['status']=='PASS'
raw=json.loads((WORK/'PAIRED_BLOCK_MAXIMUM_CENSUS.json').read_text())['weights']
hists={(int(w),int(f)):sorted(tuple(r['hist']) for r in rr) for w,fs in raw.items() for f,rr in fs.items()}
bounds={};dual_count=0;inequalities=0
for line in (WORK/'PAIRED_BLOCK_MATCHING_DUAL_CERTIFICATES.jsonl').read_text().splitlines():
 c=json.loads(line);w,f,ell=c['weight'],c['flag'],c['cutoff'];qs=tuple(c['neighbors']);key=w,f,ell,qs
 assert key not in bounds
 assert {d['index'] for d in c['spectra']}==set(range(len(hists[w,f])))
 vals=[]
 for d in c['spectra']:
  dual_count+=1;hh=hists[w,f][d['index']];ps=[p for p,n in enumerate(hh) for _ in range(n)]
  assert len(ps)==15 and sum(ps)==d['mass']
  lam,mu=d['lambda'],d['mu'];assert len(lam)==len(qs) and len(mu)==15 and min(mu)>=0
  assert all(isinstance(x,int) for x in lam+mu)
  for i,q in enumerate(qs):
   for j,p in enumerate(ps):
    assert lam[i]+mu[j]>=max(0,2*maximum_sumset(p,q)-ell*p)
    inequalities+=1
  b=sum(lam)+sum(mu);assert b==d['bound'];vals.append(ell*sum(ps)+b)
 b=max(vals);assert b==c['upper_doubled'];bounds[key]=b
out={'status':'PASS','census_completeness_inherited':False,'method':'independent normalized block census plus all exact integer assignment dual inequalities','dual_keys':len(bounds),'spectrum_duals':dual_count,'integer_inequalities':inequalities,'supports':{}}
prev=json.loads((R/'ROOT_VERIFIED_OUTSIDE_SUPPORT_STAGE.json').read_text())
for s in (11,12):
 inputs={}
 for line in (R/f's{s}_after_spectrum.txt').read_text().splitlines():
  pid,z,rows=read_profile(list(map(int,line.split())));inputs[pid]=(z,rows)
 prior=set(prev['supports'][str(s)]['excluded_parent_ids']);inputs={p:v for p,v in inputs.items() if p not in prior}
 cuts=set();gaps=[];examples=[]
 for line in (WORK/f'S{s}_PAIRED_BLOCK_CANDIDATES.jsonl').read_text().splitlines():
  c=json.loads(line);pid=c['parent_id'];assert pid in inputs and pid not in cuts
  z,rows=inputs[pid];assert len(rows)+1==s;ell=c['cutoff'];need=16*(32-s)
  assert c['required_capacity']==need
  hs=tuple(sorted(w//2 for f,w in rows if w//2>ell));hh=2*sum(maximum_sumset(a,b) for a,b in combinations(hs,2))
  light=[];loss=[]
  for f,w in rows:
   cap=w//2
   if cap<=ell:light.append(bounds[w,f,ell,hs])
   else:
    other=list(hs);other.remove(cap);other=tuple(other)
    b=bounds[w,f,0,other];assert b%2==0
    l=sum(maximum_sumset(cap,q) for q in other)-b//2;assert l>=0;loss.append(l)
  plain=hh+sum(light);corr=2*max(max(loss,default=0),(sum(loss)+1)//2);upper=plain-corr
  assert (plain,corr,upper,light,loss)==(c['block_plain_doubled'],c['heavy_correction_doubled'],c['upper_doubled'],c['light_bounds'],c['heavy_losses'])
  assert upper<2*need;cuts.add(pid);gaps.append(2*need-upper)
  if len(examples)<2:examples.append({'parent_id':pid,'rows':rows,'demand':need,'cutoff':ell,'heavy_caps':hs,'heavy_heavy_doubled':hh,'light_bounds':light,'heavy_losses':loss,'upper_doubled':upper})
 out['supports'][str(s)]={'input_count':len(inputs),'new_exclusions':len(cuts),'remaining':len(inputs)-len(cuts),'excluded_parent_ids':sorted(cuts),'minimum_doubled_gap':min(gaps),'examples':examples,'certificate_sha256':hashlib.sha256((WORK/f'S{s}_PAIRED_BLOCK_CANDIDATES.jsonl').read_bytes()).hexdigest()}
out['total_exclusions']=sum(x['new_exclusions'] for x in out['supports'].values());out['remaining_selected_profiles']=sum(x['remaining'] for x in out['supports'].values())
(R/'ROOT_VERIFIED_PAIRED_BLOCK_STAGE.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({**{k:v for k,v in out.items() if k!='supports'},'supports':{s:{k:v for k,v in x.items() if k not in ('excluded_parent_ids','examples')} for s,x in out['supports'].items()}},indent=2))
