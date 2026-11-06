#define SPECTRUM_LIBRARY_ONLY
#include "../../research_round2/geometric/spectrum_resource_screen.cpp"
#include "../../research_round2/geometric/paired_block_spectra.hpp"
#include "own_periodic_blocks.hpp"
#include <functional>

struct Row{int w,f,mode;int cap()const{return mode==1?2*((w/2)/2):w/2;}int ownmax()const{return f==0?0:(mode==2?w/2-1:w/2);}bool periodic()const{return mode==1;}};
using Neighbors=array<uint8_t,32>; // index cap+16*(positive period-rank mode)
bool own_allowed(Row r,int p){
 if(r.f==0)return p==0;
 if(r.mode==1)return p==r.w/2;
 if(r.mode==2)return p>=1&&p<r.w/2;
 return p>=1;
}
int edge_cap(int p,int q,bool a,bool b){int v=sumset_cap(p,q);return a&&b?min(v,p*q/2):v;}
int assign_max(const vector<vector<int>>&score,vector<int>*lambda=nullptr,vector<int>*mu=nullptr){
 int n=score.size(),m=n?score[0].size():0;if(!n){if(lambda)lambda->clear();if(mu)mu->assign(15,0);return 0;}
 require(n<=m&&m<=40,"assignment dimensions");vector<int>u(n+1),v(m+1),p(m+1),way(m+1);
 for(int i=1;i<=n;i++){
  p[0]=i;int j0=0;vector<int>minv(m+1,10000000);vector<bool>used(m+1);
  do{
   used[j0]=true;int i0=p[j0],delta=10000000,j1=0;
   for(int j=1;j<=m;j++)if(!used[j]){int cur=-score[i0-1][j-1]-u[i0]-v[j];if(cur<minv[j])minv[j]=cur,way[j]=j0;if(minv[j]<delta)delta=minv[j],j1=j;}
   for(int j=0;j<=m;j++)if(used[j])u[p[j]]+=delta,v[j]-=delta;else minv[j]-=delta;j0=j1;
  }while(p[j0]);
  do{int j1=way[j0];p[j0]=p[j1];j0=j1;}while(j0);
 }
 if(lambda){lambda->clear();for(int i=1;i<=n;i++)lambda->push_back(-u[i]);}
 if(mu){mu->clear();for(int j=1;j<=m;j++)mu->push_back(-v[j]);}
 return v[0];
}
vector<array<int,10>> spectra_for(Row r,int channel){
 vector<array<int,10>>out;
 if(channel==0){
  for(auto h:exact_spectra[r.w]){
   bool eligible=r.f<0;for(int p=0;p<10;p++)if(h[p]&&own_allowed(r,p))eligible=true;
   if(eligible)out.push_back(h);
  }
 }else if(r.mode==1)out=own_period_blocks.at(r.w);
 else out=block_spectra[r.w][r.f];
 require(!out.empty(),"empty own-period mode");return out;
}
vector<pair<int,int>> expand(Neighbors h){vector<pair<int,int>>qs;for(int period=0;period<=1;period++)for(int q=1;q<16;q++)for(int n=0;n<h[q+16*period];n++)qs.push_back({q,period});return qs;}
Neighbors normalize(Neighbors h,bool period){if(!period)for(int q=1;q<16;q++){h[q]+=h[q+16];h[q+16]=0;}return h;}
struct PeriodicDP{
 unordered_map<string,int>cache;
 int value(Row r,Neighbors h,int ell,int channel){
  h=normalize(h,r.periodic());string key;key+=char(r.w);key+=char(r.f);key+=char(r.mode);key+=char(ell);key+=char(channel);for(int x:h)key+=char(x);
  auto it=cache.find(key);if(it!=cache.end())return it->second;
  auto qs=expand(h);int best=-10000000;
  for(auto spectrum:spectra_for(r,channel)){
   vector<int>ps;int mass=0;for(int p=0;p<10;p++)for(int j=0;j<spectrum[p];j++){ps.push_back(p);mass+=p;}
   int n=qs.size()+(channel==0&&r.f>=0);vector<vector<int>>score(n,vector<int>(ps.size()));
   for(int i=0;i<int(qs.size());i++)for(int j=0;j<int(ps.size());j++){int p=ps[j],v=2*edge_cap(p,qs[i].first,r.periodic(),qs[i].second)-ell*p;score[i][j]=channel?max(0,v):v;}
   if(channel==0&&r.f>=0)for(int j=0;j<int(ps.size());j++){int p=ps[j];score.back()[j]=own_allowed(r,p)?2*sumset_cap(p,9)-ell*p:-1000000;}
   int constant=ell*(channel?mass:r.w*(r.w-1)/2);best=max(best,constant+assign_max(score));
  }
  require(best>=0,"negative local bound");cache.emplace(key,best);return best;
 }
};
struct PeriodicBound{int channel=-1,ell=0,plain=0,corr=0,groupdef=0,upper=10000000;vector<int>losses,lights;};
PeriodicBound bound_branch(const vector<Row>&rows,int support,PeriodicDP&dp){
 PeriodicBound best;
 for(int channel=0;channel<=1;channel++)for(int ell=0;ell<=8;ell++){
  Neighbors hist{},hubhist{};vector<Row>heavies;
  for(auto r:rows)if(r.cap()>ell){hist[r.cap()+16*r.periodic()]++;heavies.push_back(r);if(r.f)hubhist[r.ownmax()]++;}
  int plain=0,hubbase=0;
  for(int i=0;i<int(heavies.size());i++)for(int j=0;j<i;j++)plain+=2*edge_cap(heavies[i].cap(),heavies[j].cap(),heavies[i].periodic(),heavies[j].periodic());
  if(channel==0){for(auto r:heavies)if(r.f)hubbase+=sumset_cap(r.ownmax(),9);plain+=2*hubbase;}
  vector<int>lights,losses;int sumloss=0,maxloss=0,outsideloss=0,maxoutside=0,lowheavy=0;
  for(auto r:rows)if(r.cap()<=ell){int b=dp.value(r,hist,ell,channel);plain+=b;lights.push_back(b);}
  for(auto r:heavies){
   auto ns=hist;ns[r.cap()+16*r.periodic()]--;int base=channel==0?sumset_cap(r.ownmax(),9):0;
   for(auto [q,period]:expand(ns))base+=edge_cap(r.cap(),q,r.periodic(),period);
   int b=dp.value(r,ns,0,channel);require(b%2==0,"heavy local parity");int loss=base-b/2;require(loss>=0,"negative heavy deficit");
   losses.push_back(loss);sumloss+=loss;maxloss=max(maxloss,loss);
   if(!r.periodic()){outsideloss+=loss;maxoutside=max(maxoutside,loss);}else lowheavy++;
  }
  if(channel==0){int hb=dp.value({19,-1,0},hubhist,0,0);require(hb%2==0,"hub parity");int loss=hubbase-hb/2;require(loss>=0,"negative hub deficit");losses.push_back(loss);sumloss+=loss;maxloss=max(maxloss,loss);}
  int lower=max(maxloss,(sumloss+1)/2),groupdef=0;
  int corr=2*lower,upper=plain-corr;int need=channel==0?992:32*(32-support);
  if(upper<best.upper)best={channel,ell,plain,corr,groupdef,upper,losses,lights};
  if(upper<need)return {channel,ell,plain,corr,groupdef,upper,losses,lights};
 }
 return best;
}
vector<Row> mode_rows(const Profile&p,const array<int,8>&counts){
 vector<Row>rows;for(int f=0;f<=1;f++)for(int w=2;w<=19;w++)for(int j=0;j<p.groups[32*f+w];j++){
  int mode=0;if(f&&w%2==0)mode=w==2?1:(j<counts[(w-4)/2]?1:2);rows.push_back({w,f,mode});
 }return rows;
}
void print_vec(const vector<int>&v){cout<<'[';for(int i=0;i<int(v.size());i++){if(i)cout<<',';cout<<v[i];}cout<<']';}
int main(int argc,char**argv){
 try{
  use_exact_sumset=true;
  if(argc==3&&string(argv[1])=="--dual-keys"){
   ifstream input(argv[2]);require(bool(input),"dual keys input");string line;
   while(getline(input,line)){
    istringstream in(line);Row r;int ell,channel,k;in>>r.w>>r.f>>r.mode>>ell>>channel>>k;vector<pair<int,int>>qs(k);for(auto&[q,period]:qs)in>>q>>period;require(bool(in),"dual key parse");
    auto all=spectra_for(r,channel);int best=-10000000;ostringstream out;out<<"{\"weight\":"<<r.w<<",\"flag\":"<<r.f<<",\"mode\":"<<r.mode<<",\"cutoff\":"<<ell<<",\"channel\":"<<channel<<",\"neighbors\":[";
    for(int i=0;i<k;i++){if(i)out<<',';out<<'['<<qs[i].first<<','<<qs[i].second<<']';}out<<"],\"spectra\":[";
    for(int si=0;si<int(all.size());si++){
     auto h=all[si];vector<int>ps;int mass=0;for(int p=0;p<10;p++)for(int j=0;j<h[p];j++){ps.push_back(p);mass+=p;}
     int n=k+(channel==0&&r.f>=0);vector<vector<int>>score(n,vector<int>(ps.size()));
     for(int i=0;i<k;i++)for(int j=0;j<int(ps.size());j++){int p=ps[j],v=2*edge_cap(p,qs[i].first,r.periodic(),qs[i].second)-ell*p;score[i][j]=channel?max(0,v):v;}
     if(channel==0&&r.f>=0)for(int j=0;j<int(ps.size());j++){int p=ps[j];score.back()[j]=own_allowed(r,p)?2*sumset_cap(p,9)-ell*p:-1000000;}
     vector<int>lambda,mu;int val=assign_max(score,&lambda,&mu);if(n==0)mu.assign(ps.size(),0);
     int constant=ell*(channel?mass:r.w*(r.w-1)/2);best=max(best,constant+val);
     if(si)out<<',';out<<"{\"index\":"<<si<<",\"bound\":"<<val<<",\"constant\":"<<constant<<",\"lambda\":[";for(int j=0;j<int(lambda.size());j++){if(j)out<<',';out<<lambda[j];}out<<"],\"mu\":[";for(int j=0;j<int(mu.size());j++){if(j)out<<',';out<<mu[j];}out<<"]}";
    }
    out<<"],\"upper_doubled\":"<<best<<'}';cout<<out.str()<<'\n';
   }return 0;
  }
  require(argc==2,"profile input");Profiles profiles(argv[1],19);PeriodicDP dp;long long count=0,kills=0,branches=0;
  for(;profiles.active;profiles.next()){
   auto p=profiles.current;bool survives=false;vector<pair<array<int,8>,PeriodicBound>>certs;
   vector<array<int,8>>choices;array<int,8>chosen{};
   function<void(int)>enumerate=[&](int i){if(i==8){choices.push_back(chosen);return;}for(int k=0;k<=p.groups[36+2*i];k++){chosen[i]=k;enumerate(i+1);}};enumerate(0);
   for(auto modes:choices){
    auto rows=mode_rows(p,modes);PeriodicBound bound=bound_branch(rows,p.support,dp);branches++;
    int need=bound.channel==0?992:32*(32-p.support);
    if(bound.upper>=need){survives=true;break;}certs.push_back({modes,bound});
   }
   if(!survives){
    kills++;cout<<"{\"parent_id\":"<<p.id<<",\"support\":"<<p.support<<",\"branches\":[";
    for(int i=0;i<int(certs.size());i++){
     if(i)cout<<',';auto [m,b]=certs[i];cout<<"{\"periodic_counts\":[";for(int j=0;j<8;j++){if(j)cout<<',';cout<<m[j];}cout<<"],\"channel\":"<<b.channel<<",\"cutoff\":"<<b.ell<<",\"plain_doubled\":"<<b.plain<<",\"correction_doubled\":"<<b.corr<<",\"group_deficit\":"<<b.groupdef<<",\"upper_doubled\":"<<b.upper<<",\"heavy_losses\":";print_vec(b.losses);cout<<",\"light_bounds\":";print_vec(b.lights);cout<<'}';
    }cout<<"]}\n";
   }
   count++;
  }
  cerr<<"DONE profiles="<<count<<" cuts="<<kills<<" explored_branches="<<branches<<" local_keys="<<dp.cache.size()<<"\n";
 }catch(const exception&e){cerr<<"ERROR "<<e.what()<<endl;return 2;}return 0;
}
