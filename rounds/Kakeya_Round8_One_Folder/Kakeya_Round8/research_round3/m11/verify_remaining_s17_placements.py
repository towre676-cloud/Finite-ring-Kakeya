"""Independent finite-geometry replay for all remaining support17 placements.

P/R are regenerated using cube graph equality patterns, then exact frozen
energy bounds and per-direction capacity. Q uses only residue incidence and
an explicit rank obstruction for forced periods; no optimization solver.
"""
from pathlib import Path
from collections import Counter
from itertools import combinations,permutations,product
import hashlib,json,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
SOURCE=ROOT/'research_sources/extracted/Kakeya_Reconciled_Proofs_2026-10-27/late_parallel_2214/extracted/m11_directional/inputs/CAP11_STRUCTURAL_REDUCTION.json'

def edge_cap(p,q):
    return 13 if sorted((p,q))==[3,5] else min(16,p*q)

def binary_rank(vectors):
    basis={}
    for vector in vectors:
        while vector:
            pivot=vector.bit_length()-1
            if pivot in basis:vector^=basis[pivot]
            else:basis[pivot]=vector;break
    return len(basis)

def pair_differences(points):
    return Counter(a^b for a,b in combinations(points,2))

def replay_pr(record,mode):
    S=tuple(record['support']);Sset=set(S);counts=Counter()
    minimum={int(a):v for a,v in record['minimum_weights'].items()}
    energy={int(a):{int(w):int(q) for w,q in table.items()} for a,table in record['local_upper_envelopes'].items()}
    for heavy_tuple in combinations(S,9):
        counts['subsets']+=1
        differences=pair_differences(heavy_tuple)
        if len(differences)!=28:continue
        counts['maximal_subsets']+=1
        T=set(heavy_tuple);L=tuple(a for a in S if a not in T)
        F=tuple(d for d in range(1,32) if d not in differences)
        assert len(F)==3 and binary_rank(F)==3
        ports={a:tuple(k for k,d in enumerate(F) if a^d in T) for a in L}
        if any(not ports[a] for a in L):continue
        special_choices=(permutations([a for a in L if len(ports[a])>=2],2)
                         if mode=='P' else ((a,) for a in L if len(ports[a])==3))
        for specials in special_choices:
            local_patterns=[]
            if mode=='P':
                four,three=specials
                for active4 in combinations(ports[four],2):
                    for active3 in combinations(ports[three],2):
                        rows={a:[0]*32 for a in L}
                        p,q=(F[k] for k in active4)
                        for d in (p,q,p^q):rows[four][d]=2
                        p,q=(F[k] for k in active3)
                        for d in (p,q,p^q):rows[three][d]=1
                        local_patterns.append((rows,{four:4,three:3}))
            else:
                five=specials[0]
                for singled in range(3):
                    p,q=(F[k] for k in range(3) if k!=singled);r=F[singled]
                    rows={a:[0]*32 for a in L}
                    for d in (p,q,p^q):rows[five][d]=2
                    for u in (0,p,q,p^q):rows[five][r^u]=1
                    local_patterns.append((rows,{five:5}))
            for rows,special_weights in local_patterns:
                counts['port_cases']+=1
                units=tuple(a for a in L if a not in specials)
                required=tuple(4-sum(rows[a][d] for a in specials) for d in F)
                for choices in product(*(ports[a] for a in units)):
                    if tuple(choices.count(k) for k in range(3))!=required:continue
                    counts['low_assignments']+=1
                    low_rows={a:row[:] for a,row in rows.items()}
                    for a,k in zip(units,choices):low_rows[a][F[k]]=1
                    low_weights={a:special_weights.get(a,2) for a in L}
                    for hub,weak in permutations(heavy_tuple,2):
                        weights={a:(11 if a==hub else 7 if a==weak else 8) for a in heavy_tuple}
                        weights.update(low_weights)
                        if any(weights[a]<minimum[a] for a in S):continue
                        counts['weighted_cases']+=1
                        if sum(energy[a][weights[a]] for a in S)<992:continue
                        counts['energy_pass']+=1
                        witness=None
                        for d in range(1,32):
                            total=0
                            for a in S:
                                b=a^d
                                if b not in Sset or a>b:continue
                                p=weights[a]//2 if a in T else low_rows[a][d]
                                q=weights[b]//2 if b in T else low_rows[b][d]
                                total+=edge_cap(p,q)
                            if total<16:witness=(d,total);break
                        assert witness is not None, ('UNRESOLVED_PR',record['orbit'],mode,weights,low_rows)
                        counts['capacity_excluded']+=1
    return dict(orbit=record['orbit'],profile=mode,status='CLOSED_ALL_PLACEMENTS',**dict(counts))

def replay_q(record):
    S=tuple(record['support']);counts=Counter();certificates=[]
    for T in combinations(S,10):
        counts['subsets']+=1
        directions=pair_differences(T)
        if len(directions)<31:
            counts['missing_direction_budget_exclusions']+=1;continue
        counts['full_difference_subsets']+=1
        unique={a:tuple(a^b for b in T if b!=a and directions[a^b]==1) for a in T}
        for weak in combinations(T,2):
            counts['weak_pairs']+=1
            cost=sum(len(unique[a]) for a in weak)
            if cost>7:counts['unique_degree_budget_exclusions']+=1;continue
            # Each such unique edge needs one low pair for each weak endpoint.
            # At most7-cost low pairs can occur in any other direction.
            assert cost==6
            robust=[];rank_details=[]
            for a in T:
                if a in weak:continue
                strong=tuple(a^b for b in T if b!=a and b not in weak and directions[a^b]==1)
                ranks=[binary_rank(strong)]
                ranks.extend(binary_rank(d for d in strong if d!=removed) for removed in strong)
                if min(ranks)>=4:
                    robust.append(a);rank_details.append(dict(vertex=a,strong_unique_directions=strong,
                                                              rank_after_any_one_deletion=min(ranks)))
            # Only one nonweak vertex can receive weight11. All others are8.
            assert len(robust)>=2, ('UNRESOLVED_Q',T,weak,cost,robust)
            counts['forced_period_rank_exclusions']+=1
            certificates.append(dict(heavy_residues=T,weak_six_residues=weak,
                                     minimum_low_pairs_on_weak_unique_edges=cost,
                                     remaining_light_pair_budget=7-cost,
                                     robust_vertices=rank_details))
    return dict(status='CLOSED_ALL_PLACEMENTS',orbit=record['orbit'],profile='Q',**dict(counts)),certificates

def run():
    started=time.monotonic();records={r['orbit']:r for r in json.loads(SOURCE.read_text())['records']}
    result=[]
    for orbit,mode in ((367,'P'),(374,'P'),(377,'P'),(377,'R')):
        row=replay_pr(records[orbit],mode);result.append(row);print(json.dumps(row),flush=True)
    qrow,qcerts=replay_q(records[377]);result.append(qrow);print(json.dumps(qrow),flush=True)
    receipt=dict(status='PASS',scope='Remaining exactmax11 support17 profiles on orbits367,374,377',
                 records=result,new_whole_support_class_exclusions=[367,374,377],
                 combined_with_envelope_stage_new_exclusions=[367,373,374,376,377],
                 previous_M11_open_support_classes=57,new_M11_open_support_classes=52,
                 source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                 seconds=time.monotonic()-started)
    (HERE/'S17_PLACEMENT_INDEPENDENT_REPLAY.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (HERE/'Q_FORCED_PERIOD_RANK_CERTIFICATES.json').write_text(json.dumps(qcerts,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('status','new_M11_open_support_classes','seconds')}),flush=True)

if __name__=='__main__':run()
