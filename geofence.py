import json
import logging
from shapely.geometry import Point, Polygon
from typing import List, Optional, Union

from models import Geofence  # ต้องมี models.py ใน project root

logger = logging.getLogger(__name__)


def parse_polygon(polygon_text: Union[str, List[List[float]]]) -> Optional[Polygon]:
    """
    Parse polygon JSON stored in DB.
    Accept formats:
      - [[lat, lon], [lat, lon], ...]
      - [[lon, lat], [lon, lat], ...]
    Return shapely.geometry.Polygon or None on error.
    """
    try:
        data = json.loads(polygon_text) if isinstance(polygon_text, str) else polygon_text
        if not isinstance(data, list) or len(data) < 3:
            return None

        first = data[0]
        if not (isinstance(first, list) and len(first) >= 2):
            return None
        try:
            # Convert all points to float tuples upfront.
            all_coords = [(float(p[0]), float(p[1])) for p in data]
        except (ValueError, TypeError, IndexError):
            logger.warning("Invalid coordinate format in polygon data", exc_info=True)
            return None

        a, b = all_coords[0]
        # If first value looks like longitude (abs>90) assume [lon, lat]
        if abs(a) > 90 and abs(b) <= 90:
            coords = all_coords  # already (lon, lat)
        else:
            # Assume (lat, lon) and swap to (lon, lat) for shapely
            coords = [(p[1], p[0]) for p in all_coords]

        poly = Polygon(coords)
        if not poly.is_valid:
            poly = poly.buffer(0)
        return poly
    except Exception as e:
        logger.exception("parse_polygon error: %s", e)
        return None


def get_geofences_containing_point(session: "Session", lat: float, lon: float) -> List[Geofence]:
    """
    Return list of Geofence model instances (from models.Geofence) that contain the point (lat, lon).
    Uses SQLAlchemy session passed by caller.
    """
    result = []
    try:
        geofences = session.query(Geofence).all()
        p = Point(lon, lat)  # shapely Point expects (lon, lat)
        for gf in geofences:
            try:
                poly = parse_polygon(gf.polygon)
                if poly is None:
                    continue
                if poly.contains(p) or poly.touches(p):
                    result.append(gf)
            except Exception:
                logger.exception("Error checking geofence id=%s name=%s", getattr(gf, "id", None), getattr(gf, "name", None))
                continue
    except Exception:
        logger.exception("get_geofences_containing_point failed")
    return result
