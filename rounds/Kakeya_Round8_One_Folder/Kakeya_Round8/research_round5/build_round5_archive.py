"""Create one complete archive, preserving every prior Round4 entry exactly."""
from hashlib import sha256
from pathlib import Path
import json
import zipfile

ROOT = Path(__file__).resolve().parent.parent
OLD = ROOT/'Kakeya_Complete_Round4.zip'
OUTPUT = ROOT/'Kakeya_Complete_Round5.zip'
OLD_SHA = '866650cf3640b5ddf4e8e33873c361797e821d4458379d6b0e39ae39321e5ca9'


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def refresh_snapshot_hashes():
    # Replays legitimately change elapsed-time receipts. Pin the final
    # archive snapshot after all root checks, without altering source files.
    for name in ('FROZEN_STAGE_HASHES.json','FULL_S10_STAGE_HASHES.json'):
        path = ROOT/'research_round5/support10_roles'/name
        data = json.loads(path.read_text())
        for filename in data:
            data[filename] = digest(path.parent/filename)
        path.write_text(json.dumps(data,indent=2)+'\n')
    path = ROOT/'research_round5/middle_duals/MODEL_AUDIT_AND_RESULTS.json'
    data = json.loads(path.read_text())
    for filename in data['files_sha256']:
        data['files_sha256'][filename] = digest(ROOT/filename)
    data['snapshot_note'] = 'File hashes refreshed after root replay for the delivered archive; elapsed-time receipts may change on a new replay.'
    path.write_text(json.dumps(data,indent=2)+'\n')


def main():
    if digest(OLD) != OLD_SHA:
        raise SystemExit('Prior archive hash mismatch.')
    refresh_snapshot_hashes()
    additions = {}
    excluded_names = {'certify_marked_cover','enumerate_marked_supports'}
    for path in (ROOT/'research_round5').rglob('*'):
        if not path.is_file() or '__pycache__' in path.parts or path.name in excluded_names:
            continue
        if path.suffix in ('.pyc','.o','.olean','.ilean','.exe'):
            continue
        additions[str(path.relative_to(ROOT))] = path.read_bytes()
    for name in ('Kakeya_Research_Frontier_Round5.json','README_Round5.txt','VERIFY_ROUND5.py',
                 'Kakeya_Round5_Portable_Replay_Receipt.json'):
        path = ROOT/name
        if path.exists():
            additions[name] = path.read_bytes()
    with zipfile.ZipFile(OLD) as source:
        previous = {name:source.read(name) for name in source.namelist()}
    if set(previous) & set(additions):
        raise SystemExit('A new file would overwrite a historical archive entry.')
    payload = previous | additions
    manifest = {
        'title':'Complete Kakeya Round5 archive', 'date':'2026-10-28',
        'prior_archive':{'filename':OLD.name,'sha256':OLD_SHA,'entries_preserved':len(previous),
                         'all_entry_bytes_preserved':True},
        'new_payload_files':len(additions), 'payload_files':len(payload),
        'current_frontier':'Kakeya_Research_Frontier_Round5.json',
        'main_new_proof':'research_round5/support10_roles/SUPPORT10_UNRESTRICTED_PROOF.md',
        'monograph_words':len((ROOT/'research_round5/Kakeya_Round5_Monograph.txt').read_text().split()),
        'new_Claude_CNF_DRAT_pairs_included':0,
        'files_sha256':{name:sha256(data).hexdigest() for name,data in sorted(payload.items())}
    }
    assert manifest['monograph_words'] == 1500
    manifest_bytes = (json.dumps(manifest,indent=2)+'\n').encode()
    (ROOT/'MANIFEST_ROUND5.json').write_bytes(manifest_bytes)
    with zipfile.ZipFile(OUTPUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as target:
        for name,data in sorted(payload.items()):
            target.writestr(name,data)
        target.writestr('MANIFEST_ROUND5.json',manifest_bytes)
    with zipfile.ZipFile(OUTPUT) as target:
        assert target.testzip() is None
        assert len(target.namelist()) == len(payload)+1
        assert all(target.read(name) == data for name,data in previous.items())
    print(json.dumps({'archive':str(OUTPUT),'bytes':OUTPUT.stat().st_size,'sha256':digest(OUTPUT),
                      'entries':len(payload)+1,'prior_entries_preserved':len(previous),
                      'new_payload_files':len(additions),'monograph_words':1500},indent=2))


if __name__ == '__main__':
    main()
