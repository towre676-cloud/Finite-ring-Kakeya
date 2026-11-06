#include <bits/stdc++.h>
using namespace std;
int M(int p,int q){int z=min(16,p*q);if(min(p,q)==3&&max(p,q)==5)z=13;return z;}
struct Search{
 int orbit,mode;array<int,17>S,mn;int Q[17][12]{};int idx[32],mate[17][32];
 long long subsets=0,maximal_subsets=0,port_cases=0,low_assignments=0,weighted_cases=0,energy_pass=0,capacity_pass=0,period_pass=0;
 vector<int>T,L,F,units;bool heavy[17]{};int low[17][32]{},weights[17],remaining[3];
 array<int,17>first_weights{};int first_low[17][32]{};array<int,17>first_periods{};
 static int rankmask(unsigned mask){int b[5]={};int r=0;for(int x=1;x<32;x++)if(mask>>x&1u){int y=x;for(int k=4;k>=0;k--)if(y>>k&1){if(b[k])y^=b[k];else{b[k]=y;r++;break;}}}return r;}
 static unsigned closure(unsigned mask){unsigned out=1;for(int x=1;x<32;x++)if(mask>>x&1u){unsigned z=out;for(int y=0;y<32;y++)if(out>>y&1u)z|=1u<<(x^y);out=z;}return out;}
 bool check(int hub,int weak){
  int energy=0;
  for(int i=0;i<17;i++){weights[i]=heavy[i]?(i==hub?11:i==weak?7:8):weights[i];if(weights[i]<mn[i])return false;energy+=Q[i][weights[i]];}
  weighted_cases++;if(energy<992)return false;energy_pass++;
  unsigned periods[17]{};int ranks[17]{};bool changed=true;int rounds=0;
  while(changed){changed=false;rounds++;if(rounds>30)abort();
   int caps[17][32]{};
   for(int i=0;i<17;i++)for(int d=1;d<32;d++)caps[i][d]=heavy[i]?(weights[i]==8&&ranks[i]==3?((periods[i]>>d&1u)?4:0):weights[i]/2):low[i][d];
   int cover[32]{};
   for(int d=1;d<32;d++){
    for(int i=0;i<17;i++){int j=mate[i][d];if(j>i)cover[d]+=M(caps[i][d],caps[j][d]);}
    if(cover[d]<16)return false;
   }
   if(rounds==1)capacity_pass++;
   for(int i:T)if(weights[i]==8){
    unsigned forced=periods[i];
    for(int d=1;d<32;d++){
     if(periods[i]>>d&1u)continue;int j=mate[i][d];if(j<0)continue;
     int nonperiod=ranks[i]>=2?0:ranks[i]==1?2:3;
     int replaced=cover[d]-M(caps[i][d],caps[j][d])+M(nonperiod,caps[j][d]);
     if(replaced<16)forced|=1u<<d;
    }
    unsigned closed=closure(forced);int rank=__builtin_popcount(closed)==1?0:__builtin_ctz(__builtin_popcount(closed));
    if(rank>3)return false;
    if(closed!=periods[i]){periods[i]=closed;ranks[i]=rank;changed=true;}
   }
  }
  period_pass++;
  if(period_pass==1){for(int i=0;i<17;i++){first_weights[i]=weights[i];first_periods[i]=periods[i];for(int d=0;d<32;d++)first_low[i][d]=low[i][d];}}
  return true;
 }
 void assign_units(int pos){
  if(pos==(int)units.size()){
   if(remaining[0]||remaining[1]||remaining[2])return;low_assignments++;
   for(int hub:T)for(int weak:T)if(hub!=weak)check(hub,weak);
   return;
  }
  int a=units[pos];
  for(int k=0;k<3;k++)if(remaining[k]&&mate[a][F[k]]>=0&&heavy[mate[a][F[k]]]){
   remaining[k]--;low[a][F[k]]=1;assign_units(pos+1);low[a][F[k]]=0;remaining[k]++;
  }
 }
 void process(){
  subsets++;unsigned D=0;for(int i=0;i<9;i++)for(int j=0;j<i;j++)D|=1u<<(S[T[i]]^S[T[j]]);
  if(__builtin_popcount(D)!=28)return;maximal_subsets++;F.clear();for(int d=1;d<32;d++)if(!(D>>d&1u))F.push_back(d);
  L.clear();for(int i=0;i<17;i++)if(!heavy[i])L.push_back(i);
  int ports[17]{};
  for(int a:L){for(int d:F)if(mate[a][d]>=0&&heavy[mate[a][d]])ports[a]++;if(!ports[a])return;}
  memset(low,0,sizeof(low));for(int a:L)weights[a]=2;
  if(mode==0){
   for(int four:L)if(ports[four]>=2)for(int three:L)if(three!=four&&ports[three]>=2){
    weights[four]=4;weights[three]=3;
    for(int z4=0;z4<3;z4++)for(int z3=0;z3<3;z3++){
     bool ok=true;for(int k=0;k<3;k++){
      if(k!=z4&&(mate[four][F[k]]<0||!heavy[mate[four][F[k]]]))ok=false;
      if(k!=z3&&(mate[three][F[k]]<0||!heavy[mate[three][F[k]]]))ok=false;
     }if(!ok)continue;port_cases++;
     vector<int>p4,p3;
     for(int k=0;k<3;k++){
      low[four][F[k]]=k==z4?0:2;low[three][F[k]]=k==z3?0:1;
      if(k!=z4)p4.push_back(F[k]);if(k!=z3)p3.push_back(F[k]);
      remaining[k]=4-low[four][F[k]]-low[three][F[k]];
     }
     low[four][p4[0]^p4[1]]=2;low[three][p3[0]^p3[1]]=1;
     units.clear();for(int a:L)if(a!=four&&a!=three)units.push_back(a);assign_units(0);
     for(int d=1;d<32;d++)low[four][d]=low[three][d]=0;
    }
    weights[four]=weights[three]=2;
   }
  }else{
   for(int five:L)if(ports[five]==3){weights[five]=5;
    for(int singled=0;singled<3;singled++){
     port_cases++;vector<int>plane;for(int k=0;k<3;k++)if(k!=singled)plane.push_back(F[k]);
     int p=plane[0],q=plane[1],r=F[singled];low[five][p]=low[five][q]=low[five][p^q]=2;
     for(int v:{0,p,q,p^q})low[five][r^v]=1;
     for(int k=0;k<3;k++)remaining[k]=4-low[five][F[k]];
     units.clear();for(int a:L)if(a!=five)units.push_back(a);assign_units(0);
     for(int d=1;d<32;d++)low[five][d]=0;
    }weights[five]=2;
   }
  }
 }
 void choose(int start,int left){if(!left){process();return;}for(int i=start;i<=17-left;i++){T.push_back(i);heavy[i]=true;choose(i+1,left-1);heavy[i]=false;T.pop_back();}}
 void run(){fill(idx,idx+32,-1);for(int i=0;i<17;i++)idx[S[i]]=i;for(int i=0;i<17;i++)for(int d=1;d<32;d++)mate[i][d]=idx[S[i]^d];choose(0,9);
  cout<<"{\"orbit\":"<<orbit<<",\"mode\":"<<mode<<",\"subsets\":"<<subsets<<",\"maximal_subsets\":"<<maximal_subsets<<",\"port_cases\":"<<port_cases<<",\"low_assignments\":"<<low_assignments<<",\"weighted_cases\":"<<weighted_cases<<",\"energy_pass\":"<<energy_pass<<",\"capacity_pass\":"<<capacity_pass<<",\"period_pass\":"<<period_pass;
  if(period_pass){cout<<",\"first_weights\":[";for(int i=0;i<17;i++){if(i)cout<<',';cout<<first_weights[i];}cout<<"],\"first_periods\":[";for(int i=0;i<17;i++){if(i)cout<<',';cout<<first_periods[i];}cout<<"],\"first_low_pairs\":[";for(int i=0;i<17;i++){if(i)cout<<',';cout<<'[';for(int d=0;d<32;d++){if(d)cout<<',';cout<<first_low[i][d];}cout<<']';}cout<<']';}cout<<"}"<<endl;
 }
};
int main(int argc,char**argv){if(argc!=2)return 2;ifstream in(argv[1]);int cases;in>>cases;while(cases--){Search s;in>>s.orbit>>s.mode;for(int&i:s.S)in>>i;for(int i=0;i<17;i++){in>>s.mn[i];for(int w=2;w<=11;w++)in>>s.Q[i][w];}s.run();}}
