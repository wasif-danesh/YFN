"""Regression and release checks against the actual complete-area database."""
import csv
import hashlib
import json
import math
import re
from pathlib import Path
import sqlite3
import unittest

from acquire_greater_melbourne import BASE
from melbourne_common import growth, per_resident
from melbourne_source_checks import quickstats_rent


class GreaterMelbourneChecks(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(f'file:{BASE / "yfn.sqlite"}?mode=ro',uri=True)
        self.db.row_factory=sqlite3.Row

    def tearDown(self): self.db.close()

    def test_all_361_areas_have_four_observations_and_six_years(self):
        self.assertEqual(self.db.execute('SELECT count(*) FROM areas').fetchone()[0],361)
        self.assertEqual(self.db.execute('SELECT sum(is_comparable) FROM areas').fetchone()[0],359)
        for a in self.db.execute('SELECT * FROM areas'):
            self.assertEqual(a['gccsa_code'],'2GMEL');self.assertEqual(a['boundary_year'],2021)
            self.assertIsInstance(a['sa2_code'],str)
            self.assertEqual(self.db.execute('SELECT count(*) FROM observations WHERE sa2_code=?',(a['sa2_code'],)).fetchone()[0],4)
            self.assertEqual([r[0] for r in self.db.execute('SELECT year FROM population_history WHERE sa2_code=? ORDER BY year',(a['sa2_code'],))],list(range(2020,2026)))

    def test_all_derived_values_reconstruct_from_database_components(self):
        for o in self.db.execute("SELECT * FROM observations WHERE indicator_key!='rent_weekly'"):
            c=dict(self.db.execute('SELECT component_key,value FROM observation_components WHERE sa2_code=? AND indicator_key=?',(o['sa2_code'],o['indicator_key'])))
            if o['indicator_key']=='population_growth': expected=growth(c['population_start'],c['population_end'])
            elif o['indicator_key']=='transport_access':
                expected=c['weighted_index_area_sum']/c['valid_intersection_area'] if c['valid_intersection_area']>0 else None
            else:
                expected=per_resident(c['eligible_open_space_area'],c['population_denominator']) if c['eligible_open_space_area']>0 else None
            if expected is None:self.assertIsNone(o['raw_value'])
            else:self.assertTrue(math.isclose(o['raw_value'],expected,rel_tol=1e-12,abs_tol=1e-12))

    def test_abs_zero_rent_is_withheld_and_original_token_preserved(self):
        with (BASE/'audit/census-g02-source-rows.csv').open() as f:
            original={r['SA2_CODE_2021']:r['Median_rent_weekly'] for r in csv.DictReader(f)}
        zero=[]
        for r in self.db.execute("SELECT * FROM observations WHERE indicator_key='rent_weekly'"):
            token=original[r['sa2_code']]
            if token=='0':
                zero.append(r['sa2_code']);self.assertIsNone(r['raw_value']);self.assertEqual(r['quality_status'],'unavailable')
            else:self.assertEqual(r['raw_value'],int(token))
        self.assertEqual(set(zero),{'206041127','206041507','210011227'})

    def test_unavailable_and_partial_spatial_results_do_not_imply_zero(self):
        for r in self.db.execute('SELECT * FROM observations'):
            self.assertIsNone(r['score']);self.assertIsNone(r['rating'])
            if r['quality_status']=='unavailable':self.assertIsNone(r['raw_value'])
            else:self.assertIsNotNone(r['raw_value'])
            if r['indicator_key']=='transport_access':
                self.assertTrue(0<=r['coverage_fraction']<=1)
                if r['coverage_fraction']==0:self.assertIsNone(r['raw_value'])
                else:self.assertEqual(r['quality_status'],'limited')
            if r['indicator_key']=='green_space_per_resident':self.assertIsNone(r['coverage_fraction'])
        self.assertEqual(self.db.execute("SELECT count(*) FROM observations WHERE indicator_key='transport_access' AND coverage_fraction=0").fetchone()[0],1)

    def test_quickstats_parser_ignores_embedded_historical_tables(self):
        page='<tr><th>Median weekly rent (b)</th><td>$421</td></tr><tr><th>Median weekly rent (a)</th><td>440</td><td>N/A</td></tr>'
        self.assertEqual(quickstats_rent(page),(421,'published_median'))
        self.assertEqual(quickstats_rent('No information can be provided because the area selected had no people or a very low population in the 2021 Census.')[0],None)
        with self.assertRaises(AssertionError):quickstats_rent('<p>Download failed</p>')

    def test_independent_publication_cross_checks(self):
        checks=json.loads((BASE/'audit/rent-cross-checks.json').read_text())
        self.assertEqual(len(checks),14)
        self.assertEqual(sum(c['quickstats_rent'] is None for c in checks),3)
        totals=json.loads((BASE/'audit/population-total-cross-checks.json').read_text())
        self.assertEqual(len(totals),6)
        for r in totals:self.assertEqual(r['sum_sa2_erp'],r['gccsa_table_4_erp'])

    def test_original_four_area_results_remain_consistent(self):
        prior=json.loads((Path(__file__).parent/'fixtures/four-area-regression.json').read_text())
        now={r['sa2_code']:r for r in json.loads((BASE/'sample-summary.json').read_text())}
        for a in prior:
            for k in ['rent_2021_aud_week','erp_2020','erp_2025','population_growth_2020_2025_percent','transport_raw_index_sample','selected_open_space_m2']:
                self.assertTrue(math.isclose(a[k],now[a['sa2_code']][k],rel_tol=1e-9,abs_tol=0.01),(a['name'],k))

    def test_all_raw_snapshots_and_database_provenance(self):
        manifest=json.loads((BASE/'acquisition.json').read_text())
        self.assertEqual(self.db.execute('SELECT count(*) FROM source_files').fetchone()[0],len(manifest))
        for r in manifest.values():self.assertEqual(hashlib.sha256((BASE/r['file']).read_bytes()).hexdigest(),r['sha256'])
        self.assertEqual(self.db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
        self.assertEqual(self.db.execute('PRAGMA foreign_key_check').fetchall(),[])
        for r in self.db.execute('SELECT sa2_code,indicator_key FROM observations'):
            self.assertGreaterEqual(self.db.execute('SELECT count(*) FROM observation_sources WHERE sa2_code=? AND indicator_key=?',tuple(r)).fetchone()[0],2)
        release=self.db.execute('SELECT * FROM sample_release').fetchone()
        self.assertEqual(release['data_mode'],'real');self.assertEqual(release['publication_ready'],0)

    def test_spatial_repairs_and_independent_source_area_checks(self):
        repairs=json.loads((BASE/'audit/geometry-repairs.json').read_text())
        for r in repairs:self.assertLess(abs(r['area_after_m2']-r['area_before_m2']),0.01)
        outliers=json.loads((BASE/'audit/source-hectare-exceptions.json').read_text())
        # The stricter 0.51 m2 rounding exceptions remain reported. For large
        # polygons, require agreement within 0.01% with publisher-stored HA.
        for r in outliers:self.assertLess(abs(r['calculated_feature_m2']/(r['source_HA']*10000)-1),0.0001)

    def test_database_enforces_constraints_and_opens_readonly(self):
        with self.assertRaises(sqlite3.OperationalError):self.db.execute("UPDATE areas SET name='changed'")
        db=sqlite3.connect(':memory:');self.db.backup(db);db.execute('PRAGMA foreign_keys=ON')
        for sql in ["UPDATE observations SET sa2_code='999999999'",'INSERT INTO observations SELECT * FROM observations LIMIT 1',
                    'UPDATE observations SET score=101',"UPDATE observations SET quality_status='available',raw_value=NULL",
                    'UPDATE areas SET is_comparable=2',"UPDATE observations SET raw_value=-1 WHERE indicator_key='rent_weekly'"]:
            with self.assertRaises(sqlite3.IntegrityError):db.execute(sql)
        db.execute("UPDATE observations SET raw_value=-10,quality_status='available' WHERE indicator_key='population_growth'")
        db.close()

    def test_erd_matches_all_tables_foreign_keys_and_selected_columns(self):
        mermaid=(BASE/'schema-erd.mmd').read_text()
        names={a:(alias or a) for a,alias in re.findall(r'^    (\w+)(?:\["([^"]+)"\])? \{',mermaid,re.M)}
        tables={r[0] for r in self.db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertEqual(set(names.values()),tables)
        edges={(names[child],names[parent]) for parent,child in re.findall(r'^    (\w+) [|o.{}-]+ (\w+) :',mermaid,re.M)}
        fks={(t,r[2]) for t in tables for r in self.db.execute(f'PRAGMA foreign_key_list({t})')}
        self.assertEqual(edges,fks)
        for node,alias,body in re.findall(r'^    (\w+)(?:\["([^"]+)"\])? \{\n(.*?)^    \}',mermaid,re.M|re.S):
            columns={r[1] for r in self.db.execute(f'PRAGMA table_info({names[node]})')}
            mentioned=set(re.findall(r'^        \w+ (\w+)',body,re.M))
            self.assertTrue(mentioned<=columns,(node,mentioned-columns))


if __name__=='__main__':unittest.main()
