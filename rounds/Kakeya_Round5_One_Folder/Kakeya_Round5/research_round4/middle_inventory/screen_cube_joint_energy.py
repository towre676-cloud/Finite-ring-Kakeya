"""Apply the proved cube-energy inequality to every residual middle profile.

Local pair energy and cube-edge surplus are optimized on one same spectrum.
The finite price bank L=2*lambda in8..16 supplies exact integer certificates.
"""
from collections import Counter
from functools import lru_cache
from pathlib import Path
import hashlib,json,time
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CENSUS=ROOT/'research_round2/geometric/PAIR_SPECTRUM_CENSUS.json'
histograms={int(w):sorted(tuple(r['hist']) for r in rows)
            for w,rows in json.loads(CENSUS.read_text())['weights'].items()}

@lru_cache(None)
def joint(w,r,L):
    rows=[]
    for ix,h in enumerate(histograms[w]):
        if w==8 and h[4]==7:
            continue
        energy=sum(p*p*n for p,n in enumerate(h))
        gain=sorted((max(0,2*min(16,4*p)-p*p-L)
                     for p,n in enumerate(h) for _ in range(n)),reverse=True)
        rows.append((energy+sum(gain[:r]),ix))
    return max(rows)

def branch(weights,r):
    rest=list(weights)
    for _ in range(r):rest.remove(8)
    values=[]
    for L in range(8,17):
        upper=7*L*r+(32-2*L)*(r*r//4)
        upper+=sum(joint(w,r,L)[0] for w in rest)
        values.append((upper,L))
    upper,L=min(values)
    return {'cubes':r,'twice_price':L,'upper_doubled':upper}

def main():
    started=time.monotonic();counts=Counter();by=Counter();cuts=[]
    input_path=HERE/'final_weight_survivors.txt'
    with (HERE/'after_cube_weight_survivors.txt').open('w') as survivors:
        for line in input_path.open():
            s,m,old,*ws=map(int,line.split());w=tuple(ws)
            assert len(w)==s and sum(w)==93 and w[0]==m
            branches=[]
            for r in range(w.count(8)+1):
                b=branch(w,r);branches.append(b)
                if b['upper_doubled']>=992:
                    survivors.write(line);counts['survives']+=1;by[s,m,'survives']+=1
                    break
            else:
                cuts.append({'weights':w,'support':s,'maximum':m,'branches':branches})
                counts['excluded']+=1;by[s,m,'excluded']+=1
    (HERE/'CUBE_JOINT_ENERGY_CUTS.jsonl').write_text(''.join(json.dumps(c,separators=(',',':'))+'\n' for c in cuts))
    table=[{'weight':w,'cubes':r,'twice_price':L,'bound':joint(w,r,L)[0],
            'attaining_spectrum_index':joint(w,r,L)[1]}
           for w in range(2,19) for r in range(11) for L in range(8,17)]
    (HERE/'CUBE_JOINT_LOCAL_TABLE.json').write_text(json.dumps({'census_sha256':hashlib.sha256(CENSUS.read_bytes()).hexdigest(),'rows':table},indent=2)+'\n')
    summary={'status':'PRODUCED','counts':dict(counts),'records':[{'support':s,'maximum':m,'status':status,'profiles':n} for (s,m,status),n in sorted(by.items())],'seconds':time.monotonic()-started}
    (HERE/'CUBE_JOINT_PRODUCER_COUNTS.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
