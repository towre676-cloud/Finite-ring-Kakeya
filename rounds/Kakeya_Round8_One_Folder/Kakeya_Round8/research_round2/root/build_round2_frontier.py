"""Consolidate verified branch ledgers without merging incompatible census units."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]
load=lambda p:json.loads((ROOT/p).read_text())
m11=load('research_round2/structural/m11_support/M11_SUPPORT_THROUGH18_INDEPENDENT_REPLAY.json')
middle=load('research_round2/middle/MIDDLE_MAXIMA_SUPPORT_COMPLETION.json')
m19=load('research_round2/geometric/M19_ROUND2_FINAL_MANIFEST.json')
assert m11['status']=='PASS' and middle['status']=='PASS_COMPLETE_MIDDLE_MAXIMA_SUPPORT_REDUCTION' and m19['status']=='ROOT_VERIFIED'
assert m11['new_whole_support_class_exclusions']==73 and m11['remaining_support_classes']==57
assert m19['total_new_exclusions']==38734 and m19['total_remaining_selected_profiles']==30471
out={'title':'Kakeya research continuation, round2','status':'VERIFIED_PARTIAL_THEOREMS_AND_EXCLUSIONS','rings':['Z/4Z','F2[epsilon]/(epsilon^2)'],'general_target':'3*2^n-2','unrestricted_general_theorem':'OPEN','dimension5_target':94,'unrestricted_dimension5_theorem':'OPEN','verified_small_dimension_minima_inherited':{'1':4,'2':10,'3':22,'4':46},'dimension5_strata':{
 'maximum_at_most10':'EXCLUDED_INHERITED',
 'maximum11':{'status':'OPEN','new_necessary_pair_active_support_upper_bound':17,'previous_open_affine_support_classes':130,'new_whole_affine_support_class_exclusions':73,'remaining_affine_support_classes':57,'remaining_counts_by_support':m11['remaining_counts_by_support'],'remaining_orbits':m11['remaining_orbits'],'exhaustive_weight_partitions_verified':m11['total_profiles'],'resource_exclusions':m11['resource_exclusions'],'analytic_geometry_exclusions':m11['geometric_exclusions']},
 'maximum12_through18':{'status':'OPEN','new_necessary_pair_active_support_upper_bound':18,'exhaustive_weight_partitions_verified':middle['total_weight_partitions'],'exhaustively_excluded_supports':'19 through32','method_counts':middle['method_counts'],'selected_additional_lower_support_weight_multisets_excluded':23381,'additional_cut_supports':'15 through18','count_scope':'These weight-multiset counts are separate from M19 profiles and M11 affine support classes.'},
 'maximum19':{'status':'OPEN','remaining_pair_active_support_sizes':[11,12],'previous_selected_profiles':69205,'new_disjoint_whole_profile_exclusions':38734,'remaining_selected_profiles':30471,'supports':{s:{'previous':r['initial_profiles'],'new_exclusions':r['new_exclusions'],'remaining':r['remaining_profiles']} for s,r in m19['supports'].items()},'stages':[{'method':x['name'],'total_exclusions':x['total_exclusions'],'support11':x['supports']['11']['new_exclusions'],'support12':x['supports']['12']['new_exclusions']} for x in m19['stages']]},
 'maximum_at_least20':'EXCLUDED_INHERITED'},
 'new_analytic_results':[
  'Outside-support selector budget: sum p <= C(w,2)-t*(w-t), hence <=C(w-1,2) for positive own pair count.',
  'Eight residues in F2^5 have at most25 nonzero differences; missing count is6 or at least9. If6, missing directions form an affine3-flat minus a line, and each residue has at most3 heavy neighbours through them.',
  'Nine residues in F2^5 have at most28 nonzero differences.',
  'Ten-heavy deletion/unique-edge inequality: light pair mass >=4r+k*max(0,3-r)>=min(3k,12), for heavy caps<=5 with k selected caps<=3 and light fibre sizes<=3.',
  'Full-hub outer-cap6 theorem for n>=4: size>=3*2^n-2.',
  'Full-hub outer-cap7 theorem for n>=5: size>=3*2^n-2, equality exactly generalized stars.',
  'For r affine3-flat tangent fibres, the sum of actual quotient-sumset edge capacities<=8*floor(r^2/2). This is not a bound on the coarser scalar M(p,q). No profile cuts credited.'
 ],
 'new_exact_halfspace_pair_square_energy':{str(w):h for w,h in zip(range(13,21),(222,301,392,512,520,561,618,712))},
 'finite_censuses':{'complete_pair_spectrum_counts_weights1_to19':[1,1,1,2,2,3,5,7,9,14,16,21,24,27,30,32,30,27,24],'paired_block_census':'independently complete via adapted affine-basis normalization','outside_support_degree_patterns':{'11':12,'12':18}},
 'prior_checkpoint':{'library_file_id':'libfile_484e32ac6d5081918c800c09cd6cf3d2','sha256':'f32a2dc052e12c483f5e7ddfbf3715edf22ffc3df82b35e55d020785e5c1200e','scope':'Inherited strata exclusions, exact small-dimensional minima, original selected M19 input census, prior16,841 profile cuts and balanced-two-image theorem.'},
 'counting_caution':'M11 counts affine support classes; middle counts weight multisets; M19 counts selected weight/own-direction profiles. These are different objects and are not summed. Surviving relaxations are not Kakeya constructions.',
 'next_mathematical_frontier':'Simultaneous residue adjacency, actual tangent subspaces, common shape choices and exact quotient lift coverage; no support17 M11 closure claimed.'}
(ROOT/'Kakeya_Research_Frontier_Round2.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'status':out['status'],'M11_remaining':57,'middle_support_upper':18,'M19_remaining':30471},indent=2))
