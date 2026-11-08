#!/usr/bin/env python3
"""Independent finite projection checks and exact baseline regeneration."""
from itertools import combinations, product
from pathlib import Path
import importlib.util, json, sys, tempfile
import encode_projected as E
from campaign import R
HERE=Path(__file__).resolve().parent

def require(ok, why):
    if not ok: raise ValueError(why)

def main():
    rows=json.loads((HERE.parent/'research_round9/REMAINING_CASES.json').read_text())['cases']
    results=[];nassign=ntuple=0
    for row in rows:
        c=row['case'];S=c['support'];m=c['maximum_interval'][0]
        f=R.formula(c);before=(f.n,len(f.cl));original=[x[:] for x in f.cl]
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'input.cnf';E.N.write_dimacs(f,p)
            require(R.sha(p)==row['cnf_sha256'],'baseline hash')
            E.append_projection(f,S,m,enabled=False);E.N.write_dimacs(f,p)
            require(R.sha(p)==row['cnf_sha256'],'disabled identity')
            meta=E.append_projection(f,S,m)
            require(f.cl[:before[1]]==original and f.n==before[0],'prefix/numbering')
            E.N.write_dimacs(f,p);newhash=R.sha(p)
        heavy=f.r8_incidence['heavy']
        patternclauses=f.cl[before[1]:before[1]+meta['pattern_clauses']]
        surviving=[]
        for bits in product([False,True],repeat=12):
            weights={0:m,**{a:(m if b else 2) for a,b in zip(S[1:],bits)}}
            L=[a for a in S if weights[a]==2]
            if len(L)>3:continue
            nassign+=1
            H=[a for a in S if a not in L]
            missing=set(range(1,32))-{a^b for a,b in combinations(H,2)}
            capacity={d:sum(min(16,(weights[a]//2)*(weights[b]//2))
                             for a,b in combinations(S,2) if a^b==d) for d in range(1,32)}
            good=min(capacity.values())>=16 and len(missing)<=2
            values={heavy[a]:a in H for a in S}
            accepted=all(any(values[x] for x in clause) for clause in patternclauses)
            require(good==accepted,'projected Boolean predicate')
            if accepted:surviving.append(tuple(L))
        require(set(surviving)=={tuple(r['light']) for r in meta['survivors']},'survivor enumeration')
        # Independently evaluate the emitted gated clauses against all exact
        # pair-count triples 4..6 on every surviving missing direction.
        pairclauses=f.cl[before[1]+meta['pattern_clauses']:]
        for r in meta['survivors']:
            L=r['light']
            for d in r['missing']:
                partners=[a^d for a in L]
                ys={f.y[b,d,p]:(j,p) for j,b in enumerate(partners) for p in range(4,7)}
                active=[cl for cl in pairclauses if set(x for x in cl if x>0)=={heavy[a] for a in L}
                        and all(-x in ys for x in cl if x<0)]
                for counts in product(range(4,7),repeat=3):
                    ntuple+=1
                    actual=all(any(counts[ys[-x][0]]!=ys[-x][1] for x in cl if x<0) for cl in active)
                    require(actual==(sum(counts)>=16),'pair projection semantics')
        results.append({'case_id':c['case_id'],'baseline_sha256':row['cnf_sha256'],
                        'projected_sha256':newhash,'baseline_variables':before[0],
                        'baseline_clauses':before[1],'added_clauses':meta['added_clauses'],
                        'pattern_clauses':meta['pattern_clauses'],
                        'pair_projection_clauses':meta['pair_projection_clauses'],
                        'surviving_patterns':meta['surviving_patterns'],
                        'baseline_regenerated':True,'disabled_byte_identity':True,'prefix_unchanged':True})
        print('PASS',c['nonzero_support_mask'],m,meta['added_clauses'],meta['surviving_patterns'],flush=True)
    invalid=0
    for S,m in [([0]*13,12),(list(range(13)),11),(list(range(13)),14),(list(range(1,14)),12)]:
        try:E.patterns(S,m)
        except ValueError:invalid+=1
        else:raise ValueError('invalid scope accepted')
    report={'status':'PASS','cases':results,'heavy_assignments_checked':nassign,
            'pair_tuples_checked':ntuple,'invalid_scopes_rejected':invalid,
            'source_sha256':{p.name:R.sha(p) for p in [Path(__file__),HERE/'encode_projected.py']},
            'mathematical_exclusions_credited':0}
    R.dump(HERE/'PROJECTION_VALIDATION.json',report)
    print('ALL PASS',nassign,ntuple,flush=True)
if __name__=='__main__':main()
