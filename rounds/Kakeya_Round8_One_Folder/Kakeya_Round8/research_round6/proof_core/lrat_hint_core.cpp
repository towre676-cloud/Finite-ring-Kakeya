// Untrusted LRAT RUP-hint minimizer. Mandatory fresh CakeML acceptance required.
// Simulate each supplied positive hint sequence, then retain only the reason
// cone of its conflict. Clauses with negative RAT hints are copied unchanged.
// Original CNF/proof files are opened read-only; outputs preserve clause IDs.
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include <sys/stat.h>
using i64=int64_t;using u64=uint64_t;
void ws(const char*&p,const char*e){while(p<e && (*p==' '||*p=='\t'||*p=='\r'))++p;}
i64 num(const char*&p,const char*e){
 ws(p,e);bool neg=false;if(p<e&&*p=='-'){neg=true;++p;}
 if(p==e||*p<'0'||*p>'9')throw std::runtime_error("expected integer");
 i64 v=0;while(p<e&&*p>='0'&&*p<='9'){
  if(v>900000000000000000LL)throw std::runtime_error("integer too large");
  v=10*v+(*p++-'0');
 }return neg?-v:v;
}
struct Engine{
 std::vector<std::vector<int>> db;
 std::vector<int8_t> value;
 std::vector<i64> reason;
 std::vector<u64> needed;
 std::vector<int> trail;
 u64 epoch=0;
 void variable(int v){
  if(v<=0)throw std::runtime_error("invalid variable");
  if(size_t(v)>=value.size()){
   value.resize(v+1,0);reason.resize(v+1,-1);needed.resize(v+1,0);
  }
 }
 void store(u64 id,std::vector<int>&&clause){
  if(id>=db.size())db.resize(id+1);
  if(!db[id].empty())throw std::runtime_error("reused nonempty clause ID");
  for(int lit:clause)variable(std::abs(lit));
  db[id]=std::move(clause);
 }
 void erase(u64 id){if(id<db.size())std::vector<int>().swap(db[id]);}
 void clear(){for(int v:trail)value[v]=0;trail.clear();}
 void assign(int lit,i64 source){
  int v=std::abs(lit);variable(v);
  value[v]=lit>0?1:-1;reason[v]=source;trail.push_back(v);
 }
 bool minimize(const std::vector<int>&clause,const std::vector<i64>&hints,std::vector<i64>&out){
  ++epoch;clear();
  for(int lit:clause){
   int v=std::abs(lit);variable(v);int wanted=lit>0?-1:1;
   if(value[v] && value[v]!=wanted){clear();return false;}
   if(!value[v])assign(-lit,-1);
  }
  i64 conflict=-1;
  for(size_t j=0;j<hints.size();++j){
   i64 id=hints[j];
   if(id<=0 || size_t(id)>=db.size()){clear();return false;}
   const auto& c=db[id];int unit=0,count=0;bool satisfied=false;
   // Empty referenced clauses are treated as conflicts; the final checker
   // rejects a nonexistent/deleted reference if any malformed input had one.
   for(int lit:c){
    int v=std::abs(lit);int val=value[v];
    if(val && ((val>0)==(lit>0))){satisfied=true;break;}
    if(!val){unit=lit;++count;}
   }
   if(satisfied)continue;
   if(count==0){conflict=j;break;}
   if(count!=1){clear();return false;}
   assign(unit,j);
  }
  if(conflict<0){clear();return false;}
  std::vector<unsigned char> keep(hints.size(),0);
  keep[conflict]=1;
  for(int lit:db[hints[conflict]])needed[std::abs(lit)]=epoch;
  for(auto it=trail.rbegin();it!=trail.rend();++it){
   int v=*it;if(needed[v]!=epoch || reason[v]<0)continue;
   size_t j=reason[v];keep[j]=1;
   for(int lit:db[hints[j]])if(std::abs(lit)!=v)needed[std::abs(lit)]=epoch;
  }
  out.clear();for(size_t j=0;j<=size_t(conflict);++j)if(keep[j])out.push_back(hints[j]);
  clear();return true;
 }
};
int main(int argc,char**argv){
 try{
  if(argc!=4)throw std::runtime_error("usage: lrat_hint_core exact.cnf input.lrat output.lrat");
  struct stat is{},os{};if(!stat(argv[3],&os))for(int input=1;input<=2;++input)
   if(!stat(argv[input],&is)&&is.st_dev==os.st_dev&&is.st_ino==os.st_ino)
    throw std::runtime_error("output equals an original input");
  Engine engine;std::ifstream cnf(argv[1]);std::string line;u64 declared=0,loaded=0;
  std::vector<int> pending;
  while(std::getline(cnf,line)){
   const char*p=line.data(),*e=p+line.size();ws(p,e);if(p==e||*p=='c')continue;
   if(*p=='p'){
    std::string tag,kind;u64 variables;std::istringstream row(line);row>>tag>>kind>>variables>>declared;
    if(!row||kind!="cnf")throw std::runtime_error("bad CNF header");
    continue;
   }
   while(true){ws(p,e);if(p==e)break;i64 lit=num(p,e);
    if(!lit){engine.store(++loaded,std::move(pending));pending.clear();}
    else{if(lit>INT32_MAX||lit<-INT32_MAX)throw std::runtime_error("variable out of range");pending.push_back(lit);}
   }
  }
  if(!declared||loaded!=declared||!pending.empty())throw std::runtime_error("CNF clause-count mismatch");
  std::ifstream in(argv[2]);std::ofstream output(argv[3],std::ios::binary|std::ios::trunc);
  if(!in||!output)throw std::runtime_error("cannot open proof streams");
  u64 adds=0,rat=0,minimized=0,fallback=0,hints_before=0,hints_after=0,literal_count=0;
  std::vector<i64> hints,small;
  while(std::getline(in,line)){
   const char*p=line.data(),*e=p+line.size();ws(p,e);
   if(p==e||*p=='c'){output<<line<<'\n';continue;}
   i64 id=num(p,e);if(id<=0)throw std::runtime_error("bad clause ID");ws(p,e);
   if(p<e&&*p=='d'){
    ++p;while(true){i64 d=num(p,e);if(!d)break;if(d<0)throw std::runtime_error("bad deletion ID");engine.erase(d);}
    output<<line<<'\n';continue;
   }
   std::vector<int> clause;
   while(true){i64 lit=num(p,e);if(!lit)break;if(lit>INT32_MAX||lit<-INT32_MAX)throw std::runtime_error("variable out of range");clause.push_back(lit);}
   size_t prefix=p-line.data();hints.clear();bool negative=false;
   while(true){i64 hint=num(p,e);if(!hint)break;hints.push_back(hint);negative|=hint<0;}
   ws(p,e);if(p!=e)throw std::runtime_error("trailing tokens");
   ++adds;literal_count+=clause.size();hints_before+=hints.size();
   if(negative){++rat;output<<line<<'\n';hints_after+=hints.size();}
   else if(engine.minimize(clause,hints,small)){
    ++minimized;output.write(line.data(),prefix);
    for(i64 hint:small)output<<' '<<hint;
    output<<" 0\n";hints_after+=small.size();
   }else{++fallback;output<<line<<'\n';hints_after+=hints.size();}
   engine.store(id,std::move(clause));
  }
  output.flush();if(!output)throw std::runtime_error("output failure");
  u64 bytes=output.tellp();
  std::cout<<"{\"status\":\"UNTRUSTED_HINT_CORE_WRITTEN\",\"input_additions\":"<<adds
    <<",\"positive_hint_lines_minimized\":"<<minimized<<",\"negative_hint_lines_unchanged\":"<<rat
    <<",\"fallback_lines_unchanged\":"<<fallback<<",\"hint_count_before\":"<<hints_before
    <<",\"hint_count_after\":"<<hints_after<<",\"derived_literal_count\":"<<literal_count
    <<",\"output_bytes\":"<<bytes<<",\"checker_required\":true}\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
}
