#!/usr/bin/env python3
"""Diagnostic only: ask unit propagation if each projection is RUP."""
from pathlib import Path
import json
from pysat.solvers import Solver
import encode_projected as E
from campaign import R
HERE=Path(__file__).resolve().parent
row=json.loads((HERE.parent/'research_round9/REMAINING_CASES.json').read_text())['cases'][0]
f=R.formula(row['case']);n=len(f.cl)
E.append_projection(f,row['case']['support'],12)
U=R.module('round10_unit',HERE.parent/'research_round7/support13/rup_unit_solver.py')
units,_=U.derive_units(f.cl[:n])
record={'role':'UNTRUSTED_DIAGNOSTIC_NOT_AN_EXCLUSION','baseline_sha256':row['cnf_sha256'],'prefix_rup_units':len(units),'added_clauses':len(f.cl)-n,'rup_clauses':0,'non_rup_clause_indices':[]}
with Solver(name='minisat22',bootstrap_with=f.cl[:n]) as s:
 for u in units:
  ok,_=s.propagate(assumptions=[-u])
  if ok:raise ValueError('Claimed RUP unit did not propagate')
  s.add_clause([u])
 for i,clause in enumerate(f.cl[n:]):
  ok,_=s.propagate(assumptions=[-l for l in clause])
  if not ok:record['rup_clauses']+=1;s.add_clause(clause)
  else:record['non_rup_clause_indices'].append(i)
R.dump(HERE/'TARGET_RUP_DIAGNOSTIC.json',record)
print(record)
