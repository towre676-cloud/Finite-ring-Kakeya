// Independent census of pair-spectrum histograms for all subsets of F2^5 of weight w<=19.
// Method: every subset is affinely equivalent to one containing 0 and lying in span with basis e1..er among its points;
// we instead enumerate by orbit-free brute force over weights<=16 via normalized sets containing {0,e1,..,er} inside F2^r coords,
// and weights>=17 via complement. Histogram counts directions d!=0 by p(d)=|A cap (A+d)|/2.
#include <bits/stdc++.h>
using namespace std; typedef unsigned u32;
set<vector<int>> H[33];
int rk(u32 A){ int x0=__builtin_ctz(A); vector<int> b; for(int x=0;x<32;x++) if(A>>x&1){int v=x^x0; for(int y:b) v=min(v,v^y); if(v) b.push_back(v);} return b.size(); }
void record(u32 A){
    int w=__builtin_popcount(A); vector<int> h(17,0);
    for(int d=1;d<32;d++){ u32 B=0; for(int x=0;x<32;x++) if(A>>x&1) B|=1u<<(x^d); h[__builtin_popcount(A&B)/2]++; }
    h.push_back(rk(A)); H[w].insert(h);
    // complement
    u32 C=~A; int wc=32-w; vector<int> hc(17,0);
    for(int d=1;d<32;d++){ u32 B=0; for(int x=0;x<32;x++) if(C>>x&1) B|=1u<<(x^d); hc[__builtin_popcount(C&B)/2]++; }
    hc.push_back(rk(C)); H[wc].insert(hc);
}
int main(){
    // rank r subsets: contain 0,e1..er (bits 1<<0 for 0? element x has bit (1u<<x)); live in {0..2^r-1}
    for(int r=0;r<=5;r++){
        int sz=1<<r; u32 base=1u; for(int i=0;i<r;i++) base|=1u<<(1<<i);
        vector<int> rest; for(int x=1;x<sz;x++) if(__builtin_popcount(x)>1) rest.push_back(x);
        int m=rest.size();
        for(u32 sub=0; sub<(1u<<m); sub++){
            int w=r+1+__builtin_popcount(sub); if(w>16) continue;
            u32 A=base; for(int i=0;i<m;i++) if(sub>>i&1) A|=1u<<rest[i];
            record(A);
        }
    }
    { u32 A=0xffffffffu; vector<int> h(17,0); h[16]=31; h.push_back(5); H[32].insert(h); }
    for(int w=1;w<=32;w++) for(auto&h:H[w]){ printf("%d",w); for(int v=0;v<=16;v++) printf(",%d",h[v]); printf(",%d\n",h[17]); }
}
