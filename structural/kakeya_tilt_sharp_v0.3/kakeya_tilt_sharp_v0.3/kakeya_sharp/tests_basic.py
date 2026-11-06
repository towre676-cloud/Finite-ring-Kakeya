import random, sys
sys.path.insert(0,'.')
from kakeya_sharp.rings import *
for n in range(1,6):
    for R in RINGS:
        K=K_star(n)
        print(n,R,len(K),3*2**n-2,is_kakeya(R,K,n),covers_via_fibre_identity(R,K,n))
# equivalence on random / perturbed sets
random.seed(1)
bad=0;tot=0
for n in (2,3):
  for R in RINGS:
    pts=list(all_points(n))
    for trial in range(3000):
        k=random.randint(3*2**n-6, min(len(pts),3*2**n+10))
        K=set(random.sample(pts,k)) if trial%2 else (K_star(n)-set(random.sample(sorted(K_star(n)),random.randint(0,2)))|set(random.sample(pts,random.randint(0,4))))
        a=is_kakeya(R,K,n); b=covers_via_fibre_identity(R,K,n); tot+=1
        if a!=b: bad+=1
print("fibre-identity mismatches",bad,"of",tot)
