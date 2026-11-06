import sys, time
from soundness import *
ring=sys.argv[1]
pts,L=lines_by_dir(ring)
for line in open('../T11.txt').read().split()[:int(sys.argv[2])]:
    T=[x for x in range(1,32) if int(line)>>x&1]
    for total in (150,):
        t=time.time(); K=from_support(ring,T,19,total,L)
        if K is None: print(line,total,'no set'); continue
        print(line,len(K),round(time.time()-t,1),test(K,ring,L),flush=True)
