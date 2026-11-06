#define SPECTRUM_LIBRARY_ONLY
#include "spectrum_resource_screen.cpp"

struct HubDP{
 unordered_map<string,int>cache;
 int value(int w,int flag,const array<uint8_t,16>&heavy,int ell){
  string key;key.push_back(char(w));key.push_back(char(flag));key.push_back(char(ell));for(int x:heavy)key.push_back(char(x));
  auto it=cache.find(key);if(it!=cache.end())return it->second;
  vector<int>qs;for(int q=1;q<16;q++)for(int k=0;k<heavy[q];k++)qs.push_back(q);
  int best=-10000000;
  for(auto h:exact_spectra[w])best=max(best,match_upper(qs,h,flag,ell,nullptr,nullptr,9));
  require(best>-1000000,"no own-compatible pair spectrum");best+=ell*w*(w-1)/2;cache.emplace(key,best);return best;
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
    for(int si=0;si<int(exact_spectra[w].size());si++){
     vector<int>lambda,mu;int val=match_upper(qs,exact_spectra[w][si],f,ell,&lambda,&mu,9);if(val< -1000000)continue;
     best=max(best,val);if(!first)out<<',';first=false;out<<"{\"index\":"<<si<<",\"bound\":"<<val<<",\"lambda\":[";
     for(int i=0;i<int(lambda.size());i++){if(i)out<<',';out<<lambda[i];}out<<"],\"mu\":[";for(int i=0;i<int(mu.size());i++){if(i)out<<',';out<<mu[i];}out<<"]}";
    }
    out<<"],\"upper_doubled\":"<<best+ell*w*(w-1)/2<<'}';cout<<out.str()<<'\n';
   }return 0;
  }
  require(argc==2,"profile file");Profiles profiles(argv[1],19);HubDP dp;long long count=0,kills=0;
  for(;profiles.active;profiles.next()){
   const auto&p=profiles.current;vector<Moment>rows;
   for(int f=0;f<=1;f++)for(int w=2;w<=19;w++)for(int k=0;k<p.groups[32*f+w];k++)rows.push_back({w,f,w/2,0});
   int best=10000000,cut=-1,bb=0,bc=0;vector<int>bl,bli;
   for(int ell=0;ell<=8;ell++){
    array<uint8_t,16>hist{},hubhist{};vector<int>hs;for(auto r:rows)if(r.s>ell){hist[r.s]++;hs.push_back(r.s);if(r.j)hubhist[r.s]++;}
    int plain=0;for(int i=0;i<int(hs.size());i++)for(int j=0;j<i;j++)plain+=2*sumset_cap(hs[i],hs[j]);
    int hubbase=0;for(int q=0;q<16;q++)hubbase+=hubhist[q]*sumset_cap(9,q);plain+=2*hubbase;
    vector<int>lights;for(auto r:rows)if(r.s<=ell){int val=dp.value(r.w,r.j,hist,ell);plain+=val;lights.push_back(val);}
    vector<int>losses;int sumloss=0,maxloss=0;
    for(auto r:rows)if(r.s>ell){
     auto nei=hist;nei[r.s]--;int base=r.j*sumset_cap(9,r.s);for(int q=0;q<16;q++)base+=nei[q]*sumset_cap(r.s,q);
     int opt2=dp.value(r.w,r.j,nei,0);require(opt2%2==0,"endpoint parity");int loss=base-opt2/2;require(loss>=0,"negative loss");
     losses.push_back(loss);sumloss+=loss;maxloss=max(maxloss,loss);
    }
    int hb=dp.value(19,-1,hubhist,0);require(hb%2==0,"hub endpoint parity");int hub_loss=hubbase-hb/2;require(hub_loss>=0,"negative hub loss");losses.push_back(hub_loss);sumloss+=hub_loss;maxloss=max(maxloss,hub_loss);
    int corr=2*max(maxloss,(sumloss+1)/2),upper=plain-corr;
    if(upper<best){best=upper;cut=ell;bb=plain;bc=corr;bl=losses;bli=lights;}
   }
   if(best<992){
    kills++;cout<<"{\"parent_id\":"<<p.id<<",\"support\":"<<p.support<<",\"required_capacity\":496,\"cutoff\":"<<cut<<",\"hub_plain_doubled\":"<<bb<<",\"heavy_correction_doubled\":"<<bc<<",\"upper_doubled\":"<<best<<",\"heavy_losses\":[";
    for(int i=0;i<int(bl.size());i++){if(i)cout<<',';cout<<bl[i];}cout<<"],\"light_bounds\":[";for(int i=0;i<int(bli.size());i++){if(i)cout<<',';cout<<bli[i];}cout<<"]}\n";
   }
   count++;
  }
  cerr<<"DONE profiles="<<count<<" cuts="<<kills<<" hub_keys="<<dp.cache.size()<<"\n";
 }catch(const exception&e){cerr<<"ERROR "<<e.what()<<endl;return 2;}return 0;
}
