"""Build the current frontier from reviewed, disjoint exact checkpoints."""
from collections import Counter
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[2]
HERE=ROOT/'research_round3/root'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
old=read(ROOT/'Kakeya_Research_Frontier_Round2.json')
s17=read(HERE/'ROOT_VERIFIED_M11_SUPPORT16.json')
s16path=ROOT/'research_round3/m11/s16/S16_INDEPENDENT_REPLAY.json'
s16=read(s16path)
assert s16['status']=='PASS' and s16['remaining_affine_support_classes']==46
closed17=s17['new_closed_classes']
closed16=s16['new_whole_affine_support_class_exclusions']
assert closed16==[177,187,198,201,202,203]
before=old['dimension5_strata']['maximum11']['remaining_orbits']
assert set(before)-set(closed17)==set(s17['remaining_orbits'])
assert set(s17['remaining_orbits'])-set(closed16)==set(s16['remaining_orbits'])
assert not set(closed17)&set(closed16)
source=ROOT/'research_sources/extracted/Kakeya_Reconciled_Proofs_2026-10-27/late_parallel_2214/extracted/m11_directional/inputs/CAP11_STRUCTURAL_REDUCTION.json'
records={r['orbit']:r for r in read(source)['records']}
counts=dict(sorted(Counter(records[o]['support_size'] for o in s16['remaining_orbits']).items()))
assert counts=={13:4,14:9,15:16,16:17}
profiles={tuple(w) for r in s16['records'] for w in r['surviving_weight_profiles']}
incidences=sum(r['surviving_profile_count'] for r in s16['records'])
assert len(profiles)==66 and incidences==764
review={
    'status':'PASS_ROOT_ANALYTIC_REVIEW_AND_FRESH_REPLAY',
    'scope':'Exact maximum11, support16, |K|<=93, both rings in dimension5.',
    'new_whole_affine_support_class_exclusions':closed16,
    'remaining_affine_support_classes':46,
    'remaining_counts_by_support':counts,
    'normalized_partitions':s16['partition_counts']['total'],
    'exact_assignment_dual_certificates':s16['exact_assignment_dual_certificates'],
    'valid_assignment_edge_inequalities':s16['valid_assignment_edge_inequalities'],
    'review':'Root read the complete proof and verifier and reran the exact chain. The new ten-heavy, sum-free, and cube graph bounds are valid. A unique support edge forces a period in a weight8 fibre; its active energy is then at most64 whenever the frozen envelope is70. Every assignment dual and all23-by782 assignments were checked. The inherited minimum weights and local envelopes remain explicit dependencies.',
    'stable_source_hashes':{str(p.relative_to(ROOT)):sha(p) for p in [
        source,ROOT/'research_round3/m11/s16/verify_s16_checkpoint.py',
        ROOT/'research_round3/m11/s16/S16_EXACT_CHECKPOINT.json',
        ROOT/'research_round3/m11/s16/S16_ASSIGNMENT_DUAL_CERTIFICATES.json',
        ROOT/'research_round3/m11/s16/M11_SIX_SUPPORT16_CLASS_EXCLUSIONS.md',
    ]},
}
(HERE/'ROOT_VERIFIED_M11_S16_CLASSES.json').write_text(json.dumps(review,indent=2)+'\n')

