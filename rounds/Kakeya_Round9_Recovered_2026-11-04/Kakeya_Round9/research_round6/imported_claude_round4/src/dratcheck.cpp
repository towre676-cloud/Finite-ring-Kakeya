// Minimal forward DRAT checker (written for this project).
// Usage: dratcheck formula.cnf proof.drat   -> prints "s VERIFIED" and exits 0 iff the empty clause is derived
// Each lemma must be RUP w.r.t. the current clause database, or RAT on its first literal.
// Deletions of clauses currently acting as reasons for top-level assignments are ignored (as in drat-trim).
#include <bits/stdc++.h>
using namespace std;
struct Clause{ vector<int> lits; bool alive=true; };
static vector<Clause> db; static int nv=0;
static vector<signed char> val; // index by literal encoding
static vector<vector<int>> watches; static vector<int> trail; static vector<int> reason;
static size_t qhead=0;
static inline int enc(int l){ return l>0? 2*l : 2*(-l)+1; }
static inline int value(int l){ int v=val[abs(l)]; if(v==0) return 0; return (l>0)==(v>0)?1:-1; }
static void assign(int l,int r){ val[abs(l)]= l>0?1:-1; trail.push_back(l); reason[abs(l)]=r; }
static void ensure(int v){ if(v>nv){ nv=v; val.resize(nv+1,0); reason.resize(nv+1,-1); watches.resize(2*nv+2);} }
static bool propagate(){ // returns false on conflict
    while(qhead<trail.size()){
        int l=trail[qhead++]; int fl=-l; auto &ws=watches[enc(fl)];
        size_t i=0,j=0;
        for(;i<ws.size();i++){
            int ci=ws[i]; Clause &c=db[ci];
            if(!c.alive) continue; // drop
            auto &L=c.lits;
            if(L[0]==fl) swap(L[0],L[1]);
            if(value(L[0])==1){ ws[j++]=ci; continue; }
            bool found=false;
            for(size_t k=2;k<L.size();k++) if(value(L[k])!=-1){ swap(L[1],L[k]); watches[enc(L[1])].push_back(ci); found=true; break; }
            if(found) continue;
            ws[j++]=ci;
            if(value(L[0])==-1){ for(i++;i<ws.size();i++) ws[j++]=ws[i]; ws.resize(j); return false; }
            assign(L[0],ci);
        }
        ws.resize(j);
    }
    return true;
}
static bool topconflict=false;
static void backtrack(size_t sz){ while(trail.size()>sz){ int l=trail.back(); trail.pop_back(); val[abs(l)]=0; reason[abs(l)]=-1; } qhead=sz; }
static void addClause(vector<int> L){
    for(int l:L) ensure(abs(l));
    sort(L.begin(),L.end()); L.erase(unique(L.begin(),L.end()),L.end());
    for(size_t i=0;i+1<L.size();i++) if(L[i]==-L[i+1]) { db.push_back({L,false}); return; } // tautology: ignore
    // order: non-false first
    stable_partition(L.begin(),L.end(),[](int l){return value(l)!=-1;});
    int ci=db.size(); db.push_back({L,true});
    if(topconflict) return;
    if(L.empty() || value(L[0])==-1){ topconflict=true; return; }
    if(L.size()==1 || value(L[1])==-1){
        if(L.size()>=2){ watches[enc(L[0])].push_back(ci); watches[enc(L[1])].push_back(ci);} 
        if(value(L[0])==0){ assign(L[0],ci); if(!propagate()) topconflict=true; }
        return;
    }
    watches[enc(L[0])].push_back(ci); watches[enc(L[1])].push_back(ci);
}
static bool rup(const vector<int>& L){
    if(topconflict) return true;
    size_t sz=trail.size(); bool ok=false;
    for(int l:L){ int v=value(l); if(v==1){ ok=true; break;} if(v==0) assign(-l,-1); }
    if(!ok) ok=!propagate();
    backtrack(sz); return ok;
}
int main(int argc,char**argv){
    FILE*f=fopen(argv[1],"r"); char buf[1<<16]; long ncl=0;
    vector<int> cur; int x;
    // parse DIMACS
    while(true){ int c=fgetc(f); if(c==EOF) break; if(c=='c'||c=='p'){ if(!fgets(buf,sizeof buf,f)) break; continue;} ungetc(c,f);
        if(fscanf(f,"%d",&x)!=1) break; if(x==0){ addClause(cur); cur.clear(); ncl++; } else cur.push_back(x); }
    fclose(f);
    fprintf(stderr,"c parsed %ld clauses, %d vars\n",ncl,nv);
    // map for deletion lookup: sorted lits -> clause indices
    map<vector<int>,vector<int>> idx;
    for(size_t i=0;i<db.size();i++) if(db[i].alive){ auto k=db[i].lits; sort(k.begin(),k.end()); idx[k].push_back(i);} 
    FILE*p=fopen(argv[2],"r"); long nl=0,nd=0,nrat=0; bool del=false;
    while(true){ int c=fgetc(p); if(c==EOF) break; if(isspace(c)) continue; if(c=='d'){ del=true; continue;} ungetc(c,p);
        if(fscanf(p,"%d",&x)!=1) break; if(x){ cur.push_back(x); continue; }
        vector<int> L=cur; cur.clear();
        if(del){ del=false; nd++; auto k=L; sort(k.begin(),k.end()); k.erase(unique(k.begin(),k.end()),k.end()); auto it=idx.find(k);
            if(it!=idx.end() && !it->second.empty()){ int ci=it->second.back(); bool isreason=false;
                for(int l:db[ci].lits) if(value(l)==1 && reason[abs(l)]==ci) isreason=true;
                if(!isreason){ db[ci].alive=false; it->second.pop_back(); } }
            continue; }
        nl++;
        if(!rup(L)){
            // RAT on first literal
            if(L.empty()){ printf("s NOT VERIFIED (empty clause not RUP) at lemma %ld\n",nl); return 1; }
            int pv=L[0]; bool ok=true;
            for(size_t i=0;i<db.size()&&ok;i++){ if(!db[i].alive) continue; auto &D=db[i].lits; if(find(D.begin(),D.end(),-pv)==D.end()) continue;
                vector<int> R=L; for(int l:D) if(l!=-pv) R.push_back(l); if(!rup(R)) ok=false; }
            if(!ok){ printf("s NOT VERIFIED at lemma %ld\n",nl); return 1; }
            nrat++;
        }
        { auto k=L; sort(k.begin(),k.end()); k.erase(unique(k.begin(),k.end()),k.end()); int ci=db.size(); addClause(L); idx[k].push_back(ci); }
        if(topconflict){ printf("s VERIFIED lemmas=%ld deletions=%ld rat=%ld\n",nl,nd,nrat); return 0; }
    }
    printf("s NOT VERIFIED (no empty clause)\n"); return 1;
}
