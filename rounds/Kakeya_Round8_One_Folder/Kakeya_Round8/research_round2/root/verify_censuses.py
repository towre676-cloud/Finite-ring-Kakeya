"""Compile independent exact finite-census checkers and compare all records."""
import csv,json,subprocess,tempfile,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];GEO=ROOT/'research_round2/geometric'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='kakeya_censuses_') as tmp:
 tmp=Path(tmp)
 for stem in('verify_pair_spectra','verify_block_census'):
  exe=tmp/stem;outfile=tmp/(stem+'.csv')
  subprocess.run(['g++','-O3','-std=c++17',str(HERE/(stem+'.cpp')),'-o',str(exe)],check=True)
  run=subprocess.run([str(exe),str(outfile)],check=True,text=True,capture_output=True)
  records=list(csv.reader(outfile.open()))
  if stem=='verify_pair_spectra':
   path=GEO/'PAIR_SPECTRUM_CENSUS.json';j=json.loads(path.read_text());c={w:set() for w in range(1,20)}
   for row in records:c[int(row[0])].add(tuple(map(int,row[1:])))
   counts=[]
   for w in range(1,20):
    expected={tuple(x['hist']) for x in j['weights'][str(w)]};assert expected==c[w]
    for x in j['weights'][str(w)]:
     A={v for v in range(32) if x['mask']>>v&1};assert len(A)==w
     ps=[len(A&{v^d for v in A})//2 for d in range(1,32)]
     assert [ps.count(i) for i in range(10)]==x['hist']
    counts.append({'weight':w,'spectra':len(expected)})
   out={'status':'PASS','method':'Independent normalized-set census recomputes unordered differences; all witness masks checked directly. Complements cover17–19.','normalized_sets_by_rank':j['normalized_sets_by_rank'],'counts':counts,'census_sha256':sha(path)}
   target=HERE/'ROOT_VERIFIED_PAIR_SPECTRUM_CENSUS.json'
  else:
   path=GEO/'PAIRED_BLOCK_MAXIMUM_CENSUS.json';j=json.loads(path.read_text());c={(w,f):set() for w in range(2,20) for f in(0,1)}
   for row in records:
    w,f,*h=map(int,row);c[w,f].add(tuple(h))
   counts={}
   for w in range(2,20):
    counts[str(w)]={}
    for f in(0,1):
     expected={tuple(x['hist']) for x in j['weights'][str(w)][str(f)]};assert expected==c[w,f]
     for x in j['weights'][str(w)][str(f)]:
      A={v for v in range(32) if x['mask']>>v&1};a=x['own_direction'];assert len(A)==w
      ps=[len(A&{v^d for v in A})//2 for d in range(32)]
      hh=[max(ps[d],ps[d^a]) for d in range(1,32) if d<(d^a)]
      assert bool(ps[a])==bool(f) and ps[a]==x['own_pairs']
      assert [hh.count(i) for i in range(10)]==x['hist']
     counts[str(w)][str(f)]=len(expected)
   out={'status':'PASS','source_affine_census_dependency':False,'method':'Positive own pair normalized to0,e1 and extended to affine basis; every zero-pair own direction checked on every normalized subset. Complements supply17–19. All witness masks checked.','counts':counts,'block_census_sha256':sha(path)}
   target=HERE/'ROOT_VERIFIED_BLOCK_CENSUS.json'
  target.write_text(json.dumps(out,indent=2)+'\n');print(stem,'PASS',flush=True)
