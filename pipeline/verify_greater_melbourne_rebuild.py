"""Verify an existing release is byte-identical after an offline rebuild."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

from acquire_greater_melbourne import BASE


def main():
    files=sorted(set(list((BASE/'curated').glob('*.csv'))+
        list((BASE/'audit').glob('*.csv'))+
        [p for p in (BASE/'audit').glob('*.json') if p.name!='rebuild-check.json']+
        [BASE/n for n in ['sample.sqlite','sample-summary.csv','sample-summary.json','manifest.json','selected-sa2.geojson','schema-guide.md','data-dictionary.md']]))
    def hashes():return {str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    before=hashes();start=time.monotonic()
    subprocess.run([sys.executable,str(Path(__file__).with_name('build_greater_melbourne.py'))],check=True)
    subprocess.run([sys.executable,str(Path(__file__).with_name('document_greater_melbourne.py'))],check=True)
    after=hashes()
    changed=[n for n in before if before[n]!=after[n]]
    result={'status':'passed' if not changed else 'failed','files_compared':len(files),
        'changed_files':changed,'sha256_after':after,'rebuild_seconds':round(time.monotonic()-start,3),
        'scope':'Same saved raw snapshots and pipeline code, same runtime; acquisition not rerun.'}
    (BASE/'audit/rebuild-check.json').write_text(json.dumps(result,indent=2)+'\n')
    assert not changed,changed
    print(f'Byte-identical offline rebuild: {len(files)} files.',flush=True)


if __name__=='__main__':main()
