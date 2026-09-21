"""Document the built SQLite schema and observed coverage without editing data."""
import csv
import json
from pathlib import Path
import sqlite3

from acquire_greater_melbourne import BASE


def main():
    db=sqlite3.connect(f'file:{BASE / "yfn.sqlite"}?mode=ro',uri=True)
    db.row_factory=sqlite3.Row
    purposes={
        'areas':'One spatial 2021 Greater Melbourne SA2 per row; identity and provisional comparison eligibility.',
        'indicators':'Four reusable measure labels and units.',
        'methods':'Versioned calculation definitions and their approval status.',
        'observations':'One current measure per area/indicator in this database release; value, quality, period and method.',
        'population_history':'Six annual population observations per SA2, with revision status and original workbook cell.',
        'data_sources':'One dataset/release per source; publisher, period, licence and limitations.',
        'source_files':'Several original files or API responses per source; exact URLs and hashes.',
        'observation_sources':'Many-to-many provenance with the source role in each observation.',
        'observation_components':'Numerators, denominators and transport-weight components with their own source and period.',
        'area_diagnostics':'Spatial coverage, inventory area, overlap and water-filter sensitivity; unknown coverage stays null.',
        'sample_release':'Metadata for the entire SQLite file; one release, real data and publication_ready=0.'}
    lines=['# Database column dictionary','',
        'Generated from the delivered SQLite schema. See [executable SQL](../../pipeline/greater_melbourne_schema.sql) for all CHECK constraints and view definitions. Identifiers are text. Blank numeric CSV cells load as SQL NULL.','']
    for table,purpose in purposes.items():
        lines += [f'## `{table}`','',purpose,'',f'Rows: {db.execute(f"SELECT count(*) FROM {table}").fetchone()[0]}.','',
            '| Column | SQLite type | Nullable | Key |','|---|---|---|---|']
        cols=list(db.execute(f'PRAGMA table_info({table})'))
        fks=list(db.execute(f'PRAGMA foreign_key_list({table})'))
        for c in cols:
            keys=[]
            if c['pk']:keys.append(f"PK position {c['pk']}")
            for fk in fks:
                if fk['from']==c['name']:keys.append('FK → '+fk['table']+('.'+fk['to'] if fk['to'] else ' primary key'))
            lines.append(f"| `{c['name']}` | {c['type']} | {'No' if c['notnull'] or c['pk'] else 'Yes'} | {'; '.join(keys)} |")
        lines.append('')
    lines += ['## `v_area_summary` view','',
        'One row per SA2, with four raw measures, comparison eligibility, quality statuses and transport coverage. Join observations for quality notes, periods and sources before presenting the values to renters.','',
        'Columns: '+', '.join('`'+r['name']+'`' for r in db.execute('PRAGMA table_info(v_area_summary)'))+'.','']
    (BASE/'data-dictionary.md').write_text('\n'.join(lines))
    intro='''# ER diagram and schema design notes

This diagram reflects the delivered [SQLite database](yfn.sqlite), not an unimplemented target. It shows selected columns; the [column dictionary](data-dictionary.md) and [SQL DDL](../../pipeline/greater_melbourne_schema.sql) contain the full schema. The editable source is [schema-erd.mmd](schema-erd.mmd).

'''
    mermaid=(BASE/'schema-erd.mmd').read_text()
    notes='''

## Reading the relationships

An area has four observations in this release and six population-history rows. The SQL schema allows any number; the builder validates the required four/six cardinalities. Each observation is uniquely identified by `(sa2_code, indicator_key)`.

An observation can use multiple sources. `observation_sources` joins it to each dataset and records a role such as numerator, denominator or boundary. `observation_components` retains the actual inputs and their periods. For open space, the inventory area and 2025 population are separate components from different sources.

One dataset can have many downloaded files. `source_files` records exact API requests, checksums and retrieval dates, while `data_sources` stores shared meaning and limitations. Intersection audit rows identify source feature IDs and their exact raw file; those large audits and geometry are kept outside the runtime database.

Solid identifying relationships indicate a parent key forms part of a child's primary key; dotted relationships are other foreign keys. Mandatory parent references use `||`; SQL permits zero or more children unless an additional constraint says otherwise. The single diagnostics row per area is enforced by its primary key. The builder supplies one for every area.

`sample_release` describes the whole database file and has no row-level foreign key to the other tables. This is deliberate for one release per file. Do not add a fictitious relationship to the diagram.

## Design decisions supported by the real data

1. **Retain geography independently of indicator availability.** Two SA2s have zero residents. Keep them for traceability while a provisional eligibility flag controls comparison use.
2. **Separate raw input tokens from display values.** Three source rent zeros become unavailable medians; original tokens remain in the audit. Zero population remains a genuine integer zero.
3. **Keep coverage independent of value and quality.** A numeric PTAL average can cover less than 1% of an SA2. Open-space inventory completeness is unknown even when a polygon is present. Both need explicit handling.
4. **Store numerator and denominator.** Large public-open-space ratios can reflect a tiny resident population. The denominator must be inspectable, not hidden behind a rounded ratio.
5. **Version methods and dates.** A 2021 rent, a 2020–2025 population change and an undated inventory must not share a fabricated single observation date. A transport raw index and its future percentile are separate fields.

## Boundaries of this schema example

The database stores one boundary edition and one current observation per area/indicator per release. For multiple boundary editions or observation releases in one database, extend the primary and foreign keys consistently (for example with a geography-edition identity and release ID). Do not merely add a year column while keeping an incompatible unique key.

The schema is intentionally marked as a real-data sample, with `publication_ready=0`. Generalize the release metadata and approval rules when implementing the application's shared synthetic/real loader. `is_comparable` currently means positive 2025 ERP and does not approve transport scoring eligibility or a minimum population threshold. Source quality cannot be fixed by a database constraint.

No suburb-alias table is populated because a verified one-to-many suburb/SA2 mapping has not been acquired. The diagram does not invent one. The application can begin with official SA2 names, and a future alias relationship can be added with its own source and mapping basis.
'''
    (BASE/'schema-guide.md').write_text(intro+'```mermaid\n'+mermaid+'```\n'+notes)
    rows=[dict(r) for r in db.execute('SELECT a.sa2_code,a.name,a.is_comparable,o.indicator_key,o.raw_value,o.quality_status,o.coverage_fraction,o.quality_note FROM areas a JOIN observations o USING(sa2_code) ORDER BY a.sa2_code,o.indicator_key')]
    with (BASE/'audit/coverage-and-quality.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    db.close()


if __name__=='__main__':main()
