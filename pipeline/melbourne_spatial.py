"""Complete-layer spatial indexes and independently checked source inventories."""
import json
import math
import xml.etree.ElementTree as ET

import numpy as np
import shapely
from shapely import STRtree
from shapely.geometry import shape
from shapely.ops import transform

from melbourne_common import esri_polygon, projected, polygonal


def geodesic_area(geometry, geod):
    from shapely.geometry.polygon import orient
    if geometry.is_empty: return 0.0
    if geometry.geom_type=='Polygon':
        return abs(geod.geometry_area_perimeter(orient(geometry))[0])
    return sum(geodesic_area(g,geod) for g in geometry.geoms)


class SpatialSources:
    def __init__(self, raw, to_area, parks_to_area, repairs):
        self.ptal=[]; self.parks=[]; pg=[]; og=[]
        expected=int(ET.fromstring((raw/'ptal-hits-before.xml').read_text()).attrib['numberMatched'])
        after=int(ET.fromstring((raw/'ptal-hits-after.xml').read_text()).attrib['numberMatched'])
        assert expected==after
        for path in sorted(raw.glob('ptal-all-*.json')):
            d=json.loads(path.read_text())
            assert int(d['numberMatched'])==expected
            assert d['numberReturned']==len(d['features'])
            assert d['crs']['properties']['name'].endswith('7844')
            # Vectorized transformation reduces Python overhead for 360k cells.
            assert all(f['geometry'] is not None for f in d['features']),path.name
            geometries=shapely.get_parts(shapely.from_geojson(json.dumps(d)))
            assert len(geometries)==len(d['features'])
            transformed=shapely.transform(geometries,to_area.transform,interleaved=False)
            for f,g in zip(d['features'],transformed):
                if not g.is_valid:
                    before=g.area; g=polygonal(shapely.make_valid(g))
                    repairs.append({'source':'ptal','feature_id':f['id'],'area_before_m2':before,'area_after_m2':g.area})
                assert g.is_valid and not g.is_empty
                value=f['properties']['sum_ai_8_9']
                assert value is None or (isinstance(value,(int,float)) and math.isfinite(value) and value>=0)
                self.ptal.append({'id':f['id'],'properties':f['properties'],'source_file':path.name})
                pg.append(g)
        assert len(self.ptal)==expected
        assert len({f['id'] for f in self.ptal})==expected, 'PTAL pagination duplicates or omissions'
        print(f'Indexed {len(pg)} unique PTAL cells.',flush=True)
        before_ids=json.loads((raw/'parks-ids-before.json').read_text())['objectIds']
        after_ids=json.loads((raw/'parks-ids-after.json').read_text())['objectIds']
        assert set(before_ids)==set(after_ids)
        for path in sorted(raw.glob('parks-all-*.json')):
            d=json.loads(path.read_text())
            assert not d.get('exceededTransferLimit',False)
            assert d['spatialReference'].get('latestWkid',d['spatialReference'].get('wkid'))==3857
            for f in d['features']:
                assert f.get('geometry') is not None,(path.name,f['attributes']['FID'])
                g=projected(esri_polygon(f['geometry']['rings']),parks_to_area,repairs,'open-space',f['attributes']['FID'])
                self.parks.append({'attributes':f['attributes'],'source_file':path.name})
                og.append(g)
        actual=[f['attributes']['FID'] for f in self.parks]
        assert len(actual)==len(set(actual))==len(before_ids)
        assert set(actual)==set(before_ids)
        print(f'Indexed {len(og)} unique open-space features.',flush=True)
        self.pg=np.array(pg,dtype=object); self.og=np.array(og,dtype=object)
        self.ptree=STRtree(self.pg); self.otree=STRtree(self.og)
        self.inventory={'ptal_unique_features':len(pg),'open_space_unique_features':len(og),
            'ptal_counts_stable':True,'park_id_inventory_stable':True,'no_duplicate_ids':True,
            'all_source_geometries_present_and_valid_after_documented_repairs':True}

    def ptal_candidates(self, area):
        return [(self.ptal[i],self.pg[i]) for i in sorted(self.ptree.query(area))]

    def park_candidates(self, area):
        return [(self.parks[i],self.og[i]) for i in sorted(self.otree.query(area))]
