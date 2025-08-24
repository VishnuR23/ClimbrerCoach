import numpy as np
from shapely.geometry import Point, Polygon, LineString

def support_polygon(feet_xy):
    pts = [p for p in feet_xy if p is not None]
    if not pts: return None
    if len(pts)==1:
        return Polygon([pts[0], (pts[0][0]+0.01, pts[0][1]), (pts[0][0], pts[0][1]+0.01)])
    if len(pts)==2:
        return LineString(pts).buffer(0.01, cap_style=2).envelope
    return Polygon(pts)

def stability_margin(com_xy, feet_xy):
    poly = support_polygon(feet_xy)
    if poly is None or com_xy is None: return float("-inf")
    p = Point(com_xy[0], com_xy[1])
    inside = poly.contains(p) or poly.touches(p)
    d = poly.exterior.distance(p)
    return float(d if inside else -d)
