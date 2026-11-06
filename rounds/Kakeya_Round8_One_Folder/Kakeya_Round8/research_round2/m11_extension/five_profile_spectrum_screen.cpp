#define SPECTRUM_LIBRARY_ONLY
#include "../geometric/spectrum_resource_screen.cpp"
int main(int argc,char**argv){
 require(argc==2,"global weights input");ifstream input(argv[1]);string line;SpectrumDP dp;use_exact_sumset=true;
 int count=0,kills=0;
 while(getline(input,line)){
  istringstream in(line);int support,maximum,old;in>>support>>maximum>>old;
  vector<int>weights(support);for(int&w:weights)in>>w;require(bool(in),"global line");

  int best=10000000,cut=-1,plain0=0,corr0=0;vector<int>loss0,light0;
  for(int ell=0;ell<=9;ell++){
   array<uint8_t,16>hist{};vector<int>hs;for(int w:weights)if(w/2>ell){hist[w/2]++;hs.push_back(w/2);}
   int plain=0;for(int i=0;i<int(hs.size());i++)for(int j=0;j<i;j++)plain+=2*sumset_cap(hs[i],hs[j]);
   vector<int>lights;for(int w:weights)if(w/2<=ell){int val=dp.value(w,-1,hist,ell);plain+=val;lights.push_back(val);}
   int lm=0,ls=0;vector<int>losses;
   for(int w:weights)if(w/2>ell){auto ns=hist;ns[w/2]--;int base=0;for(int q=0;q<16;q++)base+=ns[q]*sumset_cap(w/2,q);int loss=base-dp.value(w,-1,ns,0)/2;losses.push_back(loss);ls+=loss;lm=max(lm,loss);}
   int corr=2*max(lm,(ls+1)/2),b=plain-corr;if(b<best)best=b,cut=ell,plain0=plain,corr0=corr,loss0=losses,light0=lights;
  }
  count++;kills+=best<992;
  cout<<"{\"support\":"<<support<<",\"maximum\":"<<maximum<<",\"weights\":[";for(int i=0;i<support;i++){if(i)cout<<',';cout<<weights[i];}cout<<"],\"old_bound\":"<<old<<",\"upper_doubled\":"<<best<<",\"cutoff\":"<<cut<<",\"plain_doubled\":"<<plain0<<",\"correction_doubled\":"<<corr0<<",\"heavy_losses\":[";for(int i=0;i<int(loss0.size());i++){if(i)cout<<',';cout<<loss0[i];}cout<<"],\"light_bounds\":[";for(int i=0;i<int(light0.size());i++){if(i)cout<<',';cout<<light0[i];}cout<<"]}\n";
 }
 cerr<<"global profiles "<<count<<" excluded "<<kills<<" localkeys "<<dp.cache.size()<<"\n";
}
