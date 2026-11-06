// Untrusted backward LRAT dependency trimmer.
// Every output MUST be independently accepted by the pinned CakeML checker
// against the unchanged original CNF before it is credited as a certificate.
//
// Usage: lrat_core exact.cnf original.lrat core.lrat
// Original inputs are opened read-only. Three streaming/mmap passes avoid
// storing the proof or all hints in RAM. One byte per largest clause ID is used.
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <algorithm>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using u64 = uint64_t;
struct File {
 int fd=-1; size_t size=0; const char* data=nullptr;
 explicit File(const char* path) {
  fd=open(path,O_RDONLY); if(fd<0) throw std::runtime_error("cannot open input");
  struct stat st{}; if(fstat(fd,&st))throw std::runtime_error("fstat failed");
  size=st.st_size; if(!size)throw std::runtime_error("empty proof");
  data=static_cast<const char*>(mmap(nullptr,size,PROT_READ,MAP_PRIVATE,fd,0));
  if(data==MAP_FAILED)throw std::runtime_error("mmap failed");
 }
 ~File(){if(data && data!=MAP_FAILED)munmap(const_cast<char*>(data),size);if(fd>=0)close(fd);}
};
void space(const char*& p,const char* end){while(p<end && (*p==' '||*p=='\t'||*p=='\r'))++p;}
int64_t number(const char*& p,const char* end){
 space(p,end); bool negative=false;if(p<end && *p=='-'){negative=true;++p;}
 if(p==end || *p<'0' || *p>'9')throw std::runtime_error("expected integer");
 u64 n=0;while(p<end && *p>='0' && *p<='9'){
  if(n>900000000000000000ULL)throw std::runtime_error("integer too large");
  n=10*n+(*p++-'0');
 }
 if(n>INT64_MAX)throw std::runtime_error("integer out of range");
 return negative?-int64_t(n):int64_t(n);
}
u64 positive(const char*& p,const char* end){
 auto n=number(p,end);if(n<=0)throw std::runtime_error("nonpositive clause ID");return n;
}
size_t next_line(const File& f,size_t at){
 const void* q=memchr(f.data+at,'\n',f.size-at);
 return q?static_cast<const char*>(q)-f.data+1:f.size;
}
const char* line_end(const File& f,size_t next){
 const char* p=f.data+next;if(p>f.data && p[-1]=='\n')--p;return p;
}
u64 cnf_clauses(const char* path){
 std::ifstream in(path);std::string line;
 while(std::getline(in,line)){
  if(!line.empty() && line[0]=='p'){
   std::string tag,kind;u64 variables,clauses;
   std::istringstream row(line);row>>tag>>kind>>variables>>clauses;
   if(!row || tag!="p" || kind!="cnf")throw std::runtime_error("bad CNF header");
   return clauses;
  }
 }
 throw std::runtime_error("missing CNF header");
}
int main(int argc,char**argv){
 try{
  if(argc!=4)throw std::runtime_error("usage: lrat_core exact.cnf input.lrat output.lrat");
  struct stat input_stat{},output_stat{};
  if(!stat(argv[3],&output_stat))for(int input=1;input<=2;++input)
   if(!stat(argv[input],&input_stat) && input_stat.st_dev==output_stat.st_dev
       && input_stat.st_ino==output_stat.st_ino)
    throw std::runtime_error("output must differ from both original inputs");
  u64 original=cnf_clauses(argv[1]);File f(argv[2]);
  u64 last_add=original,max_id=original,add_count=0,del_count=0,root_id=0;
  size_t root_end=0;
  // Pass1: validate increasing added IDs and locate the final empty clause.
  for(size_t at=0;at<f.size;){
   size_t next=next_line(f,at);const char* end=line_end(f,next);const char* p=f.data+at;space(p,end);
   if(p<end && *p!='c'){
    u64 id=positive(p,end);space(p,end);
    if(p<end && *p=='d'){++del_count;}
    else{
     if(id<=last_add)throw std::runtime_error("added IDs are not strictly increasing");
     last_add=id;max_id=std::max(max_id,id);++add_count;
     if(number(p,end)==0){root_id=id;root_end=next;}
    }
   }
   at=next;
  }
  if(!root_id)throw std::runtime_error("proof contains no empty-clause addition");
  if(max_id>2000000000ULL)throw std::runtime_error("clause-ID range exceeds 2GB bitmap guard");
  std::vector<unsigned char> needed(max_id+1,0);
  needed[root_id]=1;u64 kept_add=0,negative_hints=0,hints=0;
  // Pass2: dependency closure in reverse chronology. Include negative RAT IDs.
  size_t cursor=root_end;
  while(cursor){
   size_t endpos=cursor;if(endpos && f.data[endpos-1]=='\n')--endpos;
   size_t at=endpos;while(at && f.data[at-1]!='\n')--at;
   const char* p=f.data+at;const char* end=f.data+endpos;space(p,end);
   if(p<end && *p!='c'){
    u64 id=positive(p,end);space(p,end);
    if(!(p<end && *p=='d') && needed[id]){
     ++kept_add;
     while(number(p,end)!=0){} // Skip the clause literals.
     while(true){
      int64_t hint=number(p,end);if(!hint)break;
      ++hints;if(hint<0)++negative_hints;
      u64 dependency=hint<0?u64(-hint):u64(hint);
      if(dependency>=id || dependency>max_id)throw std::runtime_error("forward hint reference");
      needed[dependency]=1;
     }
     space(p,end);if(p!=end)throw std::runtime_error("trailing tokens after hints");
    }
   }
   cursor=at;
  }
  u64 needed_derived=0;for(u64 id=original+1;id<=max_id;++id)needed_derived+=needed[id]!=0;
  if(needed_derived!=kept_add)throw std::runtime_error("dependency refers to an absent derived clause");
  // Pass3: retain original addition bytes and deletion chronology. Keep all
  // deletion targets that are input clauses or retained derived clauses.
  std::ofstream out(argv[3],std::ios::binary|std::ios::trunc);
  if(!out)throw std::runtime_error("cannot open output");
  u64 kept_del=0,deleted_targets=0;
  for(size_t at=0;at<root_end;){
   size_t next=next_line(f,at);const char* end=line_end(f,next);const char* p=f.data+at;space(p,end);
   if(p<end && *p!='c'){
    u64 id=positive(p,end);space(p,end);
    if(p<end && *p=='d'){
     ++p;std::vector<u64> targets;
     while(true){
      auto value=number(p,end);if(!value)break;
      if(value<0)throw std::runtime_error("negative deletion target");
      u64 d=value;
      if(d<=original || (d<=max_id && needed[d]))targets.push_back(d);
     }
     space(p,end);if(p!=end)throw std::runtime_error("trailing deletion tokens");
     if(!targets.empty()){
      out<<id<<" d";for(u64 d:targets)out<<" "<<d;out<<" 0\n";
      ++kept_del;deleted_targets+=targets.size();
     }
    }else if(needed[id]){
     out.write(f.data+at,next-at);if(next==f.size && f.data[next-1]!='\n')out<<'\n';
    }
   }
   at=next;
  }
  out.flush();if(!out)throw std::runtime_error("failed output write");
  u64 bytes=out.tellp();out.close();
  std::cout<<"{\"status\":\"UNTRUSTED_CORE_WRITTEN\",\"input_bytes\":"<<f.size
    <<",\"core_bytes\":"<<bytes<<",\"original_cnf_clauses\":"<<original
    <<",\"input_additions\":"<<add_count<<",\"kept_additions\":"<<kept_add
    <<",\"input_deletions\":"<<del_count<<",\"kept_deletions\":"<<kept_del
    <<",\"retained_deletion_targets\":"<<deleted_targets
    <<",\"retained_hint_references\":"<<hints<<",\"retained_negative_hints\":"<<negative_hints
    <<",\"final_empty_clause_id\":"<<root_id<<",\"checker_required\":true}\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}
}
