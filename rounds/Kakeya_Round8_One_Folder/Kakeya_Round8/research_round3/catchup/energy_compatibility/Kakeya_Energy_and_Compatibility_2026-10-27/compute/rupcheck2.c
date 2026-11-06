/* rupcheck2: independent forward RUP checker for DRUP proofs, with persistent top-level
   propagation and deletion support.
   Soundness: the database only ever contains formula clauses and lemmas already checked; a
   deletion only removes a clause (weakening), and deletions of clauses satisfied at top level are
   ignored (keeping a valid clause is always sound).  A lemma is accepted iff unit propagation on
   (database + negated lemma) reaches a conflict.  Output: VERIFIED ... / FAIL ...  */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct { int *l; int n; int dead; unsigned h; } Cl;
static Cl *C; static int nC, capC;
static int **W, *Wn, *Wc; static int nv;
static signed char *val; static int *trail; static int nt, ntop; static int topconf = 0;
#define HB (1<<22)
static int *hh, *hn; static int hcap;
static unsigned chash(int *l, int n){ unsigned a=0,b=1,c=0; for(int i=0;i<n;i++){ a ^= (unsigned)l[i]*2654435761u; b *= (unsigned)(2*l[i]+7); c += (unsigned)(l[i]*l[i]); } return a^b^c^(unsigned)n; }
static int Lx(int x){ return x>0 ? 2*x : 2*(-x)+1; }
static int value(int x){ int v=val[abs(x)]; if(!v) return 0; return ((x>0)==(v>0)) ? 1 : -1; }
static void setv(int x){ val[abs(x)] = x>0 ? 1 : -1; trail[nt++] = x; }
static void watch(int lit, int ci){ int k=Lx(lit); if(Wn[k]==Wc[k]){ Wc[k]=Wc[k]?2*Wc[k]:4; W[k]=realloc(W[k],Wc[k]*sizeof(int)); } W[k][Wn[k]++]=ci; }
static int propagate(int qh){ /* returns 1 on conflict */
  while(qh < nt){
    int fl = -trail[qh++]; int k = Lx(fl); int j = 0;
    while(j < Wn[k]){
      int ci = W[k][j];
      if(C[ci].dead){ W[k][j] = W[k][--Wn[k]]; continue; }
      int *c = C[ci].l, m = C[ci].n;
      if(c[0] == fl){ c[0] = c[1]; c[1] = fl; }
      if(c[1] != fl){ W[k][j] = W[k][--Wn[k]]; continue; }   /* stale watch */
      if(value(c[0]) == 1){ j++; continue; }
      int moved = 0;
      for(int t=2;t<m;t++) if(value(c[t]) != -1){ int y=c[t]; c[t]=c[1]; c[1]=y; watch(y,ci); W[k][j]=W[k][--Wn[k]]; moved=1; break; }
      if(moved) continue;
      if(value(c[0]) == 0){ setv(c[0]); j++; continue; }
      return 1;
    }
  }
  return 0;
}
static int sameset(int *a,int na,int *b,int nb){ if(na!=nb) return 0; for(int i=0;i<na;i++){ int f=0; for(int j=0;j<nb;j++) if(a[i]==b[j]){f=1;break;} if(!f) return 0;} return 1; }
static void add(int *l, int n){
  if(nC==capC){ capC=capC?2*capC:1<<16; C=realloc(C,capC*sizeof(Cl)); }
  if(nC>=hcap){ hcap=hcap?2*hcap:1<<20; hn=realloc(hn,hcap*sizeof(int)); }
  int ci = nC++; C[ci].l = malloc((n?n:1)*sizeof(int)); memcpy(C[ci].l,l,n*sizeof(int)); C[ci].n=n; C[ci].dead=0; C[ci].h=chash(l,n);
  unsigned b = C[ci].h & (HB-1); hn[ci]=hh[b]; hh[b]=ci;
  if(topconf) return;
  if(n==0){ topconf=1; return; }
  /* order: non-false literals first */
  int *c = C[ci].l, p = 0;
  for(int i=0;i<n;i++) if(value(c[i]) != -1){ int y=c[p]; c[p]=c[i]; c[i]=y; p++; }
  if(n >= 2){ watch(c[0],ci); watch(c[1],ci); }
  if(p == 0){ topconf = 1; return; }
  if(p == 1 && value(c[0]) == 0){ int q = nt; setv(c[0]); if(propagate(q)) topconf = 1; ntop = nt; }
}
static void del(int *l, int n){
  if(n < 2) return;
  unsigned h = chash(l,n);
  for(int i=hh[h&(HB-1)]; i>=0; i=hn[i]) if(!C[i].dead && C[i].h==h && sameset(C[i].l,C[i].n,l,n)){
    for(int t=0;t<C[i].n;t++) if(value(C[i].l[t]) == 1) return;   /* satisfied at top level: keep */
    C[i].dead = 1; return; }
}
static int rup(int *l, int n){
  if(topconf) return 1;
  int q = nt, conf = 0;
  for(int i=0;i<n && !conf;i++){ int v=value(-l[i]); if(v==-1) conf=1; else if(v==0) setv(-l[i]); }
  if(!conf) conf = propagate(q);
  for(int i=nt-1;i>=q;i--) val[abs(trail[i])] = 0;
  nt = q; return conf;
}
static int readcl(FILE *f, int *buf, int *n, int *isdel){
  int x, c; *n=0; *isdel=0;
  for(;;){ c=fgetc(f); if(c==EOF) return 0;
    if(c=='c'||c=='p'){ while((c=fgetc(f))!='\n' && c!=EOF); continue; }
    if(c=='d'){ *isdel=1; continue; }
    if(c==' '||c=='\n'||c=='\t'||c=='\r') continue;
    ungetc(c,f); break; }
  while(fscanf(f,"%d",&x)==1){ if(x==0) return 1; if(abs(x)>=nv){ fprintf(stderr,"var out of range\n"); exit(2);} buf[(*n)++]=x; }
  return 0;
}
int main(int argc, char **argv){
  FILE *f=fopen(argv[1],"r"); char line[256]; int ncl;
  while(fgets(line,256,f)) if(line[0]=='p'){ sscanf(line,"p cnf %d %d",&nv,&ncl); break; }
  nv += 2;
  hh=malloc(HB*sizeof(int)); for(int i=0;i<HB;i++) hh[i]=-1;
  W=calloc(2*nv+2,sizeof(int*)); Wn=calloc(2*nv+2,sizeof(int)); Wc=calloc(2*nv+2,sizeof(int));
  val=calloc(nv+1,1); trail=malloc((nv+1)*sizeof(int)); int *buf=malloc((nv+1)*sizeof(int)); int n,d;
  while(readcl(f,buf,&n,&d)) add(buf,n); fclose(f);
  f=fopen(argv[2],"r"); long a=0, dl=0;
  while(readcl(f,buf,&n,&d)){
    if(d){ dl++; del(buf,n); continue; }
    if(!rup(buf,n)){ printf("FAIL: lemma %ld not RUP\n",a); return 1; }
    if(n==0){ printf("VERIFIED (empty clause reached) lemmas=%ld deletions=%ld\n",a,dl); return 0; }
    add(buf,n); a++;
  }
  if(rup(buf,0)){ printf("VERIFIED (empty clause RUP at end) lemmas=%ld deletions=%ld\n",a,dl); return 0; }
  printf("FAIL: empty clause not derived\n"); return 1;
}
