"""Losslessly compress the official formula/DRAT/LRAT files with exact hash gates.

Raw files are preserved. Only atomic .xz companions are written. Every companion
is decompressed and its exact bytes hashed before it is accepted for packaging.
"""
from pathlib import Path
import argparse,concurrent.futures,hashlib,json,lzma,time
HERE=Path(__file__).resolve().parent

def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def one(task):
 rel,expected,preset=task;src=HERE/rel;start=time.monotonic()
 import importlib.util
 spec=importlib.util.spec_from_file_location('round6_storage_compress',HERE.parent/'certificate_storage.py')
 storage=importlib.util.module_from_spec(spec);spec.loader.exec_module(storage)
 result=storage.compress_verified(src,expected,preset=preset,remove_raw=False)
 n=result.get('raw_bytes')
 if n is None:
  with storage.open_logical(src,prefer_compressed=True) as f:n=sum(len(b) for b in iter(lambda:f.read(1<<20),b''))
 return {'raw_path':rel,'xz_path':str(Path(result['compressed_path']).relative_to(HERE)),
  'uncompressed_sha256':expected,'uncompressed_bytes':n,
  'xz_sha256':result['xz_sha256'],'xz_bytes':result['xz_bytes'],'preset':preset,
  'seconds':round(time.monotonic()-start,6),'status':'PASS_DECOMPRESSED_BYTES_IDENTICAL'}

def main():
 p=argparse.ArgumentParser();p.add_argument('--jobs',type=int,default=2);p.add_argument('--preset',type=int,default=3);p.add_argument('--case-id',action='append',default=[]);args=p.parse_args()
 if not 1<=args.jobs<=3:raise ValueError('Use at most three compression workers')
 manifest=json.loads((HERE/'M19_CERTIFICATE_MANIFEST.json').read_text());tasks=[]
 for case in manifest['cases']:
  if args.case_id and case['case_id'] not in args.case_id:continue
  for key in ('cnf','proof','lrat'):tasks.append((case[key],case[key+'_sha256'],args.preset))
 out=HERE/('COMPRESSION_PILOT_RECEIPT.json' if args.case_id else 'COMPRESSION_RECEIPT.json');start=time.monotonic();rows=[]
 with concurrent.futures.ProcessPoolExecutor(args.jobs) as pool:
  for r in pool.map(one,tasks):
   rows.append(r);print(json.dumps({k:r[k] for k in ('raw_path','uncompressed_bytes','xz_bytes','seconds')}),flush=True)
   out.write_text(json.dumps({'status':'RUNNING','requested_files':len(tasks),'completed_files':len(rows),'files':rows},indent=2)+'\n')
 receipt={'status':'PASS_ALL_REQUESTED_COMPRESSIONS_BYTE_IDENTICAL','requested_files':len(tasks),'completed_files':len(rows),'uncompressed_bytes':sum(r['uncompressed_bytes'] for r in rows),'xz_bytes':sum(r['xz_bytes'] for r in rows),'seconds':round(time.monotonic()-start,6),'files':rows}
 out.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ('status','completed_files','uncompressed_bytes','xz_bytes','seconds')},indent=2))
if __name__=='__main__':main()
