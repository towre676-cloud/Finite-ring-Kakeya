"""Isolated unique-edge tetrahedral-four-pair extension of the frozen encoder."""
from pathlib import Path
import importlib.util
import itertools

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=ROOT/'research_round6/joint_maxima/encode_joint_maxima.py'
spec=importlib.util.spec_from_file_location('four_pair_frozen_baseline',BASE)
E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)
load_spectra=E.load_spectra
load_M=E.load_M
all_subspaces=E.all_subspaces
write_dimacs=E.write_dimacs


def nonplanar_four_pair_type(spectrum):
    weight,hist,rank_min,rank_max=spectrum
    if rank_min!=4 or rank_max!=4:return False
    energy=sum(k*k*count for k,count in enumerate(hist))
    return (weight==8 and energy==64 and hist[4]==1) or (weight==11 and energy==205)


def append_unique_four_pair_cuts(f,S,SPEC,enabled=True):
    original_variables,original_clauses=f.n,len(f.cl)
    eligible=[i for i,spectrum in enumerate(SPEC) if nonplanar_four_pair_type(spectrum)]
    by_direction={d:[] for d in range(1,32)}
    for a,b in itertools.combinations(S,2):by_direction[a^b].append((a,b))
    unique=[(d,edges[0][0],edges[0][1]) for d,edges in by_direction.items() if len(edges)==1]
    metadata={'enabled':enabled,'eligible_spectrum_indices':eligible,
              'unique_direction_edges':unique,'conditional_edge_clauses':0,
              'new_variables':0,'new_clauses':0}
    if not enabled:
        f.four_pair_metadata=metadata
        return metadata
    selected={v:[f.z[v,i] for i in eligible if (v,i) in f.z] for v in S}
    useful=[(d,a,b) for d,a,b in unique if selected[a] and selected[b]
            and (a,d,4) in f.y and (b,d,4) in f.y]
    vertices=sorted({v for d,a,b in useful for v in (a,b)})
    type_literals={}
    for v in vertices:
        options=selected[v]
        if len(options)==1:type_literals[v]=options[0]
        else:
            u=f.new();type_literals[v]=u
            f.add([-u]+options)
            for z in options:f.add([-z,u])
    for d,a,b in useful:
        f.add([-type_literals[a],-type_literals[b],-f.y[a,d,4],-f.y[b,d,4]])
    metadata.update(conditional_edge_clauses=len(useful),new_variables=f.n-original_variables,
                    new_clauses=len(f.cl)-original_clauses)
    f.four_pair_metadata=metadata
    return metadata


def encode(T,m,SPEC,M,SUBS,outtotal=None,hub_min=11,enabled=True):
    f=E.encode(T,m,SPEC,M,SUBS,outtotal=outtotal,hub_min=hub_min)
    append_unique_four_pair_cuts(f,[0]+list(T),SPEC,enabled=enabled)
    return f
