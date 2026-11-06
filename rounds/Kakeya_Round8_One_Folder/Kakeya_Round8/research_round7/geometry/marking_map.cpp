// Canonicalize a spanning nonzero binary 5-space subset and print a witness.
// The equivariant invariant and basis restriction are the same as the
// imported complete catalogue. The emitted map is checked independently.
#include <bits/stdc++.h>
using namespace std;
using U = uint32_t;
vector<int> points;
int invv[32], basis[5], best_map[32];
U best;
void visit(int depth, U span) {
    if (depth == 5) {
        int vec[32] = {}, inverse[32];
        for (int m=1; m<32; ++m) {
            int k=__builtin_ctz(unsigned(m));
            vec[m]=vec[m^(1<<k)]^basis[k];
        }
        for (int m=0;m<32;++m) inverse[vec[m]]=m;
        U image=0;
        for (int x:points) image |= U(1)<<inverse[x];
        if(image < best) {
            best=image;
            copy(inverse,inverse+32,best_map);
        }
        return;
    }
    int minimum=INT_MAX;
    for(int x:points) if(!(span>>x&1)) minimum=min(minimum,invv[x]);
    for(int x:points) {
        if((span>>x&1)||invv[x]!=minimum) continue;
        basis[depth]=x;
        U larger=span;
        for(int y=0;y<32;++y) if(span>>y&1) larger|=U(1)<<(x^y);
        visit(depth+1,larger);
    }
}
int main() {
    unsigned long long input;
    while(cin>>input) {
        U mask=U(input); points.clear(); int a[32]={};
        for(int i=1;i<32;++i) if(mask>>i&1) points.push_back(i);
        for(int x:points) for(int y:points)
            if(x!=y && (mask>>(x^y)&1)) ++a[x];
        for(int x:points) {
            long s=0;
            for(int y:points) if(x!=y && (mask>>(x^y)&1))
                s+=a[y]*a[x^y]+a[y]+a[x^y];
            invv[x]=a[x]*100000+int(s%100000);
        }
        best=~U(0); visit(0,1);
        if(best==~U(0)) return 2;
        cout<<input<<' '<<best;
        for(int i=0;i<5;++i) cout<<' '<<best_map[1<<i];
        cout<<'\n';
    }
}
