import random, subprocess, sys
from pysat.solvers import Solver
random.seed(int(sys.argv[1])); bad=0; tested=0; pos=0
for it in range(int(sys.argv[2])):
    n=random.randint(30,70); m=int(n*random.uniform(4.4,5.5))
    F=[[random.choice([1,-1])*v for v in random.sample(range(1,n+1),3)] for _ in range(m)]
    s=Solver(name='cadical195',with_proof=True,bootstrap_with=F)
    if s.solve(): continue
    P=s.get_proof()
    open('fuzz/p.drat','w').write('\n'.join(P)+'\n')
    def wr(G):
        open('fuzz/f.cnf','w').write(f'p cnf {n} {len(G)}\n'+''.join(' '.join(map(str,c))+' 0\n' for c in G))
    wr(F)
    for chk in ('./dratcheck','./dratback'):
        r=subprocess.run([chk,'fuzz/f.cnf','fuzz/p.drat'],capture_output=True,text=True).stdout
        if not r.startswith('s VERIFIED'): print('FALSE NEGATIVE',chk,it); 
        else: pos+=1
    # weaken
    for k in range(5):
        G=[c for c in F if random.random()>0.08]
        with Solver(name='minisat22' if False else 'glucose4',bootstrap_with=G) as t:
            if not t.solve(): continue
        wr(G); tested+=1
        for chk in ('./dratcheck','./dratback'):
            r=subprocess.run([chk,'fuzz/f.cnf','fuzz/p.drat'],capture_output=True,text=True).stdout
            if r.startswith('s VERIFIED'): print('UNSOUND',chk,it,k); bad+=1
print('positive ok',pos,'sat-weakened tests',tested,'unsound',bad)
