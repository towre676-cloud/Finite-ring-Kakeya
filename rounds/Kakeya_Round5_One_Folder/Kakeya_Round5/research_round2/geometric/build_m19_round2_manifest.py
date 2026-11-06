from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
RROOT=ROOT/'research_round2/root'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def record(p):return {'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)}

stages=[
    ('full_pair_spectra',HERE,'S{support}_SPECTRUM_VERIFIED_CERTIFICATES.jsonl','ROOT_VERIFIED_SPECTRUM_STAGE.json'),
    ('outside_support_pair_budget',RROOT,'S{support}_OUTSIDE_SUPPORT_CANDIDATES.jsonl','ROOT_VERIFIED_OUTSIDE_SUPPORT_STAGE.json'),
    ('paired_direction_blocks',HERE,'S{support}_PAIRED_BLOCK_VERIFIED_CERTIFICATES.jsonl','ROOT_VERIFIED_PAIRED_BLOCK_STAGE.json'),
    ('hub_inclusive_spectra',HERE,'S{support}_HUB_COUPLED_VERIFIED_CERTIFICATES.jsonl','ROOT_VERIFIED_HUB_COUPLED_STAGE.json'),
    ('actual_support_degrees',HERE,'S{support}_DEGREE_BLOCK_VERIFIED_CERTIFICATES.jsonl','ROOT_VERIFIED_DEGREE_BLOCK_STAGE.json'),
]
summary={'title':'M19 common-fibre compatibility round2','scope':'Selected size93, maximum19 weight/own-direction profile lists; every exclusion is uniform over support placement and fibre shape for both rings','unrestricted_dimension5_closed':False,'maximum19_closed':False,'stages':[],'supports':{},'complete_censuses':{},'proofs':[]}
all_stage_counts={name:{} for name,_,_,_ in stages}
for s in(11,12):
    inputfile=HERE/f's{s}_remaining_input.txt';lines=inputfile.read_text().splitlines();remaining={int(l.split()[0]):l for l in lines};initial=set(remaining);seen=set()
    for name,directory,template,reviewname in stages:
        path=directory/template.format(support=s);rows=[json.loads(l) for l in path.read_text().splitlines()];ids={r['parent_id'] for r in rows}
        assert len(ids)==len(rows) and ids<=remaining.keys() and not ids&seen
        seen|=ids
        for pid in ids:del remaining[pid]
        all_stage_counts[name][str(s)]={'new_exclusions':len(ids),'remaining':len(remaining),'certificate':record(path)}
    final=HERE/f's{s}_final_round2_survivors.txt';expected=''.join(remaining[pid]+'\n' for pid in sorted(remaining));assert final.read_text()==expected
    summary['supports'][str(s)]={'initial_profiles':len(initial),'new_exclusions':len(seen),'remaining_profiles':len(remaining),'initial_input':record(inputfile),'final_survivors':record(final)}
for name,directory,template,reviewname in stages:
    review=RROOT/reviewname
    item={'name':name,'supports':all_stage_counts[name],'total_exclusions':sum(x['new_exclusions'] for x in all_stage_counts[name].values()),'root_review':record(review) if review.exists() else {'status':'pending','expected_path':str(review.relative_to(ROOT))}}
    if review.exists():item['root_review']['status']=json.loads(review.read_text()).get('status')
    summary['stages'].append(item)
summary['total_new_exclusions']=sum(r['new_exclusions'] for r in summary['supports'].values())
summary['total_remaining_selected_profiles']=sum(r['remaining_profiles'] for r in summary['supports'].values())
assert summary['total_new_exclusions']==38734 and summary['total_remaining_selected_profiles']==30471
for name,path,review in[
    ('full_pair_spectra',HERE/'PAIR_SPECTRUM_CENSUS.json',RROOT/'ROOT_VERIFIED_PAIR_SPECTRUM_CENSUS.json'),
    ('paired_direction_blocks',HERE/'PAIRED_BLOCK_MAXIMUM_CENSUS.json',RROOT/'ROOT_VERIFIED_BLOCK_CENSUS.json'),
    ('support_degree_patterns',HERE/'OUTSIDE_SUPPORT_DEGREE_PATTERNS.json',RROOT/'ROOT_VERIFIED_DEGREE_CENSUS.json'),
]:
    summary['complete_censuses'][name]={'data':record(path),'root_review':record(review) if review.exists() else {'status':'pending','expected_path':str(review.relative_to(ROOT))}}
for name in('FULL_PAIR_SPECTRUM_RESOURCE_PROOF.md','PAIRED_BLOCK_RESOURCE_PROOF.md','PROFILE2_ANALYTIC_BLOCK_EXCLUSION.md','HUB_COUPLED_RESOURCE_PROOF.md','DEGREE_BLOCK_RESOURCE_PROOF.md','M19_NEXT_FRONTIER.md'):
    summary['proofs'].append(record(HERE/name))
summary['status']='ROOT_VERIFIED' if all(r['root_review'].get('status')=='PASS' for r in summary['stages']) else 'LOCALLY_VERIFIED_ROOT_DEGREE_STAGE_PENDING'
(HERE/'M19_ROUND2_FINAL_MANIFEST.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'status':summary['status'],'new_exclusions':summary['total_new_exclusions'],'remaining':summary['total_remaining_selected_profiles'],'supports':{s:{k:v for k,v in r.items() if isinstance(v,int)} for s,r in summary['supports'].items()}},indent=2))
