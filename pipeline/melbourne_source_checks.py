"""Independent source-publication checks, separate from spatial calculations."""
import html
import re


def quickstats_rent(page):
    text=html.unescape(re.sub('<[^>]+>',' ',page))
    text=' '.join(text.split())
    if 'No information can be provided because the area selected had no people or a very low population' in text:
        return None,'no_or_very_low_census_population'
    values=[]
    for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>',page,re.S|re.I):
        cells=re.findall(r'<t[hd]\b[^>]*>(.*?)</t[hd]>',row,re.S|re.I)
        cells=[' '.join(html.unescape(re.sub('<[^>]+>',' ',c)).split()) for c in cells]
        # The HTML also embeds historical comparison tables. Only the two-cell
        # current-release summary row is the 2021 value for the selected area.
        if len(cells)==2 and cells[0].startswith('Median weekly rent'):
            token=cells[1].replace('$','').replace(',','').strip()
            assert token.isdigit(),cells
            values.append(int(token))
    assert values and len(set(values))==1, 'QuickStats rent missing or inconsistent'
    return values[0],'published_median'


def check_sources(raw, census, workbook, population, year_cols, codes):
    checks=[]
    for path in sorted(raw.glob('quickstats-*.html')):
        code=path.stem.split('-')[1]
        page=path.read_text()
        assert code in page and code in codes
        value,status=quickstats_rent(page)
        token=census[code]['Median_rent_weekly']
        assert (value is None and token=='0') or (value is not None and value==int(token)),code
        checks.append({'sa2_code':code,'datapack_rent_token':token,'quickstats_rent':value,'quickstats_status':status,
            'snapshot_file':path.name,'url':f'https://www.abs.gov.au/census/find-census-data/quickstats/2021/{code}',
            'result':'match' if value is not None else 'zero_withheld_consistent_with_no_population_notice'})
    zero_codes={c for c in codes if census[c]['Median_rent_weekly']=='0'}
    assert zero_codes<={c['sa2_code'] for c in checks if c['quickstats_rent'] is None}
    dictionary=(raw/'rent-dictionary-2021.html').read_text()
    assert '0001-9999' in dictionary and 'category 0000' in dictionary
    # A separately published aggregate in Table 4 detects missing/extra areas
    # and erroneous year selection in Table 1. Exact integer reconciliation.
    rows=list(workbook['Table 4'].iter_rows(max_col=29,values_only=True))
    matches=[(n,r) for n,r in enumerate(rows,1) if r[2]=='2GMEL']
    assert len(matches)==1
    rownum,total=matches[0]
    totals=[]
    for year,col in year_cols.items():
        aggregate=sum(population[c][1][col] for c in codes)
        official=total[rows[4].index(year)]
        assert aggregate==official,(year,aggregate,official)
        totals.append({'year':year,'sum_sa2_erp':aggregate,'gccsa_table_4_erp':official,
            'source_worksheet':'Table 4','source_row':rownum,'result':'exact_match'})
    return checks,totals
