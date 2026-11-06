#!/usr/bin/env python3
"""Create an explicit exhaustive interval queue; unrun entries give no credit."""
import argparse
import json
import verify_support13 as V


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh',action='store_true',help='Snapshot completed baseline certificates before planning')
    args=parser.parse_args()
    if args.refresh:
        V.freeze_manifest()
    manifest,catalogue=V.load_manifest()
    coverage=manifest['inventory_coverage']
    cases={c['nonzero_support_mask']:c for c in catalogue}
    result={'status':'UNRUN_EXHAUSTIVE_BAND_QUEUE','source_manifest_sha256':V.A.sha(V.MANIFEST),
            'intervals':[[18,18],[17,17],[15,16],[2,14]],
            'disjoint_union_equals':list(range(2,19)),
            'reason':'Prioritize exact18, then17, then15..16 and2..14; separating18 from17 targets a complete maximum cell.',
            'exclusion_credit_for_unrun_entries':False,'bands':[]}
    actual=sorted(m for lo,hi in result['intervals'] for m in range(lo,hi+1))
    V.A.require(actual==list(range(2,19)),'Intervals are not an exhaustive disjoint partition')
    for lo,hi in result['intervals']:
        masks=coverage['band_coverage'][f'{lo}_{hi}']['remaining_masks']
        rows=[]
        for mask in masks:
            rows.append({'nonzero_support_mask':mask,'support':cases[mask]['support'],
                         'distinguished_hub':0,'maximum_interval':[lo,hi],'total_upper_bound':93,
                         'status':'NEEDS_CHECKED_CERTIFICATE_FOR_THIS_INTERVAL'})
        result['bands'].append({'maximum_interval':[lo,hi],'remaining_case_count':len(rows),'cases':rows})
    V.P.dump(V.HERE/'EXHAUSTIVE_BAND_QUEUE.json',result)
    print(json.dumps({'status':result['status'],'bands':[
        {'interval':b['maximum_interval'],'remaining':b['remaining_case_count'],
         'masks':[r['nonzero_support_mask'] for r in b['cases']]} for b in result['bands']]}))


if __name__=='__main__':main()
