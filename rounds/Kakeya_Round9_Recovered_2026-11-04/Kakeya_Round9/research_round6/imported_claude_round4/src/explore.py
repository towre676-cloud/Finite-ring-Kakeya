"""Exploration (no proofs): solve per (m, orbit) CNF with CaDiCaL; record SAT/UNSAT and a model summary if SAT.
usage: explore.py m1,m2 smin smax out.jsonl [timeout]"""
import sys, os, json, time, multiprocessing as mp
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import encode_cnf2 as E
from pysat.solvers import Solver
SPEC=E.load_spectra(HERE+'/../spec32.csv'); M=E.load_M(HERE+'/../Mtable.txt'); SUBS=E.all_subspaces()
def work(a):
    m,s,Tm=a; T=[x for x in range(1,32) if Tm>>x&1]
    t=time.time(); f=E.encode(T,m,SPEC,M,SUBS)
    with Solver(name='cadical195',bootstrap_with=f.cl) as sv:
        r=sv.solve(); mdl=sv.get_model() if r else None
    rec={'m':m,'s':s,'T':Tm,'sat':r,'sec':round(time.time()-t,1),'clauses':len(f.cl)}
    if r:
        pos=set(l for l in mdl if l>0)
        rec['w']={str(v):SPEC[i][0] for (v,i),var in f.z.items() if var in pos}
    return rec
if __name__=='__main__':
    ms=[int(x) for x in sys.argv[1].split(',')]; kmin,kmax=int(sys.argv[2]),int(sys.argv[3]); outp=sys.argv[4]
    done=set()
    if os.path.exists(outp):
        for l in open(outp): r=json.loads(l); done.add((r['m'],r['T']))
    jobs=[]
    for l in open(HERE+'/../orbits_all.txt'):
        k,T,st,cov=map(int,l.split()); s=k+1
        if not cov or not(kmin<=s<=kmax): continue
        for m in ms:
            if (m,T) in done or 2*(s-1)>93-m: continue
            jobs.append((m,s,T))
    print(len(jobs),'jobs',flush=True)
    with mp.Pool(int(os.environ.get('NPROC','4'))) as pool, open(outp,'a') as f:
        for r in pool.imap_unordered(work,jobs):
            f.write(json.dumps(r)+'\n'); f.flush()
            print(r['m'],r['s'],r['T'],'SAT' if r['sat'] else 'UNSAT',r['sec'],r.get('w',''),flush=True)
