#include <array>
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <unordered_set>
#include <vector>
std::array<std::array<std::unordered_set<uint64_t>,2>,20> out;
std::array<uint64_t,6> visits{};
std::vector<int> points,opts;
int rnk;uint64_t cases=0;
uint64_t hist(const std::array<int,32>&p,int a){uint64_t k=0;for(int d=1;d<32;++d)if(d<(d^a))k+=uint64_t(1)<<(4*std::max(p[d],p[d^a]));return k;}
void visit(int next){
 ++visits[rnk];int w=points.size();std::array<int,32>p{};
 for(int i=0;i<w;++i)for(int j=0;j<i;++j)++p[points[i]^points[j]];
 if(w>=2){out[w][1].insert(hist(p,1));++cases;}
 for(int a=1;a<32;++a)if(!p[a]){out[w][0].insert(hist(p,a));++cases;}
 if(w==16)return;
 for(int i=next;i<(int)opts.size();++i){points.push_back(opts[i]);visit(i+1);points.pop_back();}
}
int main(int argc,char**argv){
 if(argc!=2)return 2;
 for(int r=0;r<=5;++r){rnk=r;points={0};opts.clear();for(int i=0;i<r;++i)points.push_back(1<<i);for(int x=0;x<(1<<r);++x)if(std::find(points.begin(),points.end(),x)==points.end())opts.push_back(x);visit(0);}
 for(int w=17;w<=19;++w)for(int f=0;f<2;++f)for(uint64_t k:out[32-w][f])out[w][1].insert(k<<(4*(w-16)));
 std::ofstream file(argv[1]);for(int w=2;w<=19;++w)for(int f=0;f<2;++f)for(uint64_t k:out[w][f]){file<<w<<','<<f;for(int p=0;p<10;++p)file<<','<<((k>>(4*p))&15);file<<'\n';}
 for(int r=0;r<=5;++r)std::cout<<r<<' '<<visits[r]<<'\n';std::cout<<"distinguished cases "<<cases<<'\n';
}
