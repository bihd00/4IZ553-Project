from fastapi import APIRouter
from be.api.deps import SessionDep
from be.schemas.http import ResponseBody
from be.schemas.routing import PointNode
from be.schemas.routing import Route
from be.schemas.routing import AddressOption


router = APIRouter()


@router.get('')
def get_addresses(
    session: SessionDep, search: str, limit: int = 25
) -> ResponseBody[list[AddressOption]]:
    query = '''
        CALL 
            db.index.fulltext.queryNodes("search_index", $search) 
        YIELD
            node, score
        // TODO: POI
        WHERE
            labels(node)[0] = "Address"
        RETURN
            coalesce(node.full_address, node.name) AS value,
            score,
            labels(node)[0] AS label,
            toInteger(node.id) AS id
        ORDER BY
            score DESC
        LIMIT $limit
    '''
    params = {'search': search, 'limit': limit}
    result = session.run(query=query, parameters=params).data()
    return ResponseBody(data=[AddressOption.from_python(x) for x in result])


@router.get('/route')
def get_route(
    session: SessionDep, source: int, dest: int
) -> ResponseBody[Route]:
    query = '''
        MATCH (to {id: $dest})-[:NEAREST_INTERSECTION]->(source:Intersection) 
        MATCH (from {id: $source})-[:NEAREST_INTERSECTION]->(target:Intersection)
        CALL
            apoc.algo.dijkstra(source, target, 'ROAD_SEGMENT', 'length')
        YIELD
            path, weight
        RETURN
            [n in nodes(path) | [n.location.latitude, n.location.longitude]] AS route
    '''
    params = {'source': source, 'dest': dest}
    result = session.run(query=query, parameters=params).data()
    resp = Route(route=[])
    if result and result[0]['route']:
        resp.route = [PointNode(lat=x[0], lon=x[1]) for x in result[0]['route']]
    return ResponseBody(data=resp)

