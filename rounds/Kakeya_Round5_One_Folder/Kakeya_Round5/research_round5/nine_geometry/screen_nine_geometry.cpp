#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <vector>
using namespace std;

// Each row is (number of missing directions, outside-neighbour degree histogram).
const int missing[7]={3,4,6,8,9,10,16};
const int degree_hist[7][10]={
 {1,18,3,1,0,0,0,0,0,0},
 {7,0,12,4,0,0,0,0,0,0},
 {3,0,12,2,6,0,0,0,0,0},
 {0,8,2,0,9,0,4,0,0,0},
 {0,0,15,0,0,0,7,0,0,1},
 {1,0,0,8,12,0,0,0,0,2},
 {7,0,0,0,0,0,0,0,0,16}
};

int M(int p,int q){
 int a=min(p,q),b=max(p,q);
 return a==3 && b>=5 && b<=7 ? b+8 : min(16,p*q);
}
int quota(int w){return w%2 ? max((w-1)&-(w-1),(w+1)&-(w+1))-1 : (w&-w)-1;}
map<array<int,11>,array<int,10>> cache;

array<int,10> local(int w,const array<int,9>& heavy,int ell){
 array<int,11> key{}; key[0]=w;key[1]=ell;
 for(int i=0;i<9;i++)key[i+2]=heavy[i];
 auto found=cache.find(key);if(found!=cache.end())return found->second;
 int B=w*w/4,c=w/2,q=(quota(w)+1)/2;
 const int NEG=-100000000;
 vector<vector<int>> dp(B+1,vector<int>(q+1,NEG));dp[0][0]=0;
 array<int,10> out{};out[0]=ell*B;
 for(int k=1;k<=9;k++){
  vector<vector<int>> next(B+1,vector<int>(q+1,NEG));
  for(int used=0;used<=B;used++)for(int full=0;full<=q;full++)if(dp[used][full]>NEG)
   for(int p=0;p<=c && used+p<=B;p++){
    int f=full+(p==c);if(f>q)continue;
    next[used+p][f]=max(next[used+p][f],dp[used][full]+2*M(p,heavy[k-1])-ell*p);
   }
  dp.swap(next);int best=0;
  for(auto& row:dp)for(int x:row)best=max(best,x);
  out[k]=ell*B+best;
 }
 cache.emplace(key,out);return out;
}

int assignment_bound(const vector<array<int,10>>& rows,int branch){
 int n=rows.size();vector<int> slots;
 for(int k=9;k>=0;k--)for(int j=0;j<degree_hist[branch][k] && int(slots.size())<n;j++)slots.push_back(k);
 vector<int> dp(1<<n,-100000000);dp[0]=0;
 for(int mask=0;mask<(1<<n);mask++){
  int pos=__builtin_popcount((unsigned)mask);if(pos==n)continue;
  for(int i=0;i<n;i++)if(!(mask&(1<<i)))
   dp[mask|(1<<i)]=max(dp[mask|(1<<i)],dp[mask]+rows[i][slots[pos]]);
 }
 return dp.back();
}

int main(int argc,char**argv){
 if(argc!=4){cerr<<"usage: screen input cuts survivors\n";return 2;}
 ifstream in(argv[1]);ofstream cuts(argv[2]),survivors(argv[3]);
 if(!in||!cuts||!survivors)return 2;
 string line;long long count=0,excluded=0;map<pair<int,int>,long long> by;
 while(getline(in,line)){
  istringstream s(line);int n,m,old;s>>n>>m>>old;vector<int>w(n);for(int&x:w)s>>x;
  if(n<10||n>17||m<12||m>18||!s)return 3;
  array<int,9> h{};for(int i=0;i<9;i++)h[i]=w[i]/2;
  int ell=w[9]/2;vector<array<int,10>> rows;
  for(int i=9;i<n;i++)rows.push_back(local(w[i],h,ell));
  array<int,7> bounds{};bool cut=true;
  for(int j=0;j<7;j++){
   bounds[j]=assignment_bound(rows,j);
   if(bounds[j]>=32*missing[j]){cut=false;break;}
  }
  count++;
  if(cut){
   excluded++;by[{n,m}]++;
   cuts<<"{\"support\":"<<n<<",\"maximum\":"<<m<<",\"weights\":[";
   for(int i=0;i<n;i++){if(i)cuts<<',';cuts<<w[i];}
   cuts<<"],\"cutoff\":"<<ell<<",\"doubled_bounds\":[";
   for(int j=0;j<7;j++){if(j)cuts<<',';cuts<<bounds[j];}
   cuts<<"]}\n";
  }else survivors<<line<<'\n';
 }
 cout<<"{\"input\":"<<count<<",\"cuts\":"<<excluded<<",\"remaining\":"<<(count-excluded)<<",\"local_keys\":"<<cache.size()<<",\"by_cell\":[";
 bool first=true;for(auto [key,value]:by){if(!first)cout<<',';first=false;cout<<"["<<key.first<<","<<key.second<<","<<value<<"]";}
 cout<<"]}\n";
}
