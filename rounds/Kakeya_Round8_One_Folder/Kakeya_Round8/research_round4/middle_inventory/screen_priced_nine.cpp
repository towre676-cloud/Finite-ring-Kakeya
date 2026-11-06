// Exact single-heavy incidence-price family, applied after the frozen inventory.
#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <vector>
using namespace std;
int M(int a,int b){if(min(a,b)==3&&max(a,b)>=5&&max(a,b)<=7)return max(a,b)+8;return min(16,a*b);}
int quota(int w){return w%2?max((w-1)&-(w-1),(w+1)&-(w+1))-1:(w&-w)-1;}
map<string,array<int,2>> cache;
array<int,2> local(int w,const vector<int>&heavy,int ell){
 string key;key+=char(w);key+=char(ell);for(int h:heavy)key+=char(h);auto found=cache.find(key);if(found!=cache.end())return found->second;
 int c=w/2,mass=w*w/4,q=(quota(w)+1)/2;q=min(q,9);int cols=q+1;
 vector<int>a((mass+1)*cols,-1000000),b(a.size());a[0]=0;
 for(int i=1;i<9;i++){fill(b.begin(),b.end(),-1000000);for(int used=0;used<=mass;used++)for(int full=0;full<=q;full++){
  int old=a[used*cols+full];if(old<-999999)continue;
  for(int x=0;x<=min(c,mass-used);x++){int ff=full+(x==c);if(ff<=q)b[(used+x)*cols+ff]=max(b[(used+x)*cols+ff],old+2*M(x,heavy[i])-ell*x);}
 }a.swap(b);}
 vector<int>prefix=a;
 for(int u=0;u<=mass;u++)for(int f=0;f<=q;f++){if(u)prefix[u*cols+f]=max(prefix[u*cols+f],prefix[(u-1)*cols+f]);if(f)prefix[u*cols+f]=max(prefix[u*cols+f],prefix[u*cols+f-1]);}
 int inactive=ell*mass+prefix[mass*cols+q],active=-1000000;
 for(int x=1;x<=min(c,mass);x++){int ff=q-(x==c);if(ff>=0)active=max(active,ell*mass+2*M(x,heavy[0])-ell*x+prefix[(mass-x)*cols+ff]);}
 return cache[key]={inactive,active};
}
int main(int argc,char**argv){
 if(argc!=4)return 2;ifstream input(argv[1]);ofstream cuts(argv[2]),survivors(argv[3]);string line;long long total=0,removed=0;map<array<int,2>,array<int,2>>by;
 while(getline(input,line)){istringstream is(line);int s,m,old;is>>s>>m>>old;vector<int>w(s),heavy;for(int &v:w)is>>v;for(int i=0;i<9;i++)heavy.push_back(w[i]/2);int ell=w[9]/2;
  vector<array<int,2>>rows;for(int i=9;i<s;i++)rows.push_back(local(w[i],heavy,ell));
  int best=1000000,price=-1;for(int t=0;t<=32;t++){int upper=3*t;for(auto a:rows)upper+=max(a[0],a[1]-t);if(upper<best){best=upper;price=t;}}
  auto &count=by[{s,m}];count[0]++;total++;
  if(best>=96){survivors<<line<<'\n';continue;}
  count[1]++;removed++;
  cuts<<"{\"support\":"<<s<<",\"maximum\":"<<m<<",\"price\":"<<price<<",\"upper_doubled\":"<<best<<",\"weights\":[";
  for(int i=0;i<s;i++){if(i)cuts<<',';cuts<<w[i];}cuts<<"],\"light_rows\":[";
  for(int i=9;i<s;i++){if(i>9)cuts<<',';auto a=rows[i-9];cuts<<'['<<w[i]<<','<<a[0]<<','<<a[1]<<']';}cuts<<"]}\n";
 }
 cout<<"{\"status\":\"PRODUCED\",\"input\":"<<total<<",\"cuts\":"<<removed<<",\"remaining\":"<<total-removed<<",\"local_keys\":"<<cache.size()<<",\"records\":[";bool first=true;
 for(auto r:by){if(!first)cout<<',';first=false;cout<<"{\"support\":"<<r.first[0]<<",\"maximum\":"<<r.first[1]<<",\"input\":"<<r.second[0]<<",\"cuts\":"<<r.second[1]<<",\"remaining\":"<<r.second[0]-r.second[1]<<'}';}cout<<"]}\n";
}
