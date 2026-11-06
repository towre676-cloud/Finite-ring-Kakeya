#include <array>
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <set>
#include <vector>
using H=std::array<unsigned char,10>;
std::array<std::set<H>,20> census;
std::array<uint64_t,6> visits{};
std::vector<int> pts,opt;
int rank_now;
void visit(int next){
 ++visits[rank_now];
 std::array<int,32> pc{};
 for(size_t i=0;i<pts.size();++i)for(size_t j=0;j<i;++j)++pc[pts[i]^pts[j]];
 H h{};for(int d=1;d<32;++d)++h[pc[d]];
 census[pts.size()].insert(h);
 if(pts.size()==16)return;
 for(int i=next;i<(int)opt.size();++i){pts.push_back(opt[i]);visit(i+1);pts.pop_back();}
}
int main(int argc,char**argv){
 if(argc!=2)return 2;
 for(int r=0;r<=5;++r){rank_now=r;pts={0};opt.clear();for(int k=0;k<r;++k)pts.push_back(1<<k);for(int v=1;v<(1<<r);++v)if(std::find(pts.begin(),pts.end(),v)==pts.end())opt.push_back(v);visit(0);}
 for(int w=17;w<=19;++w)for(auto h:census[32-w]){H c{};for(int p=0;p<10;++p)if(h[p])c[p+w-16]=h[p];census[w].insert(c);}
 std::ofstream out(argv[1]);for(int w=1;w<=19;++w)for(auto h:census[w]){out<<w;for(auto t:h)out<<','<<int(t);out<<'\n';}
 for(int r=0;r<=5;++r)std::cout<<r<<' '<<visits[r]<<'\n';
}
