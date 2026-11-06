"""Reproduce the standalone energy12 audit; Python stdlib plus a C++ compiler.

Reads only the adjacent newly authored C++ source. No prior Kakeya census,
saved energy values, affine-orbit list, or previous producer is loaded.
"""
from hashlib import sha256
from itertools import combinations,product
import json
from pathlib import Path
import subprocess
import tempfile
import time

HERE=Path(__file__).resolve().parent

def affine_rank(a):
    pivots={}
    for x in a:
        y=x^a[0]
        while y:
            k=y.bit_length()-1
            if k in pivots:y^=pivots[k]
            else:pivots[k]=y;break
    return len(pivots)

def control_witness(a):
    points=set(a)
    counts=[len(points & {x^d for x in points})//2 for d in range(1,32)]
    energy=sum(p*p for p in counts)
    planes=sum(x^y^z^t==0 for x,y,z,t in combinations(a,4))
    assert energy==66+6*planes
    return dict(affine_rank=affine_rank(a),energy=energy,planes=planes,
                directional_pair_counts=counts)

def main():
    start=time.monotonic()
    source=HERE/'verify_energy12.cpp'
    with tempfile.TemporaryDirectory(prefix='energy12_fresh_') as temp:
        executable=Path(temp)/'verify_energy12'
        command=['g++','-O3','-std=c++17',str(source),'-o',str(executable)]
        subprocess.run(command,check=True,capture_output=True,text=True)
        run=subprocess.run([str(executable)],check=True,capture_output=True,text=True)
    result=json.loads(run.stdout)
    assert result['status']=='PASS' and result['reads_prior_census'] is False
    assert result['maximum_energy']==300 and result['total_normalized_sets_checked']==230560
    for r,count,maximum,planes in ((4,330,300,39),(5,230230,222,26)):
        row=result['ranks'][r-4]
        assert (row['affine_rank'],row['normalized_sets_checked'],row['maximum_energy'],row['maximum_affine_planes'])==(r,count,maximum,planes)
        assert sum(row['energy_histogram'].values())==count
        assert max(map(int,row['energy_histogram']))==maximum
        assert row['energy_histogram'][str(maximum)]==row['normalized_maximizers']
        w=control_witness(row['witness'])
        assert (w['affine_rank'],w['energy'],w['planes'])==(r,maximum,planes)
        row['independent_witness_control']=w
    # The exact finite occupancy inequalities used in the analytic8+4 case.
    patterns=[p for p in product(range(5),repeat=4) if sum(p)==8]
    noncube=[p for p in patterns if sorted(p)!=[0,0,4,4]]
    assert max(sum(x*(x-1)//2 for x in p) for p in noncube)==9
    tetra=[k*(k-1)//2-max(0,k-4)+(8-k)*(7-k)//2-max(0,4-k) for k in range(1,8)]
    assert tetra==[18,14,12,12,12,14,18]
    assert [211+0+11,153+1+20+6*5,120+3+27+6*12]==[222,204,222]
    assert 66+6*((1<<5)-1)==252<300
    record=dict(status='PASS_STANDALONE_ENERGY12_AUDIT',
        theorem='Every binary twelve-point set has Q<=300, with equality exactly an affine4-flat minus an affine plane.',
        analytic_rank5_bound=222,analytic_higher_rank_bound=252,
        proof='ENERGY12_ANALYTIC_PROOF.md',
        enumeration=result,
        analytic_occupancy_controls={'plane_non_cube_max_pairs':9,'tetrahedron_two_coset_pair_bounds':tetra},
        source_sha256=sha256(source.read_bytes()).hexdigest(),
        proof_sha256=sha256((HERE/'ENERGY12_ANALYTIC_PROOF.md').read_bytes()).hexdigest(),
        reviewer_scope='A new model-authored implementation and analytic derivation, not epistemically independent human review or Lean formalization.',
        seconds=round(time.monotonic()-start,6))
    (HERE/'ENERGY12_ENUMERATION.json').write_text(json.dumps(result,indent=2)+'\n')
    (HERE/'ENERGY12_REPLAY_RECEIPT.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:record[k] for k in ('status','theorem','analytic_rank5_bound','analytic_higher_rank_bound','seconds')},indent=2))

if __name__=='__main__':main()
