"""Shared indicator calculations and geometry conversion helpers."""
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import transform, unary_union
from shapely.validation import make_valid

def growth(start, end):
    return None if start is None or end is None or start <= 0 else 100*(end-start)/start


def per_resident(area, population):
    return None if area is None or population is None or population <= 0 else area/population


def esri_polygon(rings):
    """Interpret Esri clockwise shells and counterclockwise holes explicitly."""
    shells = []
    holes = []
    for ring in rings:
        p = Polygon(ring)
        if p.exterior.is_ccw:
            holes.append(p)
        else:
            shells.append(p)
    assert shells, 'Esri polygon has no clockwise exterior'
    assigned = [[] for _ in shells]
    for hole in holes:
        parents = [(s.area,i) for i,s in enumerate(shells) if s.covers(hole.representative_point())]
        assert parents, 'Unassigned interior ring'
        assigned[min(parents)[1]].append(list(hole.exterior.coords))
    polygons = [Polygon(s.exterior.coords,assigned[i]) for i,s in enumerate(shells)]
    return polygons[0] if len(polygons)==1 else MultiPolygon(polygons)


def polygonal(g):
    if g.geom_type in ['Polygon','MultiPolygon']:
        return g
    return unary_union([polygonal(p) for p in getattr(g,'geoms',[]) if p.geom_type in ['Polygon','MultiPolygon','GeometryCollection']])


def projected(g, transformer, repairs, source, feature_id):
    p = transform(transformer.transform,g)
    if not p.is_valid:
        before = p.area
        p = polygonal(make_valid(p))
        repairs.append({'source':source,'feature_id':str(feature_id),'area_before_m2':before,'area_after_m2':p.area})
    assert p.is_valid and not p.is_empty
    return p

