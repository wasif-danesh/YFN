"""Paths and official source URLs for the single Greater Melbourne dataset."""
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/greater-melbourne-v1"
RAW = BASE / "raw"
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

