// Lossless storage codec for ASCII LRAT before ordinary XZ.
// Decode to ASCII, verify SHA256, then run CakeML on the unchanged CNF.
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
#include <sys/stat.h>
using i64=int64_t;using u64=uint64_t;
void put(std::ostream&o,u64 n){while(n>=128){o.put(char((n&127)|128));n>>=7;}o.put(char(n));}
u64 get(std::istream&i){
 u64 v=0;for(unsigned s=0;s<70;s+=7){int c=i.get();if(c<0)throw std::runtime_error("truncated varint");
  if(s==63&&(c&127)>1)throw std::runtime_error("overflow");
  v|=u64(c&127)<<s;if(!(c&128))return v;
 }throw std::runtime_error("varint too long");
}
u64 zig(i64 n){return n>=0?u64(n)*2:u64(-(n+1))*2+1;}
i64 unzig(u64 n){return n&1?-i64(n>>1)-1:i64(n>>1);}
i64 num(const char*&p,const char*e){
 bool neg=false;if(p<e&&*p=='-'){neg=true;++p;}const char*s=p;
 if(p==e||*p<'0'||*p>'9')throw std::runtime_error("noncanonical");
 i64 v=0;while(p<e&&*p>='0'&&*p<='9'){
  if(v>90000000000000000LL)throw std::runtime_error("noncanonical");
  v=v*10+(*p++-'0');
 }
 if((*s=='0'&&p-s>1)||(neg&&v==0))throw std::runtime_error("noncanonical");
 return neg?-v:v;
}
void sp(const char*&p,const char*e){if(p==e||*p!=' ')throw std::runtime_error("noncanonical");++p;}
void write_list(std::ostream&o,const std::vector<i64>&v){
 put(o,v.size());i64 prev=0;for(i64 x:v){put(o,zig(x-prev));prev=x;}
}
void read_list(std::istream&i,std::ostream&o){
 u64 n=get(i);if(n>1000000000ULL)throw std::runtime_error("list too big");
 i64 prev=0;for(u64 k=0;k<n;k++){prev+=unzig(get(i));o<<' '<<prev;}
}
int main(int argc,char**argv){
 try{
  if(argc!=4)throw std::runtime_error("usage: lrat_pack pack|unpack input output");
  struct stat a{},b{};if(!stat(argv[2],&a)&&!stat(argv[3],&b)&&a.st_dev==b.st_dev&&a.st_ino==b.st_ino)
   throw std::runtime_error("output equals input");
  std::ifstream in(argv[2],std::ios::binary);std::ofstream out(argv[3],std::ios::binary|std::ios::trunc);
  if(!in||!out)throw std::runtime_error("cannot open streams");
  const std::string magic="KLRAT01\n";i64 previous=0;u64 lines=0,raw_lines=0,integers=0;
  if(std::string(argv[1])=="pack"){
   out<<magic;std::string line;
   while(std::getline(in,line)){
    ++lines;bool newline=!in.eof(),canonical=newline;std::vector<i64> clause,hints;i64 id=0;int type=0;
    if(canonical)try{
     const char*p=line.data(),*e=p+line.size();id=num(p,e);if(id<=0)throw std::runtime_error("noncanonical");sp(p,e);
     if(p<e&&*p=='d'){type=1;++p;sp(p,e);}
     if(type==0)while(true){i64 n=num(p,e);sp(p,e);if(!n)break;clause.push_back(n);}
     while(true){i64 n=num(p,e);if(!n)break;hints.push_back(n);sp(p,e);}
     if(p!=e)throw std::runtime_error("noncanonical");
    }catch(const std::exception&){canonical=false;}
    if(!canonical){
     out.put(char(2));put(out,line.size()+(newline?1:0));out<<line;if(newline)out<<'\n';++raw_lines;continue;
    }
    out.put(char(type));put(out,zig(id-previous));previous=id;
    if(type==0)write_list(out,clause);
    write_list(out,hints);integers+=1+clause.size()+hints.size();
   }
  }else if(std::string(argv[1])=="unpack"){
   std::string got(magic.size(),'\0');in.read(got.data(),got.size());if(got!=magic)throw std::runtime_error("bad magic");
   while(true){
    int type=in.get();if(type<0)break;++lines;
    if(type==2){
     u64 n=get(in);if(n>1000000000ULL)throw std::runtime_error("raw line too big");
     std::string raw(n,'\0');in.read(raw.data(),n);if(u64(in.gcount())!=n)throw std::runtime_error("truncated raw line");
     out.write(raw.data(),n);++raw_lines;continue;
    }
    if(type!=0&&type!=1)throw std::runtime_error("bad type");
    previous+=unzig(get(in));if(previous<=0)throw std::runtime_error("bad ID");out<<previous;
    if(type==0){read_list(in,out);out<<" 0";}else out<<" d";
    read_list(in,out);out<<" 0\n";
   }
  }else throw std::runtime_error("bad operation");
  out.flush();if(!out)throw std::runtime_error("write failure");
  std::cerr<<"{\"status\":\"STORAGE_CODEC_COMPLETE\",\"operation\":\""<<argv[1]<<"\",\"lines\":"<<lines
   <<",\"raw_lines\":"<<raw_lines<<",\"integers\":"<<integers<<",\"output_bytes\":"<<u64(out.tellp())
   <<",\"decode_sha256_and_cakeml_required\":true}\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
}
