from fastapi import APIRouter
from typing import Sequence
from be.api.deps import SessionDep
from be.schemas.http import ResponseBody
from be.schemas.routing import PointOfInterest


router = APIRouter()


@router.get('/circle')
def get_poi_circle(
    session: SessionDep, lat: float, lon: float, radius: float
) -> ResponseBody[Sequence[PointOfInterest]]:
    query = '''
        WITH
            point({latitude: $latitude, longitude:$longitude}) AS radiusCenter
        MATCH
            (p:Point)-[:HAS_GEOMETRY]-(poi:PointOfInterest)-[:HAS_TAGS]->(t:Tags) 
        WHERE
            point.distance(p.location, radiusCenter) < $radius
        RETURN p {
            latitude: p.location.latitude, 
            longitude: p.location.longitude, 
            name: poi.name, 
            categories: labels(poi),
            tags: t{.*}
        } 
        AS point
    '''
    params = {'latitude': lat, 'longitude': lon, 'radius': radius}
    result = session.run(query=query, parameters=params).data()
    if not result:
        return ResponseBody(data=[])
    pois = [PointOfInterest.from_python(obj.get('point')) for obj in result]
    return ResponseBody(data=pois)


@router.get('/polygon')
def get_poi_circle(
    session: SessionDep,
    lat_min: float,
    lat_max: float,
    lon_min: float,
    lon_max: float,
) -> ResponseBody[Sequence[PointOfInterest]]:
    query = '''
        MATCH
            (p:Point)-[:HAS_GEOMETRY]-(poi:PointOfInterest)-[:HAS_TAGS]->(t:Tags) 
        WHERE
            point.withinBBox(
                p.location, 
                point({longitude: $lon_min, latitude: $lat_min }), 
                point({longitude: $lon_max, latitude: $lat_max})
            )
        RETURN p {
            latitude: p.location.latitude, 
            longitude: p.location.longitude, 
            name: poi.name, 
            categories: labels(poi),
            tags: t{.*}
        } 
        AS point
    '''
    params = {
        'lat_min': lat_min,
        'lat_max': lat_max,
        'lon_min': lon_min,
        'lon_max': lon_max,
    }
    result = session.run(query=query, parameters=params).data()
    if not result:
        return ResponseBody(data=[])
    pois = [PointOfInterest.from_python(obj.get('point')) for obj in result]
    return ResponseBody(data=pois)