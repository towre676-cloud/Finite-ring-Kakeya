"""Record root reviews after fresh independent middle and M19-role replays."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT/'research_round3/root'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

m = ROOT/'research_round3/middle'
receipt = json.loads((m/'MIDDLE_SUPPORT18_INDEPENDENT_REPLAY.json').read_text())
assert receipt['status']=='PASS'
assert receipt['all_weight_partitions']==239246
assert receipt['remaining_weight_profiles']==0
data = {
    'status':'PASS_ROOT_ANALYTIC_REVIEW_AND_FRESH_REPLAY',
    'theorem':'Dimension5, both rings, |K|<=93 and maximum12..18 imply pair-active support<=17.',
    'all_support18_weight_partitions':239246,
    'round3_new_weight_multiset_exclusions':285,
    'remaining_support18_weight_multisets':0,
    'final_cube_upper_bounds_doubled':[972,991,954,972,962,980],
    'required_doubled_capacity':992,
    'review':'Root read every analytic proof and the complete checker, independently derived the cube-energy inequality, and reran the complete partition and certificate chain. The structural reviewer separately accepted the cube-energy argument.',
    'inherited_dependency':'The complete frozen support>=19 theorem and independently complete pair-spectrum census.',
    'scope_limit':'Supports17 and below remain open. The unrestricted94 lower bound is not claimed.',
    'hashes':{str(p.relative_to(ROOT)):sha(p) for p in [
        m/'verify_support18_completion.py',m/'MIDDLE_SUPPORT18_INDEPENDENT_REPLAY.json',
        m/'MIDDLE_SUPPORT_AT_MOST_SEVENTEEN.md',m/'RESOURCE_COMPATIBILITY_LEMMAS.md',
        m/'CUBE_ENERGY_SUPPORT18_EXCLUSIONS.md',m/'BOUNDARY16_ACTUAL_SUMSET_EXCLUSION.md',
    ]},
}
(HERE/'ROOT_VERIFIED_MIDDLE_SUPPORT17.json').write_text(json.dumps(data,indent=2)+'\n')

g=ROOT/'research_round3/m19'
r=json.loads((g/'UNIQUE_EDGE_ROLE_VERIFICATION_RECEIPT.json').read_text())
assert r['status']=='PASS_EXACT_NORMALIZED_SUPPORT_CENSUS_AND_HALL_CERTIFICATES'
assert r['total_whole_profile_exclusions']==8837 and r['total_remaining_profiles']==3798
assert r['total_hall_witnesses_checked']==88370
data={
    'status':'PASS_ROOT_ANALYTIC_REVIEW_AND_FRESH_REPLAY',
    'scope':'Whole tracked weight/own-direction profiles at exact maximum19, dimension5, both rings.',
    'new_whole_profile_exclusions':8837,
    'remaining_profiles':3798,
    'remaining_by_support':{'11':896,'12':2902},
    'normalized_supports_enumerated':296010,
    'hall_witnesses_checked':88370,
    'analytic_review':[
        'A sole outside-support residue edge must cover all16 labels; under the verified outer cap14, either endpoint of weight<=7 makes this impossible by the three-point sumset obstruction.',
        'A sole hub edge requires an own-positive fibre of weight>=4.',
        'A covering support spans F2^5 and contains a basis. A linear change fixing the hub normalizes that basis, so all marked supports occur in the enumerated supersets of {0,1,2,4,8,16}.',
        'Each failed Hall inequality is a necessary capacity obstruction. Every excluded profile has one failed inequality for every observed role pattern; exact role-pattern enumeration establishes completeness.',
        'The verifier independently counts translated-mask intersections, checks every profile outer cap, and checks exact survivor subtraction. No inherited affine-orbit catalogue is used at this stage.',
    ],
    'stable_hashes':{str(p.relative_to(ROOT)):sha(p) for p in [
        g/'UNIQUE_EDGE_ROLE_PROOF.md',g/'verify_unique_edge_roles.py',
        g/'UNIQUE_EDGE_ROLE_NORMALIZED_CENSUS.json',
        g/'S11_UNIQUE_EDGE_ROLE_CANDIDATES.jsonl',g/'S12_UNIQUE_EDGE_ROLE_CANDIDATES.jsonl',
        g/'s11_after_unique_edge_roles.txt',g/'s12_after_unique_edge_roles.txt',
    ]},
}
(HERE/'ROOT_VERIFIED_M19_UNIQUE_EDGE_ROLES.json').write_text(json.dumps(data,indent=2)+'\n')
print('PASS: middle support<=17; M19 roles leave3798 profiles.')
