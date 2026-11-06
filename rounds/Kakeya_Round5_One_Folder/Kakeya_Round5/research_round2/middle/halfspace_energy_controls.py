from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent
N=16
mx={w:0 for w in (6,7,8,9,10)}
nonflat8=0; noncube9=0
checked=0
for mask in range(1<<N):
    w=mask.bit_count()
    if w not in mx:continue
    A=[x for x in range(N) if mask>>x&1]
    p=[sum(bool(mask>>(x^d)&1) for x in A)//2 for d in range(1,N)]
    E=w*w+4*sum(t*t for t in p)
    Z=sum(1 for i,a in enumerate(A) for j in range(i+1,w) for k in range(j+1,w)
          if (a^A[j]^A[k])>A[k] and mask>>(a^A[j]^A[k])&1)
    assert sum(t*t for t in p)==w*(w-1)//2+6*Z
    mx[w]=max(mx[w],E);checked+=1
    if w==6:assert E<=168
    if w==7:assert E<=301
    if w==8:
        cube=sum(t==4 for t in p)==7
        if not cube:nonflat8=max(nonflat8,E);assert E<=344
    if w==9:
        H=[0]+[d for d in range(1,N) if p[d-1]==4]
        assert all((a^b) in H for a in H for b in H)
        cubeplus=sum(t==4 for t in p)==7
        if len(H)>=4:assert cubeplus and E==561
        if not cubeplus:noncube9=max(noncube9,E);assert E<=529
        assert E<=561
    if w==10:assert E<=840
attain=[]
for w,p,q,h in [(13,6,7,222),(14,7,7,301),(15,7,8,392),(16,8,8,512),(17,8,9,520),(18,9,9,561)]:
    A=set(range(p))|{16+x for x in range(q)}
    energy=sum((sum((x^d) in A for x in A)//2)**2 for d in range(16,32))
    assert len(A)==w and energy==h
    attain.append({'weight':w,'split':[p,q],'value':energy,'set':sorted(A),'character_bit':16})
result={'status':'PASS','subsets_checked':checked,'actual_F2_4_max_additive_energies':mx,'nonflat8_max_in_F2_4':nonflat8,'noncubepluspoint9_max_in_F2_4':noncube9,'attainment':attain,'scope':'Finite controls corroborate analytic arbitrary-dimensional proofs; no finite test substitutes for the proofs.'}
(ROOT/'HALFSPACE_ENERGY_CONTROLS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
