// Independent replay: frequency-vector partition enumeration and backward local recursion.
// Does not include the forward-DP producer or any of its implementation.
#include <algorithm>
#include <array>
#include <cassert>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <vector>
using namespace std;
int M(int a,int b){if(a>b)swap(a,b);if(a==3&&b>=5&&b<=7)return b+8;return min(16,a*b);}
int qmax(int w){auto power=[](int n){int p=1;while(n%2==0){p*=2;n/=2;}return p;};return (w%2?max(power(w-1),power(w+1)):power(w))-1;}
map<string,int> cache,declared;
string encode(const vector<int>&v){string s;for(int x:v)s.push_back(char(x));return s;}
int local(int w,vector<int>neighbors,int ell){
 sort(neighbors.begin(),neighbors.end());string key;key+=char(w);key+=char(ell);key+=encode(neighbors);
 auto found=cache.find(key);if(found!=cache.end())return found->second;
 int n=neighbors.size(),c=w/2,mass=w*(w-1)/2,budget=min(mass,n*c),q=min(n,qmax(w));
 vector<int>memo((n+1)*(budget+1)*(q+1),-1000000000);
 function<int(int,int,int)> solve=[&](int pos,int remaining,int maxima){
  if(pos==n)return 0;
  int index=(pos*(budget+1)+remaining)*(q+1)+maxima;int &value=memo[index];if(value!=-1000000000)return value;
  value=-100000000;
  for(int p=0;p<=min(c,remaining);p++)if(p<c||maxima>0)value=max(value,2*M(p,neighbors[pos])-ell*p+solve(pos+1,remaining-p,maxima-(p==c)));
  return value;
 };
 return cache[key]=ell*mass+solve(0,budget,q);
}
int cutoff_bound(const vector<int>&w,int ell){
 array<int,19>hist{};vector<int>heavy;
 for(int v:w){hist[v]++;if(v/2>ell)heavy.push_back(v/2);}sort(heavy.begin(),heavy.end());
 int answer=0;
 for(int i=0;i<(int)heavy.size();i++)for(int j=0;j<i;j++)answer+=2*M(heavy[i],heavy[j]);
 int maxloss=0,sumloss=0;
 for(int v=2;v<=18;v++)if(hist[v]){
  if(v/2<=ell)answer+=hist[v]*local(v,heavy,ell);
  else{auto ns=heavy;ns.erase(find(ns.begin(),ns.end(),v/2));int base=0;for(int x:ns)base+=M(v/2,x);int upper=local(v,ns,0);assert(upper%2==0);int loss=base-upper/2;assert(loss>=0);maxloss=max(maxloss,loss);sumloss+=hist[v]*loss;}
 }
 return answer-2*max(maxloss,(sumloss+1)/2);
}
array<int,10>cutoffs={2,3,1,4,0,5,6,7,8,9};
map<array<int,2>,array<long long,3>>counts;
vector<int>weights;long long visited=0,seen_survivors=0;
void inspect(){
 int best=1000000;
 for(int ell:cutoffs){best=min(best,cutoff_bound(weights,ell));if(best<992)break;}
 auto &row=counts[{int(weights.size()),weights[0]}];row[0]++;
 auto found=declared.find(encode(weights));
 if(best<992){assert(found==declared.end());row[1]++;}
 else{assert(found!=declared.end()&&found->second==best);row[2]++;seen_survivors++;}
 visited++;
}
void frequencies(int value,int slots,int total,bool require_maximum){
 if(slots==0){if(total==0)inspect();return;}
 if(value<2||total<2*slots||total>value*slots)return;
 for(int count=require_maximum?1:0;count<=min(slots,total/value);count++){
  int rest=slots-count,mass=total-count*value;
  if(rest==0&&mass!=0)continue;
  if(rest>0&&(mass<2*rest||mass>(value-1)*rest))continue;
  for(int j=0;j<count;j++)weights.push_back(value);
  frequencies(value-1,rest,mass,false);
  for(int j=0;j<count;j++)weights.pop_back();
 }
}
int main(int argc,char**argv){
 assert(argc==2);ifstream input(argv[1]);string line;
 while(getline(input,line)){istringstream is(line);int s,m,b;is>>s>>m>>b;vector<int>w(s);int sum=0;for(int &x:w){is>>x;sum+=x;}assert(sum==93&&w[0]==m&&s>=10&&s<=17&&m>=12&&m<=18&&b>=992);assert(is_sorted(w.rbegin(),w.rend()));assert(!declared.count(encode(w)));declared[encode(w)]=b;}
 for(int s=10;s<=17;s++){for(int m=12;m<=18;m++)frequencies(m,s,93,true);cerr<<"Verified support "<<s<<"; total "<<visited<<"; local keys "<<cache.size()<<'\n';}
 assert(visited==2163945&&seen_survivors==(long long)declared.size());
 for(auto r:counts)cout<<"{\"support\":"<<r.first[0]<<",\"maximum\":"<<r.first[1]<<",\"profiles\":"<<r.second[0]<<",\"quota_cuts\":"<<r.second[1]<<",\"quota_survivors\":"<<r.second[2]<<"}\n";
 cerr<<"PASS complete quota inventory: "<<visited<<" profiles, "<<seen_survivors<<" survivors\n";
}
