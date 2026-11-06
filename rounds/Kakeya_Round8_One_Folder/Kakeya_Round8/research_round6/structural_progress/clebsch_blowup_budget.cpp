// Complete 3^16 integer count enumeration for the two-fold independent blowup
// of the Clebsch Cayley graph (F2^4, generators 1,2,4,8,15).
#include <array>
#include <cstdint>
#include <iostream>
#include <vector>
std::array<int,16> occ{};
std::array<int,33> best{};
std::array<std::vector<int>,16> prior;
uint64_t leaves=0;
void visit(int i,int w,int edges){
 if(i==16){ ++leaves; if(edges>best[w])best[w]=edges; return; }
 int neighbours=0;for(int j:prior[i])neighbours+=occ[j];
 for(int k=0;k<=2;k++){occ[i]=k;visit(i+1,w+k,edges+k*neighbours);}
}
int main(){
 best.fill(-1);
 for(int i=0;i<16;i++)for(int d:{1,2,4,8,15})if((i^d)<i)prior[i].push_back(i^d);
 visit(0,0,0);
 std::cout<<"{\"occupancy_vectors\":"<<leaves<<",\"max_edges\":[";
 for(int w=0;w<=32;w++)std::cout<<(w?",":"")<<best[w];
 std::cout<<"]}\n";
}
