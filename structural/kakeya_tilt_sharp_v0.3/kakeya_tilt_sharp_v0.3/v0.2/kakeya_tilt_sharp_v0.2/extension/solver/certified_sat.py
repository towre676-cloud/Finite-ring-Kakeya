"""Timeout-safe Kakeya SAT decisions with explicit CNF and DRAT artifacts.

The producer runs in a child process: a wall-clock limit cannot be mistaken
for UNSAT, and does not depend on native solver interrupt support. The bundled
small independent checker validates ASCII DRAT proofs using RUP/RAT rules.
It is intended for small proofs; larger proofs should use a specialist checker.
"""
from __future__ import annotations
import argparse,json,multiprocessing as mp,time
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'kakeya_sharp'))
from kakeya_sharp.rings import all_points,directions,lines_in_direction,line,pack,is_kakeya


def generate(r,n,bound):
    from pysat.formula import CNF,IDPool
    from pysat.card import CardEnc,EncType
    pool=IDPool();points={x:pool.id(('p',x)) for x in all_points(n)}
    cnf=CNF()
    for x in line(r,0,pack(1,0,n),n):cnf.append([points[x]])
    for v in directions(n):
        selectors=[]
        for L in lines_in_direction(r,v,n):
            y=pool.id(('line',v,tuple(sorted(L))))
            selectors.append(y)
            for x in L:cnf.append([-y,points[x]])
        cnf.append(selectors)
    cnf.extend(CardEnc.atmost(list(points.values()),bound,vpool=pool,encoding=EncType.totalizer).clauses)
    return cnf,points


def worker(conn,r,n,bound,prefix,solver):
    from pysat.solvers import Solver
    start=time.perf_counter()
    try:
        cnf,points=generate(r,n,bound)
        cnf.to_file(str(prefix)+'.cnf')
        with Solver(name=solver,bootstrap_with=cnf.clauses,with_proof=True) as s:
            sat=s.solve()
            out={'ring':r,'n':n,'bound':bound,'status':'SAT' if sat else 'UNSAT',
                 'solver':solver,'variables':cnf.nv,'clauses':len(cnf.clauses)}
            if sat:
                model={x for x in s.get_model() if x>0}
                K=[x for x,v in points.items() if v in model]
                assert len(K)<=bound and is_kakeya(r,K,n)
                out.update(witness=K,witness_rechecked=True)
            else:
                proof=s.get_proof()
                Path(str(prefix)+'.drat').write_text('\n'.join(proof)+'\n')
                out.update(proof_lines=len(proof),proof_file=prefix.name+'.drat')
            out['seconds']=round(time.perf_counter()-start,6)
            conn.send(out)
    except BaseException as e:
        conn.send({'status':'ERROR','error':repr(e)})
    finally:conn.close()


def decide(r,n,bound,prefix,seconds=120,solver='cadical195'):
    ctx=mp.get_context('spawn');parent,child=ctx.Pipe(duplex=False)
    process=ctx.Process(target=worker,args=(child,r,n,bound,Path(prefix),solver))
    process.start();child.close()
    if parent.poll(seconds):
        try:out=parent.recv()
        except EOFError:out={'status':'ERROR','error':'solver child ended without a result'}
        process.join(5)
        if process.is_alive():process.terminate();process.join()
    else:
        process.terminate();process.join()
        out={'ring':r,'n':n,'bound':bound,'status':'TIMEOUT','limit_seconds':seconds}
    parent.close()
    return out


def rup(clauses,clause):
    assigned={}
    for x in clause:
        v=abs(x);value=x<0
        if v in assigned and assigned[v]!=value:return True
        assigned[v]=value
    change=True
    while change:
        change=False
        for C in clauses:
            unresolved=[];satisfied=False
            for x in C:
                v=abs(x)
                if v in assigned:
                    if assigned[v]==(x>0):satisfied=True;break
                else:unresolved.append(x)
            if satisfied:continue
            if not unresolved:return True
            if len(unresolved)==1:
                x=unresolved[0];assigned[abs(x)]=x>0;change=True
    return False


def verify_drat(cnf_path,proof_path):
    clauses=[]
    for line_ in Path(cnf_path).read_text().splitlines():
        if line_ and line_[0] not in 'cp':
            C=tuple(map(int,line_.split()))
            assert C[-1]==0
            clauses.append(frozenset(C[:-1]))
    additions=deletions=rat_steps=0;empty=False
    for number,line_ in enumerate(Path(proof_path).read_text().splitlines(),1):
        tok=line_.split()
        if not tok or tok[0]=='c':continue
        delete=tok[0]=='d'
        values=list(map(int,tok[1:] if delete else tok))
        assert values[-1]==0
        ordered=values[:-1];C=frozenset(ordered)
        if delete:
            if C in clauses:clauses.remove(C)
            deletions+=1;continue
        if not rup(clauses,C):
            if not ordered:raise AssertionError(f'empty clause not RUP at line {number}')
            pivot=ordered[0]
            for D in clauses:
                if -pivot in D:
                    R=(C-{pivot})|(D-{-pivot})
                    if any(-x in R for x in R):continue
                    if not rup(clauses,R):raise AssertionError(f'failed RAT at line {number}')
            rat_steps+=1
        clauses.append(C);additions+=1
        if not C:empty=True
    assert empty,'proof does not derive the empty clause'
    return {'accepted':True,'additions':additions,'deletions':deletions,'rat_only_steps':rat_steps,
            'checker':'independent standard-library RUP/RAT checker'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('ring',choices=['Z4','D2']);ap.add_argument('n',type=int);ap.add_argument('bound',type=int)
    ap.add_argument('--seconds',type=float,default=120);ap.add_argument('--prefix',type=Path,required=True)
    ap.add_argument('--verify',action='store_true');a=ap.parse_args()
    out=decide(a.ring,a.n,a.bound,a.prefix,a.seconds)
    if a.verify and out['status']=='UNSAT':out['proof_check']=verify_drat(str(a.prefix)+'.cnf',str(a.prefix)+'.drat')
    Path(str(a.prefix)+'.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()
