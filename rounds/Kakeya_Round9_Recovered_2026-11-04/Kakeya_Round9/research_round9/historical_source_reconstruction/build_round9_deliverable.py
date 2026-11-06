from pathlib import Path
import hashlib,json,shutil,zipfile,lzma

BASE=Path('/workspace/scratch/c084111f9526')
ROOT=BASE/'sources/round8/Kakeya_Round8'
DEST=BASE/'deliverables/Kakeya_Round9'
R=ROOT/'research_round9'
d=json.loads((R/'ROUND9_VERIFIED_FRONTIER.json').read_text())
assert d['status']=='PASS_FRESH_NEW_PROOFS_AND_EXACT_CNF_REGENERATION'
s=json.loads((R/'COMPLETE_QUEUE_CAMPAIGN.json').read_text())
assert s['status']=='COMPLETE_ALL_QUEUE_CASES_ACCOUNTED_FOR' and len(s['results'])==54 and not s['errors']
assert d['new_marked_exclusions']==sum(x['exclusion_credited'] for x in s['results'])
for p in R.rglob('*'):
    if not p.is_file() or '__pycache__' in p.parts or 'tools' in p.relative_to(R).parts or 'replay_tools' in p.relative_to(R).parts:continue
    if p.suffix not in ('.py','.json','.xz','.txt'):continue
    target=DEST/'research_round9'/p.relative_to(R);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
incident=next((R/'cases').glob('*/rejected_truncated_input.cnf'))
target=DEST/'research_round9/integrity_incident/rejected_truncated_input.cnf.xz';target.parent.mkdir(parents=True,exist_ok=True)
with incident.open('rb') as a,lzma.open(target,'wb',preset=1) as b:shutil.copyfileobj(a,b)
closed=d['complete_support13_affine_classes_by_exact_maximum'];counts=d['marked_coverage_out_of55'];remaining=d['remaining_queued_masks_by_maximum']
n=d['new_marked_exclusions'];unknown=54-n
lines=['# Kakeya Round 9 — certified support-13 progress','',
'Date: November 4, 2026. Rings: Z/4Z and F2[epsilon]/(epsilon^2).',
'',f'**{n} new marked-case exclusions have complete refutations accepted by pinned CakeML against exactly regenerated CNFs.** Every one of the 54 prepared exact-maximum-12/13 support-13 cases has a retained bounded-search outcome. '+str(unknown)+' remain unexcluded after the 45-second search cap. No actual Kakeya counterexample was obtained.','',
'| Exact maximum | Marked cases covered, of 55 | Remaining marked cases | Complete affine support classes |','|---|---:|---:|---|']
for m in ('12','13'):lines.append(f"| {m} | {counts[m]} | {len(remaining[m])} | {', '.join(map(str,closed[m])) or 'None'} |")
lines += ['', 'The covered marked counts include 28 inherited joint-maxima certificates at each maximum. The new checks freshly verify only the Round 9 refutations. Whole affine-class closures combine these inherited certificates with new ones after independently checking all 169 largest-fibre transports. No claim is made that all 54 new searches were UNSAT. A timeout remains UNKNOWN.', '',
'## Precisely what is proved','',
'For either target ring, a Kakeya subset of R^5 with at most 93 points, pair-active support 13 and exact maximum 12 or 13 cannot have an affine support class listed in its row above, conditional on the inherited mathematical reduction, complete spectrum data and the one-way soundness of the frozen necessary-condition encoder. Ties for the largest fibre are allowed. Every marked role needed by a closed class is accounted for.', '',
'The new marked exclusions are geometric placements, not whole weight profiles. The tracked 182,526 middle-maximum weight profiles and 42 maximum-11 affine classes have not been reduced by arithmetic subtraction of these results. The unrestricted dimension-five lower bound 94 and the all-dimensional law 3*2^n-2 remain OPEN.', '',
'## Verification','',
'From this extracted folder, on Linux x86_64 with Python 3 and gcc:', '',
'```bash','python3 research_round9/replay_and_merge.py --fresh-proofs','```','',
'This performs no SAT search and requires no PySAT installation or network. It regenerates every one of the 54 exact formulas, verifies stored bytes and scope metadata, reconstructs LRAT from every new binary DRAT proof, and requires acceptance by the pinned CakeML checker. It also verifies the explicit affine transports and merges the marked-case ledger. Run without Python -O. Temporary LRAT files are removed after checking.', '',
'`research_round9/ROUND9_VERIFIED_FRONTIER.json` records the completed fresh replay. `COMPLETE_QUEUE_CAMPAIGN.json` contains all 54 explicit outcomes. Each case has its exact compressed CNF, hashes, search logs and receipt; certified cases additionally have the compressed complete proof and checker logs. `SOLVER_PROVENANCE.json` identifies the untrusted search engine. The C LRAT utility remains diagnostic only and is never an acceptance authority.', '',
'Search reproduction, optionally requiring python-sat, uses `research_round9/resume_campaign.py`. Existing receipts are reused. Original Round 8 files were not edited; this is a compact continuation package with the required encoder/data/checker sources. Earlier proof streams are not duplicated. The original Round 8 archive remains the source for independently replaying inherited exclusions.', '',
'## Integrity incident','',
'One initial pilot working CNF was found truncated to a prefix after search. Its hash mismatch was rejected, no exclusion was credited, and the rejected bytes and incident record are retained. The cause is undetermined. The case was regenerated and rerun; its final outcome remains UNKNOWN. Every final retained formula was subsequently regenerated byte for byte in the fresh replay. No mismatch was waived.', '',
'## Remaining boundary and next computation','',
'The full mathematical reduction, spectrum census and Python encoder are not proof-assistant formalized. A checked Boolean refutation establishes the declared CNF is unsatisfiable; the separate one-way soundness argument supplies its Kakeya meaning. Model-based reviews are not independent human refereeing.', '',
'The remaining exact-maximum-12/13 marked masks are listed in ROUND9_VERIFIED_FRONTIER.json. Prioritize new geometry or separately frozen stronger encodings on these hard cases; rerunning unchanged short searches is not a new result. The maximum-11/support-14 branch and larger middle-maximum supports remain open.', '',
'The scope-specific incidence proof is in research_round8/incidence/MISSING_DIRECTION_INCIDENCE.md. The baseline assignment argument is in research_round6/encoder_audit/ONE_WAY_SOUNDNESS_AUDIT.md. The tetrahedral extension argument and its proof are retained alongside the frozen encoders.', '']
(DEST/'README.md').write_text('\n'.join(lines))
(DEST/'VERIFY_ROUND9.py').write_text("from pathlib import Path\nimport subprocess,sys\nroot=Path(__file__).resolve().parent\nraise SystemExit(subprocess.call([sys.executable,str(root/'research_round9/replay_and_merge.py'),'--fresh-proofs'],cwd=root))\n")
manifest={str(p.relative_to(DEST)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(DEST.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='PAYLOAD_SHA256.json'}
(DEST/'PAYLOAD_SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
archive=BASE/'deliverables/Kakeya_Round9_Certified_Advance_2026-11-04.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
    for name in sorted(manifest):z.write(DEST/name,'Kakeya_Round9/'+name)
    z.write(DEST/'PAYLOAD_SHA256.json','Kakeya_Round9/PAYLOAD_SHA256.json')
print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'files':len(manifest)+1,'new_exclusions':n,'remaining':remaining,'closed_classes':closed},indent=2))
