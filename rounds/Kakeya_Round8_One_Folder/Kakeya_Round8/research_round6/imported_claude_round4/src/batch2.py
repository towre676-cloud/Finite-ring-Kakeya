"""Run the certified per-support test over (m, covering support orbit) jobs in parallel.
Each job: encode CNF, solve with CaDiCaL (proof logging), check proof with ./dratcheck, record hashes, delete files.
usage: batch.py m1,m2,.. smin smax out.jsonl [job_timeout_sec]"""
import sys, os, json, subprocess, hashlib, time
from concurrent.futures import ProcessPoolExecutor
HERE=os.path.dirname(os.path.abspath(__file__))
JOBTL=float(sys.argv[5]) if len(sys.argv)>5 else 1800

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def job(a):
    m,s,Tm,tmp=a
    t=time.time()
    base=f'{tmp}/m{m}_T{Tm}'
    try:
        out=subprocess.run([sys.executable,HERE+'/run_cert2.py',str(m),str(Tm),tmp],capture_output=True,text=True,timeout=JOBTL)
        r=json.loads(out.stdout.strip().splitlines()[-1])
    except subprocess.TimeoutExpired:
        for e in ('.cnf','.drat'):
            if os.path.exists(base+e): os.remove(base+e)
        return {'m':m,'s':s,'T':Tm,'status':'TIMEOUT','sec':round(time.time()-t,1)}
    except Exception as e:
        return {'m':m,'s':s,'T':Tm,'status':'ERROR','err':str(e)[:300]}
    r['s']=s; r['cnf_sha256']=sha(base+'.cnf')
    if r['sat']:
        r['status']='SAT_RELAXATION'
    else:
        c=subprocess.run([HERE+'/dratcheck',base+'.cnf',base+'.drat'],capture_output=True,text=True)
        r['drat_sha256']=sha(base+'.drat'); r['check']=c.stdout.strip()
        ok=c.returncode==0 and c.stdout.startswith('s VERIFIED')
        r['status']='EXCLUDED_DRAT_VERIFIED' if ok else 'CHECK_FAILED'
        os.remove(base+'.drat')
    os.remove(base+'.cnf')
    r['sec']=round(time.time()-t,1)
    return r

if __name__=='__main__':
    ms=[int(x) for x in sys.argv[1].split(',')]; kmin,kmax=int(sys.argv[2]),int(sys.argv[3]); outp=sys.argv[4]
    tmp=HERE+'/tmp'; os.makedirs(tmp,exist_ok=True)
    done=set()
    if os.path.exists(outp):
        for l in open(outp):
            r=json.loads(l)
            if r['status'] not in ('TIMEOUT','ERROR'): done.add((r['m'],r['T']))
    jobs=[]
    for l in open(HERE+'/../orbits_all.txt'):
        k,T,st,cov=map(int,l.split()); s=k+1
        if not cov or not(kmin<=s<=kmax): continue
        for m in ms:
            if (m,T) in done: continue
            if 2*(s-1)>93-m: continue   # every outer fibre in S has >=2 points
            jobs.append((m,s,T,tmp))
    print(len(jobs),'jobs',flush=True)
    with ProcessPoolExecutor(int(os.environ.get('NPROC','4'))) as ex, open(outp,'a') as f:
        for r in ex.map(job,jobs):
            f.write(json.dumps(r)+'\n'); f.flush()
            print(r['m'],r['s'],r['T'],r['status'],r.get('sec'),flush=True)
