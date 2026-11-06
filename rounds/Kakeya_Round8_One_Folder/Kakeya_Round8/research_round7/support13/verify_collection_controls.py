#!/usr/bin/env python3
"""Finite bookkeeping controls; these are not mathematical exclusions."""
import json
import time
import verify_support13 as V


def main():
    start=time.monotonic();catalogue=V.P.universe()
    masks=[c['nonzero_support_mask'] for c in catalogue]
    def row(mask,lo,hi):
        return {'nonzero_support_mask':mask,'maximum_interval':[lo,hi]}
    controls=[]
    def check(name,rows,expected_cells,expected_joint):
        result=V.coverage(rows,catalogue)
        V.A.require(result['closed_support13_exact_maximum_cells']==expected_cells,name+': wrong complete columns')
        V.A.require(result['complete_marked_cases']==expected_joint,name+': wrong joint case count')
        V.A.require(result['support13_closed_for_maximum2_through18']==(expected_joint==55),name+': wrong full support claim')
        controls.append({'name':name,'status':'PASS','checked_closed_cells':expected_cells,
                         'checked_joint_marked_cases':expected_joint})
        return result
    check('empty_collection',[],[],0)
    check('one_joint_case_is_not_a_full_support_exclusion',[row(masks[0],2,18)],[],1)
    check('one_missing_marked_case_keeps_every_cell_open',[row(m,2,18) for m in masks[:-1]],[],54)
    exact18=check('all55_at18_closes_only18',[row(m,18,18) for m in masks],[18],0)
    V.A.require(len(exact18['complete_unmarked_affine_classes_by_exact_maximum']['18'])==13,
                'All55at18 must cover all13unmarked geometries')
    check('complete_upper_band_closes_only17_and18',[row(m,17,18) for m in masks],[17,18],0)
    split=[row(m,lo,hi) for m in masks for lo,hi in ((2,14),(15,16),(17,18))]
    check('exhaustive_split_is_complete',split,list(range(2,19)),55)
    gap=[r for r in split if not(r['nonzero_support_mask']==masks[-1] and r['maximum_interval']==[15,16])]
    check('one_missing_middle_branch_preserves_two_open_cells',gap,
          [m for m in range(2,19) if m not in (15,16)],54)
    duplicated=[row(m,2,18) for m in masks[:-1]]+[row(masks[0],2,18)]*20
    check('duplicate_proofs_do_not_fill_a_missing_case',duplicated,[],54)
    whole=check('all55_joint_cases_close_the_support',[row(m,2,18) for m in masks],list(range(2,19)),55)
    V.A.require(len(whole['complete_unmarked_affine_classes_for_maximum2_through18'])==13,
                'Expected13complete unmarked classes')
    open_groups=[g for g in V.checked_unmarked_groups(catalogue)
                 if g['exact_maximum11_still_open_in_inherited_frontier']]
    m11_rows=[row(mask,11,11) for g in open_groups for mask in g['marked_nonzero_masks']]
    slice_all=check('fourteen_m11_roles_do_not_pretend_to_be_fiftyfive_new_proofs',m11_rows,[],0)
    dep=slice_all['separate_inherited_maximum11_slice']
    V.A.require(dep['support13_maximum11_closed_with_inherited_reduction']
                and dep['remaining_total_maximum11_affine_class_count']==42,
                'Complete inherited m11 slice failed to close exactly4classes')
    first=open_groups[0]
    only=[row(mask,11,11) for mask in first['marked_nonzero_masks']]
    slice_one=check('one_whole_previously_open_m11_class_is_one_class',only,[],0)
    dep=slice_one['separate_inherited_maximum11_slice']
    V.A.require(dep['newly_closed_previously_open_affine_classes']==[first['unmarked_affine_orbit_id']]
                and dep['remaining_total_maximum11_affine_class_count']==45,
                'Single m11 class subtraction is wrong')
    slice_gap=check('one_missing_hub_role_prevents_that_m11_class_closure',only[:-1],[],0)
    V.A.require(slice_gap['separate_inherited_maximum11_slice']['remaining_total_maximum11_affine_class_count']==46,
                'Incomplete m11 class was subtracted')
    output={'status':'PASS_COLLECTION_COVERAGE_AND_TRANSPORT_CONTROLS','controls':controls,
            'control_count':len(controls),'marked_catalogue_cases':55,'unmarked_groups':13,
            'all_hub_transports_independently_rechecked':169,
            'catalogue_sha256':V.P.CATALOGUE_HASH,'geometry_map_sha256':V.A.sha(V.GEOMETRY_MAP),
            'certificate_exclusions_proved_by_synthetic_controls':0,
            'seconds':round(time.monotonic()-start,6)}
    V.P.dump(V.HERE/'COLLECTION_CONTROLS.json',output)
    print(json.dumps(output,indent=2))


if __name__=='__main__':main()
