"""Independent exact-integer verification of the support17 assignment certificates.

No assignment optimizer is run or trusted. All dual edge inequalities,
cardinality facts, geometric numerical hypotheses, and partition coverage
are checked directly.
"""
from pathlib import Path
from collections import Counter
import hashlib,json,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'research_round2/structural/m11_support'))
from verify_cap11_support import tails,complete_graph_bound,CUTOFFS
from verify_cap11_support_through18 import geometry_certificate

def run():
    started=time.monotonic()
    summary=json.loads((HERE/'S17_SUPPORT_REDUCTION.json').read_text())
    source=ROOT/summary['source']['path']
    assert hashlib.sha256(source.read_bytes()).hexdigest()==summary['source']['sha256']
    records={r['orbit']:r for r in json.loads(source.read_text())['records']}
    expected=set();counts=Counter()
    for tail in tails(16,82,11):
        w=(11,)+tail;counts['total']+=1
        if any(complete_graph_bound(w,e)<992 for e in CUTOFFS):counts['resource']+=1
        elif geometry_certificate(w) is not None:counts['inherited_geometry']+=1
        else:expected.add(w)
    assert len(expected)==110 and dict(counts)==summary['global_partition_counts']
    certs=json.loads((HERE/'S17_ASSIGNMENT_DUAL_CERTIFICATES.json').read_text())
    grouped={o:[] for o in (367,373,374,376,377)}
    for cert in certs:
        orbit=cert['orbit'];w=tuple(cert['weights']);rec=records[orbit]
        assert w in expected and len(w)==17 and sum(w)==93 and w[0]==11
        alpha=cert['row_dual'];beta=cert['column_dual']
        assert len(alpha)==len(beta)==17
        assert all(isinstance(z,int) for z in alpha+beta)
        assert sum(alpha)+sum(beta)==cert['maximum_energy']
        for i,a in enumerate(rec['support']):
            for j,weight in enumerate(w):
                if weight<rec['minimum_weights'][str(a)]:continue
                q=int(rec['local_upper_envelopes'][str(a)][str(weight)])
                assert alpha[i]+beta[j]>=q
        method=cert['method']
        if method=='EXACT_ASSIGNMENT_ENVELOPE':assert cert['maximum_energy']<992
        elif method=='NINE_HEAVY_INDEPENDENT_MISSING_DIRECTIONS':
            p=sum(x*(x-1)//2 for x in w[9:]);q=sum(x*x//4 for x in w[9:])
            assert p==cert['low_pair_mass']<=15
            assert q==cert['low_halfspace_mass']<12
        else:assert method=='UNRESOLVED_PROFILE'
        grouped[orbit].append((w,method))
    statuses=[]
    for orbit,items in grouped.items():
        assert len(items)==len(expected) and {w for w,_ in items}==expected
        methods=Counter(m for _,m in items)
        statuses.append(dict(orbit=orbit,methods=dict(methods),
            status='OPEN' if methods['UNRESOLVED_PROFILE'] else 'CLOSED',
            surviving_profiles=[w for w,m in items if m=='UNRESOLVED_PROFILE']))
    closed=[r['orbit'] for r in statuses if r['status']=='CLOSED']
    assert closed==[373,376]
    result=dict(status='PASS',new_whole_support_class_exclusions=closed,
                previous_M11_open_support_classes=57,new_M11_open_support_classes=55,
                exact_assignment_certificates=len(certs),partition_counts=dict(counts),
                records=statuses,seconds=time.monotonic()-started)
    (HERE/'S17_ENVELOPE_INDEPENDENT_REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':run()
