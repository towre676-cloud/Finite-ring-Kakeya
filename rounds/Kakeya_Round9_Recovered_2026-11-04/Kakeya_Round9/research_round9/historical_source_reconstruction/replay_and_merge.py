#!/usr/bin/env python3
"""Check new exact CNFs/proofs and merge marked coverage without SAT search.

Inherited Round8 coverage remains explicitly inherited, not newly certified.
"""
import argparse,collections,gc,json,lzma,shutil,tempfile,time,sys
from pathlib import Path
import campaign as C

def transport_check(groups):
    checked=0
    for group in groups:
        support=group['representative_support'];roles=group['all_thirteen_hub_choices']
        assert len(support)==len(set(support))==13
        assert {x['largest_vertex_in_representative'] for x in roles}==set(support)
        seen=set()
        for role in roles:
            hub=role['largest_vertex_in_representative'];cols=role['linear_columns_after_translation']
            assert len(cols)==5
            def linear(x):
                y=0
                for i,c in enumerate(cols):
                    if (x>>i)&1:y^=c
                return y
            assert len({linear(x) for x in range(32)})==32
            transformed={linear(x^hub) for x in support}
            mask=sum(1<<x for x in transformed if x)
            assert 0 in transformed and mask==role['target_marked_nonzero_mask']
            seen.add(mask);checked+=1
        assert seen==set(group['marked_nonzero_masks'])
    return checked

def main():
    if sys.flags.optimize:raise SystemExit('Run without -O: exact verification uses assertions.')
    ap=argparse.ArgumentParser();ap.add_argument('--fresh-proofs',action='store_true');args=ap.parse_args()
    started=time.monotonic();queue=json.loads((C.ROOT/'research_round8/NEXT_ATTACK_QUEUE.json').read_text())['cases'];expected={x['case_id']:x for x in queue};assert len(expected)==54
    oldpath=C.ROOT/'Kakeya_Research_Frontier_Round8.json';old=json.loads(oldpath.read_text());oldcoverage=old['support13_partial_coverage'];inherited=set(oldcoverage['complete_masks']);assert len(inherited)==28
    groups=json.loads((C.ROOT/'research_round7/geometry/SUPPORT13_MARKING_MAP.json').read_text())['groups'];assert len(groups)==13
    transports=transport_check(groups)
    C.A.verify_sources()
    bins,build=C.A.build_checkers(C.HERE/'replay_tools/bin',C.HERE/'replay_tools/logs')
    source=C.source_hashes();new={12:set(),13:set()};rows=[];seen=set()
    for path in sorted((C.HERE/'cases').glob('*/CASE_RECEIPT.json')):
        row=json.loads(path.read_text());case=row['case'];cid=case['case_id'];assert cid in expected and case==expected[cid] and cid not in seen;seen.add(cid)
        assert row['source_hashes']==source
        folder=path.parent
        for name,info in row['storage'].items():assert C.sha(folder/(name+'.xz'))==info['xz_sha256']
        if row['exclusion_credited']:
            assert row['status']=='CERTIFIED_EXCLUSION' and row['audit']['status']=='PASS_CNF_UNSAT_VIA_CAKEML_LRAT'
            with tempfile.TemporaryDirectory(prefix='kakeya_r9_verify_') as tmp:
                tmp=Path(tmp)
                for name in ('input.cnf','proof.drat'):
                    with lzma.open(folder/(name+'.xz'),'rb') as a,(tmp/name).open('wb') as b:shutil.copyfileobj(a,b)
                    assert C.sha(tmp/name)==row['storage'][name]['raw_sha256']
                assert C.sha(tmp/'input.cnf')==row['cnf_sha256']
                f=C.make(case);C.N.write_dimacs(f,tmp/'regenerated.cnf');metadata=f.r8_next_frontier_metadata;del f;gc.collect()
                assert C.sha(tmp/'regenerated.cnf')==row['cnf_sha256'] and metadata==row['extension']
                assert row['audit']['input_sha256']=={'cnf':row['cnf_sha256'],'drat':C.sha(tmp/'proof.drat')}
                if args.fresh_proofs:
                    audit=C.A.check_pair(tmp/'input.cnf',tmp/'proof.drat',tmp/'audit',bins,900,1024,256,False)
                    assert audit['status']=='PASS_CNF_UNSAT_VIA_CAKEML_LRAT',case
                else:audit={'status':'PRODUCTION_RECEIPT_REUSED_NO_FRESH_PROOF_CHECK'}
            maximum=case['maximum_interval'][0];new[maximum].add(case['nonzero_support_mask'])
            rows.append({'case_id':cid,'mask':case['nonzero_support_mask'],'maximum':maximum,'cnf_sha256':row['cnf_sha256'],'audit':audit})
        else:
            assert row['status']=='UNKNOWN_TIMEOUT_OR_RESOURCE_STOP' or row['status']=='SAT_RELAXATION_NO_RING_WITNESS'
            with tempfile.TemporaryDirectory(prefix='kakeya_r9_unknown_input_') as tmp:
                tmp=Path(tmp)
                with lzma.open(folder/'input.cnf.xz','rb') as a,(tmp/'input.cnf').open('wb') as b:shutil.copyfileobj(a,b)
                assert C.sha(tmp/'input.cnf')==row['cnf_sha256']==row['storage']['input.cnf']['raw_sha256']
                f=C.make(case);C.N.write_dimacs(f,tmp/'regenerated.cnf');metadata=f.r8_next_frontier_metadata;del f;gc.collect()
                assert C.sha(tmp/'regenerated.cnf')==row['cnf_sha256'] and metadata==row['extension']
    assert seen==set(expected),'Every queued case must have an explicit retained outcome.'
    closed={};remaining={};counts={}
    for maximum in (12,13):
        covered=inherited|new[maximum];closed[maximum]=[g['unmarked_affine_orbit_id'] for g in groups if set(g['marked_nonzero_masks'])<=covered]
        remaining[maximum]=sorted(set(c['nonzero_support_mask'] for c in queue if c['maximum_interval'][0]==maximum)-new[maximum]);counts[maximum]=len(covered)
    summary={'status':'PASS_FRESH_NEW_PROOFS_AND_EXACT_CNF_REGENERATION' if args.fresh_proofs else 'PASS_EXACT_CNF_REGENERATION_AND_BOUND_PRODUCTION_RECEIPTS','date':'2026-11-04','replayer_sha256':C.sha(Path(__file__)),'new_marked_exclusions':len(rows),'fresh_proof_checks':args.fresh_proofs,'new_cases':rows,'inherited_round8_joint_marked_cases':28,'inherited_proofs_freshly_replayed':False,'round8_frontier_sha256':C.sha(oldpath),'all_hub_transports_independently_checked':transports,'complete_support13_affine_classes_by_exact_maximum':closed,'marked_coverage_out_of55':counts,'remaining_queued_masks_by_maximum':remaining,'whole_weight_profiles_removed':0,'middle_whole_weight_profiles_still_tracked':182526,'maximum11_affine_classes_still_tracked':42,'full_dimension5_theorem':'OPEN','all_dimension_law':'OPEN','seconds':time.monotonic()-started}
    C.dump(C.HERE/'ROUND9_VERIFIED_FRONTIER.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ('new_cases',)},indent=2),flush=True)
if __name__=='__main__':main()
