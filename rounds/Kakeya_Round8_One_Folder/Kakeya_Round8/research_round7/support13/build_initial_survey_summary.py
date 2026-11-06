#!/usr/bin/env python3
"""Inventory the complete initial joint survey; this is not a proof checker."""
import json
import certify_support13 as P


def main():
    cases=P.universe();rows=[]
    for c in cases:
        mask=c['nonzero_support_mask']
        if mask==37848950:
            path=P.R6/'strengthened_trials/cases/s13_T37848950_m2_18_baseline/CASE_RECEIPT.json'
            role='INHERITED_ROUND6_CHECKED_CASE'
        elif mask==1022358:
            path=P.HERE.parent/'variant_cases/s13_T1022358_m2_18_baseline_dense_comparison/CASE_RECEIPT.json'
            role='RESERVED_MATCHED_BASELINE_60_SECOND_TRIAL'
        else:
            path=P.HERE/'cases'/f's13_T{mask}_m2_18_baseline_t30'/'CASE_RECEIPT.json'
            role='INITIAL_BASELINE_30_SECOND_SURVEY'
        r=json.loads(path.read_text())
        P.A.require(r['support']==c['support'] and r['maximum_interval']==[2,18]
                    and r['distinguished_hub']==0,'Wrong marked case or interval')
        P.A.require(r.get('total_upper_bound',r.get('total_budget'))==93,'Wrong budget')
        checked=r['status'] in (P.ACCEPTED,'PASS_CNF_UNSAT_VIA_CAKEML_LRAT')
        P.A.require(checked or r['status'] in ('TIMEOUT_OR_RESOURCE_UNCERTIFIED','TIMEOUT_UNCERTIFIED'),
                    'An initial case did not reach a classified outcome')
        rows.append({'nonzero_support_mask':mask,'support':c['support'],'role':role,
                     'production_status':r['status'],'production_records_checked_refutation':checked,
                     'source_receipt':str(path.relative_to(P.ROOT)),'source_receipt_sha256':P.A.sha(path),
                     'cnf_sha256':r['cnf_sha256'],'solve_seconds':r['solve_seconds'],
                     'timeout_is_exclusion':False})
    P.A.require(len(rows)==len({r['nonzero_support_mask'] for r in rows})==55,'Incomplete outcome universe')
    report={'status':'PASS_COMPLETE_INITIAL_55_CASE_OUTCOME_INVENTORY',
            'scope':'All55 marked support13 classes; largest fibre2..18; total at most93.',
            'this_report_does_not_verify_unsat':True,
            'proof_authority':'Use the complete certificate replay, including exact CNF regeneration and mandatory CakeML.',
            'initial_baseline_30_second_cases':53,'reserved_baseline_60_second_cases':1,
            'inherited_checked_cases':1,
            'production_checked_joint_case_records':sum(r['production_records_checked_refutation'] for r in rows),
            'initial_timeouts_uncertified':sum(not r['production_records_checked_refutation'] for r in rows),
            'timing_caveat':'Shared environment, unequal inherited/diagnostic limits and no general speed claim.',
            'later_split_or_retried_results':'Separate current certificate inventory; this historical survey summary does not overwrite them.',
            'catalogue_sha256':P.CATALOGUE_HASH,'cases':rows}
    P.dump(P.HERE/'INITIAL_JOINT_SURVEY_SUMMARY.json',report)
    print(json.dumps({k:report[k] for k in ('status','production_checked_joint_case_records','initial_timeouts_uncertified')}))


if __name__=='__main__':main()
