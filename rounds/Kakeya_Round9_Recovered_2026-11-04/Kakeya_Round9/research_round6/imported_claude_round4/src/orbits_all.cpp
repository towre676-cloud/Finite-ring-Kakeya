// GL_5(F2)-orbits of spanning sets T of nonzero vectors of F2^5, all sizes 5..31.
// Canonical form: min image mask over ordered bases b chosen from T, where at each step the candidate set is
// {x in T \ span(prefix) with minimal invariant inv(x)}; inv is GL-invariant w.r.t. T, so explored tuple set is equivariant.
// Outputs per size: orbit count, stabilizer orders (for orbit-stabilizer check), covering flag, canonical mask.
#include <bits/stdc++.h>
using namespace std; typedef unsigned u32; typedef unsigned long long u64;
static int inv[32];
static u32 Tg; static vector<int> v; static u32 best; static long cnt;
static int B[5];
static void rec(int depth,u32 spanmask){
    if(depth==5){
        int vec[32]; vec[0]=0;
        for(int m=1;m<32;m++){int low=__builtin_ctz(m); vec[m]=vec[m^(1<<low)]^B[low];}
        int img[32]; for(int m=0;m<32;m++) img[vec[m]]=m;
        u32 im=0; for(int x:v) im|=1u<<img[x];
        if(im<best){best=im;cnt=1;} else if(im==best) cnt++;
        return;
    }
    int mn=INT_MAX; for(int x:v) if(!(spanmask>>x&1)) mn=min(mn,inv[x]);
    for(int x:v){ if((spanmask>>x&1)||inv[x]!=mn) continue;
        B[depth]=x; u32 ns=spanmask; for(int y=0;y<32;y++) if(spanmask>>y&1) ns|=1u<<(y^x);
        rec(depth+1,ns);
    }
}
pair<u32,long> canon(u32 T){
    v.clear(); for(int i=1;i<32;i++) if(T>>i&1) v.push_back(i);
    // invariant: (#{y in T: x^y in T}, #{y notin T, y!=0: x^y in T}) combined; plus second-order sum
    int a[32]={0};
    for(int x:v){ int c=0; for(int y:v) if(y!=x && (T>>(x^y)&1)) c++; a[x]=c; }
    for(int x:v){ long s=0; for(int y:v) if(y!=x && (T>>(x^y)&1)) s+=a[y]*a[x^y]+a[y]+a[x^y]; inv[x]=a[x]*100000+(int)(s%100000); }
    best=~0u; cnt=0; rec(0,1u); return {best,cnt};
}
int main(){
    set<u32> cur; cur.insert(canon((1u<<1)|(1u<<2)|(1u<<4)|(1u<<8)|(1u<<16)).first);
    map<u32,long> stab; stab[*cur.begin()]=canon(*cur.begin()).second;
    auto dump=[&](int k){
        long GL=9999360; __int128 sum=0; int cov=0;
        for(u32 T:cur){ auto pr=canon(T); assert(pr.first==T); sum+=GL/pr.second;
            u32 S=T|1u, D=0; for(int a=0;a<32;a++) if(S>>a&1) for(int c=0;c<32;c++) if(S>>c&1) D|=1u<<(a^c);
            bool c=(D==0xffffffffu); cov+=c; printf("%d %u %ld %d\n",k,T,pr.second,(int)c); }
        fprintf(stderr,"k=%d orbits=%zu covering=%d spanning_sets=%lld\n",k,cur.size(),cov,(long long)sum);
    };
    dump(5);
    for(int k=5;k<31;k++){
        set<u32> nxt;
        for(u32 T:cur) for(int x=1;x<32;x++) if(!(T>>x&1)) nxt.insert(canon(T|1u<<x).first);
        cur=nxt; dump(k+1);
    }
}
