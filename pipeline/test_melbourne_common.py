"""Targeted regression checks for the sample's calculation and storage risks."""
import math
from pathlib import Path
import sqlite3
import unittest

from shapely.geometry import Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

from melbourne_common import esri_polygon, growth, per_resident
from melbourne_config import BASE


class SampleChecks(unittest.TestCase):
    def test_growth_handles_missing_zero_negative_and_decline(self):
        self.assertEqual(growth(1000,1100),10)
        self.assertEqual(growth(1000,900),-10)
        self.assertEqual(growth(1000,0),-100)
        for a,b in [(0,100),(-1,100),(None,100),(100,None)]:
            self.assertIsNone(growth(a,b))

    def test_open_space_zero_is_different_from_missing(self):
        self.assertEqual(per_resident(20000,1000),20)
        self.assertEqual(per_resident(0,1000),0)
        for a,p in [(None,100),(1,None),(1,0),(1,-1)]:
            self.assertIsNone(per_resident(a,p))

    def test_esri_holes_and_multiple_shells(self):
        shell=list(orient(box(0,0,10,10),sign=-1).exterior.coords)
        hole=list(orient(box(2,2,4,4),sign=1).exterior.coords)
        second=list(orient(box(20,0,21,1),sign=-1).exterior.coords)
        g=esri_polygon([shell,hole,second])
        self.assertTrue(g.is_valid)
        self.assertEqual(g.area,97)

    def test_parcels_cross_boundary_and_overlap(self):
        sa2=box(0,0,10,10)
        a=box(-5,0,5,5);b=box(0,0,7,5)
        result=unary_union([a,b]).intersection(sa2)
        self.assertEqual(result.area,35)
        self.assertEqual(a.intersection(sa2).area+b.intersection(sa2).area,60)

    def test_database_constraints_and_negative_growth(self):
        original=sqlite3.connect(BASE/'yfn.sqlite')
        db=sqlite3.connect(':memory:');original.backup(db);original.close()
        db.execute('PRAGMA foreign_keys=ON')
        with self.assertRaises(sqlite3.IntegrityError):
            db.execute("UPDATE observations SET sa2_code='999999999' WHERE indicator_key='rent_weekly'")
        with self.assertRaises(sqlite3.IntegrityError):
            db.execute('INSERT INTO observations SELECT * FROM observations LIMIT 1')
        with self.assertRaises(sqlite3.IntegrityError):
            db.execute("UPDATE observations SET score=101 WHERE indicator_key='transport_access'")
        with self.assertRaises(sqlite3.IntegrityError):
            db.execute("UPDATE observations SET raw_value=NULL WHERE indicator_key='rent_weekly'")
        db.execute("UPDATE observations SET quality_status='unavailable',raw_value=NULL,score=NULL,rating=NULL WHERE indicator_key='transport_access'")
        self.assertEqual(db.execute("SELECT count(*) FROM observations WHERE indicator_key='transport_access' AND raw_value IS NULL").fetchone()[0],361)
        db.execute("UPDATE observations SET raw_value=-10 WHERE indicator_key='population_growth' AND quality_status='available'")
        db.close()

    def test_readonly_runtime(self):
        db=sqlite3.connect((BASE/'yfn.sqlite').resolve().as_uri()+'?mode=ro',uri=True)
        with self.assertRaises(sqlite3.OperationalError):
            db.execute("UPDATE areas SET name='Changed'")
        db.close()


if __name__=='__main__':
    unittest.main()
