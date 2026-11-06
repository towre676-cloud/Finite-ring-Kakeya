from pathlib import Path
import json,math
HERE=Path(__file__).resolve().parent

def rank(vs):
    bs={}
    for v in vs:
        while v:
            b=v.bit_length()-1
            if b in bs:v^=bs[b]
            else:bs[b]=v;break
    return len(bs)

def energy(A,N=16):
    S=set(A)
    return sum(sum(x^d in S for x in S)**2 for d in range(N))

count=0;mx9other=0;mx10=0
for mask in range(1<<16):
    w=mask.bit_count()
    if w not in(9,10):continue
    A=[x for x in range(16) if mask>>x&1];B=[x for x in range(16) if not(mask>>x&1)]
    E=energy(A);r=rank([x^A[0] for x in A]);assert r==4
    if w==9:
        cubeplus=rank([x^B[0] for x in B])==3
        if cubeplus:assert E==561
        else:assert E<=465;mx9other=max(mx9other,E)
    else:assert E<=712;mx10=max(mx10,E)
    count+=1

def g(n):return 8*n*n if n<=8 else 8*n*n-96*n+768
for a in range(12):
    for b in range(12-a):assert g(a)+g(b)<=g(a+b)
for a,b,c in [(465,712,618),(344,1061,618),(465,1061,712),(344,1464,712)]:assert a*b<c*c
att=[]
for p,q,h in[(9,10,618),(10,10,712)]:
    A=set(range(p))|{16+x for x in range(q)}
    H=sum((sum(x^d in A for x in A)//2)**2 for d in range(16,32))
    assert H==h
    att.append({'weight':p+q,'split':[p,q],'halfspace_energy':H,'set':sorted(A)})
r={'status':'PASS','nine_and_ten_point_subsets_of_F2_4_checked':count,'nine_point_non_cube_plus_point_maximum_in_F2_4':mx9other,'ten_point_maximum_in_F2_4':mx10,'new_attainments':att,'scope':'Exact finite controls corroborate the arbitrary-dimensional analytic proof.'}
(HERE/'STABILITY_HALFSPACE20_CONTROLS.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
