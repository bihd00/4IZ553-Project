from pydantic_settings import BaseSettings
from pathlib import Path


_BASE_DIR = Path(__file__).resolve().parent.parent
_DATA_DIR = _BASE_DIR.joinpath('data')

if not _DATA_DIR.exists():
    _DATA_DIR.mkdir(exist_ok=True)


class Settings(BaseSettings):

    class ConfigDict:
        case_sensitive = True

    BASE_DIR: Path = _BASE_DIR
    DATA_DIR: Path = _DATA_DIR

    NEO_URI: str = 'bolt://localhost:7687'
    NEO_DATABASE: str = 'neo4j'
    NEO_USERNAME: str = 'neo4j'
    NEO_PASSWORD: str

    DS_POI_PRG_NODES_FILENAME: str = 'prague_det_poi_nodes.csv'
    DS_ADDRESS_PRG_NODES_FILENAME: str = 'prague_address_nodes.csv'
    DS_ROAD_PRG_NODES_FILENAME: str = 'prague_road_nodes.csv'
    DS_ROAD_PRG_RELS_FILENAME: str = 'prague_road_relationships.csv'

    API_V1_PREFIX: str = '/api/v1'
    API_ALLOW_DOCS: bool = True
    

settings = Settings()


if __name__ == '__main__':
    print(settings)