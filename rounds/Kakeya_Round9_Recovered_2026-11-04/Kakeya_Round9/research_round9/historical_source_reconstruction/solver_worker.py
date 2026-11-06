#!/usr/bin/env python3
"""Untrusted proof-producing search. Parent enforces wall limits."""
import json, sys, time, importlib.util, shutil
from pathlib import Path
from pysat.formula import CNF
from pysat.solvers import Solver
import pysolvers

def main():
    cnf, proof, result, preprocessor = map(Path, sys.argv[1:])
    spec = importlib.util.spec_from_file_location('r9_untrusted_preprocess', preprocessor)
    U = importlib.util.module_from_spec(spec); spec.loader.exec_module(U)
    original = CNF(from_file=str(cnf))
    units, witnesses = U.derive_units(original.clauses)
    (result.parent/'PREPROCESS.json').write_text(json.dumps({'units':units,'witnesses':witnesses,'trusted':False},indent=1)+'\n')
    start = time.monotonic()
    with Solver(name='cadical195', bootstrap_with=original.clauses, with_proof=True) as s:
        for u in units:s.add_clause([u])
        answer = s.solve()
        stats = s.accum_stats()
        if not answer:
            # PySAT's native binary DRAT is retained exactly, preceded by
            # binary unit additions. DRAT-trim detects this standard format.
            pysolvers.flushpr(s.solver.prfp)
            with proof.open('wb') as out:
                for u in units:
                    out.write(b'a'); v=2*abs(u)+(u<0)
                    while v>127:out.write(bytes([(v&127)|128]));v>>=7
                    out.write(bytes([v,0]))
                s.solver.prfile.seek(0);shutil.copyfileobj(s.solver.prfile,out)
        else:
            (result.parent/'MODEL.json').write_text(json.dumps(s.get_model())+'\n')
    result.write_text(json.dumps({'answer':'SAT_RELAXATION' if answer else 'UNSAT_UNCHECKED','seconds':time.monotonic()-start,'stats':stats,'added_rup_units':len(units)},indent=2)+'\n')
    print('s SATISFIABLE' if answer else 's UNSATISFIABLE',flush=True)
    return 10 if answer else 20

if __name__=='__main__':sys.exit(main())
