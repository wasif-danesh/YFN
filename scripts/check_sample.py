"""Validate committed dataset artifacts without downloads or GIS dependencies.

This verifies artifact consistency; project publication status comes from the
checked manifest and matching database release metadata.
"""
import csv
import hashlib
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/greater-melbourne-v1'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_sample(base=BASE):
    manifest=json.loads((base/'manifest.json').read_text())
    evidence=json.loads((base/'audit/rebuild-check.json').read_text())
    require(evidence['status']=='passed','Original rebuild evidence did not pass')
    # Only require the committed subset. Bulky raw geometry and intersection
    # audits are intentionally excluded from Git and are not reverified here.
    files=['yfn.sqlite','manifest.json','sample-summary.csv','sample-summary.json']
    files += [str(p.relative_to(base)) for p in sorted((base/'curated').glob('*.csv'))]
    require(len(files)==14,'Expected ten curated CSV tables')
    for filename in files:
        expected=evidence['sha256_after'].get(filename)
        require(expected==hashlib.sha256((base/filename).read_bytes()).hexdigest(),f'Artifact hash mismatch: {filename}')
    require(hashlib.sha256((base/'acquisition.json').read_bytes()).hexdigest()==manifest['source_manifest_sha256'],'Acquisition manifest changed')
    require(manifest['data_mode']=='real' and manifest['publication_ready'] is True,'Unexpected release mode')
    db=sqlite3.connect((base/'yfn.sqlite').resolve().as_uri()+'?mode=ro',uri=True)
    try:
        require(db.execute('PRAGMA integrity_check').fetchone()[0]=='ok','SQLite integrity failed')
        require(not db.execute('PRAGMA foreign_key_check').fetchall(),'Broken foreign keys')
        release=db.execute('SELECT manifest_json FROM sample_release').fetchall()
        require(len(release)==1 and json.loads(release[0][0])==manifest,'Database/release metadata disagree')
        area_count=db.execute('SELECT count(*) FROM areas').fetchone()[0]
        require(area_count==manifest['area_count'],'Area count differs from manifest')
        require(db.execute('SELECT count(*) FROM observations').fetchone()[0]==area_count*4,'Missing indicator rows')
        require(db.execute('SELECT count(*) FROM population_history').fetchone()[0]==area_count*6,'Missing population rows')
        require(not db.execute("SELECT 1 FROM observations WHERE (quality_status='unavailable') != (raw_value IS NULL) LIMIT 1").fetchall(),'Inconsistent missing values')
        require(not db.execute('SELECT 1 FROM observations WHERE score IS NOT NULL OR rating IS NOT NULL LIMIT 1').fetchall(),'Sample contains unapproved scores')
        for path in sorted((base/'curated').glob('*.csv')):
            with path.open(newline='') as f:
                count=sum(1 for _ in csv.DictReader(f))
            require(db.execute(f'SELECT count(*) FROM "{path.stem}"').fetchone()[0]==count,f'CSV/SQLite row mismatch: {path.name}')
        return area_count
    finally:
        db.close()


if __name__=='__main__':
    count=check_sample()
    print(f'PASS: {count} SA2s, {count*4} indicator rows; committed release hashes and SQLite integrity verified.')
    print('Scope: committed release artifacts only. Raw acquisition, spatial recomputation and application tests are separate checks.')
