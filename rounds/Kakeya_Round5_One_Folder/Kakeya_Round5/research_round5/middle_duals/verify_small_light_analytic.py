"""Replay every new multi-price cut by one elementary small-light theorem.

This checker uses no optimizer, local DP, pair-spectrum census, or producer
table. It scans the entire previous275755-profile list and evaluates the
closed-form baseline-cap bound on the exact2/3-point light-fibre domain.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
INPUT=ROOT/'research_round4/middle_inventory/after_priced_nine_survivors.txt'


def main():
    if sys.flags.optimize:
        raise SystemExit('Do not disable assertions.')
    cuts={}
    by=Counter()
    checked=0
    for raw in INPUT.open():
        support,maximum,old,*weights=map(int,raw.split())
        if weights[9]>3:
            continue
        checked+=1
        assert set(weights[9:])<={2,3}
        heavy=tuple(w//2 for w in weights[:9])
        pair_budget=sum(w-1 for w in weights[9:])
        candidates=[]
        # b=1/2 and b equal to a heavy cap cover every breakpoint of the
        # convex function b*pair_budget+3*sum_h(c_h-b)_+ on b>=1/2.
        for twice_b in sorted({1}|{2*c for c in heavy}):
            excess=sum(max(0,2*c-twice_b) for c in heavy)
            upper=twice_b*pair_budget+3*excess
            candidates.append((upper,twice_b,excess))
        upper,twice_b,excess=min(candidates)
        if upper>=96:
            continue
        assert excess<32
        record={'support':support,'maximum':maximum,'weights':weights,
                'light_pair_budget':pair_budget,'baseline_cap_twice':twice_b,
                'heavy_excess_twice':excess,'doubled_bound_at_three':upper,
                'required_doubled_at_three':96}
        cuts[tuple(weights)]=record
        by[support,maximum]+=1
    supplied={tuple(json.loads(line)['weights']) for line in
              (HERE/'FULL_MULTI_PRICE_CUTS.jsonl').open()}
    assert set(cuts)==supplied and len(cuts)==240
    witnesses=HERE/'SMALL_LIGHT_ANALYTIC_CERTIFICATES.jsonl'
    witnesses.write_text(''.join(json.dumps(cuts[w],separators=(',',':'))+'\n'
                                 for w in sorted(cuts,reverse=True)))
    result={
        'status':'PASS_CLOSED_FORM_ANALYTIC_REPLAY',
        'whole_baseline_profiles':275755,
        'profiles_with_all_light_weights_two_or_three':checked,
        'exactly_matches_all_new_multi_price_exclusions':True,
        'profile_exclusions':len(cuts),
        'bound':'C_F <= b*L+r*sum_h(c_h-b)_+, where b>=1/2 and L=sum_light(w-1). A strict b*L+3*sum_h(c_h-b)_+<48 excludes every r>=3.',
        'optimizer_needed_for_verification':False,
        'local_dynamic_program_needed_for_verification':False,
        'spectrum_census_needed_for_these_profile_proofs':False,
        'baseline_completeness_dependency':'The Round4 inventory and its earlier exclusions are separate inherited inputs; this analytic replay proves the240 listed weight-profile contradictions.',
        'remaining_weight_profiles':275515,
        'by_cell':[{'support':s,'maximum':m,'cuts':n} for (s,m),n in sorted(by.items())],
        'input_sha256':sha256(INPUT.read_bytes()).hexdigest(),
        'multi_price_certificates_sha256':sha256((HERE/'FULL_MULTI_PRICE_CUTS.jsonl').read_bytes()).hexdigest(),
        'analytic_witnesses_sha256':sha256(witnesses.read_bytes()).hexdigest(),
    }
    (HERE/'SMALL_LIGHT_ANALYTIC_REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','profiles_with_all_light_weights_two_or_three',
                      'profile_exclusions','exactly_matches_all_new_multi_price_exclusions',
                      'remaining_weight_profiles']},indent=2))


if __name__=='__main__':
    main()
