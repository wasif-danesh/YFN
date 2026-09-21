"""Acquire official ABS and spatial sources directly into the dataset raw folder.

Public read-only requests only. Resumable cache; offline build is separate.
"""
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
import subprocess
from threading import Lock
from urllib.parse import urlencode
import xml.etree.ElementTree as ET
import zipfile
import shapefile

from melbourne_config import BASE, RAW, DOWNLOADS, WFS, PARKS


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    manifest_path = BASE / 'acquisition.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    lock = Lock()

    def fetch(name, url, refresh=False):
        target = RAW/name
        if not target.exists() or refresh:
            temp = target.with_suffix(target.suffix+'.part')
            subprocess.run(['curl','-sSL','--fail','--retry','3','--max-time','180',url,'-o',str(temp)],check=True)
            temp.replace(target)
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        with lock:
            if name in manifest and not refresh:
                assert manifest[name]['sha256']==digest and manifest[name]['url']==url, name
            else:
                manifest[name] = {'url':url,'file':'raw/'+name,'sha256':digest,'bytes':target.stat().st_size,
                    'retrieved_at':dt.datetime.fromtimestamp(target.stat().st_mtime,dt.timezone.utc).isoformat()}
            manifest_path.write_text(json.dumps(dict(sorted(manifest.items())),indent=2)+'\n')
        return target

    for name,url in DOWNLOADS.items(): fetch(name,url)
    z=zipfile.ZipFile(RAW/'SA2_2021_AUST_SHP_GDA2020.zip')
    reader=shapefile.Reader(**{e:io.BytesIO(z.read(next(n for n in z.namelist() if n.endswith('.'+e)))) for e in ['shp','shx','dbf']})
    codes=sorted(r.as_dict()['SA2_CODE21'] for r in reader.iterRecords() if r.as_dict()['GCC_CODE21']=='2GMEL')
    check_codes=sorted(set(codes[::60]+['206041117','213031348','212051568','212051567','206041127','206041507','210011227']))
    for code in check_codes:
        fetch(f'quickstats-{code}.html',f'https://www.abs.gov.au/census/find-census-data/quickstats/2021/{code}')
    fetch('rent-dictionary-2021.html','https://www.abs.gov.au/census/guide-census-data/census-dictionary/2021/variables-topic/housing/rent-weekly-dollar-values-rntd')
    hits_url = WFS+'?'+urlencode({'service':'WFS','version':'2.0.0','request':'GetFeature',
        'typeNames':'open-data-platform:ptal_metro','resultType':'hits'})
    hits = fetch('ptal-hits-before.xml',hits_url)
    total = int(ET.fromstring(hits.read_text()).attrib['numberMatched'])
    ids_url = PARKS+'/query?'+urlencode({'where':'1=1','returnIdsOnly':'true','f':'json'})
    ids = json.loads(fetch('parks-ids-before.json',ids_url).read_text())
    assert ids['objectIdFieldName']=='FID'
    park_ids = sorted(ids['objectIds'])
    assert len(set(park_ids))==len(park_ids)
    jobs=[]
    for start in range(0,total,5000):
        params={'service':'WFS','version':'2.0.0','request':'GetFeature','typeNames':'open-data-platform:ptal_metro',
            'outputFormat':'application/json','srsName':'EPSG:7844','count':5000,'startIndex':start}
        jobs.append((f'ptal-all-{start:06d}.json',WFS+'?'+urlencode(params)))
    for start in range(0,len(park_ids),500):
        # Short numeric ranges avoid URL-length limits. Exact IDs are reconciled
        # against the inventory during the offline build, including any gaps.
        batch=park_ids[start:start+500]
        params={'where':f'FID >= {batch[0]} AND FID <= {batch[-1]}','outFields':'*','returnGeometry':'true',
            'outSR':3857,'f':'json','orderByFields':'FID'}
        jobs.append((f'parks-all-{start:06d}.json',PARKS+'/query?'+urlencode(params)))
    print(f'Acquiring {total} PTAL cells and {len(park_ids)} open-space features in {len(jobs)} cached requests.',flush=True)
    def job(args):
        name,url=args
        p=fetch(name,url)
        d=json.loads(p.read_text())
        assert 'error' not in d and 'features' in d, (name,d)
        if name.startswith('ptal'):
            assert int(d['numberMatched'])==total
            assert d['numberReturned']==len(d['features'])
        else:
            assert not d.get('exceededTransferLimit',False),name
        return name,len(d['features'])
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i,(name,n) in enumerate(pool.map(job,jobs),1):
            if i%10==0 or i==len(jobs): print(f'{i}/{len(jobs)} files checked; {name}: {n} features',flush=True)
    # End inventory is refreshed on a resumed acquisition, while original chunks
    # stay immutable. The build additionally checks every unique feature ID.
    final_hits=ET.fromstring(fetch('ptal-hits-after.xml',hits_url,refresh=True).read_text())
    final_ids=json.loads(fetch('parks-ids-after.json',ids_url,refresh=True).read_text())
    assert int(final_hits.attrib['numberMatched'])==total
    assert sorted(final_ids['objectIds'])==park_ids
    print('Source inventories stable; acquisition complete.',flush=True)


if __name__=='__main__': main()
