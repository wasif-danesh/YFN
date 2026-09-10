"""Build display-only SA2 GeoJSON from the verified local ABS archive.

Run with the pipeline dependencies installed: python pipeline/build_homepage_map.py
No acquisition or database changes. Commit the generated asset and provenance together.
"""
import hashlib
import io
import json
import sqlite3
import zipfile
from pathlib import Path

import shapefile
from pyproj import CRS, Transformer
from shapely import coverage_is_valid, coverage_simplify
from shapely.geometry import shape, mapping
from shapely.ops import transform

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/greater-melbourne-v1'
OUTPUT = ROOT / 'frontend/public/maps'


def main():
    source = json.loads((DATA / 'acquisition.json').read_text())['SA2_2021_AUST_SHP_GDA2020.zip']
    archive = DATA / source['file']
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == source['sha256'], 'ABS source hash mismatch'
    with sqlite3.connect(f'file:{DATA / "yfn.sqlite"}?mode=ro', uri=True) as db:
        areas = {code: (name, bool(eligible)) for code, name, eligible in db.execute('SELECT sa2_code,name,is_comparable FROM areas')}
    with zipfile.ZipFile(archive) as z:
        stem = 'SA2_2021_AUST_GDA2020'
        crs = CRS.from_wkt(z.read(stem + '.prj').decode())
        assert crs.to_epsg() == 7844
        reader = shapefile.Reader(**{ext: io.BytesIO(z.read(f'{stem}.{ext}')) for ext in ('shp', 'shx', 'dbf')})
        project = Transformer.from_crs(crs, 7855, always_xy=True)
        records = []
        for item in reader.iterShapeRecords():
            record = item.record.as_dict()
            if record['GCC_CODE21'] != '2GMEL':
                continue
            code = record['SA2_CODE21']
            assert code in areas and record['SA2_NAME21'] == areas[code][0]
            geometry = transform(project.transform, shape(item.shape.__geo_interface__))
            assert geometry.is_valid and not geometry.is_empty
            records.append((code, geometry))
    records.sort(key=lambda item: item[0])
    assert len(records) == len(areas) == 361 and {code for code, _ in records} == set(areas)
    geometries = [geometry for _, geometry in records]
    assert coverage_is_valid(geometries), 'Source coverage requires review before simplifying'
    simplified = coverage_simplify(geometries, tolerance=30)
    assert coverage_is_valid(simplified)
    to_web = Transformer.from_crs(7855, 4326, always_xy=True)
    features = []
    for (code, original), geometry in zip(records, simplified):
        assert geometry.is_valid and not geometry.is_empty
        web = transform(to_web.transform, geometry)
        assert 143 < web.bounds[0] < web.bounds[2] < 147 and -40 < web.bounds[1] < web.bounds[3] < -36
        features.append({'type': 'Feature', 'properties': {'sa2_code': code, 'name': areas[code][0], 'boundary_year': 2021, 'is_comparable': areas[code][1]}, 'geometry': mapping(web)})
    payload = {'type': 'FeatureCollection', 'features': features}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(payload, separators=(',', ':')) + '\n').encode()
    (OUTPUT / 'greater-melbourne-sa2.geojson').write_bytes(encoded)
    provenance = {'source_url': source['url'], 'source_sha256': source['sha256'], 'licence': 'CC BY 4.0', 'attribution': 'Australian Bureau of Statistics, ASGS Edition 3, 2021 SA2 boundaries', 'boundary_year': 2021, 'feature_count': len(features), 'eligible_count': sum(value[1] for value in areas.values()), 'output_crs': 'EPSG:4326', 'simplification': 'Shapely coverage_simplify, tolerance 30 in EPSG:7855; shared edges preserved. Display only, never use for indicator calculations.', 'sha256': hashlib.sha256(encoded).hexdigest(), 'bytes': len(encoded)}
    (OUTPUT / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    print(f'PASS: {len(features)} valid, matched SA2s; topology preserved; {len(encoded):,} bytes')


if __name__ == '__main__':
    main()
