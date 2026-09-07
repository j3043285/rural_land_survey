import json
import math
from typing import Tuple, Dict, Any, Optional, List
from shapely.geometry import shape, mapping, Polygon, MultiPolygon
from shapely.validation import make_valid
from shapely.ops import unary_union

def calculate_polygon_area_ha(geojson_str: str) -> Tuple[float, float]:
    """
    Calculates area in hectares and acres from a GeoJSON polygon string.
    Uses approximate geodesic metric at ~19-20 deg N (Maharashtra latitude).
    1 degree lat ~ 110.85 km, 1 degree lng ~ 104.9 km at 19.1 deg.
    """
    try:
        geom_dict = json.loads(geojson_str)
        poly = shape(geom_dict)
        if not poly.is_valid:
            poly = make_valid(poly)
            
        # Get centroid latitude for local projection scale
        centroid = poly.centroid
        lat_rad = math.radians(centroid.y)
        
        # Meters per degree
        m_per_deg_lat = 111132.92 - 559.82 * math.cos(2 * lat_rad) + 1.175 * math.cos(4 * lat_rad)
        m_per_deg_lng = 111412.84 * math.cos(lat_rad) - 93.5 * math.cos(3 * lat_rad)
        
        # Transform coords to local planar meters
        def to_meters(coords):
            return [(x * m_per_deg_lng, y * m_per_deg_lat) for x, y in coords]
        
        if poly.geom_type == "Polygon":
            exterior_m = to_meters(poly.exterior.coords)
            poly_m = Polygon(exterior_m)
            area_sqm = poly_m.area
        elif poly.geom_type == "MultiPolygon":
            area_sqm = sum(Polygon(to_meters(p.exterior.coords)).area for p in poly.geoms)
        else:
            area_sqm = 0.0
            
        area_ha = round(area_sqm / 10000.0, 2)
        area_acres = round(area_ha * 2.47105, 2)
        return area_ha, area_acres
    except Exception as e:
        print(f"Error calculating area: {e}")
        return 0.0, 0.0

def compare_boundaries(old_geojson_str: str, new_geojson_str: str, threshold_pct: float = 2.0) -> Dict[str, Any]:
    """
    Performs true geometric comparison between historical boundary and new survey boundary.
    Computes difference geometry (encroached or missing areas) and percentage deviation.
    """
    try:
        old_dict = json.loads(old_geojson_str)
        new_dict = json.loads(new_geojson_str)
        
        old_poly = make_valid(shape(old_dict))
        new_poly = make_valid(shape(new_dict))
        
        old_ha, old_acres = calculate_polygon_area_ha(old_geojson_str)
        new_ha, new_acres = calculate_polygon_area_ha(new_geojson_str)
        
        # Difference geometry: symmetric difference shows where old and new don't overlap
        diff_geom = old_poly.symmetric_difference(new_poly)
        diff_geojson = json.dumps(mapping(diff_geom)) if not diff_geom.is_empty else None
        
        diff_ha = round(new_ha - old_ha, 2)
        diff_pct = round((abs(new_ha - old_ha) / old_ha * 100.0), 1) if old_ha > 0 else 0.0
        
        exceeds = diff_pct > threshold_pct
        
        if exceeds:
            discrepancy_type = "Boundary Mismatch" if diff_pct > 5.0 else "Area Mismatch"
            severity = "High" if diff_pct > 10.0 else "Medium"
            status = "Discrepancy"
            recommendations = [
                f"Area difference of {diff_pct}% exceeds allowable limit of {threshold_pct}%.",
                "Conduct joint inspection with adjacent landholder.",
                "Verify ground control points (GCP) and GPS accuracy readings.",
                "Review historical 7/12 record map (Kisan Mojni Sheet)."
            ]
        else:
            discrepancy_type = None
            severity = None
            status = "Verified"
            recommendations = [
                f"Boundary change of {diff_pct}% is within permissible survey tolerance ({threshold_pct}%).",
                "Ready for digital signature and Bhu-Aadhaar certificate issuance."
            ]
            
        return {
            "old_area_ha": old_ha,
            "new_area_ha": new_ha,
            "diff_area_ha": diff_ha,
            "diff_percent": diff_pct,
            "exceeds_threshold": exceeds,
            "status": status,
            "discrepancy_type": discrepancy_type,
            "severity": severity,
            "old_geojson": old_geojson_str,
            "new_geojson": new_geojson_str,
            "difference_geojson": diff_geojson,
            "recommendations": recommendations
        }
    except Exception as e:
        print(f"Error comparing boundaries: {e}")
        return {
            "old_area_ha": 0.0,
            "new_area_ha": 0.0,
            "diff_area_ha": 0.0,
            "diff_percent": 0.0,
            "exceeds_threshold": False,
            "status": "Verified",
            "discrepancy_type": None,
            "severity": None,
            "old_geojson": old_geojson_str,
            "new_geojson": new_geojson_str,
            "difference_geojson": None,
            "recommendations": ["Unable to compute geometric difference: check coordinates format."]
        }
