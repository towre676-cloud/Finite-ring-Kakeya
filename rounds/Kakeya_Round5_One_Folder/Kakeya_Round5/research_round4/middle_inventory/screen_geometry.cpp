#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <sstream>
#include <string>
#include <vector>
using namespace std;
const int NEG=-10000000;
int cap(int x,int y){if(min(x,y)==3&&max(x,y)>=5&&max(x,y)<=7)return max(x,y)+8;return min(16,x*y);}
int quota(int w){return w%2?max((w-1)&-(w-1),(w+1)&-(w+1))-1:(w&-w)-1;}
map<string,int> memo;
int row(int w,const vector<int>&h,int ell,int mass,int q,int positives){
 int c=w/2,n=h.size();q=min(q,n);positives=min(positives,n);mass=min(mass,n*c);
 string key;for(int x:{w,ell,mass,q,positives})key+=char(x);for(int x:h)key+=char(x);
 auto found=memo.find(key);if(found!=memo.end())return found->second;
 int stride=(q+1)*(positives+1);vector<int>a((mass+1)*stride,NEG),b(a.size());a[0]=0;
 int processed=0;
 for(int y:h){fill(b.begin(),b.end(),NEG);
  for(int used=0;used<=min(mass,processed*c);used++)for(int full=0;full<=min(q,processed);full++)for(int pos=0;pos<=min(positives,processed);pos++){
   int old=a[used*stride+full*(positives+1)+pos];if(old==NEG)continue;
   for(int x=0;x<=min(c,mass-used);x++){int nf=full+(x==c),np=pos+(x>0);if(nf>q||np>positives)continue;
    int &slot=b[(used+x)*stride+nf*(positives+1)+np];slot=max(slot,old+2*cap(x,y)-ell*x);
   }
  }a.swap(b);processed++;
 }
 int value=*max_element(a.begin(),a.end());memo[key]=value;return value;
}
int light_bound(int w,const vector<int>&h,int ell,int mass,int q,int positive){return ell*mass+row(w,h,ell,mass,q,positive);}
int missing(const vector<int>&w,int heavy,bool half,bool sumfree,int positive){
 vector<int>h;for(int i=0;i<heavy;i++)h.push_back(w[i]/2);int ell=w[heavy]/2,total=0;
 for(int i=heavy;i<(int)w.size();i++){int v=w[i],mass=half||sumfree?v*v/4:v*(v-1)/2,q=sumfree?(quota(v)+1)/2:quota(v);total+=light_bound(v,h,ell,mass,q,positive);}
 return total;
}
vector<array<int,3>> triples[19];map<array<int,4>,int> deletedmemo;
void make_triples(){
 set<array<int,4>> patterns,states;states.insert({0,0,0,0});
 for(int mask=0;mask<16;mask++){array<int,4>x={__builtin_popcount((unsigned)mask),0,0,0};for(int a=0;a<4;a++)if(mask>>a&1)for(int b=a+1;b<4;b++)if(mask>>b&1)x[a^b]++;patterns.insert(x);}
 for(int k=0;k<8;k++){set<array<int,4>>next;for(auto a:states)for(auto b:patterns){array<int,4>x;for(int i=0;i<4;i++)x[i]=a[i]+b[i];if(x[0]<=18)next.insert(x);}states.swap(next);}
 for(auto x:states)triples[x[0]].push_back({x[1],x[2],x[3]});
}
int deleted_row(int w,int c1,int c2,int ell){array<int,4>key={w,c1,c2,ell};auto it=deletedmemo.find(key);if(it!=deletedmemo.end())return it->second;int best=NEG;
 for(auto x:triples[w]){int p=x[0],q=x[1],t=x[2];best=max(best,ell*(w*(w-1)/2-t)+2*cap(p,c1)+2*cap(q,c2)-ell*(p+q));}return deletedmemo[key]=best;}
