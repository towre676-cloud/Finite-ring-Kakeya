#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <vector>
#include <algorithm>
#include <map>
using namespace std;

// Every source support contains the coordinate affine basis 0,1,2,4,8,16.
// An affine automorphism is uniquely determined by its ordered images.
struct Census {
  uint32_t mask;
  vector<int> points;
  vector<array<int,6>> automorphisms;
  array<int,32> parent;
  array<int,5> cols{};
  int offset=0;
  uint64_t full_affine_bases=0;
  int root(int x) {return parent[x]==x?x:parent[x]=root(parent[x]);}
  void unite(int x,int y) {x=root(x);y=root(y);if(x!=y)parent[y]=x;}
  void visit(int depth,uint32_t span) {
    if(depth==5) {
      ++full_affine_bases;
      array<int,32> image{};image[0]=offset;
      for(int x=1;x<32;x++) {
        int j=__builtin_ctz((unsigned)x);
        image[x]=image[x^(1<<j)]^cols[j];
      }
      uint32_t imask=0;
      for(int x:points)imask|=uint32_t(1)<<image[x];
      if(imask!=mask)return;
      array<int,6> code{};code[0]=offset;
      for(int j=0;j<5;j++)code[j+1]=cols[j];
      automorphisms.push_back(code);
      for(int x:points)unite(x,image[x]);
      return;
    }
    for(int y:points) {
      int v=y^offset;
      if(span&(uint32_t(1)<<v))continue;
      uint32_t expanded=span;
      for(int x=0;x<32;x++)if(span&(uint32_t(1)<<x))expanded|=uint32_t(1)<<(x^v);
      cols[depth]=v;
      visit(depth+1,expanded);
    }
  }
  void run() {
    for(int x=0;x<32;x++){parent[x]=x;if(mask&(uint32_t(1)<<x))points.push_back(x);}
    for(int v:array<int,6>{0,1,2,4,8,16})if(!(mask&(uint32_t(1)<<v)))throw 1;
    for(int t:points){offset=t;visit(0,1);}
  }
};

int main(int argc,char**argv) {
  if(argc!=3)return 2;
  ifstream in(argv[1]);ofstream out(argv[2]);
  int id;uint32_t mask;int records=0,total_orbits=0;
  out<<"{\"schema\":\"affine-marked-support-census-v1\",\"records\":[";
  while(in>>id>>mask) {
    Census c;c.mask=mask;c.run();
    map<int,vector<int>> parts;
    for(int x:c.points)parts[c.root(x)].push_back(x);
    vector<vector<int>> orbits;
    for(auto &entry:parts)orbits.push_back(entry.second);
    sort(orbits.begin(),orbits.end());
    if(records++)out<<',';
    out<<"{\"global_orbit\":"<<id<<",\"mask\":"<<mask<<",\"support_size\":"<<c.points.size();
    out<<",\"full_affine_basis_images_checked\":"<<c.full_affine_bases;
    out<<",\"automorphism_count\":"<<c.automorphisms.size()<<",\"hub_orbits\":[";
    for(size_t j=0;j<orbits.size();j++){if(j)out<<',';out<<'[';for(size_t k=0;k<orbits[j].size();k++){if(k)out<<',';out<<orbits[j][k];}out<<']';}
    out<<"],\"affine_automorphisms\":[";
    for(size_t j=0;j<c.automorphisms.size();j++){if(j)out<<',';out<<'[';for(int k=0;k<6;k++){if(k)out<<',';out<<c.automorphisms[j][k];}out<<']';}
    out<<"]}";
    total_orbits+=orbits.size();
    cerr<<id<<' '<<c.points.size()<<' '<<c.full_affine_bases<<' '<<c.automorphisms.size()<<' '<<orbits.size()<<'\n';
  }
  out<<"],\"support_representatives\":"<<records<<",\"total_marked_orbits\":"<<total_orbits<<"}\n";
}
