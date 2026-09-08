"""Acquire public source snapshots for the four-area schema investigation.

Network is used only here. build_real_sample.py runs offline on saved inputs.
Requires pyshp, shapely and pyproj, plus curl on PATH.
"""
import datetime as dt
import hashlib
import io
import json
from pathlib import Path
import subprocess
from urllib.parse import urlencode
import zipfile

import shapefile
from shapely.geometry import shape
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/samples/real-sa2-v1'
RAW = BASE / 'raw'
NAMES = ['Carlton', 'Footscray', 'Clayton - Central', 'Clayton (North) - Notting Hill']
WFS = 'https://opendata.maps.vic.gov.au/geoserver/wfs'
PARKS = 'https://services5.arcgis.com/DmRfik4clMVydXO3/arcgis/rest/services/VPA_Draft_Open_Space_Data/FeatureServer/0'
ABS = 'https://www.abs.gov.au'
DOWNLOADS = {
    '32180DS0003_2001-25.xlsx': ABS + '/statistics/people/population/regional-population/2024-25/32180DS0003_2001-25.xlsx',
    '2021_GCP_SA2_for_VIC_short-header.zip': ABS + '/census/find-census-data/datapacks/download/2021_GCP_SA2_for_VIC_short-header.zip',
    'SA2_2021_AUST_SHP_GDA2020.zip': ABS + '/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files/SA2_2021_AUST_SHP_GDA2020.zip',
    'open-space-layer.json': PARKS + '?f=pjson',
    'open-space-catalogue.json': 'https://discover.data.vic.gov.au/api/3/action/package_show?id=open-space',
    'ptal-catalogue.json': 'https://discover.data.vic.gov.au/api/3/action/package_show?id=public-transport-accessibility-level-ptal-melbourne-metro',
    'ptal-schema.xml': WFS + '?' + urlencode({'service':'WFS','version':'2.0.0','request':'DescribeFeatureType','typeNames':'open-data-platform:ptal_metro'}),
    'ptal-metadata.xml': 'https://metashare.maps.vic.gov.au/geonetwork/srv/api/records/ca93f889-e9a2-4774-b7c5-dab6cb2ea2aa/formatters/xml',
}


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    manifest_path = BASE / 'acquisition.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

    def fetch(name, url):
        target = RAW / name
        if not target.exists():
            temporary = target.with_suffix(target.suffix + '.part')
            subprocess.run(['curl','-sSL','--fail','--retry','2','--max-time','90',url,'-o',str(temporary)],check=True)
            temporary.replace(target)
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        if name in manifest:
            assert manifest[name]['sha256'] == digest, f'Snapshot changed: {name}'
            assert manifest[name]['url'] == url, f'Request changed: {name}'
        else:
            manifest[name] = {'url':url,'file':'raw/'+name,'sha256':digest,'bytes':target.stat().st_size,
                'retrieved_at':dt.datetime.fromtimestamp(target.stat().st_mtime,dt.timezone.utc).isoformat()}
        manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
        return target

    for name,url in DOWNLOADS.items():
        fetch(name,url)
    z = zipfile.ZipFile(RAW/'SA2_2021_AUST_SHP_GDA2020.zip')
    parts = {suffix:io.BytesIO(z.read(next(n for n in z.namelist() if n.endswith('.'+suffix)))) for suffix in ['shp','shx','dbf']}
    reader = shapefile.Reader(**parts)
    features = []
    for sr in reader.iterShapeRecords():
        record = sr.record.as_dict()
        if record['SA2_NAME21'] in NAMES:
            assert record['GCC_CODE21'] == '2GMEL'
            features.append({'type':'Feature','properties':record,'geometry':sr.shape.__geo_interface__})
    assert len(features) == len(NAMES)
    (BASE/'selected-sa2.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features})+'\n')
    tx = Transformer.from_crs(7844,3857,always_xy=True)
    for f in features:
        code = f['properties']['SA2_CODE21']
        bounds = shape(f['geometry']).bounds
        # Bounding boxes acquire candidate features only; exact clipping occurs offline.
        bbox = ','.join(str(v) for v in bounds)
        params = {'service':'WFS','version':'2.0.0','request':'GetFeature','typeNames':'open-data-platform:ptal_metro',
            'outputFormat':'application/json','srsName':'EPSG:7844','cql_filter':f"BBOX(geom,{bbox},'EPSG:7844')",'count':5000,'startIndex':0}
        count = 0
        while True:
            params['startIndex'] = count
            path = fetch(f'ptal-{code}-{count}.json', WFS+'?'+urlencode(params))
            response = json.loads(path.read_text())
            assert response['type'] == 'FeatureCollection'
            n = len(response['features'])
            count += n
            if count >= int(response['numberMatched']): break
            assert n > 0
        x0,y0,x1,y1 = tx.transform_bounds(*bounds,densify_pts=21)
        envelope = ','.join(str(v) for v in [x0-50,y0-50,x1+50,y1+50])
        params = {'where':'1=1','geometry':envelope,'geometryType':'esriGeometryEnvelope','inSR':3857,
            'spatialRel':'esriSpatialRelIntersects','f':'json'}
        count_path = fetch(f'parks-count-{code}.json',PARKS+'/query?'+urlencode({**params,'returnCountOnly':'true'}))
        expected = json.loads(count_path.read_text())['count']
        fetched = 0
        while fetched < expected:
            q = {**params,'outFields':'*','returnGeometry':'true','outSR':3857,'orderByFields':'FID','resultOffset':fetched,'resultRecordCount':1000}
            path = fetch(f'parks-{code}-{fetched}.json',PARKS+'/query?'+urlencode(q))
            response = json.loads(path.read_text())
            assert 'error' not in response,response
            n = len(response['features'])
            assert n > 0
            fetched += n
        assert fetched == expected
        print(f"{f['properties']['SA2_NAME21']}: {count} PTAL candidates; {fetched} open-space candidates",flush=True)


if __name__ == '__main__':
    main()
