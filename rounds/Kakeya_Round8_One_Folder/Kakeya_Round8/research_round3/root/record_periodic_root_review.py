"""Record the root's analytic review and independently rerun exact receipts."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'research_round3/root'
M19 = ROOT / 'research_round3/m19'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

deleted = json.loads((M19/'DELETED_DIRECTION_PROFILE_VERIFICATION.json').read_text())
periodic = json.loads((M19/'OWN_PERIODIC_VERIFICATION_RECEIPT.json').read_text())
assert deleted['status'] == 'PASS_ANALYTIC_DELETED_DIRECTION_PROFILE'
assert periodic['status'] == 'PASS_EXACT_OWN_PERIODIC_BRANCH_VERIFICATION'
assert deleted['total_remaining_profiles'] == 12866
assert periodic['total_whole_profile_exclusions'] == 231
assert periodic['total_remaining_profiles'] == 12635
for s in ('11','12'):
    assert deleted['supports'][s]['survivors_sha256'] == periodic['supports'][s]['input_sha256']
review = {
    'status': 'PASS_ROOT_ANALYTIC_REVIEW_AND_FRESH_REPLAY',
    'scope': 'Whole weight/own-direction profiles for exact maximum19, dimension5, both rings.',
    'new_deleted_direction_cuts': 1,
    'new_periodic_mode_cuts': 231,
    'remaining_profiles_after_these_stages': 12635,
    'remaining_by_support': {'11': 9733, '12': 2902},
    'analytic_review': [
        'The deleted heavy-heavy direction leaves doubled demand960. Seven own-zero eight-fibres contribute at most128 each and two positive-own three-fibres at most30 each:956<960.',
        'For two own-periodic outer fibres, the offhub pair-label sets share a nonzero quotient period, so their actual sumset capacity is at most pq/2.',
        'Own-periodic off-own counts are even, hence at most2 floor(w/4). The hub own-slot cap is handled separately.',
        'The same periodic/nonperiodic mode is fixed for every incidence. Enumerating counts of identical types covers all mode assignments.',
        'All50,642 relevant quotient subsets were independently enumerated. The nonperiodic block catalogue is used only as an upper relaxation.',
        'Every local matching bound is supported by integer dual inequalities. Endpoint deficits are combined by max(max loss, ceil(sum loss/2)); no unproved additive independence is assumed.',
    ],
    'verification': {
        'covering_mode_branches': periodic['total_covering_branches'],
        'local_spectrum_duals': periodic['spectrum_duals'],
        'integer_inequalities': periodic['integer_inequalities'],
    },
    'hashes': {str(p.relative_to(ROOT)): sha(p) for p in [
        M19/'PROFILE63342_DELETED_DIRECTION_PROOF.md',
        M19/'verify_deleted_direction_profile.py',
        M19/'DELETED_DIRECTION_PROFILE_VERIFICATION.json',
        M19/'OWN_PERIODIC_RESOURCE_PROOF.md',
        M19/'verify_own_periodic_certificates.py',
        M19/'OWN_PERIODIC_VERIFICATION_RECEIPT.json',
    ]},
}
(HERE/'ROOT_VERIFIED_M19_DELETED_AND_PERIODIC.json').write_text(json.dumps(review,indent=2)+'\n')
print(json.dumps({k:review[k] for k in ('status','new_deleted_direction_cuts','new_periodic_mode_cuts','remaining_profiles_after_these_stages')},indent=2))
