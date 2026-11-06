#!/usr/bin/env python3
"""Untrusted SAT-search wrapper that supplies a proof for the ORIGINAL CNF.

For each positive clause C, any common binary consequence u of all literals
of C is entailed. Search with these units made explicit; prefix every added
unit to the solver's standard textual DRAT stream. A checker must validate
the concatenated proof against the unchanged original CNF. Therefore this
preprocessor is outside the trusted mathematical/encoding boundary.
"""
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time

SOLVER = Path('/tmp/kakeya_lean_round4/lean-4.24.0-linux/bin/cadical')


def sha(path):
    out=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1<<20),b''):out.update(block)
    return out.hexdigest()


def read_cnf(path):
    variables=declared=None;clauses=[];pending=[]
    with Path(path).open() as stream:
        for line in stream:
            line=line.strip()
            if not line or line.startswith('c'):continue
            if line.startswith('p '):
                if variables is not None:raise ValueError('Repeated DIMACS header')
                tag,kind,n,m=line.split()
                if kind!='cnf':raise ValueError('Expected CNF')
                variables,declared=int(n),int(m)
                continue
            if variables is None:raise ValueError('Clause precedes header')
            for word in line.split():
                literal=int(word)
                if literal==0:clauses.append(pending);pending=[]
                elif abs(literal)>variables:raise ValueError('Literal out of range')
                else:pending.append(literal)
    if variables is None or pending or len(clauses)!=declared:
        raise ValueError('Malformed DIMACS input')
    return variables,clauses


def derive_units(clauses):
    implications=defaultdict(set)
    existing={c[0] for c in clauses if len(c)==1}
    for c in clauses:
        if len(c)==2:
            a,b=c
            implications[-a].add(b);implications[-b].add(a)
    witnesses={}
    for index,c in enumerate(clauses,1):
        if len(c)<2 or not all(literal>0 for literal in c):continue
        ordered=sorted(set(c),key=lambda l:len(implications[l]))
        common=set(implications[ordered[0]])|{ordered[0]}
        for literal in ordered[1:]:
            common.intersection_update(implications[literal]|{literal})
            if not common:break
        for unit in sorted(common):
            if unit not in existing and unit not in witnesses:
                witnesses[unit]={'positive_clause_index':index,'positive_clause':c,
                                 'rule':'Every disjunct implies this literal via an original binary clause or identity.'}
    return sorted(witnesses,key=lambda x:(abs(x),x)),witnesses


def write_formula(path,n,clauses,units):
    with Path(path).open('w') as out:
        out.write(f'p cnf {n} {len(clauses)+len(units)}\n')
        for clause in clauses:out.write(' '.join(map(str,clause))+' 0\n')
        for unit in units:out.write(f'{unit} 0\n')


def main():
    args=sys.argv[1:]
    if args==['--version']:
        print('rup-unit-wrapper-v1',flush=True)
        return subprocess.call([str(SOLVER),'--version'])
    if len(args)<2:raise ValueError('Expected options, original.cnf and proof.drat')
    flags=args[:-2];cnf=Path(args[-2]).resolve();proof=Path(args[-1]).resolve()
    if cnf==proof:raise ValueError('Proof output aliases original CNF')
    if any(flag in ('--lrat','--frat','--binary') or flag.startswith('--binary=1') for flag in flags):
        raise ValueError('This wrapper requires standard textual DRAT')
    n,clauses=read_cnf(cnf);units,witnesses=derive_units(clauses)
    started=time.monotonic();original_hash=sha(cnf)
    # These files are in the producer's private working directory. Publication
    # is the producer's responsibility, after every child has stopped.
    augmented=proof.with_name('search_augmented.cnf')
    solver_proof=proof.with_name('search_solver.drat')
    prefix=proof.with_name('rup_unit_prefix.txt')
    metadata=proof.with_name('rup_unit_preprocessing.txt')
    write_formula(augmented,n,clauses,units)
    prefix.write_text(''.join(f'{u} 0\n' for u in units))
    record={'status':'SEARCHING_UNTRUSTED_AUGMENTED_FORMULA','original_cnf_sha256':original_hash,
            'augmented_cnf_sha256':sha(augmented),'solver_binary_sha256':sha(SOLVER),
            'added_units':units,'added_unit_count':len(units),'witnesses':witnesses,
            'prefix_sha256':sha(prefix),'trusted_preprocessor':False,
            'required_check':'Concatenated prefix+solver DRAT must pass mandatory checker against original CNF.'}
    metadata.write_text(json.dumps(record,indent=2)+'\n')
    print(f'c rup-unit-wrapper added {len(units)} redundant search units',flush=True)
    if '-t' in flags:
        position=flags.index('-t')
        requested=int(flags[position+1])
        remaining=max(1,requested-int(time.monotonic()-started)-1)
        flags[position+1]=str(remaining)
        record['requested_total_limit_seconds']=requested
        record['solver_time_limit_seconds_after_preprocessing']=remaining
    command=[str(SOLVER)]+flags+['--no-binary',str(augmented),str(solver_proof)]
    child=subprocess.Popen(command)
    try:
        code=child.wait()
    finally:
        if child.poll() is None:
            child.kill();child.wait()
    if sha(cnf)!=original_hash:raise ValueError('Original formula changed during search')
    with proof.open('wb') as out:
        out.write(prefix.read_bytes())
        if solver_proof.exists():
            with solver_proof.open('rb') as source:
                for block in iter(lambda:source.read(1<<20),b''):out.write(block)
    record.update(status='UNTRUSTED_SEARCH_COMPLETE_NEEDS_ORIGINAL_CNF_CHECK',
                  solver_returncode=code,solver_proof_sha256=sha(solver_proof) if solver_proof.exists() else None,
                  concatenated_drat_sha256=sha(proof),seconds=round(time.monotonic()-started,6))
    metadata.write_text(json.dumps(record,indent=2)+'\n')
    return code


if __name__=='__main__':raise SystemExit(main())
