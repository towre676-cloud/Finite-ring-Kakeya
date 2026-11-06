"""Package immutable inherited payloads and the credited round3 proof chain."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT=Path(__file__).resolve().parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()
old=ROOT/'Kakeya_Research_Round2_Proofs.zip'
assert sha(old.read_bytes())=='6ddf3c88c04aa8880dc034146578a720a5d71e433409595a3b29e7f008b70948'
with zipfile.ZipFile(old) as z:
    payload={name:z.read(name) for name in z.namelist() if not name.endswith('/')}
old_names=set(payload)

def add(relative):
    path=ROOT/relative
    assert path.is_file(),relative
    data=path.read_bytes()
    if relative in payload:
        assert payload[relative]==data,'Inherited payload changed: '+relative
    else:
        payload[relative]=data

for relative in ('VERIFY_ROUND3.py','README_Round3.txt','Kakeya_Research_Round3_Report.txt',
                 'Kakeya_Research_Frontier_Round3.json'):
    add(relative)

m19=ROOT/'research_round3/m19/M19_ROUND3_AUTHORITATIVE_FILES.txt'
for relative in m19.read_text().splitlines():
    if relative.strip():add(relative.strip())
add(str(m19.relative_to(ROOT)))

middle=ROOT/'research_round3/middle'
receipt=json.loads((middle/'MIDDLE_SUPPORT18_INDEPENDENT_REPLAY.json').read_text())
for relative in receipt['dependencies']:
    add(relative)
for name in ('MIDDLE_SUPPORT18_INDEPENDENT_REPLAY.json','MIDDLE_SUPPORT_AT_MOST_SEVENTEEN.md',
             'eight_heavy_gap_screen.py','eight_heavy_slot_price_screen.py',
             'three_heavy_period_screen.py','three_neighbor_slot_price_screen.py',
             'two_heavy_deleted_direction_screen.py','nine_heavy_slot_price_screen.py',
             'nine_heavy_sumfree_price_screen.py','halfspace_maximal_direction_bonus_screen.py',
             'final_analytic_support18_screen.py'):
    add('research_round3/middle/'+name)

for name in (
 'FULL_HUB_TWELVE_ANALYTIC_REVIEW.md','FULL_HUB_TWELVE_INDEPENDENT_REVIEW.json',
 'M11_CURRENT_FRONTIER_ROUND3.json','M11_SUPPORT_SEVENTEEN_EXCLUSION.md',
 'NINE_POINT_DIFFERENCE_RIGIDITY.md','S17_SUPPORT_REDUCTION.json',
 'S17_ASSIGNMENT_DUAL_CERTIFICATES.json','S17_ENVELOPE_INDEPENDENT_REPLAY.json',
 'S17_PLACEMENT_INDEPENDENT_REPLAY.json','Q_FORCED_PERIOD_RANK_CERTIFICATES.json',
 'S17_NINE_HEAVY_SUBSETS.json','verify_s17_envelope_duals.py',
 'verify_remaining_s17_placements.py','certify_s17_envelopes.py',
 'search_pr_placements.cpp','PR_PLACEMENT_INPUT.txt','PR_PLACEMENT_RESULTS.jsonl',
 's16/M11_CURRENT_FRONTIER_AFTER_S16.json','s16/M11_SIX_SUPPORT16_CLASS_EXCLUSIONS.md',
 's16/S16_ASSIGNMENT_DUAL_CERTIFICATES.json','s16/S16_EXACT_CHECKPOINT.json',
 's16/S16_INDEPENDENT_REPLAY.json','s16/certify_s16_checkpoint.py','s16/verify_s16_checkpoint.py',
):add('research_round3/m11/'+name)

for directory in ('research_round3/root','research_round3/reviews'):
    for path in sorted((ROOT/directory).iterdir()):
        if path.is_file() and path.suffix in {'.py','.txt','.md','.json'} and path.name not in {
            'TEN_HEAVY_NORMALIZED_CASES.json','PORTABLE_REPLAY_DIRECTORY.txt',
            'PACKAGE_BUILD_RECEIPT.json','PORTABLE_REPLAY_PROGRESS.txt',
        }:
            add(str(path.relative_to(ROOT)))

catchup=ROOT/'research_round3/catchup/Kakeya_Energy_and_Compatibility_2026-10-27.zip'
prefix='research_round3/catchup/energy_compatibility/'
with zipfile.ZipFile(catchup) as z:
    for name in z.namelist():
        if not name.endswith('/'):
            payload[prefix+name]=z.read(name)

items=[{'path':p,'bytes':len(b),'sha256':sha(b)} for p,b in sorted(payload.items())]
manifest={
 'title':'Kakeya research round3 verified proof checkpoint',
 'version':1,'entry_point':'VERIFY_ROUND3.py',
 'scope':'All credited round3 work with immutable round2 payloads and the caught-up fixed-shape compatibility package. Older unrestricted strata and minima remain explicitly inherited.',
 'inherited_round2_archive_sha256':sha(old.read_bytes()),
 'unchanged_round2_payload_files':len(old_names),
 'payload_count':len(items),'payload_bytes':sum(i['bytes'] for i in items),
 'files':items,
}
data=(json.dumps(manifest,indent=2)+'\n').encode()
(ROOT/'MANIFEST_ROUND3.json').write_bytes(data)
payload['MANIFEST_ROUND3.json']=data
target=ROOT/'Kakeya_Research_Round3_Proofs.zip'
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name,b in sorted(payload.items()):z.writestr(name,b)
result={'archive':target.name,'bytes':target.stat().st_size,'sha256':sha(target.read_bytes()),
        'payload_files':len(items),'payload_bytes':manifest['payload_bytes'],
        'unchanged_round2_payload_files':len(old_names),'manifest_sha256':sha(data)}
(ROOT/'research_round3/root/PACKAGE_BUILD_RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
