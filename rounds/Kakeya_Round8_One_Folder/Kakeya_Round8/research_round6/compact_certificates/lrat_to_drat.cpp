// Untrusted standard LRAT -> DRAT representation converter.
// Read the original CNF to recover clause contents for indexed deletions.
// Preserve literal/pivot order. Drop only LRAT IDs and propagation hints.
// Every result MUST pass DRAT-trim -> LRAT -> pinned CakeML on the same CNF.
#include <sys/stat.h>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
using i64=int64_t;using u64=uint64_t;
void ws(const char*&p,const char*e){while(p<e&&(*p==' '||*p=='\t'||*p=='\r'))++p;}
i64 num(const char*&p,const char*e){
 ws(p,e);bool negative=false;if(p<e&&*p=='-'){negative=true;++p;}
 if(p==e||*p<'0'||*p>'9')throw std::runtime_error("expected integer");
 i64 value=0;while(p<e&&*p>='0'&&*p<='9'){
  if(value>900000000000000000LL)throw std::runtime_error("integer too large");
  value=value*10+(*p++-'0');
 }return negative?-value:value;
}
struct Database {
 std::vector<std::vector<int>> clauses;
 std::vector<unsigned char> active;
 void put(u64 id,std::vector<int>&&clause){
  if(id>2000000000ULL)throw std::runtime_error("clause ID exceeds memory guard");
  if(id>=clauses.size()){clauses.resize(id+1);active.resize(id+1,0);}
  if(active[id])throw std::runtime_error("reused active clause ID");
  clauses[id]=std::move(clause);active[id]=1;
 }
 bool contains(u64 id)const{return id<active.size()&&active[id];}
 void erase(u64 id){active[id]=0;std::vector<int>().swap(clauses[id]);}
};
void write_clause(std::ostream&out,const std::vector<int>&clause,bool deletion){
 if(deletion)out<<"d ";
 for(int literal:clause)out<<literal<<' ';
 out<<"0\n";
}
int main(int argc,char**argv){
 try{
  if(argc!=4)throw std::runtime_error("usage: lrat_to_drat exact.cnf input.lrat output.drat");
  struct stat in_stat{},out_stat{};
  if(!stat(argv[3],&out_stat))for(int input=1;input<=2;++input)
   if(!stat(argv[input],&in_stat)&&in_stat.st_dev==out_stat.st_dev&&in_stat.st_ino==out_stat.st_ino)
    throw std::runtime_error("output aliases an original input");
  Database db;std::ifstream cnf(argv[1]);if(!cnf)throw std::runtime_error("cannot open CNF");
  u64 declared=0,loaded=0;std::string line;std::vector<int> pending;
  while(std::getline(cnf,line)){
   const char*p=line.data(),*e=p+line.size();ws(p,e);if(p==e||*p=='c')continue;
   if(*p=='p'){
    std::istringstream row(line);std::string tag,kind;u64 variables;
    row>>tag>>kind>>variables>>declared;if(!row||kind!="cnf")throw std::runtime_error("bad CNF header");
    continue;
   }
   while(true){
    ws(p,e);if(p==e)break;i64 literal=num(p,e);
    if(!literal){db.put(++loaded,std::move(pending));pending.clear();}
    else{if(literal>INT32_MAX||literal<-INT32_MAX)throw std::runtime_error("literal out of range");pending.push_back(literal);}
   }
  }
  if(!declared||loaded!=declared||!pending.empty())throw std::runtime_error("CNF clause count mismatch");
  std::ifstream proof(argv[2]);std::ofstream out(argv[3],std::ios::binary|std::ios::trunc);
  if(!proof||!out)throw std::runtime_error("cannot open proof streams");
  u64 last=loaded,additions=0,deletions=0,ignored=0,negative_hints=0,hints=0,empty=0,literals=0;
  while(std::getline(proof,line)){
   const char*p=line.data(),*e=p+line.size();ws(p,e);if(p==e||*p=='c')continue;
   i64 id=num(p,e);if(id<=0)throw std::runtime_error("bad LRAT line ID");ws(p,e);
   if(p<e&&*p=='d'){
    ++p;
    while(true){
     i64 target=num(p,e);if(!target)break;if(target<0)throw std::runtime_error("negative deletion ID");
     if(db.contains(target)){write_clause(out,db.clauses[target],true);db.erase(target);++deletions;}
     else ++ignored;
    }
   }else{
    if(u64(id)<=last)throw std::runtime_error("derived IDs not strictly increasing");
    last=id;std::vector<int> clause;
    while(true){
     i64 literal=num(p,e);if(!literal)break;
     if(literal>INT32_MAX||literal<-INT32_MAX)throw std::runtime_error("literal out of range");
     clause.push_back(literal);
    }
    while(true){i64 hint=num(p,e);if(!hint)break;++hints;if(hint<0)++negative_hints;}
    write_clause(out,clause,false);++additions;literals+=clause.size();if(clause.empty())++empty;
    db.put(id,std::move(clause));
   }
   ws(p,e);if(p!=e)throw std::runtime_error("trailing LRAT tokens");
  }
  if(!empty)throw std::runtime_error("no empty-clause conclusion");
  out.flush();if(!out)throw std::runtime_error("output write failed");
  std::cout<<"{\"status\":\"UNTRUSTED_DRAT_WRITTEN\",\"original_cnf_clauses\":"<<loaded
    <<",\"derived_additions\":"<<additions<<",\"emitted_deletions\":"<<deletions
    <<",\"inactive_deletions_ignored\":"<<ignored<<",\"derived_literals\":"<<literals
    <<",\"discarded_hint_references\":"<<hints<<",\"negative_hint_references\":"<<negative_hints
    <<",\"empty_clause_additions\":"<<empty<<",\"drat_bytes\":"<<u64(out.tellp())
    <<",\"drat_trim_and_cakeml_required\":true}\n";
 }catch(const std::exception&error){std::cerr<<error.what()<<'\n';return 1;}
}
