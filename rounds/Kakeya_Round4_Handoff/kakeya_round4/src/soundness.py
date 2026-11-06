"""Soundness test: actual Kakeya sets in (Z/4)^5 and (F2[e]/e^2)^5 must satisfy the CNF with their true data fixed."""
import random, sys, itertools
import encode_cnf2 as E
from pysat.solvers import Solver
SPEC=E.load_spectra('../spec32.csv'); M=E.load_M('../Mtable.txt'); SUBS=E.all_subspaces()
N=5
def ops(ring):
    if ring=='z4':
        add=lambda x,y: tuple((a+b)%4 for a,b in zip(x,y)); smul=lambda t,x: tuple((t*a)%4 for a in x)
        neg=lambda x: tuple((-a)%4 for a in x)
    else:
        add=lambda x,y: tuple(a^b for a,b in zip(x,y))
        def m1(t,a):
            t0,t1=t&1,t>>1; a0,a1=a&1,a>>1
            return (t0&a0)|(((t0&a1)^(t1&a0))<<1)
        smul=lambda t,x: tuple(m1(t,a) for a in x); neg=lambda x:x
    return add,smul,neg
def lines_by_dir(ring):
    add,smul,neg=ops(ring)
    pts=list(itertools.product(range(4),repeat=N))
    dirs={}
    for d in pts:
        if all(c%2==0 for c in d): continue
        key=min(d,smul(3 if ring=='z4' else 3,d))
        dirs[key]=1
    L={}
    for D in dirs:
        L[D]=[frozenset(add(a,smul(t,D)) for t in range(4)) for a in pts]
    return pts,L
def is_kakeya(K,L):
    return all(any(l<=K for l in ls) for ls in L.values())
def res(p): return sum((p[i]&1)<<i for i in range(N))
def tan(p): return sum(((p[i]>>1)&1)<<i for i in range(N))
def test(K,ring,L):
    add,smul,neg=ops(ring)
    fib={}
    for p in K: fib.setdefault(res(p),set()).add(tan(p))
    # drop singletons
    K={p for p in K if len(fib[res(p)])>=2}
    assert is_kakeya(K,L)
    fib={}
    for p in K: fib.setdefault(res(p),set()).add(tan(p))
    r0=max(fib,key=lambda r:len(fib[r]))
    lift=tuple((r0>>i)&1 for i in range(N))
    K2={add(p,neg(lift)) for p in K}
    assert is_kakeya(K2,L)
    fib={}
    for p in K2: fib.setdefault(res(p),set()).add(tan(p))
    m=len(fib[0]); T=sorted(r for r in fib if r)
    E.TOTAL=len(K2)
    f=E.encode(T,m,SPEC,M,SUBS)
    def pc(A,d): return sum(1 for x in A if x^d in A)//2
    assum=[]
    for v in [0]+T:
        A=fib[v]; hist=[0]*17
        for d in range(1,32): hist[pc(A,d)]+=1
        zi=[i for i,sv in enumerate(SPEC) if sv[0]==len(A) and sv[1]==hist]
        assert len(zi)==1,(len(A),hist)
        assum.append(f.z[v,zi[0]])
        for b in [0]+T:
            if b!=v: assum.append(f.y[v,v^b,pc(A,v^b)])
    with Solver(name='cadical195',bootstrap_with=f.cl) as s:
        ok=s.solve(assumptions=assum)
    return ok,m,len(T)+1,len(K2)
random.seed(int(sys.argv[2]) if len(sys.argv)>2 else 0)
ring=sys.argv[1]
pts,L=lines_by_dir(ring)
# star
star=set()
for p in pts:
    if res(p)==0: star.add(p)
for r in range(1,32):
    d=tuple((r>>i)&1 for i in range(N))
    star.add(d); star.add(add_:=ops(ring)[0](d,ops(ring)[1](2,d)) if ring=='z4' else ops(ring)[0](d,tuple(2*((r>>i)&1) for i in range(N))))
print('star',len(star),is_kakeya(star,L),test(star,ring,L),flush=True)
for trial in range(int(sys.argv[3]) if len(sys.argv)>3 else 4):
    # random greedy minimal Kakeya set from a random line selection
    K=set()
    for D,ls in L.items(): K|=random.choice(ls)
    order=list(K); random.shuffle(order)
    for p in order:
        K.discard(p)
        if not is_kakeya(K,L): K.add(p)
    print('greedy',len(K),test(K,ring,L),flush=True)

def from_support(ring,T,hub,total,L,seed=0):
    """Point-level SAT: a Kakeya set with fibres only over {0}+T, hub weight exactly `hub`, size<=total."""
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool
    pool=IDPool(); S=[0]+T
    X={}
    for p in L[next(iter(L))][0] if False else []: pass
    allpts=set()
    for ls in L.values():
        for l in ls: allpts|=l
    for p in allpts:
        if res(p) in S: X[p]=pool.id(('x',p))
    cl=[]
    for D,ls in L.items():
        ys=[]
        for l in ls:
            if all(p in X for p in l):
                y=pool.id(('y',l)); ys.append(y)
                for p in l: cl.append([-y,X[p]])
        cl.append(ys)
    cl+=CardEnc.atmost(list(X.values()),bound=total,vpool=pool,encoding=EncType.totalizer).clauses
    cl+=CardEnc.equals([X[p] for p in X if res(p)==0],bound=hub,vpool=pool,encoding=EncType.totalizer).clauses
    for r in T: cl+=CardEnc.atmost([X[p] for p in X if res(p)==r],bound=hub,vpool=pool,encoding=EncType.totalizer).clauses
    with Solver(name='cadical195',bootstrap_with=cl) as s:
        if not s.solve(): return None
        mdl=set(l for l in s.get_model() if l>0)
    return {p for p in X if X[p] in mdl}
