// exact max |X+Y| over X,Y subsets of F2^4 with |X|=p,|Y|=q (p<=q), p,q in 0..16
#include <bits/stdc++.h>
using namespace std; typedef unsigned u32;
int M[17][17];
int main(){
    for(int r=0;r<=4;r++){
        int sz=1<<r; u32 base=1; for(int i=0;i<r;i++) base|=1u<<(1<<i);
        vector<int> rest; for(int x=1;x<sz;x++) if(__builtin_popcount(x)>1) rest.push_back(x);
        for(u32 sub=0;sub<(1u<<rest.size());sub++){
            u32 X=base; for(size_t i=0;i<rest.size();i++) if(sub>>i&1) X|=1u<<rest[i];
            int p=__builtin_popcount(X);
            vector<int> xs; for(int x=0;x<16;x++) if(X>>x&1) xs.push_back(x);
            for(u32 Y=1;Y<65536;Y++){ u32 Z=0; for(int x:xs){ // shift Y by x
                    u32 sh=0; for(int y=0;y<16;y++) if(Y>>y&1) sh|=1u<<(y^x); Z|=sh;}
                int q=__builtin_popcount(Y), z=__builtin_popcount(Z); if(z>M[p][q]) M[p][q]=z; }
        }
    }
    for(int p=1;p<=16;p++){ for(int q=1;q<=16;q++){ int mm=max(M[p][q],M[q][p]); printf("%d ",mm);} printf("\n"); }
}
