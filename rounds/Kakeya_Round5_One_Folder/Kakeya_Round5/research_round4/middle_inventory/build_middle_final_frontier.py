"""Merge the frozen middle inventory with the disjoint priced-nine stage."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
baseline=json.loads((HERE/'MIDDLE_COMPLETE_INVENTORY.json').read_text())
priced=json.loads((HERE/'PRICED_NINE_INDEPENDENT_REPLAY.json').read_text())
assert baseline['status']==priced['status']=='PASS'
price_by={(r['support'],r['maximum']):r for r in priced['records']}
records=[]
for row in baseline['records']:
    p=price_by[row['support'],row['maximum']]
    assert row['remaining_weight_profiles']==p['input']
    records.append({**row,
                    'baseline_remaining_weight_profiles':row['remaining_weight_profiles'],
                    'priced_nine_cuts':p['cuts'],
                    'remaining_weight_profiles':p['remaining']})
assert sum(r['remaining_weight_profiles'] for r in records)==275755
final={
    'status':'PASS',
    'scope':'Complete normalized middle weight inventory, both rings, dimension5, size<=93, exact maximum12..18, pair-active support10..17.',
    'all_weight_profiles':2163945,
    'global_quota_cuts':1728113,
    'inherited_selected_spectrum_cuts':23164,
    'new_generic_geometry_cuts':135877,
    'new_joint_cube_energy_cuts':524,
    'new_priced_nine_cuts':512,
    'total_newly_recorded_weight_exclusions':136913,
    'remaining_weight_profiles':275755,
    'supports':priced['supports'],
    'records':records,
    'empty_cells':priced['new_empty_weight_cells'],
    'remaining_nonempty_cells':55,
    'necessary_support_bounds_by_maximum':{str(m):16 if m==18 else 17 for m in range(12,19)},
    'maximum18_support16_theorem_scope':'Uses complete inventory for support17 and the previously complete exclusions for support>=18; no entire maximum18 stratum is closed.',
    'baseline_receipt':'MIDDLE_COMPLETE_INVENTORY.json',
    'priced_stage_receipt':'PRICED_NINE_INDEPENDENT_REPLAY.json',
    'stable_files':{name:sha(HERE/name) for name in ['after_cube_weight_survivors.txt','PRICED_NINE_HEAVY_CUTS.jsonl','after_priced_nine_survivors.txt']},
    'scope_limit':'Remaining entries are weight-profile relaxation survivors, not constructions or enumerated residue/shape assignments.',
}
(HERE/'MIDDLE_FINAL_FRONTIER_AFTER_PRICING.json').write_text(json.dumps(final,indent=2)+'\n')
print(json.dumps({'status':'PASS','remaining_weight_profiles':275755,'new_price_cuts':512,'empty_cells':final['empty_cells']}))
