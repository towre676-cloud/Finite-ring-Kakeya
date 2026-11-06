#define main inherited_resource_main
#include "../../research_external/m19/sumset_resource.cpp"
#undef main
int maximum_quota(int w){
 if(w%2==0)return (w&-w)-1;
 return max((w-1)&-(w-1),(w+1)&-(w+1))-1;
}
struct QuotaDP{
 unordered_map<string,int> cache;LocalDP loose;long long hits=0,misses=0;
 int value(int cap,int mass,const array<uint8_t,16>&heavy,int ell,int quota){
  int count=0;for(int x:heavy)count+=x;
  if(quota>=count)return loose.value(cap,mass,heavy,ell);
  int m=min(mass,cap*count);quota=min(quota,count);
  string key;key.push_back(char(cap));key.push_back(char(m&255));key.push_back(char(m>>8));key.push_back(char(ell));key.push_back(char(quota));for(int x:heavy)key.push_back(char(x));
  auto found=cache.find(key);if(found!=cache.end()){hits++;return ell*mass+found->second;}misses++;
  constexpr int neg=-100000000;int stride=quota+1;
  vector<int>best((m+1)*stride,neg),next(best.size(),neg);best[0]=0;int limit=0,processed=0;
  for(int upper=1;upper<16;upper++)for(int rep=0;rep<heavy[upper];rep++){
   fill(next.begin(),next.end(),neg);int nl=min(m,limit+cap);
   for(int used=0;used<=limit;used++)for(int full=0;full<=min(quota,processed);full++){
    int score=best[used*stride+full];if(score==neg)continue;
    for(int t=0;t<=min(cap,m-used);t++){
     int nf=full+(t==cap);if(nf>quota)continue;
     int val=score+2*sumset_cap(upper,t)-ell*t;
     int &slot=next[(used+t)*stride+nf];slot=max(slot,val);
    }
   }
   best.swap(next);limit=nl;processed++;
  }
  int score=*max_element(best.begin(),best.end());cache.emplace(key,score);return ell*mass+score;
 }
};
int main(int argc,char**argv){
 try{
  require(argc==2,"profile file");Profiles profiles(argv[1],19);QuotaDP dp;long long count=0,kills=0;use_exact_sumset=true;
  for(;profiles.active;profiles.next()){
   const auto&p=profiles.current;vector<Moment>rows;int small=0;
   for(int f=0;f<=1;f++)for(int w=2;w<=19;w++)for(int k=0;k<p.groups[32*f+w];k++){rows.push_back({w,f,w/2,0});if(f&&w<=3)small++;}
   int need=16*(32-p.support),best=10000000,cut=-1,bb=0,bc=0;vector<int>bl;
   for(int ell=0;ell<=16;ell++){
    array<uint8_t,16>hist{};vector<int>hs;for(auto r:rows)if(r.s>ell){hist[r.s]++;hs.push_back(r.s);}
    int plain=0;for(int i=0;i<int(hs.size());i++)for(int j=0;j<i;j++)plain+=2*sumset_cap(hs[i],hs[j]);
    for(auto r:rows)if(r.s<=ell)plain+=dp.value(r.s,(r.w-r.j)*(r.w-r.j-1)/2,hist,ell,maximum_quota(r.w));
    vector<int>losses;int sumloss=0,maxloss=0;
    for(auto r:rows)if(r.s>ell){
     auto nei=hist;nei[r.s]--;int base=0;for(int q=0;q<16;q++)base+=nei[q]*sumset_cap(r.s,q);
     int opt2=dp.value(r.s,(r.w-r.j)*(r.w-r.j-1)/2,nei,0,maximum_quota(r.w));require(opt2%2==0,"endpoint parity");int loss=base-opt2/2;require(loss>=0,"negative loss");
     losses.push_back(loss);sumloss+=loss;maxloss=max(maxloss,loss);
    }
    int corr=2*max(maxloss,(sumloss+1)/2),upper=plain-corr;
    if(upper<best){best=upper;cut=ell;bb=plain;bc=corr;bl=losses;}
   }
   if(best<2*need){
    kills++;cout<<"{\"parent_id\":"<<p.id<<",\"support\":"<<p.support<<",\"required_capacity\":"<<need<<",\"cutoff\":"<<cut<<",\"outside_plain_doubled\":"<<bb<<",\"heavy_correction_doubled\":"<<bc<<",\"upper_doubled\":"<<best<<",\"heavy_losses\":[";
    for(int i=0;i<int(bl.size());i++){if(i)cout<<',';cout<<bl[i];}cout<<"]}"<<endl;
   }
   count++;
  }
  cerr<<"DONE profiles="<<count<<" cuts="<<kills<<" constrained_keys="<<dp.cache.size()<<" loose_keys="<<dp.loose.cache.size()<<"\n";
 }catch(const exception&e){cerr<<"ERROR "<<e.what()<<endl;return 2;}return 0;
}
