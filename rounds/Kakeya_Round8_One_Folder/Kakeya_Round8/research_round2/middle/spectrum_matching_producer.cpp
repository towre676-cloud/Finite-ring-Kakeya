#define main inherited_resource_main
#include "../../research_external/m19/sumset_resource.cpp"
#undef main
#include "pair_spectra.hpp"

int match_upper(const vector<int>& qs,const array<int,10>&hist,int flag,int ell,vector<int>*lambda=nullptr,vector<int>*mu=nullptr){
 int n=int(qs.size())+(flag>=0);
 vector<int>ps;for(int p=0;p<10;p++)for(int k=0;k<hist[p];k++)ps.push_back(p);
 int m=ps.size();require(m<=31&&n<=m&&(flag<0||m==31),"hist mass / assignment size");
 if(flag==0&&hist[0]==0)return -10000000;
 if(flag==1&&hist[0]==31)return -10000000;
 int cost[33][32]{};
 for(int i=1;i<=n;i++)for(int j=1;j<=m;j++){
  int p=ps[j-1];
  if(flag>=0&&i==n)cost[i][j]=int((flag ? p>=1 : p==0)) ? ell*p : 1000000;
  else {int score=2*sumset_cap(p,qs[i-1])-ell*p;if(flag==-2)score=max(0,score);cost[i][j]=-score;}
 }
 // Rectangular Hungarian algorithm: assign each selected direction, including
 // the reserved own direction, to a distinct entry of the full spectrum.
 int u[33]{},v[32]{},p[32]{},way[32]{};
 for(int i=1;i<=n;i++){
  p[0]=i;int j0=0;int minv[32];bool used[32]{};
  fill(minv,minv+32,10000000);
  do{
   used[j0]=true;int i0=p[j0],delta=10000000,j1=0;
   for(int j=1;j<=m;j++)if(!used[j]){
    int cur=cost[i0][j]-u[i0]-v[j];
    if(cur<minv[j])minv[j]=cur,way[j]=j0;
    if(minv[j]<delta)delta=minv[j],j1=j;
   }
   for(int j=0;j<=m;j++)if(used[j])u[p[j]]+=delta,v[j]-=delta;else minv[j]-=delta;
   j0=j1;
  }while(p[j0]);
  do{int j1=way[j0];p[j0]=p[j1];j0=j1;}while(j0);
 }
 if(lambda){lambda->clear();for(int i=1;i<=n;i++)lambda->push_back(-u[i]);}
 if(mu){mu->clear();for(int j=1;j<=m;j++)mu->push_back(-v[j]);}
 return v[0];
}

struct SpectrumDP{
 unordered_map<string,int>cache;long long hits=0,misses=0;
 int value(int w,int flag,const array<uint8_t,16>&heavy,int ell){
  string key;key.push_back(char(w));key.push_back(char(flag));key.push_back(char(ell));for(int x:heavy)key.push_back(char(x));
  auto found=cache.find(key);if(found!=cache.end()){hits++;return found->second;}misses++;
  vector<int>qs;for(int q=1;q<16;q++)for(int k=0;k<heavy[q];k++)qs.push_back(q);
  int best=-10000000;
  for(auto h:exact_spectra[w])best=max(best,match_upper(qs,h,flag,ell));
  require(best>-1000000,"no realizable own-direction spectrum");
  best+=ell*w*(w-1)/2;cache.emplace(key,best);return best;
 }
};