middle=read(ROOT/'research_round3/middle/MIDDLE_SUPPORT18_INDEPENDENT_REPLAY.json')
assert middle['status']=='PASS' and middle['remaining_weight_profiles']==0
assert read(HERE/'ROOT_VERIFIED_MIDDLE_SUPPORT17.json')['status'].startswith('PASS')
m19=read(ROOT/'research_round3/m19/M19_ROUND3_FINAL_MANIFEST.json')
assert m19['status']=='ROOT_VERIFIED'
assert m19['total_new_whole_profile_exclusions']==26673
assert m19['total_remaining_selected_profiles']==3798
assert read(HERE/'FULL_HUB_TWELVE_CONTROLS.json')['status']=='PASS'
assert read(HERE/'SHARED_GEOMETRY_CONTROLS.json')['status']=='PASS'
data={
    'title':'Kakeya research continuation, round3',
    'date':'2026-10-28',
    'status':'ROOT_VERIFIED_PARTIAL_THEOREMS_AND_EXCLUSIONS',
    'rings':['Z/4Z','F2[epsilon]/(epsilon^2)'],
    'general_target':'3*2^n-2',
    'unrestricted_general_theorem':'OPEN',
    'dimension5_target':94,
    'unrestricted_dimension5_theorem':'OPEN',
    'verified_small_dimension_minima_inherited':old['verified_small_dimension_minima_inherited'],
    'support_definition':'Residues with at least two points; singleton fibres cannot participate in primitive four-point lines.',
    'dimension5_strata':{
        'maximum_at_most10':'EXCLUDED_INHERITED',
        'maximum11':{
            'status':'OPEN','pair_active_support_upper_bound':16,
            'previous_round2_affine_support_classes':57,
            'round3_whole_affine_support_class_exclusions':11,
            'support17_closed_classes':closed17,
            'support16_closed_classes':closed16,
            'remaining_affine_support_classes':46,
            'remaining_counts_by_support':counts,
            'remaining_orbits':s16['remaining_orbits'],
            'support16_remaining_distinct_weight_profiles':66,
            'support16_remaining_support_profile_incidences':764,
            'support16_verified_partitions':20477,
            'support16_exact_assignment_duals':17986,
        },
        'maximum12_through18':{
            'status':'OPEN','pair_active_support_upper_bound':17,
            'new_exhaustively_excluded_support':18,
            'all_support18_weight_partitions':239246,
            'inherited_quota_cuts':238744,
            'inherited_spectrum_cuts':217,
            'round3_new_weight_multiset_exclusions':285,
            'round3_resource_cuts':277,
            'round3_final_analytic_cuts':8,
            'remaining_support18_weight_multisets':0,
            'last_three_cube_profile_doubled_bounds':{'C':[972,991],'D':[954,972],'E':[962,980]},
            'required_doubled_capacity':992,
            'remaining_scope':'Supports17 and below remain open; earlier selected lower-support cuts remain in force.',
        },
        'maximum19':{
            'status':'OPEN','remaining_pair_active_support_sizes':[11,12],
            'previous_round2_selected_profiles':30471,
            'round3_disjoint_whole_profile_exclusions':26673,
            'remaining_selected_profiles':3798,
            'supports':{s:{'previous':r['initial_profiles'],
                           'round3_exclusions':r['new_whole_profile_exclusions'],
                           'remaining':r['remaining_profiles']} for s,r in m19['supports'].items()},
            'stages':[{'method':r['name'],'new_exclusions':r['total_new_exclusions'],
                       'remaining':r['total_remaining_profiles']} for r in m19['stages']],
        },
        'maximum_at_least20':'EXCLUDED_INHERITED',
    },
    'new_analytic_theorems':[
        'Shared own periods: actual offhub sumset capacity<=pq/2.',
        'Own-positive affine rank<=k gives edge capacity<=2^(2k-3), and outside-support subgroup sum<=2^(2k-4)*floor(r^2/2).',
        'Cube-direction/residual-energy inequality: C_total<=E_R/2+7r*lambda+(16-2lambda)*floor(r^2/4)+sum H_A, 4<=lambda<=8.',
        'Missing differences of more than2^(n-2) binary residues are sum-free; restricted light-fibre pair mass<=floor(w^2/4).',
        'Nine-point difference28 equality normal form and independent three missing directions.',
        'Forced-period weight8 fibre: either an affine cube with active energy divisible by16, or full pair-square energy64.',
        'Full hub and all outer fibres<=12, n>=6: |K|>=3*2^n-2, equality exactly generalized stars.',
        'Actual unique-edge and sole-hub roles impose four exact Hall assignment inequalities under the outer-weight cap14.',
    ],
    'dimension_free_small_fibre_energy_maxima':read(HERE/'FULL_HUB_TWELVE_CONTROLS.json')['dimension_free_energy_maxima'],
    'catchup':{
        'scope':'Retrieved relevant prior sessions and saved research records; no claim of access to every unseen conversation.',
        'latest_authoritative_start':'Round2 frontier and proof archive.',
        'additional_compatibility_package':'Kakeya_Energy_and_Compatibility_2026-10-27.zip',
        'additional_package_replay':'PASS,57 payload files and5 finite-check stages.',
        'retained_corrections':[
            'The two-image theorem is conditional; arbitrary line representations need not have two minimal images.',
            'Shared fibre translations and Z4 carries matter for exact coverage and cannot be replaced by independent edge translations.',
            'Infeasibility of a necessary-condition relaxation is an exclusion; feasibility is not a construction.',
            'The caught-up older compatibility package contains a stale frontier; the newer round2 then round3 ledgers govern counts.',
        ],
    },
    'prior_checkpoint':{
        'library_file_id':'libfile_4b5e1c0ac7a48191a425b4db678bb7fb',
        'archive':'Kakeya_Research_Round2_Proofs.zip',
        'sha256':'6ddf3c88c04aa8880dc034146578a720a5d71e433409595a3b29e7f008b70948',
    },
    'counting_caution':'M11 affine support classes, middle weight multisets, and M19 selected weight/own-direction profiles are different objects and are not summed.',
    'verification_scope':'Exact integer and finite enumeration replays plus independent analytic review; not proof-assistant formalization or external peer review.',
    'next_mathematical_frontier':[
        'M11: actual common cube/period shapes and exact coverage on the46 remaining support classes, particularly the66 support16 weight profiles.',
        'Middle: apply coupled cube-energy and shared-direction budgets to support17 and lower.',
        'M19: assign the3798 surviving profiles to actual marked supports and enforce all edge directions with one common shape per fibre.',
        'After fixing shapes, couple all translations and ring carries; certify union coverage or unavoidable overlap direction by direction.',
    ],
}
path=ROOT/'Kakeya_Research_Frontier_Round3.json'
path.write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps({'status':data['status'],'m11_classes':46,'middle_support_upper':17,
                  'm19_profiles':3798,'frontier_sha256':sha(path)},indent=2))
