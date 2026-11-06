"""Exact frontier update from complete support11/12 certificate collections.

No uncredited exploratory result, timeout, or isolated marked-support result
is subtracted from the whole-weight-profile inventory.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    previous = load(ROOT / 'Kakeya_Research_Frontier_Round5.json')
    baseline = ROOT / 'research_round5/after_round5_survivors.txt'
    require(digest(baseline) == previous['dimension5_strata']['maximum12_through18']['survivor_sha256'],
            'Round5 baseline hash changed')
    contract = load(ROOT / 'research_round5/encoding_bridge/M19_MARKED_CASE_CONTRACT.json')
    geometric_ids = {r['case_id'] for r in contract['cases']}
    require(len(geometric_ids) == 38, 'Incomplete geometric contract')
    joint = load(HERE / 'joint_maxima/JOINT_CERTIFICATE_MANIFEST.json')
    require(joint['status'] == 'PASS_COMPLETE_38_CASE_INVENTORY_AND_ACCEPTED_FILE_HASHES', 'Joint collection is not complete')
    require(joint['maximum_interval'] == [2, 18] and joint['total_upper_bound'] == 93, 'Wrong joint theorem')
    require({r['geometric_case_id'] for r in joint['cases']} == geometric_ids and len(joint['cases']) == 38,
            'Joint coverage mismatch')
    m19 = load(HERE / 'certification/M19_CERTIFICATE_MANIFEST.json')
    m19_receipt = load(HERE / 'certification/M19_COMPLETE_CERTIFICATION_RECEIPT.json')
    require(m19_receipt['status'] == 'PASS_ALL_38_FRESH_PACKAGED_ENCODER_CNF_CERTIFICATES', 'M19 certification incomplete')
    require(m19_receipt['manifest_sha256'] == digest(HERE / 'certification/M19_CERTIFICATE_MANIFEST.json'),
            'M19 acceptance receipt does not bind this exact manifest')
    require({r['case_id'] for r in m19['cases']} == geometric_ids and len(m19['cases']) == 38, 'M19 coverage mismatch')
    initial, final, cuts = Counter(), Counter(), Counter()
    surviving, excluded, seen = [], [], set()
    for raw in baseline.read_bytes().splitlines(keepends=True):
        support, maximum, prior_bound, *weights = map(int, raw.split())
        require(len(weights) == support and max(weights) == maximum and sum(weights) == 93,
                'Malformed baseline profile')
        require(tuple(weights) not in seen, 'Duplicated baseline profile')
        seen.add(tuple(weights))
        initial[support, maximum] += 1
        if support in (11, 12):
            require(12 <= maximum <= 18, 'Unexpected maximum in middle inventory')
            cuts[support, maximum] += 1
            excluded.append(raw)
        else:
            final[support, maximum] += 1
            surviving.append(raw)
    require(len(seen) == 270779 and len(excluded) == 84297 and len(surviving) == 186482,
            'Unexpected exact frontier counts')
    require(len(initial) == 48 and len(final) == 34 and len(cuts) == 14,
            'Unexpected support/maximum cell counts')
    require(all(13 <= support <= 17 for support, maximum in final), 'Unexpected remaining support')
    survivor_file = HERE / 'after_round6_survivors.txt'
    cut_file = HERE / 'round6_excluded_profiles.txt'
    survivor_file.write_bytes(b''.join(surviving))
    cut_file.write_bytes(b''.join(excluded))
    receipt = {'status': 'PASS_EXACT_ROUND6_FRONTIER',
               'baseline_middle_weight_profiles': len(seen),
               'new_whole_weight_profile_exclusions': len(excluded),
               'remaining_middle_weight_profiles': len(surviving),
               'previous_nonempty_cells': len(initial), 'remaining_nonempty_cells': len(final),
               'newly_closed_cells': [{'support': s, 'maximum': m, 'excluded_profiles': n}
                                      for (s, m), n in sorted(cuts.items())],
               'by_support': [{'support': s,
                               'before': sum(n for (t, m), n in initial.items() if t == s),
                               'excluded': sum(n for (t, m), n in cuts.items() if t == s),
                               'remaining': sum(n for (t, m), n in final.items() if t == s)}
                              for s in range(11, 18)],
               'by_cell': [{'support': s, 'maximum': m, 'before': initial[s, m],
                            'remaining': final[s, m]} for s, m in sorted(initial)],
               'baseline_sha256': digest(baseline), 'survivors_sha256': digest(survivor_file),
               'excluded_profiles_sha256': digest(cut_file),
               'joint_certificate_manifest_sha256': digest(HERE / 'joint_maxima/JOINT_CERTIFICATE_MANIFEST.json'),
               'm19_certificate_manifest_sha256': digest(HERE / 'certification/M19_CERTIFICATE_MANIFEST.json'),
               'counting_caution': 'Weight profiles, unmarked affine support classes, marked support cases, and formulas are separate inventories.'}
    receipt['verification_scope'] = 'Exact ledger subtraction against completed certificate manifests; this bookkeeping check does not replace actual proof replay or the one-way encoder argument.'
    (HERE / 'ROUND6_MERGED_REPLAY.json').write_text(json.dumps(receipt, indent=2) + '\n')
    frontier = {'title': 'Kakeya Round6: complete support11/12 exclusions and actual encoder recertification',
                'date': '2026-10-28', 'previous_checkpoint': 'Kakeya_Research_Frontier_Round5.json',
                'rings': previous['rings'], 'general_target': '3*2^n-2',
                'unrestricted_general_theorem': 'OPEN', 'dimension5_target': 94,
                'unrestricted_dimension5_theorem': 'OPEN',
                'new_certified_statement': 'No dimension-five Kakeya set of at most93 points in either ring has pair-active support11 or12 and maximum fibre at most19.',
                'new_global_corollary': 'Together with the inherited exclusion of maximum>=20 and Round5 exclusion of support<=10, any at-most93-point counterexample has at least13 pair-active fibres.',
                'minimum_pair_active_support': 13,
                'corollary_dependencies': ['Inherited maximum>=20 exclusion',
                                           'Round5 unrestricted support<=10 exclusion',
                                           'Round6 complete support11/12 computer-assisted exclusion'],
                'new_analytic_theorem': {'statement': 'Support affinely equivalent to V union W, dimV3,dimW2,V direct-sum W=F2^5, forces at least94 points without any maximum-fibre hypothesis.',
                                         'proof': 'research_round6/structural_progress/SUPPORT11_COMPLEMENTARY_SUBSPACES_PROOF.md',
                                         'SAT_dependency': False, 'spectrum_census_dependency': False},
                'dimension5_strata': {
                    'maximum_at_most10': 'EXCLUDED_INHERITED; ALSO INCLUDED IN NEW SUPPORT11/12 CHECKS',
                    'maximum11': previous['dimension5_strata']['maximum11'],
                    'maximum12_through18': {'status': 'OPEN', 'minimum_pair_active_support': 13,
                                             'remaining_weight_profiles': 186482, 'remaining_nonempty_cells': 34,
                                             'maximum_pair_active_support_by_maximum': {str(m): 16 if m == 18 else 17 for m in range(12, 19)},
                                             'survivor_file': str(survivor_file.relative_to(ROOT)),
                                             'survivor_sha256': digest(survivor_file)},
                    'maximum19': {'status': 'CLOSED_WITH_INHERITED_SUPPORT11_12_REDUCTION',
                                   'fresh_exact_packaged_encoder_cases_accepted': 38,
                                   'old_historical_proofs_supplied': False,
                                   'old_encoder_equivalence_assumed': False,
                                   'tracked_profiles_excluded': 3798,
                                   'inherited_support_reduction_still_used': True,
                                   'outer_weight14_cap_used': False,
                                   'full_hub_or_all_support_theorem_claimed': False},
                    'maximum_at_least20': 'EXCLUDED_INHERITED'},
                'certificate_collections': {'maximum19': 38, 'joint_maximum2_through18': 38,
                                             'same_geometric_universe': {'support11': 13, 'support12': 25},
                                             'main_exact_CNF_refutations': 76,
                                             'final_authority': 'Pinned upstream verified CakeML artifact on exact CNF plus LRAT',
                                             'encoder_formally_verified': False,
                                             'one_way_soundness_hand_proof': 'research_round6/encoder_audit/ONE_WAY_SOUNDNESS_AUDIT.md'},
                'new_general_fibre_lemma': {'statement': 'For maximal-pair subspace K and nonzero d,e, d+e in K implies p_A(d)=p_A(e); odd fibres with nontrivial K differ by one point from a K-periodic set.',
                                            'proof': 'research_round6/encoder_audit/MAXIMAL_SUBSPACE_COSET_LEMMA.md',
                                            'used_in_main76_certificates': False,
                                            'global_solver_speedup_demonstrated': False},
                'new_dense_fibre_lemmas': {'proof': 'research_round6/next_frontier/DENSE_FIBRE_COMPLEMENT_LEMMAS.md',
                                           'scope': 'Complete labelled pair-pattern descriptions for weights11 and12 in affine four-flats; conditional clauses for the trivial-maximal-subspace types Q205 and Q294.',
                                           'finite_complements_checked': 6188,
                                           'implemented_in_main_encoder': False,
                                           'new_support_exclusions': 0},
                'additional_support13_result': {'nonzero_support_mask': 37848950,
                                                 'full_support_mask': 37848951,
                                                 'support': [0, 1, 2, 4, 5, 6, 8, 9, 10, 15, 16, 22, 25],
                                                 'distinguished_hub': 0, 'maximum_interval': [2, 18],
                                                 'distinct_marked_cases_excluded': 1, 'accepted_proofs_for_that_case': 2,
                                                 'whole_weight_profiles_subtracted': 0,
                                                 'other_timed_out_trial_is_excluded': False},
                'middle_update': receipt,
                'latest_external_snapshot': {'source': 'Attached Claude Round4 handoff, not live status',
                                             'middle_proof_free_cases_completed': 478,
                                             'm19_other_support_proof_free_cases_completed': 120,
                                             'those_statuses_credited_as_certificates': False},
                'next_priorities': ['Complete support13 joint-maxima marked cases, starting with proof-generating bounded splits of hard cases.',
                                     'Use maximal-subspace coset constraints selectively; current paired trials show no speed advantage from enabling them globally.',
                                     'Test the proved dense-complement direction constraints on Q205/Q294 spectrum branches, where the maximal-pair subspace is trivial.',
                                     'Develop reusable local graph and spectrum-branch exclusions for supports14..17.'],
                'review_scope': 'Separate model-agent reviews and actual checker executions; no independent human review or full Kakeya formalization claimed.'}
    (ROOT / 'Kakeya_Research_Frontier_Round6.json').write_text(json.dumps(frontier, indent=2) + '\n')
    print(json.dumps({k: receipt[k] for k in ['status', 'new_whole_weight_profile_exclusions',
                                             'remaining_middle_weight_profiles', 'remaining_nonempty_cells', 'by_support']}, indent=2))


if __name__ == '__main__':
    main()
