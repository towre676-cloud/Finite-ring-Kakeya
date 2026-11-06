#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <vector>
using namespace std;

struct Witness { int case_id;array<int,5> basis; };
map<uint32_t,Witness> certificates;
array<int,5> basis{};
vector<int> points;
int case_id;
uint64_t ordered_bases=0;

void bases(int depth,vector<int> span) {
  if(depth==5) {
    ++ordered_bases;
    array<int,32> coordinates{};
    for(int code=0;code<32;code++)coordinates[span[code]]=code;
    uint32_t normalized=0;
    for(int x:points)normalized|=uint32_t(1)<<coordinates[x];
    auto old=certificates.find(normalized);
    if(old!=certificates.end() && old->second.case_id!=case_id)throw 1;
    certificates.emplace(normalized,Witness{case_id,basis});
    return;
  }
  uint32_t used=0;for(int x:span)used|=uint32_t(1)<<x;
  for(int x:points)if(!(used&(uint32_t(1)<<x))) {
    vector<int> expanded=span;
    for(int y:span)expanded.push_back(y^x);
    basis[depth]=x;bases(depth+1,expanded);
  }
}

array<uint64_t,13> all_count{},cover_count{};
vector<int> options, chosen;
void supports(int first,int remaining,uint32_t mask,int size) {
  if(remaining==0) {
    ++all_count[size];uint32_t differences=0;
    for(size_t i=0;i<chosen.size();i++)for(size_t j=0;j<i;j++)differences|=uint32_t(1)<<(chosen[i]^chosen[j]);
    if(differences!=0xFFFFFFFEu)return;
    ++cover_count[size];
    if(!certificates.count(mask))throw 2;
    return;
  }
  for(int j=first;j<=int(options.size())-remaining;j++) {
    int x=options[j];chosen.push_back(x);
    supports(j+1,remaining-1,mask|(uint32_t(1)<<x),size);
    chosen.pop_back();
  }
}

int main(int argc,char**argv) {
  if(argc!=4)return 2;
  ifstream in(argv[1]);ofstream csv(argv[2]),out(argv[3]);
  uint32_t mask;int cases=0;
  while(in>>case_id>>mask) {
    points.clear();for(int x=0;x<32;x++)if(mask&(uint32_t(1)<<x))points.push_back(x);
    if(!(mask&1))throw 3;
    bases(0,{0});++cases;
  }
  uint32_t fixed=0;chosen={0,1,2,4,8,16};
  for(int x:chosen)fixed|=uint32_t(1)<<x;
  for(int x=0;x<32;x++)if(!(fixed&(uint32_t(1)<<x)))options.push_back(x);
  supports(0,5,fixed,11);supports(0,6,fixed,12);
  if(certificates.size()!=cover_count[11]+cover_count[12])throw 4;
  for(auto &entry:certificates) {
    csv<<entry.first<<','<<entry.second.case_id;
    for(int x:entry.second.basis)csv<<','<<x;
    csv<<'\n';
  }
  out<<"{\"status\":\"PASS\",\"cases\":"<<cases<<",\"ordered_bases\":"<<ordered_bases;
  out<<",\"normalized_all\":{\"11\":"<<all_count[11]<<",\"12\":"<<all_count[12]<<"}";
  out<<",\"normalized_covering\":{\"11\":"<<cover_count[11]<<",\"12\":"<<cover_count[12]<<"}";
  out<<",\"mapping_witnesses\":"<<certificates.size()<<",\"overlaps_between_cases\":0}\n";
  cerr<<"cases "<<cases<<" witnesses "<<certificates.size()<<" bases "<<ordered_bases<<'\n';
}
