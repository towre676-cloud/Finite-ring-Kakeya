#!/usr/bin/env python3
"""Replay inherited controls without changing historical reports."""
import importlib.util,json,sys,time
from pathlib import Path
from campaign import R
HERE=Path(__file__).resolve().parent
R8=HERE.parents[2]/'Kakeya_Round8_One_Folder/Kakeya_Round8'
# Resolve relative to repository rounds, without a machine-specific path.

def load(name,path):
 sys.path.insert(0,str(path.parent))
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
start=time.monotonic()
I=load('verify_inherited_incidence',R8/'research_round8/incidence/verify_incidence_budget.py')
X=load('verify_inherited_tetra',R8/'research_round8/strengthened/verify_strengthened.py')
data=R8/'research_round6/imported_claude_round4/data'
spec=X.X.load_spectra(data/'spec32.csv');table=X.X.load_M(data/'Mtable.txt')
report={'incidence_math':I.mathematical_controls(),'incidence_primitives':I.primitive_controls(),
 'incidence_boolean':I.boolean_controls(),'tetra_capacity':X.capacity_controls(table),'tetra_flags':X.flag_controls(spec)}
# Ensure tested semantic source is identical to the recovered active source.
files=['research_round8/incidence/incidence_cuts.py','research_round8/incidence/encode_next_frontier.py','research_round8/strengthened/encode_strengthened.py']
for p in files:
 if R.sha(R8/p)!=R.sha(HERE.parent/p):raise ValueError('Historical/current semantic mismatch')
report.update(status='PASS',seconds=time.monotonic()-start,semantic_source_hashes={p:R.sha(R8/p) for p in files})
R.dump(HERE/'INHERITED_VALIDATION.json',report)
print('INHERITED PASS',report['seconds'],flush=True)
