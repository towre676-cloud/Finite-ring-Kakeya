"""Replay archived inputs and exercise real RAT and invalid-proof controls.

The controls check the acceptance boundary: an invalid proof of a satisfiable
CNF, omitted mandatory RAT witnesses, missing contradiction hints, changed
input hashes, and an incomplete declared case inventory must be rejected.
"""
from pathlib import Path
import json
import re
import subprocess
import sys
import tempfile
import time

import audit_certificates as audit

HERE = Path(__file__).resolve().parent


def main():
    started = time.monotonic()
    archived = HERE/'archived_audit'
    subprocess.run([sys.executable, str(HERE/'audit_certificates.py'),
                    str(HERE/'ARCHIVED_EXAMPLES_MANIFEST.json'), '--output', str(archived),
                    '--heap-mb', '64', '--stack-mb', '64', '--c-diagnostic'], check=True)
    receipt = json.loads((archived/'AUDIT_RECEIPT.json').read_text())
    audit.require(receipt['status']=='PASS_ALL_DECLARED_CNF_CERTIFICATES'
                  and receipt['checked_cases']==4, 'Archived proof replay did not pass')
    controls = HERE/'control_audit'
    controls.mkdir(exist_ok=True)
    outcomes = []
    audit.verify_sources()
    with tempfile.TemporaryDirectory(prefix='kakeya_checker_controls_') as tmp:
        binaries, build = audit.build_checkers(tmp, controls/'build_logs')
        rat_cnf, rat_drat = HERE/'controls/rat_example.cnf', HERE/'controls/rat_example.drat'
        positive = audit.check_pair(rat_cnf, rat_drat, controls/'genuine_rat', binaries,
                                   timeout=30, heap_mb=64, stack_mb=64, c_diagnostic=True)
        audit.require(positive['status']=='PASS_CNF_UNSAT_VIA_CAKEML_LRAT', 'Real RAT control failed')
        drat_log = (controls/'genuine_rat/drat_trim.stdout.txt').read_text()
        rat_counts = [int(x) for x in re.findall(r'(\d+) RAT lemmas in core', drat_log)]
        audit.require(rat_counts and max(rat_counts)>=1, 'Control did not exercise a genuine RAT step')
        outcomes.append({'control':'genuine_non_RUP_RAT_derivation', 'expected':'ACCEPT', 'result':positive})

        sat = HERE/'controls/satisfiable.cnf'
        invalid = audit.check_pair(sat, HERE/'controls/invalid_empty.drat',
                                   controls/'fake_unsat', binaries, timeout=30,
                                   heap_mb=64, stack_mb=64)
        audit.require(invalid['status']=='FAIL' and not invalid['drat_trim']['accepted'],
                      'Invalid UNSAT proof of a satisfiable CNF was accepted')
        outcomes.append({'control':'fake_empty_clause_on_satisfiable_CNF',
                         'expected':'REJECT', 'result':invalid})

        good = (controls/'genuine_rat/converted.lrat').read_text().splitlines()
        missing_rat = []
        changed = False
        for line in good:
            fields = line.split()
            if not changed and len(fields)>2 and fields[1]!='d':
                # Retain the genuine learned clause and only its first RAT
                # target witness; omit other mandatory opposite-pivot cases.
                zero = fields.index('0', 1)
                hints = fields[zero+1:-1]
                boundaries = [i for i, value in enumerate(hints) if int(value)<0]
                audit.require(len(boundaries)>=2, 'Expected several RAT obligations')
                hints = hints[:boundaries[1]]
                line = ' '.join(fields[:zero+1]+hints+['0'])
                changed = True
            missing_rat.append(line)
        audit.require(changed, 'No RAT line was changed')
        missing_empty = good[:]
        fields = missing_empty[-1].split()
        audit.require(fields[1]=='0', 'Expected final empty-clause line')
        missing_empty[-1] = fields[0]+' 0 0'
        for name, lines in [('omitted_RAT_targets', missing_rat),
                            ('omitted_contradiction_hints', missing_empty)]:
            folder=controls/name
            folder.mkdir(exist_ok=True)
            proof=folder/'invalid.lrat'
            proof.write_text('\n'.join(lines)+'\n')
            c = audit.run_checker([binaries['lrat-check'], rat_cnf, proof], folder,
                                  'lrat_check_c', 30, 'c VERIFIED')
            cake = audit.run_checker([binaries['cake_lpr'], '--CML_HEAP_SIZE=64',
                                     '--CML_STACK_SIZE=64', rat_cnf, proof], folder,
                                    'cake_lpr', 30, 's VERIFIED UNSAT', True)
            audit.require(not cake['accepted'], 'CakeML accepted a tampered LRAT proof: '+name)
            audit.require(c['accepted'] == (name=='omitted_contradiction_hints'),
                          'The pinned C diagnostic behavior changed: '+name)
            outcomes.append({'control':name, 'expected':'REJECT',
                             'proof_sha256':audit.sha(proof),'lrat_check_c':c,'cake_lpr':cake})

        # A minimal actual false-UNSAT acceptance by the ordinary C checker.
        # x1=true satisfies the entire input CNF. No proof of UNSAT can exist.
        folder=controls/'C_checker_false_positive'
        folder.mkdir(exist_ok=True)
        fake=folder/'invalid.lrat'
        fake.write_text('2 0 0\n')
        c=audit.run_checker([binaries['lrat-check'],sat,fake],folder,'lrat_check_c',30,'c VERIFIED')
        cake=audit.run_checker([binaries['cake_lpr'],'--CML_HEAP_SIZE=64','--CML_STACK_SIZE=64',sat,fake],
                              folder,'cake_lpr',30,'s VERIFIED UNSAT',True)
        audit.require(c['accepted'] and not cake['accepted'],
                      'The pinned-checker false-positive reproducer behaved unexpectedly')
        outcomes.append({'control':'bogus_empty_LRAT_on_satisfiable_CNF','expected':'REJECT_BY_REQUIRED_GATE',
                         'CNF_satisfying_assignment':{'1':True},'lrat_check_c':c,'cake_lpr':cake,
                         'consequence':'The ordinary C checker is diagnostic only; CakeML acceptance is mandatory.'})

        original = json.loads((HERE/'ARCHIVED_EXAMPLES_MANIFEST.json').read_text())
        for case in original['cases']:
            for field in ('cnf','proof'):
                case[field] = str((HERE/case[field]).resolve())
        for name in ('changed_CNF_hash','missing_declared_case'):
            value=json.loads(json.dumps(original))
            if name=='changed_CNF_hash':
                value['cases'][0]['cnf_sha256']='0'*64
                expected='Input hash mismatch'
            else:
                value['expected_case_ids'].append('missing_case')
                expected='Actual cases do not equal'
            file=Path(tmp)/(name+'.json')
            audit.dump(file,value)
            try:
                audit.load_manifest(file)
            except ValueError as error:
                audit.require(expected in str(error), 'Wrong rejection reason: '+str(error))
                outcomes.append({'control':name,'expected':'REJECT','error':str(error)})
            else:
                raise ValueError('An invalid manifest was accepted: '+name)

        # These records test the metadata/transport gate only. They deliberately
        # contain no CNF/proof paths, and are never counted as checked proofs.
        contract_path=HERE/'M19_MARKED_CASE_CONTRACT.json'
        contract=json.loads(contract_path.read_text())
        metadata_cases=[{'case_id':entry['case_id'], 'marked_support':{
            'support':entry['hub_zero_support'], 'distinguished_hub':0,
            'affine_map_to_contract':[0,1,2,4,8,16]}} for entry in contract['cases']]
        coverage_manifest={'expected_case_ids':[c['case_id'] for c in metadata_cases],
            'coverage_contract':{'path':str(contract_path),
                'sha256':audit.sha(contract_path), 'ring_scope':'common_relaxation_both_rings'}}
        cover=audit.check_marked_contract(coverage_manifest,metadata_cases,HERE/'metadata_only.json')
        outcomes.append({'control':'38_contract_metadata_records_only','expected':'ACCEPT_METADATA',
                         'CNF_certificates_checked':0,'result':cover})
        for name in ('wrong_marked_support_transport','incomplete_contract_inventory'):
            value=json.loads(json.dumps(coverage_manifest))
            entries=json.loads(json.dumps(metadata_cases))
            if name=='wrong_marked_support_transport':
                entries[0]['marked_support']['affine_map_to_contract'][0]=1
                expected='Marked support does not transport'
            else:
                value['expected_case_ids']=value['expected_case_ids'][:-1]
                expected='Expected case ids do not exactly match'
            try:
                audit.check_marked_contract(value,entries,HERE/'metadata_only.json')
            except ValueError as error:
                audit.require(expected in str(error),'Wrong contract rejection reason: '+str(error))
                outcomes.append({'control':name,'expected':'REJECT','error':str(error)})
            else:
                raise ValueError('An invalid support contract was accepted: '+name)

    result = {
        'status':'PASS_ARCHIVED_CERTIFICATES_AND_ACCEPTANCE_CONTROLS',
        'archived_Kakeya_cases_checked':4,
        'genuine_RAT_control_cases':1,
        'negative_controls_rejected_by_required_gate':8,
        'ordinary_C_checker_false_UNSAT_acceptance_reproduced':True,
        'new_Claude_maximum19_proofs_checked_here':0,
        'new_Claude_maximum19_status':'REPORTED_BY_USER; SOURCE_CNF_AND_PROOF_FILES_NOT_AVAILABLE_HERE',
        'checks':['Pinned official DRAT-trim','Mandatory upstream verified CakeML LPR checker artifact'],
        'optional_diagnostic':'The ordinary C LRAT checker is not an acceptance authority; its false positive is reproduced.',
        'upstream_formal_development_rebuilt_here':False,
        'encoder_soundness_proved_by_this_audit':False,
        'case_orbit_completeness_proved_by_this_audit':False,
        'archived_receipt_sha256':audit.sha(archived/'AUDIT_RECEIPT.json'),
        'control_build':build,'controls':outcomes,
        'source_hashes':{p.name:audit.sha(p) for p in [Path(__file__),HERE/'audit_certificates.py',
                                                   HERE/'ARCHIVED_EXAMPLES_MANIFEST.json']},
        'seconds':round(time.monotonic()-started,6),
    }
    audit.dump(HERE/'PROOF_AUDIT_REPLAY.json',result)
    print(json.dumps({k:result[k] for k in ['status','archived_Kakeya_cases_checked',
                    'genuine_RAT_control_cases','negative_controls_rejected_by_required_gate',
                    'new_Claude_maximum19_proofs_checked_here','seconds']},indent=2))


if __name__=='__main__':
    main()