vector<int>energy={0,0,1,3,12,16,33,63,112,120,153,211,300,408,553,735,960,976,1041};
pair<string,vector<int>> screen(const vector<int>&w){
 int e=0;for(int v:w)e+=energy[v];if(e<992)return {"TOTAL_PAIR_ENERGY",{e}};
 vector<int>h={w[0]/2,w[1]/2,w[2]/2};int ell=w[3]/2,total=0,uplift=0;
 for(int i=0;i<3;i++)for(int j=0;j<i;j++)total+=2*cap(h[i],h[j]);
 for(int i=3;i<(int)w.size();i++){int v=w[i],q=quota(v),mass=v*(v-1)/2;int restrict=light_bound(v,h,ell,mass,q==3?2:q,3);total+=restrict;if(q==3)uplift=max(uplift,light_bound(v,h,ell,mass,q,3)-restrict);}
 total+=uplift;if(total<992)return {"THREE_HEAVY_SINGLE_EXCEPTION",{total}};
 total=0;ell=w[2]/2;for(int i=2;i<(int)w.size();i++)total+=deleted_row(w[i],w[0]/2,w[1]/2,ell);
 if(total<960)return {"TWO_HEAVY_DELETED_DIRECTION",{total}};
 int full=missing(w,8,false,false,8),half=missing(w,8,true,false,3);
 if(full<288&&half<192)return {"EIGHT_HEAVY_MISSING_DIRECTIONS",{full,half}};
 int nine=missing(w,9,false,true,9);if(nine<96)return {"NINE_HEAVY_SUMFREE_DIRECTIONS",{nine}};
 if(full<288){int Q=0;vector<int>caps;for(int i=8;i<(int)w.size();i++){Q+=w[i]*w[i]/4;caps.push_back(w[i]/2);}if(caps[0]<=8){int X=accumulate(caps.begin(),caps.begin()+min(6,(int)caps.size()),0);int bonus=4*Q;for(int i=0;i<8;i++)if(w[i]/2>4){int k=min(6,(quota(w[i])+1)/2),Y=accumulate(caps.begin(),caps.begin()+min(k,(int)caps.size()),0);bonus+=(w[i]/2-5)*X+Y;}if(bonus<96)return {"HALFSPACE_MAXIMAL_DIRECTION_BONUS",{full,bonus}};}}
 bool ten=w[0]/2==6;for(int i=1;i<10;i++)ten=ten&&w[i]/2<=4;for(int i=10;i<(int)w.size();i++)ten=ten&&w[i]<=3;
 if(ten){int weak=0,mass=0;for(int i=0;i<10;i++)weak+=w[i]/2<=3;for(int i=10;i<(int)w.size();i++)mass+=w[i]*(w[i]-1)/2;int demand=min(3*weak,12);if(mass<demand)return {"TEN_HEAVY_WEAK_UNIQUE_DIRECTIONS",{mass,demand}};}
 return {"SURVIVES",{}};
}
int main(int argc,char**argv){
 if(argc!=5){cerr<<"input quota survivors, inherited cuts, new cuts, final survivors\n";return 2;}
 make_triples();ifstream inherited(argv[2]);set<vector<int>> oldcuts;string line;
 while(getline(inherited,line)){istringstream is(line);vector<int>w;int x;while(is>>x)w.push_back(x);oldcuts.insert(w);}
 ifstream input(argv[1]);ofstream cuts(argv[3]),survivors(argv[4]);map<array<int,2>,map<string,long long>>counts;long long n=0;
 while(getline(input,line)){istringstream is(line);int s,m,b;is>>s>>m>>b;vector<int>w(s);for(int &x:w)is>>x;string method;vector<int>values;
  if(oldcuts.count(w)){method="INHERITED_EXACT_SPECTRUM";}else{auto out=screen(w);method=out.first;values=out.second;}
  counts[{s,m}][method]++;if(method=="SURVIVES")survivors<<line<<'\n';else{cuts<<method<<' '<<s<<' '<<m<<' '<<values.size();for(int x:values)cuts<<' '<<x;for(int x:w)cuts<<' '<<x;cuts<<'\n';}
  if(++n%50000==0)cerr<<n<<" profiles; "<<memo.size()<<" resource keys\n";
 }
 for(auto &r:counts){cout<<"{\"support\":"<<r.first[0]<<",\"maximum\":"<<r.first[1]<<",\"methods\":{";bool first=true;for(auto &p:r.second){if(!first)cout<<',';first=false;cout<<'\"'<<p.first<<"\":"<<p.second;}cout<<"}}\n";}cerr<<"Finished "<<n<<" profiles\n";
}
