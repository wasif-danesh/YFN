"""Check the committed display map against SQLite without GIS dependencies."""
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / 'frontend/public/maps'
DATA = ROOT / 'data/greater-melbourne-v1'


def main():
    content = (MAPS / 'greater-melbourne-sa2.geojson').read_bytes()
    provenance = json.loads((MAPS / 'provenance.json').read_text())
    source = json.loads((DATA / 'acquisition.json').read_text())['SA2_2021_AUST_SHP_GDA2020.zip']
    assert hashlib.sha256(content).hexdigest() == provenance['sha256']
    assert len(content) == provenance['bytes']
    assert provenance['source_sha256'] == source['sha256']
    with sqlite3.connect(f'file:{DATA / "yfn.sqlite"}?mode=ro', uri=True) as db:
        expected = {code: (name, year, bool(eligible)) for code, name, year, eligible in db.execute('SELECT sa2_code,name,boundary_year,is_comparable FROM areas')}
    collection = json.loads(content)
    assert collection['type'] == 'FeatureCollection'
    actual = {}
    for feature in collection['features']:
        p = feature['properties']; code = p['sa2_code']
        assert isinstance(code, str) and code not in actual
        actual[code] = (p['name'], p['boundary_year'], p['is_comparable'])
        geometry = feature['geometry']; assert geometry['type'] in ('Polygon', 'MultiPolygon')
        polygons = [geometry['coordinates']] if geometry['type'] == 'Polygon' else geometry['coordinates']
        assert polygons
        for polygon in polygons:
            assert polygon
            for ring in polygon:
                assert len(ring) >= 4 and ring[0] == ring[-1]
                assert all(len(point) == 2 and 143 < point[0] < 147 and -40 < point[1] < -36 for point in ring)
    assert actual == expected
    assert len(actual) == provenance['feature_count']
    assert sum(row[2] for row in actual.values()) == provenance['eligible_count']
    print(f'PASS: map hash, coordinates, and all {len(actual)} SA2 identities/eligibility match the database.')


if __name__ == '__main__':
    main()