#ifndef SPECTRUM_LIBRARY_ONLY
int main(int argc,char**argv){
 try{
  use_exact_sumset=true;
  if(argc==3&&string(argv[1])=="--dual-keys"){
   ifstream input(argv[2]);require(bool(input),"dual key input");string line;
   while(getline(input,line)){
    istringstream in(line);int w,f,ell,k;in>>w>>f>>ell>>k;vector<int>qs(k);for(int&i:qs)in>>i;require(bool(in),"dual key parse");
    int best=-10000000;ostringstream out;out<<"{\"weight\":"<<w<<",\"flag\":"<<f<<",\"cutoff\":"<<ell<<",\"neighbors\":[";
    for(int i=0;i<k;i++){if(i)out<<',';out<<qs[i];}out<<"],\"spectra\":[";bool first=true;
    for(int si=0;si<int(exact_spectra[w].size());si++){
     vector<int>lambda,mu;int val=match_upper(qs,exact_spectra[w][si],f,ell,&lambda,&mu);if(val< -1000000)continue;
     best=max(best,val);if(!first)out<<',';first=false;out<<"{\"index\":"<<si<<",\"bound\":"<<val<<",\"lambda\":[";
     for(int i=0;i<int(lambda.size());i++){if(i)out<<',';out<<lambda[i];}out<<"],\"mu\":[";for(int i=0;i<int(mu.size());i++){if(i)out<<',';out<<mu[i];}out<<"]}";
    }
    out<<"],\"upper_doubled\":"<<best+ell*w*(w-1)/2<<'}';cout<<out.str()<<'\n';
   }return 0;
  }
  require(argc==2,"profile file");Profiles profiles(argv[1],19);SpectrumDP dp;long long count=0,kills=0;use_exact_sumset=true;
  for(;profiles.active;profiles.next()){
   const auto&p=profiles.current;vector<Moment>rows;int small=0;
   for(int f=0;f<=1;f++)for(int w=2;w<=19;w++)for(int k=0;k<p.groups[32*f+w];k++){rows.push_back({w,f,w/2,0});if(f&&w<=3)small++;}
   int need=16*p.z+7*small+max(0,small-3),best=10000000,cut=-1,bb=0,bc=0;vector<int>bl,bli;
   for(int ell=0;ell<=16;ell++){
    array<uint8_t,16>hist{};vector<int>hs;for(auto r:rows)if(r.s>ell){hist[r.s]++;hs.push_back(r.s);}
    int plain=0;for(int i=0;i<int(hs.size());i++)for(int j=0;j<i;j++)plain+=2*sumset_cap(hs[i],hs[j]);
    vector<int>lights;for(auto r:rows)if(r.s<=ell){int val=dp.value(r.w,r.j,hist,ell);plain+=val;lights.push_back(val);}
    vector<int>losses;int sumloss=0,maxloss=0;
    for(auto r:rows)if(r.s>ell){
     auto nei=hist;nei[r.s]--;int base=0;for(int q=0;q<16;q++)base+=nei[q]*sumset_cap(r.s,q);
     int opt2=dp.value(r.w,r.j,nei,0);require(opt2%2==0,"endpoint parity");int loss=base-opt2/2;require(loss>=0,"negative loss");
     losses.push_back(loss);sumloss+=loss;maxloss=max(maxloss,loss);
    }
    int corr=2*max(maxloss,(sumloss+1)/2),upper=plain-corr;
    if(upper<best){best=upper;cut=ell;bb=plain;bc=corr;bl=losses;bli=lights;}
   }
   if(best<2*need){
    kills++;cout<<"{\"parent_id\":"<<p.id<<",\"support\":"<<p.support<<",\"required_capacity\":"<<need<<",\"cutoff\":"<<cut<<",\"spectrum_plain_doubled\":"<<bb<<",\"heavy_correction_doubled\":"<<bc<<",\"upper_doubled\":"<<best<<",\"heavy_losses\":[";
    for(int i=0;i<int(bl.size());i++){if(i)cout<<',';cout<<bl[i];}cout<<"],\"light_bounds\":[";for(int i=0;i<int(bli.size());i++){if(i)cout<<',';cout<<bli[i];}cout<<"]}\n";
   }
   count++;
  }
  cerr<<"DONE profiles="<<count<<" cuts="<<kills<<" spectrum_keys="<<dp.cache.size()<<"\n";
 }catch(const exception&e){cerr<<"ERROR "<<e.what()<<endl;return 2;}return 0;
}
#endif
