import sys, time, json, hashlib, os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from encode_cnf2 import *
from pysat.solvers import Solver
W=os.path.dirname(os.path.abspath(__file__))+'/..'
SPEC=load_spectra(W+'/spec32.csv'); M=load_M(W+'/Mtable.txt'); SUBS=all_subspaces()
m=int(sys.argv[1]); Tm=int(sys.argv[2]); outdir=sys.argv[3]
T=[x for x in range(1,32) if Tm>>x&1]
t=time.time(); f=encode(T,m,SPEC,M,SUBS); te=time.time()-t
base=f'{outdir}/m{m}_T{Tm}'
write_dimacs(f,base+'.cnf')
s=Solver(name='cadical195',with_proof=True,bootstrap_with=f.cl)
t=time.time(); r=s.solve(); ts=time.time()-t
if not r:
    with open(base+'.drat','w') as o: o.write('\n'.join(s.get_proof())+'\n')
print(json.dumps({'m':m,'T':Tm,'vars':f.n,'clauses':len(f.cl),'sat':r,'enc_sec':round(te,1),'solve_sec':round(ts,1)}),flush=True)
