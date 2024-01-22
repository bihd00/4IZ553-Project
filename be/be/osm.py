"""
optional module
(only for downloading data)
"""
from typing import Literal
from typing import Any
from be.config import settings


_OSM_BBOX_FORMAT = '[bbox:{lon_min},{lat_min},{lon_max},{lat_max}]'
_OSM_NOMINATIM_URL = 'https://nominatim.openstreetmap.org'
_OSM_OVERPASS_URL = 'https://overpass-api.de/api/interpreter'


def download_prague_address_data() -> None:
    from requests import post as POST
    from pandas import DataFrame
    resp = POST(
        url=_OSM_OVERPASS_URL,
        data={
            'data': '''
                [out:json];
                area["name"="Praha"]->.searchArea;
                (
                    node(area.searchArea)["addr:housenumber"~"."]["addr:street"~"."];
                );
                out center;
            '''
        }
    )
    elements: list[dict[str, Any]] = resp.json()['elements']
    for address in elements:
        for k in address.copy():
            if ':' in k:
                address[k.replace(':', '_')] = address.pop(k)
            if 'tags' == k and isinstance(address['tags'], dict):
                for kt in address['tags'].copy():
                    address['tags'][kt.replace(':', '_')] = \
                        address['tags'].pop(kt)
    
    DataFrame.from_records(elements).to_csv(
        settings.DATA_DIR.joinpath(settings.DS_ADDRESS_PRG_NODES_FILENAME),
        index=False
    )


def download_prague_poi_data() -> None:
    """
    get Daylight Earth Table (https://daylightmap.org/earth/)
    equivalent for Prague
    """
    from requests import get as GET
    from requests import post as POST
    from pandas import DataFrame
    from pandas import read_html

    url = f"{_OSM_NOMINATIM_URL}/details.php?" + \
        "osmtype=R&osmid=439840&class=boundary&addressdetails=1&" + \
        "hierarchy=0&group_hierarchy=1&polygon_geojson=1&format=json"

    resp_nominatim = GET(url=url)
    coords = resp_nominatim.json()['geometry']['coordinates'][0]

    lat_min, lat_max = min(c[0] for c in coords), max(c[0] for c in coords)
    lon_min, lon_max = min(c[1] for c in coords), max(c[1] for c in coords)

    tables = read_html('https://daylightmap.org/earth/poi.html')
    df_meta = tables[1]

    unique_classes = df_meta['Class'].unique().tolist()
    unique_subclasses = df_meta['Subclass'].unique().tolist()
    subclass_to_class_map = dict(zip(df_meta['Subclass'], df_meta['Class']))
    search_tags = unique_classes + unique_subclasses
    search_nodes = [f'node["{tag}"];' for tag in search_tags]
    nodes = []

    for ch in _split_bbox_into_chunks(
        lat_min  = lat_min,
        lat_max  = lat_max,
        lon_min  = lon_min,
        lon_max  = lon_max,
        n_chunks = 20,
    ):
        bbox = _OSM_BBOX_FORMAT.format(
            lon_min=ch['lon_min'],
            lat_min=ch['lat_min'],
            lon_max=ch['lon_max'],
            lat_max=ch['lat_max'],
        )
        request_data = {
            'data': f'''
                [timeout:200]
                [out:json]
                {bbox};
                (
                    {''.join(search_nodes)}
                );
                out center;
                out meta;
            '''
        }

        print('Downloading chunk:', bbox)

        resp_overpass = POST(
            url=_OSM_OVERPASS_URL,
            headers={
                'Accept-Encoding': 'gzip, deflate, br'
            },
            data=request_data
        )
        assert resp_overpass.status_code == 200, resp_overpass.text

        j = resp_overpass.json()
        assert isinstance(j, dict), type(j)

        if 'elements' in j and isinstance(j['elements'], list):
            nodes.extend(j['elements'])
        
    df_nodes = DataFrame.from_records(nodes)
    df_nodes = df_nodes.drop(columns=[
        'type', 'timestamp', 'version', 'changeset', 'user', 'uid'
        ]
    )
    df_nodes = df_nodes.drop_duplicates(subset=['id'])

    def get_name_from_tags(tags: dict) -> str:
        if 'name' in tags:
            return tags['name']
        return 'unknown'

    def get_class_from_tags(tags: dict) -> str:
        for cls in unique_classes:
            if cls in tags:
                return cls
        for cls in subclass_to_class_map:
            if cls in tags:
                return subclass_to_class_map[cls]
        return 'unknown'

    def get_subclass_from_tags(tags: dict) -> str:
        for subcls in unique_subclasses:
            if subcls in tags:
                return subcls
        for cls in unique_classes:
            if cls in tags:
                return tags[cls]
        return 'unknown'

    df_nodes['name'] = df_nodes['tags'].apply(get_name_from_tags)
    df_nodes['class'] = df_nodes['tags'].apply(get_class_from_tags)
    df_nodes['subclass'] = df_nodes['tags'].apply(get_subclass_from_tags)

    df_nodes.to_csv(
        settings.DATA_DIR.joinpath(settings.DS_POI_PRG_NODES_FILENAME),
        index=False
    )


def download_prague_road_data() -> None:
    from osmnx import graph_from_place
    from osmnx import graph_to_gdfs

    graph = graph_from_place(
        'Prague, Czech Republic',
        network_type='drive'
    )

    gdf_nodes, gdf_relationships = graph_to_gdfs(graph)
    gdf_nodes.reset_index(inplace=True)
    gdf_relationships.reset_index(inplace=True)

    if 'geometry' in gdf_nodes.columns:
        gdf_nodes.drop(columns=['geometry'], inplace=True)

    if 'geometry' in gdf_relationships.columns:
        gdf_relationships.drop(columns=['geometry'], inplace=True)

    gdf_nodes.to_csv(
        settings.DATA_DIR.joinpath(settings.DS_ROAD_PRG_NODES_FILENAME),
        index=False
    )

    gdf_relationships.to_csv(
        settings.DATA_DIR.joinpath(settings.DS_ROAD_PRG_RELS_FILENAME),
        index=False
    )


def _split_bbox_into_chunks(
    lat_min: float,
    lat_max: float,
    lon_min: float,
    lon_max: float,
    n_chunks: int,
) -> list[dict[Literal["lat_min", "lat_max", "lon_min", "lon_max"], float]]:
    n = int(n_chunks**1/2) + 1
    lat_step = (lat_max - lat_min) / n
    lon_step = (lon_max - lon_min) / n
    chunks = []
    for i in range(1, n, 1):
        for j in range(1, n, 1):
            d = dict(
                lat_min=lat_min+lat_step*(i-1),
                lat_max=lat_min+lat_step*i,
                lon_min=lon_min+lon_step*(j-1),
                lon_max=lon_min+lon_step*j,
            )
            chunks.append(d)
    return chunks