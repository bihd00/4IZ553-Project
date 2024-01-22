from neo4j import GraphDatabase
from neo4j import ManagedTransaction
from neo4j import Result as TxResult
from typing import Sequence
from typing import Any
from be.config import settings
from be.utils import get_osm_csv_records


driver = GraphDatabase.driver(
    uri=settings.NEO_URI,
    database=settings.NEO_DATABASE,
    auth=(settings.NEO_USERNAME, settings.NEO_PASSWORD)
)


def neo_batch_insert(
    tx: ManagedTransaction,
    query: str,
    data: Sequence[dict[str, Any]],
    batch_size: int = 10000
 ) -> None:
    assert '$data' in query, 'query missing "$data"'
    total, batch = 0, 0
    while batch * batch_size < len(data):
        results = tx.run(
            query=query,
            parameters={'data': data[batch*batch_size:(batch+1)*batch_size]}
        ).data()
        total += results[0]['total']
        batch += 1


def neo_run(
    tx: ManagedTransaction, query: str, params: dict[str, Any] = {}
) -> TxResult:
    return tx.run(query=query, parameters=params)


def neo_clean_db() -> None:
    query = '''
        CALL apoc.periodic.iterate(
            'MATCH (n) RETURN n',
            'DETACH DELETE n',
            {batchSize:1000}
        )
    '''
    with driver.session() as session:
        session.execute_write(neo_run, query=query)


def create_prague_road_indexes() -> None:
    intersection_constraint_query = '''
        CREATE CONSTRAINT IF NOT EXISTS FOR (i:Intersection)
        REQUIRE i.osmid IS UNIQUE
    '''
    road_segment_index_query = '''
        CREATE INDEX IF NOT EXISTS FOR ()-[r:ROAD_SEGMENT]-() ON r.osmids
    '''
    address_constraint_query = '''
        CREATE CONSTRAINT IF NOT EXISTS FOR (a:Address) REQUIRE a.id IS UNIQUE
    '''
    intersection_point_index_query = '''
        CREATE POINT INDEX IF NOT EXISTS FOR (i:Intersection) ON i.location
    '''
    with driver.session() as session:
        session.execute_write(neo_run, query=intersection_constraint_query)
        session.execute_write(neo_run, query=road_segment_index_query)
        session.execute_write(neo_run, query=address_constraint_query)
        session.execute_write(neo_run, query=intersection_point_index_query)


def load_prague_road_nodes() -> None:
    data = get_osm_csv_records(
        path=settings.DATA_DIR.joinpath(settings.DS_ROAD_PRG_NODES_FILENAME)
    )
    query = '''
        UNWIND $data AS row
        WITH row WHERE row.osmid IS NOT NULL
        MERGE (i:Intersection {osmid: toInteger(row.osmid)})
            SET i.location = 
            point({latitude: toFLoat(row.y), longitude: toFloat(row.x) }),
                i.ref = row.ref,
                i.highway = row.highway,
                i.street_count = toInteger(row.street_count)
        RETURN COUNT(*) as total
    '''
    with driver.session() as session:
        session.execute_write(neo_batch_insert, query=query, data=data)


def load_prague_road_rels() -> None:
    data = get_osm_csv_records(
        path=settings.DATA_DIR.joinpath(settings.DS_ROAD_PRG_RELS_FILENAME)
    )
    query = '''
        UNWIND $data AS road
        WITH road WHERE road.osmid IS NOT NULL
        MATCH (u:Intersection {osmid: toInteger(road.u)})
        MATCH (v:Intersection {osmid: toInteger(road.v)})
        MERGE (u)-[r:ROAD_SEGMENT {osmid: COALESCE(toInteger(road.osmid), -1)}]->(v)
            SET r.oneway = road.oneway,
                r.lanes = road.lanes,
                r.ref = road.ref,
                r.name = road.name,
                r.highway = road.highway,
                r.max_speed = road.maxspeed,
                r.length = toFloat(road.length)
        RETURN COUNT(*) AS total
    '''
    with driver.session() as session:
        session.execute_write(neo_batch_insert, query=query, data=data)


def load_prague_address_nodes() -> None:
    data = get_osm_csv_records(
        path=settings.DATA_DIR.joinpath(settings.DS_ADDRESS_PRG_NODES_FILENAME)
    )
    query = '''
        UNWIND $data AS row
        MERGE (a:Address {id: toInteger(row.id)})
        SET
            a.location = point({ latitude: toFloat(row.lat), longitude: toFloat(row.lon) }),
            a.full_address =
                + row.tags.addr_street
                + " "
                + row.tags.addr_housenumber
                + " "
                + row.tags.addr_city
                + ", "
                + row.tags.addr_postcode
                + ", Czech Republic"
        SET a += row.tags
        RETURN COUNT(*) AS total
    '''
    with driver.session() as session:
        session.execute_write(neo_batch_insert, query=query, data=data)


def create_prague_address_road_rels() -> None:
    query = '''
        CALL apoc.periodic.iterate(
        'MATCH (p:Address) WHERE NOT EXISTS ((p)-[:NEAREST_INTERSECTION]->(:Intersection)) RETURN p',
        'CALL {
            WITH p
            MATCH (i:Intersection)
            USING INDEX i:Intersection(location)
            WHERE point.distance(i.location, p.location) < 200

            WITH i
            ORDER BY point.distance(p.location, i.location) ASC 
            LIMIT 1
            RETURN i
        }
        WITH p, i

        MERGE (p)-[r:NEAREST_INTERSECTION]->(i)
        SET r.length = point.distance(p.location, i.location)
        RETURN COUNT(p)',
        {batchSize:1000, parallel:false}
    )
    '''
    with driver.session() as session:
        session.execute_write(neo_run, query=query)


def create_prague_poi_address_fulltext_index() -> None:
    query = '''
        CREATE FULLTEXT INDEX search_index IF NOT EXISTS
        FOR (p:PointOfInterest|Address) ON EACH [p.name, p.full_address]
    '''
    with driver.session() as session:
        session.execute_write(neo_run, query=query)

def load_prague_poi() -> None:
    data = get_osm_csv_records(
        path=settings.DATA_DIR.joinpath(settings.DS_POI_PRG_NODES_FILENAME)
    )
    query = '''
        UNWIND $data AS row
        CREATE (p:PointOfInterest {id: row.id, name: row.name})
        CREATE (g:Geometry)
        SET g.location = point({latitude: toFloat(row.lat), longitude: toFloat(row.lon) })
        CREATE (g)<-[:HAS_GEOMETRY]-(p)
        SET g:Point
        CREATE (t:Tags)
        SET t += row.tags
        CREATE (p)-[:HAS_TAGS]->(t)
        WITH *
        CALL apoc.create.addLabels(p, [row.class, row.subclass]) YIELD node
        RETURN COUNT(*) AS total
    '''
    with driver.session() as session:
        session.execute_write(neo_batch_insert, query=query, data=data)