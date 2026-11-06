#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <unordered_map>
#include <vector>
#include <chrono>
using namespace std;

array<unordered_map<uint64_t,uint32_t>,20> spectra;
array<uint64_t,6> visits{};
array<int,32> pairs{};
vector<int> points, options;
uint64_t key;
uint32_t mask;
int rank_now;

void add(int x){
 for(int y:points){int d=x^y,t=pairs[d]++;key-=(1ULL<<(5*t));key+=(1ULL<<(5*(t+1)));}
 points.push_back(x); mask|=uint32_t(1)<<x;
}
void remove_last(){
 int x=points.back();points.pop_back();mask^=uint32_t(1)<<x;
 for(int y:points){int d=x^y,t=pairs[d]--;key-=(1ULL<<(5*t));key+=(1ULL<<(5*(t-1)));}
}
void visit(int first){
 int w=points.size();visits[rank_now]++;
 spectra[w].emplace(key,mask);
 if(w==16)return;
 for(int i=first;i<int(options.size());i++){add(options[i]);visit(i+1);remove_last();}
}
int main(int argc,char**argv){
 if(argc!=2)return 2;
 for(int r=0;r<=5;r++){
  rank_now=r;pairs.fill(0);points.clear();options.clear();key=31;mask=0;
  add(0);for(int b=0;b<r;b++)add(1<<b);
  for(int x=0;x<(1<<r);x++)if(!(mask&(uint32_t(1)<<x)))options.push_back(x);
  visit(0);cerr<<"rank "<<r<<" normalized sets "<<visits[r]<<"\n";
 }
 for(int w=17;w<=19;w++){
  int old=32-w,shift=w-16;
  for(auto [k,m]:spectra[old])spectra[w].emplace(k<<(5*shift),~m);
 }
 ofstream out(argv[1]);out<<"{\n\"ambient_dimension\":5,\"normalization\":\"0 and coordinate affine basis\",\n\"normalized_sets_by_rank\":[";
 for(int i=0;i<=5;i++){if(i)out<<',';out<<visits[i];}out<<"],\n\"weights\":{\n";
 for(int w=1;w<=19;w++){
  if(w>1)out<<",\n";out<<'"'<<w<<"\":[";bool first=true;
  for(auto [k,m]:spectra[w]){
   if(!first)out<<',';first=false;out<<"{\"hist\":[";
   for(int p=0;p<10;p++){if(p)out<<',';out<<((k>>(5*p))&31);}out<<"],\"mask\":"<<m<<'}';
  }out<<']';cerr<<"weight "<<w<<" spectra "<<spectra[w].size()<<"\n";
 }out<<"\n}}\n";
}
