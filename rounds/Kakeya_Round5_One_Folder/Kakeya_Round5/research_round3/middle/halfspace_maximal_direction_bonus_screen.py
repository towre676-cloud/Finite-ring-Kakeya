from pathlib import Path
from collections import Counter
import json
HERE=Path(__file__).resolve().parent
quota=lambda w:(w&-w)-1 if w%2==0 else max((w-1)&-(w-1),(w+1)&-(w+1))-1
out=[];cuts=[];rem=[]
for line in(HERE/'support18_after_nine_heavy.jsonl').open():
 r=json.loads(line);w=r['weights'];H=w[:8];L=w[8:];Q=sum(v*v//4 for v in L);caps=sorted((v//2 for v in L),reverse=True);X=sum(caps[:6]);bonus=[]
 for v in H:
  c=v//2
  if c>4:
   rf=min(6,(quota(v)+1)//2);B=(c-5)*X+sum(caps[:rf]);bonus.append({'weight':v,'maximal_directions_in_halfspace':rf,'pair_mass_upper':X,'maximal_direction_pair_mass_upper':sum(caps[:rf]),'bonus':B})
 upper=4*Q+sum(b['bonus'] for b in bonus)
 rec=dict(r,halfspace_period_bonus_capacity=upper,halfspace_low_pair_mass_upper=Q,halfspace_period_bonuses=bonus);out.append(rec)
 (cuts if r['slot_full_upper_doubled']<288 and upper<96 else rem).append(rec)
(HERE/'HALFSPACE_MAXIMAL_DIRECTION_BONUS_SCREEN.jsonl').write_text(''.join(json.dumps(r,separators=(',',':'))+'\n' for r in out))
(HERE/'support18_after_period_bonus.jsonl').write_text(''.join(json.dumps(r,separators=(',',':'))+'\n' for r in rem))
print('cuts',len(cuts),Counter(r['maximum'] for r in cuts),'remaining',len(rem),Counter(r['maximum'] for r in rem))
for r in rem:print(r['maximum'],r['weights'],r['slot_full_upper_doubled'],r['halfspace_period_bonus_capacity'])
