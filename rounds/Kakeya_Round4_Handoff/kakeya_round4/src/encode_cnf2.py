"""Independent CNF encoding of the per-support necessary conditions (written separately from the CP-SAT model).

Instance: hub weight m at residue 0, pair-active support S={0} u T, outer weights in [2,m], outer total <= 93-m.
Constraints (all necessary for an actual Kakeya set over Z/4Z or F2[e]/(e^2) in dimension 5):
  (A) each fibre realises one census pair spectrum; incident directional pair counts form a sub-multiset of it;
  (B) edge {a,b} with d=a+b covers at most Mtab[p_a(d)][p_b(d)] lifted directions;
  (C) every nonzero residue direction is covered 16 times in total;
  (D) positive-count directions lie in the linear direction space H of the affine hull, dim H = affine rank;
      if the spectrum has 2^r-1 positive directions with rank r, they are exactly H minus 0;
  (E) the maximal-pair directions together with 0 form a subspace K with |K|-1 = number of maximal directions.
"""
import itertools, sys
from collections import defaultdict

def load_spectra(path):
    rk=defaultdict(set)
    for line in open(path):
        a=list(map(int,line.split(','))); rk[tuple(a[:-1])].add(a[-1])
    return [(k[0],list(k[1:]),min(v),max(v)) for k,v in sorted(rk.items())]

def load_M(path):
    rows=[list(map(int,l.split())) for l in open(path)]
    M=[[0]*17 for _ in range(17)]
    for p in range(1,17):
        for q in range(1,17): M[p][q]=rows[p-1][q-1]
    return M

def all_subspaces():
    out=set()
    for k in range(6):
        for g in itertools.combinations(range(1,32),k):
            s={0}
            for x in g: s|={y^x for y in s}
            out.add(frozenset(s))
    return sorted(out,key=lambda s:(len(s),sorted(s)))

class CNF:
    def __init__(s): s.n=0; s.cl=[]
    def new(s): s.n+=1; return s.n
    def add(s,c): s.cl.append(list(c))
    def exactly_one(s,lits):
        s.add(lits)
        if len(lits)<=6:
            for a,b in itertools.combinations(lits,2): s.add([-a,-b])
            return
        # sequential at-most-one: p_i <-> some of lits[0..i] is true
        p=[s.new() for _ in lits]
        for i,l in enumerate(lits):
            s.add([-l,p[i]])
            if i: s.add([-p[i-1],p[i]]); s.add([-l,-p[i-1]])
    def unary_sum(s,lits):
        """Totalizer: returns o[0..n-1] with o[j] <-> (count >= j+1)."""
        if len(lits)==0: return []
        if len(lits)==1: return [lits[0]]
        h=len(lits)//2
        A=s.unary_sum(lits[:h]); B=s.unary_sum(lits[h:])
        O=[s.new() for _ in range(len(A)+len(B))]
        for i in range(len(A)+1):
            for j in range(len(B)+1):
                if i+j>0:   # A>=i & B>=j -> O>=i+j
                    s.add(([-A[i-1]] if i else [])+([-B[j-1]] if j else [])+[O[i+j-1]])
                if i+j<len(O):  # A<i+1 & B<j+1 -> O<i+j+1
                    s.add(([A[i]] if i<len(A) else [])+([B[j]] if j<len(B) else [])+[-O[i+j]])
        return O

TOTAL=93
def encode(T, m, SPEC, M, SUBS, outtotal=None):
    if outtotal is None: outtotal=TOTAL-m
    S=[0]+list(T); Sset=set(S)
    f=CNF()
    D={v:[v^b for b in S if b!=v] for v in S}
    z={}; y={}
    for v in S:
        ws=[m] if v==0 else list(range(2,m+1))
        sp=[i for i,sv in enumerate(SPEC) if sv[0] in ws]
        for i in sp: z[v,i]=f.new()
        f.exactly_one([z[v,i] for i in sp])
        K=max(k for i in sp for k in range(17) if SPEC[i][1][k])
        for d in D[v]:
            for k in range(K+1): y[v,d,k]=f.new()
            f.exactly_one([y[v,d,k] for k in range(K+1)])
        # (A) sub-multiset
        for k in range(K+1):
            O=f.unary_sum([y[v,d,k] for d in D[v]])
            for i in sp:
                c=SPEC[i][1][k]
                if c<len(O): f.add([-z[v,i],-O[c]])
        # (D) direction space
        h={H:f.new() for H in SUBS}
        f.exactly_one(list(h.values()))
        fullv=f.new(); fulls=[]
        for i in sp:
            w,hist,r0,r1=SPEC[i]
            f.add([-z[v,i]]+[h[H] for H in SUBS if r0<=len(H).bit_length()-1<=r1])
            if r0==r1 and 31-hist[0]==2**r0-1: fulls.append(z[v,i])
        f.add([-fullv]+fulls)
        for l in fulls: f.add([-l,fullv])
        for d in D[v]:
            f.add([y[v,d,0]]+[h[H] for H in SUBS if d in H])
            for H in SUBS:
                if d in H: f.add([-fullv,-h[H],-y[v,d,0]])
        # (E) maximal-pair subspace
        kk={H:f.new() for H in SUBS}
        f.exactly_one(list(kk.values()))
        tops=defaultdict(list)
        for i in sp:
            w,hist,r0,r1=SPEC[i]; t=w//2; c=hist[t]
            assert (c+1)&c==0
            f.add([-z[v,i]]+[kk[H] for H in kk if len(H)==c+1])
            tops[t].append(z[v,i])
        for t,zs in tops.items():
            tv=f.new(); f.add([-tv]+zs)
            for l in zs: f.add([-l,tv])
            for d in D[v]:
                if (v,d,t) in y:
                    f.add([-tv,-y[v,d,t]]+[kk[H] for H in kk if d in H])
                    for H in kk:
                        if d in H: f.add([-tv,-kk[H],y[v,d,t]])
                else:
                    for H in kk:
                        if d in H: f.add([-tv,-kk[H]])
    # weight budget
    bits=[]
    for v in T:
        for j in range(1,m+1):
            u=f.new(); bits.append(u)
            ok=[z[v,i] for (vv,i) in z if vv==v and SPEC[i][0]>=j]
            # u <-> OR ok
            f.add([-u]+ok)
            for l in ok: f.add([-l,u])
    O=f.unary_sum(bits)
    if outtotal<len(O): f.add([-O[outtotal]])
    # (B),(C)
    cov=defaultdict(list)
    for a,b in itertools.combinations(S,2):
        d=a^b
        cbits=[f.new() for _ in range(16)]
        for j in range(15): f.add([-cbits[j+1],cbits[j]])
        Ka=[k for k in range(17) if (a,d,k) in y]; Kb=[k for k in range(17) if (b,d,k) in y]
        for i in Ka:
            for i2 in Kb:
                cap=M[i][i2]
                if cap<16: f.add([-cbits[cap],-y[a,d,i],-y[b,d,i2]])
        cov[d]+=cbits
    for d in range(1,32):
        O=f.unary_sum(cov[d])
        if len(O)<16: f.add([])
        else: f.add([O[15]])
    f.z=z; f.y=y
    return f

def write_dimacs(f,path):
    with open(path,'w') as o:
        o.write(f'p cnf {f.n} {len(f.cl)}\n')
        for c in f.cl: o.write(' '.join(map(str,c))+' 0\n')
