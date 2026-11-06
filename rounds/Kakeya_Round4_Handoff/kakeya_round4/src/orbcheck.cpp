// independent check: canonicalize every normalized covering set {0,e1..e5}+X and count; also orbit-stabilizer sum
#include <bits/stdc++.h>
using namespace std; typedef unsigned u32;
// canonical: min over all ordered bases from T of image; also count bases attaining min (=|Stab|)
pair<u32,long> canon(u32 T){
    vector<int> v; for(int i=1;i<32;i++) if(T>>i&1) v.push_back(i);
    u32 best=~0u; long cnt=0;
    for(int a:v)for(int b:v)for(int c:v)for(int d:v)for(int e:v){
        int B[5]={a,b,c,d,e}; int vec[32]; vec[0]=0;
        for(int m=1;m<32;m++){int low=__builtin_ctz(m); vec[m]=vec[m^(1<<low)]^B[low];}
        bool ok=true; bool seen[32]={0}; for(int m=0;m<32;m++){ if(seen[vec[m]]){ok=false;break;} seen[vec[m]]=1;}
        if(!ok) continue;
        int img[32]; for(int m=0;m<32;m++) img[vec[m]]=m;
        u32 im=0; for(int x:v) im|=1u<<img[x];
        if(im<best){best=im;cnt=1;} else if(im==best) cnt++;
    }
    return {best,cnt};
}
int main(int argc,char**argv){
    int s=atoi(argv[1]); // support size incl 0
    vector<int> rest; for(int x=1;x<32;x++) if(__builtin_popcount(x)!=1) rest.push_back(x);
    int need=s-6; long total=0,cov=0; map<u32,long> cnt; map<u32,long> stab;
    vector<int> idx(need); for(int i=0;i<need;i++) idx[i]=i;
    while(true){
        u32 T=(1u<<1)|(1u<<2)|(1u<<4)|(1u<<8)|(1u<<16); for(int i:idx) T|=1u<<rest[i];
        total++;
        u32 S=T|1u, D=0; for(int a=0;a<32;a++) if(S>>a&1) for(int c=0;c<32;c++) if(S>>c&1) D|=1u<<(a^c);
        if(D==0xffffffffu){ cov++; auto pr=canon(T); cnt[pr.first]++; stab[pr.first]=pr.second; }
        int i=need-1; while(i>=0 && idx[i]==(int)rest.size()-need+i) i--; if(i<0) break; idx[i]++; for(int j=i+1;j<need;j++) idx[j]=idx[j-1]+1;
    }
    printf("s=%d normalized=%ld covering=%ld orbits=%zu\n",s,total,cov,cnt.size());
    long GL=9999360; long sumorb=0;
    for(auto&kv:cnt){ printf("%u stab=%ld orbitsize=%ld normalized_hits=%ld\n",kv.first,stab[kv.first],GL/stab[kv.first],kv.second); sumorb+=GL/stab[kv.first];}
    printf("sum orbit sizes=%ld\n",sumorb);
}
