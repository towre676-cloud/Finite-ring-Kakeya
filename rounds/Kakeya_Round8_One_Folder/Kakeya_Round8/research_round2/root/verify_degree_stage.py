"""Root normalized degree census, exact dual replay, and source-set accounting."""
import itertools,json,hashlib,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];GEO=ROOT/'research_round2/geometric'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=GEO/'OUTSIDE_SUPPORT_DEGREE_PATTERNS.json';j=json.loads(source.read_text());base={0,1,2,4,8,16};rest=sorted(set(range(32))-base)
out={'status':'PASS','depends_on_old_affine_orbit_census':False,'supports':{}}
for s in(11,12):
 seen=set();total=0;covered=0
 for extra in itertools.combinations(rest,s-6):
  total+=1;S=base|set(extra)
  if len({x^y for x,y in itertools.combinations(S,2)})!=31:continue
  covered+=1;T=S-{0};seen.add(tuple(sorted(sum((a^b)not in S for b in T if b!=a) for a in T)))
 assert seen=={tuple(r['degrees']) for r in j[str(s)]['degree_patterns']}
 out['supports'][str(s)]={'normalized_supports':total,'difference_covering_supports':covered,'degree_patterns':len(seen),'patterns':[list(d) for d in sorted(seen)]}
out['source_sha256']=sha(source);out['completeness_proof']='S+S=V implies full rank. A linear map fixinghub0 sendsfiveindependent supportpoints tocoordinatebasis. Allremainingpointchoicesareenumerated.'
(HERE/'ROOT_VERIFIED_DEGREE_CENSUS.json').write_text(json.dumps(out,indent=2)+'\n')
subprocess.run([sys.executable,str(GEO/'verify_degree_block_certificates.py')],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
previous=json.loads((HERE/'ROOT_VERIFIED_HUB_COUPLED_STAGE.json').read_text());receipt=json.loads((GEO/'DEGREE_BLOCK_VERIFICATION_RECEIPT.json').read_text())
assert receipt['status']=='PASS_EXACT_DEGREE_BLOCK_AND_ASSIGNMENT_DUAL_REPLAY'
out={'status':'PASS','independent_degree_census':'research_round2/root/ROOT_VERIFIED_DEGREE_CENSUS.json','degree_census_inherits_382_orbits':False,'dual_checker':'Reviewed and rerun exact local and global assignment-dual checker','supports':{}}
for s in(11,12):
 inputs={int(l.split()[0]):l for l in(GEO/f's{s}_after_hub_coupling.txt').read_text().splitlines()}
 assert len(inputs)==previous['supports'][str(s)]['remaining']
 before={int(l.split()[0]):l for l in(GEO/f's{s}_after_paired_blocks.txt').read_text().splitlines()}
 old=set(previous['supports'][str(s)]['excluded_parent_ids']);assert inputs=={p:v for p,v in before.items() if p not in old}
 ids=[json.loads(l)['parent_id'] for l in(GEO/f'S{s}_DEGREE_BLOCK_CANDIDATES.jsonl').read_text().splitlines()]
 assert len(ids)==len(set(ids)) and set(ids)<=inputs.keys()
 final={int(l.split()[0]):l for l in(GEO/f's{s}_final_round2_survivors.txt').read_text().splitlines()}
 assert final=={p:v for p,v in inputs.items() if p not in set(ids)}
 out['supports'][str(s)]={'input_count':len(inputs),'new_exclusions':len(ids),'remaining':len(final),'excluded_parent_ids':sorted(ids),'certificate_sha256':sha(GEO/f'S{s}_DEGREE_BLOCK_CANDIDATES.jsonl')}
out['total_exclusions']=sum(x['new_exclusions'] for x in out['supports'].values());out['remaining_selected_profiles']=sum(x['remaining'] for x in out['supports'].values());out['dual_receipt_sha256']=sha(GEO/'DEGREE_BLOCK_VERIFICATION_RECEIPT.json')
(HERE/'ROOT_VERIFIED_DEGREE_BLOCK_STAGE.json').write_text(json.dumps(out,indent=2)+'\n');print('Degree census and25 profile exclusions PASS',flush=True)
