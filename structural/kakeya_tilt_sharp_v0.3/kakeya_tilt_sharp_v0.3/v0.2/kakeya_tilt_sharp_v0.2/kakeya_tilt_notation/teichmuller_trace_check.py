import itertools
def run(p, mixed, n=2):
    q=p*p
    if mixed:
        add=lambda x,y:(x+y)%q; mul=lambda x,y:(x*y)%q
        tau=lambda a:pow(a,p,q); pi=p
        res=lambda x:x%p; dig=lambda x:((x-tau(x%p))%q)//p   # x = tau(a)+p*b
        gam=lambda x,y:((tau(x)+tau(y)-tau((x+y)%p))%q)//p
    else:
        enc=lambda a,b:a%p+p*(b%p); dec=lambda x:(x%p,x//p)
        add=lambda x,y:enc(dec(x)[0]+dec(y)[0],dec(x)[1]+dec(y)[1])
        mul=lambda x,y:enc(dec(x)[0]*dec(y)[0],dec(x)[0]*dec(y)[1]+dec(x)[1]*dec(y)[0])
        res=lambda x:x%p; dig=lambda x:x//p; gam=lambda x,y:0
    bad=0;tot=0
    for x in itertools.product(range(q),repeat=n):
      for v in itertools.product(range(q),repeat=n):
        al=tuple(res(c) for c in v)
        if not any(al): continue
        a=tuple(res(c) for c in x); b=tuple(dig(c) for c in x); be=tuple(dig(c) for c in v)
        L=[tuple(add(x[i],mul(s,v[i])) for i in range(n)) for s in range(q)]
        for sg in range(p):
            fib={tuple(dig(c) for c in y) for y in L if tuple(res(c) for c in y)==tuple((a[i]+sg*al[i])%p for i in range(n))}
            base=tuple((b[i]+sg*be[i]+gam(a[i],sg*al[i]%p))%p for i in range(n))
            pred={tuple((base[i]+r*al[i])%p for i in range(n)) for r in range(p)}
            tot+=1; bad+= fib!=pred
    return tot,bad
for p in (2,3,5):
    for m in (True,False): print(p,'Z/p^2' if m else 'gr',run(p,m))
