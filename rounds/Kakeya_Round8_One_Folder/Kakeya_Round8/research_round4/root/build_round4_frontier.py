"""Consolidate only verified Round4 results, retaining the Round3 frontier."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
R4 = ROOT / 'research_round4'


def read(relative):
    return json.loads((ROOT / relative).read_text())


def main():
    previous = read('Kakeya_Research_Frontier_Round3.json')
    middle = read('research_round4/middle_inventory/MIDDLE_FINAL_FRONTIER_AFTER_PRICING.json')
    priced = read('research_round4/middle_inventory/PRICED_NINE_INDEPENDENT_REPLAY.json')
    lean = read('research_round4/lean/LEAN_REPLAY_RECEIPT.json')
    assert middle['status'] == priced['status'] == 'PASS'
    assert lean['status'] == 'PASS_PINNED_LEAN_KERNEL_COMPILATION'
    final_path = R4 / 'middle_inventory/after_priced_nine_survivors.txt'
    census = read('research_round2/geometric/PAIR_SPECTRUM_CENSUS.json')
    energies = {}
    for weight in range(2, 19):
        allowed = [x['hist'] for x in census['weights'][str(weight)]
                   if weight != 8 or x['hist'][4] != 7]
        energies[weight] = max(sum(p*p*c for p, c in enumerate(h)) for h in allowed)
    cells = Counter()
    without_forced_cube = 0
    for line in final_path.read_text().splitlines():
        support, maximum, old_bound, *weights = map(int, line.split())
        assert len(weights) == support and sum(weights) == 93 and weights[0] == maximum
        cells[support, maximum] += 1
        without_forced_cube += sum(energies[w] for w in weights) >= 992
    assert sum(cells.values()) == middle['remaining_weight_profiles'] == 275755
    assert len(cells) == 55 and cells[17, 18] == 0
    assert without_forced_cube == 269672
    for row in middle['records']:
        assert cells[row['support'], row['maximum']] == row['remaining_weight_profiles']

    frontier = deepcopy(previous)
    frontier.update(
        title='Kakeya research continuation, Round4: audited premises and complete middle weight inventory',
        status='VERIFIED_PARTIAL_THEOREMS_AND_EXPLICIT_EXCLUSIONS; UNRESTRICTED_TARGET_OPEN',
        date='2026-10-28',
        previous_checkpoint='Kakeya_Research_Frontier_Round3.json',
        review_language='Separate model-agent mathematical and implementation cross-checks within one session; no independent human review or external peer review is claimed.',
        middle_weight_inventory=middle,
    )
    branch = frontier['dimension5_strata']['maximum12_through18']
    branch.update(
        pair_active_support_lower_bound=10,
        pair_active_support_upper_bound=17,
        necessary_support_upper_bounds_by_maximum=middle['necessary_support_bounds_by_maximum'],
        complete_normalized_weight_profiles=2163945,
        remaining_weight_profiles=275755,
        new_round4_weight_profile_exclusions_after_quota_and_inherited_selected_spectrum=136913,
        newly_closed_support_maximum_cells=[{'support':17,'maximum':18}],
        remaining_nonempty_support_maximum_cells=55,
        final_survivor_file='research_round4/middle_inventory/after_priced_nine_survivors.txt',
        final_survivor_sha256=sha256(final_path.read_bytes()).hexdigest(),
        remaining_scope='Exact maxima12..17 have necessary support10..17; exact maximum18 has necessary support10..16. These are weight-profile relaxation survivors, not actual supports or fibre realizations.',
    )
    frontier['round4_analytic_energy12'] = {
        'theorem':'Every twelve-point subset of any binary affine space has Q<=300.',
        'equality':'Exactly an affine four-flat with an affine plane removed.',
        'rank_bounds':{'4':[294,300], '5':'at most222, attained', 'at_least6':'at most252'},
        'independent_normalized_enumeration':{'rank4':330, 'rank5':230230, 'total':230560},
        'census_dependency_for_this_theorem':False,
        'lean_formalized':False,
        'proof':'research_round4/energy12/ENERGY12_ANALYTIC_PROOF.md',
    }
    frontier['round4_cube_diagnostic'] = {
        'final_profiles':275755,
        'profiles_passing_all_noncube_energy_branch':without_forced_cube,
        'profiles_forcing_some_cube_by_this_energy_screen':275755-without_forced_cube,
        'scope':'The r=0 energy branch is only a necessary relaxation; passing it does not realize noncube shapes.',
    }
    frontier['round4_type_optimization'] = {
        'implemented':'Finite embedded-type IP/LP row builder; exact rational Farkas checker; complete dimension-two demonstrations.',
        'dimension5_global_type_catalogue_or_solver':'NOT_COMPLETED',
        'verified_demonstrations':14,
        'verified_farkas_certificates':12,
        'independent_ring_edge_table_entries':348,
        'four_weight3_fibres':{'dual_realizations':0,'z4_realizations':64,'fractional_label_LP_feasible_in_both':True},
        'carry_scope':'Carry translates single-edge label sets, preserving cardinality. Ring distinction enters label-incidence rows and globally shared translations.',
        'completeness_requirement':'Every actual embedded type is represented or encompassed by a proved relaxation; omitted columns need a complete pricing certificate.',
    }
    frontier['round4_lean'] = {
        'status':lean['status'], 'theorems':13,
        'lean_version':lean['lean_version'], 'mathlib_commit':lean['mathlib_commit'],
        'formalized':lean['formalized'], 'not_formalized':lean['not_formalized'],
        'source_sha256':lean['source_sha256'],
    }
    frontier['full_hub_scope_clarification'] = {
        'theorem':'n>=6, one full fibre, every other fibre of size<=12: size>=3*2^n-2 with the stated generalized-star equality classification.',
        'dimension5':'The inherited maximum>=20 exclusion already removes all subthreshold full hubs.',
        'higher_dimensions':'No-full-hub configurations and full-hub configurations with an outer fibre>12 remain outside the theorem.',
        'equality_scope':'Classifies equality under its structural hypotheses; it does not classify all unrestricted minimizers.',
    }
    frontier['verification_scope'] = 'Analytic proofs reviewed within this model session; complete exact finite replays and separately written checkers; a pinned Lean finite-incidence/algebra module. No full formalization of the Kakeya reduction, external human review, or unrestricted theorem is claimed.'
    frontier['next_mathematical_frontier'] = [
        'Use the complete275755-profile middle residual as input to common embedded-type constraints and exact endpoint-message dual optimization.',
        'Retain all omitted-type possibilities via certified upper envelopes or complete pricing; restricted-domain infeasibility is not a global exclusion.',
        'Refine actual residue placements and direction-labelled pair sets; impose shared translations, ring-aware labels, and cycle or higher-order consistency cuts.',
        'M11 remains46 affine support classes; M19 remains3798 tracked weight/own-direction profiles, with their existing structural constraints.',
        'Formalize the remaining binary-set, affine-plane, cube-triangle and Mantel bridges needed to connect the checked finite-incidence Lean theorem to actual Kakeya sets.',
    ]
    frontier['literature_corrections'] = [
        {'url':'https://arxiv.org/abs/2108.07652','fact':'Ghurumuruhan Ganesan, Size of local finite field Kakeya sets; not a Dhar paper.'},
        {'url':'https://collaborate.princeton.edu/en/publications/proof-of-the-kakeya-set-conjecture-over-rings-of-integers-modulo-/','fact':'Dhar-Dvir square-free N theorem; N=4 is not square-free.'},
        {'url':'https://arxiv.org/abs/2110.14889','fact':'Manik Dhar, The Kakeya Set Conjecture for Z/NZ for general N; general-modulus asymptotic results do not establish the exact fixed-ring formula sought here.'},
    ]
    (ROOT/'Kakeya_Research_Frontier_Round4.json').write_text(json.dumps(frontier, indent=2)+'\n')
    audit = {
        'status':'ROOT_REVIEWED_AND_REPLAYED_ROUND4_CHECKPOINT',
        'scope':frontier['verification_scope'],
        'reviewed_analytic_proofs':['Energy12 rank split and equality classification','Cube master and same-spectrum refinement','Nine-heavy priced resource and continuous price optimum','Support17/maximum18 direct47<48 exclusion','Embedded-type LP, ring carries, and dimension-two parity obstruction'],
        'fresh_root_replays':['Energy12 normalized enumeration','Complete pair-spectrum input census','2930 normalized nine-point difference checks','2163945-profile complete middle quota/geometric/joint-cube replay','Priced stage over276267 profiles','Separate priced-stage audit','Dimension-two exact type LP/ring verifier','Actual pinned Lean compilation and all13 axiom audits'],
        'theorems_open':['Unrestricted dimension5 minimum94','Unrestricted dimension-n formula3*2^n-2'],
        'middle_profiles':275755,'closed_cells':[[17,18]],
        'full_n5_type_LP_claimed_solved':False,
        'monograph_word_count':len((R4/'Kakeya_Round4_Monograph.txt').read_text().split()),
        'important_source_hashes':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in [
            R4/'energy12/ENERGY12_ANALYTIC_PROOF.md',
            R4/'middle_inventory/MIDDLE_FINAL_FRONTIER_AFTER_PRICING.json',
            final_path,R4/'optimization/TYPE_MODEL_AND_CERTIFICATES.md',R4/'lean/CubeMaster.lean',
        ]},
    }
    assert audit['monograph_word_count']==1500
    (R4/'root/ROOT_ROUND4_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps({'status':'PASS','middle_profiles':275755,'nonempty_cells':55,
                      'new_m18_support_ceiling':16,'all_noncube_energy_survivors':without_forced_cube,
                      'monograph_words':1500},indent=2))


if __name__ == '__main__':
    main()
