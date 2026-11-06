#define SPECTRUM_LIBRARY_ONLY
#include "spectrum_resource_screen.cpp"
#include "paired_block_spectra.hpp"
#include "outside_degree_patterns.hpp"

int max_assign(const vector<vector<int>>&score,vector<int>*lambda=nullptr,vector<int>*mu=nullptr){
 int n=score.size(),m=n?score[0].size():0;if(!n){if(lambda)lambda->clear();if(mu)mu->clear();return 0;}
 require(n<=m&&m<=40,"assignment dimensions");
 vector<int>u(n+1),v(m+1),p(m+1),way(m+1);
 for(int i=1;i<=n;i++){
  p[0]=i;int j0=0;vector<int>minv(m+1,10000000);vector<bool>used(m+1);
  do{
   used[j0]=true;int i0=p[j0],delta=10000000,j1=0;
   for(int j=1;j<=m;j++)if(!used[j]){
    int cur=-score[i0-1][j-1]-u[i0]-v[j];if(cur<minv[j])minv[j]=cur,way[j]=j0;
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

struct DegreeDP{
 unordered_map<string,int>cache;
 int value(int w,int f,const vector<int>&qs,int degree){
  string key;key.push_back(char(w));key.push_back(char(f));key.push_back(char(degree));for(int q:qs)key.push_back(char(q));
  auto it=cache.find(key);if(it!=cache.end())return it->second;
  int dummy=int(qs.size())-degree;require(dummy>=0,"degree limit");int best=-10000000;
  for(auto h:block_spectra[w][f]){
   vector<int>ps;for(int p=0;p<10;p++)for(int k=0;k<h[p];k++)ps.push_back(p);
   vector<vector<int>>score(qs.size(),vector<int>(15+dummy,1000));
   for(int i=0;i<int(qs.size());i++)for(int j=0;j<15;j++)score[i][j]=sumset_cap(ps[j],qs[i]);
   best=max(best,max_assign(score)-1000*dummy);
  }
  require(best>=0,"missing block spectrum");cache.emplace(key,best);return best;
 }
};

int main(int argc,char**argv){
 try{
  use_exact_sumset=true;
  if(argc==3&&string(argv[1])=="--dual-keys"){
   ifstream input(argv[2]);require(bool(input),"dual key input");string line;
   while(getline(input,line)){
    istringstream in(line);int w,f,degree,k;in>>w>>f>>degree>>k;vector<int>qs(k);for(int&i:qs)in>>i;require(bool(in),"dual key parse");int dummy=k-degree;
    int best=-10000000;ostringstream out;out<<"{\"weight\":"<<w<<",\"flag\":"<<f<<",\"degree\":"<<degree<<",\"neighbors\":[";
    for(int i=0;i<k;i++){if(i)out<<',';out<<qs[i];}out<<"],\"spectra\":[";bool first=true;
    for(int si=0;si<int(block_spectra[w][f].size());si++){
     auto h=block_spectra[w][f][si];vector<int>ps;for(int p=0;p<10;p++)for(int j=0;j<h[p];j++)ps.push_back(p);
     vector<vector<int>>score(k,vector<int>(15+dummy,1000));for(int i=0;i<k;i++)for(int j=0;j<15;j++)score[i][j]=sumset_cap(ps[j],qs[i]);
     vector<int>lambda,mu;int val=max_assign(score,&lambda,&mu);best=max(best,val-1000*dummy);
     if(!first)out<<',';first=false;out<<"{\"index\":"<<si<<",\"bound\":"<<val<<",\"lambda\":[";for(int i=0;i<int(lambda.size());i++){if(i)out<<',';out<<lambda[i];}out<<"],\"mu\":[";for(int i=0;i<int(mu.size());i++){if(i)out<<',';out<<mu[i];}out<<"]}";
    }
    out<<"],\"incident_upper\":"<<best<<'}';cout<<out.str()<<'\n';
   }return 0;
  }
  require(argc==2,"profile file");Profiles profiles(argv[1],19);DegreeDP dp;long long count=0,kills=0;
  for(;profiles.active;profiles.next()){
   const auto&p=profiles.current;vector<Moment>rows;
   for(int f=0;f<=1;f++)for(int w=2;w<=19;w++)for(int k=0;k<p.groups[32*f+w];k++)rows.push_back({w,f,w/2,0});
   int n=rows.size(),need=32*(32-p.support);vector<int>allcaps;for(auto r:rows)allcaps.push_back(r.s);sort(allcaps.begin(),allcaps.end());
   vector<array<int,11>>local(n);vector<bool>special(n);int nspecial=0;
   for(int i=0;i<n;i++){
    auto r=rows[i];auto qs=allcaps;qs.erase(find(qs.begin(),qs.end(),r.s));special[i]=(r.j==0||r.w<=3);nspecial+=special[i];
    for(int degree=(n-1)%2;degree<=n-1;degree+=2)local[i][degree]=dp.value(r.w,r.j,qs,degree);
   }
   int worst=-10000000;vector<int>patternbounds;vector<vector<int>>lams,mus;
   for(auto degrees:outside_degree_patterns.at(p.support)){
    int places=count_if(degrees.begin(),degrees.end(),[&](int d){return d<n-1;});
    if(places<nspecial){patternbounds.push_back(-1);lams.push_back({});mus.push_back({});continue;}
    vector<vector<int>>score(n,vector<int>(n));for(int i=0;i<n;i++)for(int j=0;j<n;j++)score[i][j]=(special[i]&&degrees[j]==n-1)?-1000000:local[i][degrees[j]];
    vector<int>lambda,mu;int val=max_assign(score,&lambda,&mu);require(val>=0,"degree assignment infeasible");worst=max(worst,val);patternbounds.push_back(val);lams.push_back(lambda);mus.push_back(mu);
   }
   if(worst<need){
    kills++;cout<<"{\"parent_id\":"<<p.id<<",\"support\":"<<p.support<<",\"required_doubled\":"<<need<<",\"upper_doubled\":"<<worst<<",\"patterns\":[";
    for(int k=0;k<int(patternbounds.size());k++){
     if(k)cout<<',';cout<<"{\"index\":"<<k<<",\"bound\":"<<patternbounds[k]<<",\"lambda\":[";for(int i=0;i<int(lams[k].size());i++){if(i)cout<<',';cout<<lams[k][i];}cout<<"],\"mu\":[";for(int i=0;i<int(mus[k].size());i++){if(i)cout<<',';cout<<mus[k][i];}cout<<"]}";
    }cout<<"]}\n";
   }
   count++;
  }
  cerr<<"DONE profiles="<<count<<" cuts="<<kills<<" degree_keys="<<dp.cache.size()<<"\n";
 }catch(const exception&e){cerr<<"ERROR "<<e.what()<<endl;return 2;}return 0;
}
