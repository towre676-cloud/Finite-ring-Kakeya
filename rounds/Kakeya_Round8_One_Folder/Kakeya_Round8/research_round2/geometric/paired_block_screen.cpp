#define SPECTRUM_LIBRARY_ONLY
#include "spectrum_resource_screen.cpp"
#include "paired_block_spectra.hpp"

struct BlockDP{
 unordered_map<string,int>cache;
 int value(int w,int f,const array<uint8_t,16>&heavy,int ell){
  string key;key.push_back(char(w));key.push_back(char(f));key.push_back(char(ell));for(int x:heavy)key.push_back(char(x));
  auto it=cache.find(key);if(it!=cache.end())return it->second;
  vector<int>qs;for(int q=1;q<16;q++)for(int k=0;k<heavy[q];k++)qs.push_back(q);
  int best=-10000000;
  for(auto h:block_spectra[w][f]){
   int mass=0;for(int p=0;p<10;p++)mass+=p*h[p];
   int val=ell*mass+match_upper(qs,h,-2,ell);best=max(best,val);
  }
  require(best>=0,"empty block census class");cache.emplace(key,best);return best;
 }
};

int main(int argc,char**argv){
 try{
  use_exact_sumset=true;
  if(argc==3&&string(argv[1])=="--dual-keys"){
   ifstream input(argv[2]);require(bool(input),"dual key input");string line;
   while(getline(input,line)){
    istringstream in(line);int w,f,ell,k;in>>w>>f>>ell>>k;vector<int>qs(k);for(int&i:qs)in>>i;require(bool(in),"dual key parse");
    int best=-10000000;ostringstream out;out<<"{\"weight\":"<<w<<",\"flag\":"<<f<<",\"cutoff\":"<<ell<<",\"neighbors\":[";
    for(int i=0;i<k;i++){if(i)out<<',';out<<qs[i];}out<<"],\"spectra\":[";bool first=true;
    for(int si=0;si<int(block_spectra[w][f].size());si++){
     auto h=block_spectra[w][f][si];int mass=0;for(int p=0;p<10;p++)mass+=p*h[p];
     vector<int>lambda,mu;int val=match_upper(qs,h,-2,ell,&lambda,&mu);
     best=max(best,val+ell*mass);if(!first)out<<',';first=false;out<<"{\"index\":"<<si<<",\"mass\":"<<mass<<",\"bound\":"<<val<<",\"lambda\":[";
     for(int i=0;i<int(lambda.size());i++){if(i)out<<',';out<<lambda[i];}out<<"],\"mu\":[";for(int i=0;i<int(mu.size());i++){if(i)out<<',';out<<mu[i];}out<<"]}";
    }
    out<<"],\"upper_doubled\":"<<best<<'}';cout<<out.str()<<'\n';
   }return 0;
  }
  require(argc==2,"profile file");Profiles profiles(argv[1],19);BlockDP dp;long long count=0,kills=0;
  for(;profiles.active;profiles.next()){
   const auto&p=profiles.current;vector<Moment>rows;
   for(int f=0;f<=1;f++)for(int w=2;w<=19;w++)for(int k=0;k<p.groups[32*f+w];k++)rows.push_back({w,f,w/2,0});
   int need=16*(32-p.support),best=10000000,cut=-1,bb=0,bc=0;vector<int>bl,bli;
   for(int ell=0;ell<=9;ell++){
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
    kills++;cout<<"{\"parent_id\":"<<p.id<<",\"support\":"<<p.support<<",\"required_capacity\":"<<need<<",\"cutoff\":"<<cut<<",\"block_plain_doubled\":"<<bb<<",\"heavy_correction_doubled\":"<<bc<<",\"upper_doubled\":"<<best<<",\"heavy_losses\":[";
    for(int i=0;i<int(bl.size());i++){if(i)cout<<',';cout<<bl[i];}cout<<"],\"light_bounds\":[";for(int i=0;i<int(bli.size());i++){if(i)cout<<',';cout<<bli[i];}cout<<"]}\n";
   }
   count++;
  }
  cerr<<"DONE profiles="<<count<<" cuts="<<kills<<" block_keys="<<dp.cache.size()<<"\n";
 }catch(const exception&e){cerr<<"ERROR "<<e.what()<<endl;return 2;}return 0;
}
