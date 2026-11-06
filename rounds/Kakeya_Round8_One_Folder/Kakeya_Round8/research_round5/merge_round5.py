"""Exact disjoint subtraction and current frontier for the Round5 archive."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def read_json(path):
    return json.loads(path.read_text())


def jsonl_weights(path):
    rows = [json.loads(line) for line in path.open()]
    result = {tuple(row['weights']) for row in rows}
    assert len(result) == len(rows)
    return result


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    if sys.flags.optimize:
        raise SystemExit('Assertions must remain enabled.')
    baseline = ROOT / 'research_round4/middle_inventory/after_priced_nine_survivors.txt'
    assert digest(baseline) == '4f936a1f929292aaa5bf51f113e9e4070f926b474242e4ecc08853cbbb00fde5'
    geometry = jsonl_weights(HERE / 'nine_geometry/NINE_GEOMETRY_CUTS.jsonl')
    prices = jsonl_weights(HERE / 'middle_duals/FULL_MULTI_PRICE_CUTS.jsonl')
    roles = jsonl_weights(HERE / 'support10_roles/SUPPORT10_ROLE_CUTS.jsonl')
    seven = {tuple(r['weights']) for r in read_json(HERE / 'support10_roles/SUPPORT10_ROLE_SURVIVORS.json')}
    assert [len(x) for x in (geometry, prices, roles, seven)] == [4088, 240, 641, 7]
    families = [('nine_residue_geometry', geometry), ('analytic_small_light_prices', prices),
                ('support10_unique_roles', roles), ('support10_rigidity', seven)]
    combined = set()
    for name, values in families:
        assert not combined & values
        combined |= values
    assert len(combined) == 4976
    rigidity = read_json(HERE / 'support10_roles/SUPPORT10_RIGIDITY_REPLAY.json')
    assert rigidity['status'] == 'PASS_ALL_ELEVEN_RIGIDITY_APPLICATIONS'
    assert rigidity['remaining_support10_profiles'] == 0
    assert read_json(HERE / 'support10_roles/FULL_SUPPORT10_ROLE_REPLAY.json')['status'] == 'PASS_FULL_SUPPORT10_INDEPENDENT_REPLAY'
    for path, status in [
        ('nine_geometry/NINE_GEOMETRY_REPLAY.json', 'PASS_COMPLETE_NINE_GEOMETRY_SCREEN'),
        ('middle_duals/SMALL_LIGHT_ANALYTIC_REPLAY.json', 'PASS_CLOSED_FORM_ANALYTIC_REPLAY'),
        ('support10_roles/SUPPORT10_ROLE_INDEPENDENT_REPLAY.json', 'PASS_COMPLETE_INDEPENDENT_SUPPORT10_REPLAY')]:
        assert read_json(HERE / path)['status'] == status

    initial, final, stage_counts = Counter(), Counter(), Counter()
    seen, output, cuts = set(), [], []
    for raw in baseline.read_bytes().splitlines(keepends=True):
        support, maximum, old_bound, *values = map(int, raw.split())
        weights = tuple(values)
        assert weights not in seen and len(weights) == support and sum(weights) == 93
        seen.add(weights)
        initial[support, maximum] += 1
        if weights in combined:
            method = next(name for name, family in families if weights in family)
            stage_counts[method] += 1
            cuts.append({'support': support, 'maximum': maximum, 'weights': weights,
                         'exclusion': method})
        else:
            final[support, maximum] += 1
            output.append(raw)
    assert len(seen) == 275755 and combined <= seen and len(output) == 270779
    support10 = {w for w in seen if len(w) == 10}
    assert len(support10) == 3220 and support10 <= combined
    assert len(final) == 48 and all(s >= 11 for s, m in final)
    survivor = HERE / 'after_round5_survivors.txt'
    survivor.write_bytes(b''.join(output))
    certificates = HERE / 'ROUND5_DISJOINT_CUTS.jsonl'
    certificates.write_text(''.join(json.dumps(r, separators=(',', ':')) + '\n' for r in cuts))
    by_support = [dict(support=s,
                       before=sum(v for (t, m), v in initial.items() if t == s),
                       excluded=sum(v for (t, m), v in initial.items() if t == s) - sum(v for (t, m), v in final.items() if t == s),
                       remaining=sum(v for (t, m), v in final.items() if t == s))
                  for s in range(10, 18)]
    receipt = {
        'status': 'PASS_DISJOINT_ROUND5_FRONTIER',
        'baseline_weight_profiles': 275755,
        'disjoint_stage_exclusions': dict(stage_counts),
        'additional_whole_weight_profile_exclusions': len(combined),
        'remaining_middle_weight_profiles': len(output),
        'remaining_nonempty_middle_cells': len(final),
        'newly_closed_cells': [{'support': 10, 'maximum': m} for m in range(12, 19)],
        'by_support': by_support,
        'by_cell': [dict(support=s, maximum=m, before=initial[s,m], remaining=final[s,m])
                    for s in range(10,18) for m in range(12,19)],
        'minimum_pair_active_support': 11,
        'support10_theorem': 'Unrestricted in the maximum fibre size; both rings; at most93 points.',
        'support10_proof_dependencies': 'Complete finite support classification and analytic role/cube/period/Mantel arguments. No weight-profile census, earlier middle screen, or SAT result is required for the theorem itself.',
        'baseline_sha256': digest(baseline), 'survivors_sha256': digest(survivor),
        'disjoint_certificates_sha256': digest(certificates),
        'counting_caution': 'Middle weight profiles, M11 affine support classes, and Claude SAT cases are different objects and cannot be added or subtracted across inventories.'
    }
    (HERE / 'ROUND5_MERGED_REPLAY.json').write_text(json.dumps(receipt, indent=2) + '\n')

    previous = read_json(ROOT / 'Kakeya_Research_Frontier_Round4.json')
    frontier = {
        'title': 'Kakeya Round5: unrestricted support-ten exclusion and proof acceptance bridge',
        'date': '2026-10-28',
        'previous_checkpoint': 'Kakeya_Research_Frontier_Round4.json',
        'rings': previous['rings'], 'general_target': '3*2^n-2',
        'unrestricted_general_theorem': 'OPEN', 'dimension5_target': 94,
        'unrestricted_dimension5_theorem': 'OPEN',
        'new_theorem': {'statement': 'Every dimension-five Kakeya set with at most93 points has at least11 pair-active residue fibres, in both rings, with no assumption on the largest fibre.',
                        'support10_status': 'PROVED_WITH_COMPLETE_FINITE_SUPPORT_CLASSIFICATION_AND_ANALYTIC_WEIGHT_ARGUMENT',
                        'weight_census_dependency': False, 'SAT_dependency': False,
                        'formalized_in_Lean': False,
                        'proof': 'research_round5/support10_roles/SUPPORT10_UNRESTRICTED_PROOF.md'},
        'dimension5_strata': {
            'maximum_at_most10': 'EXCLUDED_INHERITED',
            'maximum11': previous['dimension5_strata']['maximum11'],
            'maximum12_through18': {
                'status': 'OPEN', 'remaining_weight_profiles': len(output),
                'remaining_nonempty_cells': len(final), 'minimum_pair_active_support': 11,
                'maximum_pair_active_support_by_maximum': {str(m): (16 if m == 18 else 17) for m in range(12,19)},
                'survivor_file': str(survivor.relative_to(ROOT)), 'survivor_sha256': digest(survivor),
                'new_support10_cells_closed': 7,
                'scope': 'Necessary-condition weight survivors, not constructions or enumerated embedded fibre assignments.'},
            'maximum19': {
                'status': 'REPORTED_CLOSED_BY_USER_CLAUDE_SESSION; ACTUAL_CNF_AND_DRAT_AUDIT_PENDING_HERE',
                'operational_research_priority': 'Move to maxima11..18 while preserving the explicit verification obligations.',
                'reported_cases': 38, 'reported_supports': [11,12],
                'reported_tracked_profiles_excluded': 3798,
                'reported_outer_weight14_cap_used': False,
                'reported_rings': 'Both, subject to common-relaxation or ring-specific encoding soundness.',
                'reported_results_path_in_other_environment': '/home/user/kakeya_round4/results/m19_s11_12.jsonl',
                'that_path_accessible_here': False,
                'new_Claude_CNF_DRAT_pairs_checked_here': 0,
                'complete_marked_case_universe_checked_here': {'11':13, '12':25},
                'normalized_covering_supports_checked': 102324,
                'normalized_support_candidates_checked': 296010,
                'all_support_closure_dependency': 'Inherited support11/12 reduction or the separately reported exploratory all-support sweep.',
                'outstanding': ['Read exact A-E and encoder source.', 'Prove counterexample-to-satisfying-assignment implication, including tied maxima and both rings.', 'Regenerate and hash-match CNFs to exact support metadata.', 'Replay all38 actual proofs with the packaged verified-checker acceptance path.']},
            'maximum_at_least20': 'EXCLUDED_INHERITED'},
        'middle_update': receipt,
        'formal_semantic_bridge': {'new_Lean_theorems':15, 'actual_kernel_compilation':'PASS',
            'scope':'Binary coefficient operations, Z4 modulo-four arithmetic, all-dimensional line formula and exact line-to-pair/carry equivalence.',
            'not_formalized':['Support census','Full encoder','A-E','Whole Kakeya exclusion','New support10 graph proof']},
        'proof_acceptance_pipeline': {'path':'Exact CNF and DRAT -> pinned DRAT-trim -> LRAT -> mandatory upstream verified CakeML checker',
            'archived_Kakeya_proofs_replayed':4, 'new_Claude_proofs_replayed':0,
            'genuine_RAT_positive_control':1, 'rejected_negative_controls':8,
            'upstream_HOL4_CakeML_development_rebuilt_here':False,
            'ordinary_C_LRAT_utility':'Diagnostic only; pinned utility falsely accepts the bundled satisfiable negative control.'},
        'last_user_report_external_sweep': {'maxima11_through18_cases_done':191, 'cases_total':8904,
            'reported_completed_status':'All UNSAT', 'live_status_checked_here':False,
            'note':'This is the last user-supplied snapshot, not a live progress estimate.'},
        'next_priorities': ['Prioritize Claude maxima11..18 cases on supports11 and above; map case identifiers before skipping cases covered by the new theorem.', 'Bring actual A-E, encoder, support metadata, CNFs and proofs into the checker handoff.', 'Extend direction-labelled type compatibility and reusable support-role constraints on the remaining supports.'],
        'review_scope':'Separate model-agent mathematical and implementation checks in one session; no independent human review or full proof-assistant formalization is claimed.'
    }
    (ROOT / 'Kakeya_Research_Frontier_Round5.json').write_text(json.dumps(frontier, indent=2) + '\n')
    print(json.dumps({k:receipt[k] for k in ('status','additional_whole_weight_profile_exclusions',
        'remaining_middle_weight_profiles','remaining_nonempty_middle_cells','newly_closed_cells','by_support')}, indent=2))


if __name__ == '__main__':
    main()
