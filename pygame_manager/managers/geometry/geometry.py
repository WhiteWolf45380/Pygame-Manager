# ======================================== OBJET ========================================
from ._core import *
from ._vector import VectorObject
from ._point import PointObject
from ._segment import SegmentObject
from ._line import LineObject
from ._circle import CircleObject
from ._rect import RectObject
from ._polygon import PolygonObject

# ======================================== GESTIONNAIRE ========================================
class GeometryManager:
    """
    Gesionnaire de la géométrie

    Fonctionnalités:
        manipulation vectorielle
    """
    def __init__(self):
        self.Vector = VectorObject
        self.Point = PointObject
        self.Segment = SegmentObject
        self.Line = LineObject
        self.Circle = CircleObject
        self.Rect = RectObject
        self.Polygon = PolygonObject
    
    # ======================================== GENERATIONS PARTICULIERES ========================================
    def line_from_two_points(self, P1: PointObject, P2: PointObject) -> LineObject:
        """Crée une droite à partir de deux points"""
        if not isinstance(P1, PointObject) or not isinstance(P2, PointObject):
            _raise_error(self, "line_from_two_points", "Both arguments must be PointObject")
        if P1 == P2:
            _raise_error(self, "line_from_two_points", "Points must be different")
        return LineObject(P1, P2 - P1)

    def line_from_cartesian(self, a: float, b: float, c: float) -> LineObject:
        """
        Crée une droite à partir de l'équation cartésienne ax + by + c = 0
        Fonctionne uniquement en 2D
        """
        if a == 0 and b == 0:
           _raise_error(self, "line_from_cartesian", "a and b cannot both be null")
        if b != 0:
            point = PointObject(0, -c/b)
        else:
            point = PointObject(-c/a, 0)        
        vector = VectorObject(-b, a)   
        return LineObject(point, vector)

    # ======================================== POINT / VECTOR ========================================
    def point_distance(self, x1: float, y1: float, x2: float, y2: float) -> float:
        """Distance euclidienne entre deux points 2D"""
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def point_distance_sq(self, x1: float, y1: float, x2: float, y2: float) -> float:
        """Distance euclidienne au carré (évite le sqrt)"""
        return (x2 - x1)**2 + (y2 - y1)**2

    # ======================================== CERCLE - CERCLE ========================================
    def circle_circle_collide(self, cx1: float, cy1: float, r1: float, cx2: float, cy2: float, r2: float) -> bool:
        """Collision entre deux cercles"""
        return self.point_distance_sq(cx1, cy1, cx2, cy2) <= (r1 + r2)**2

    def circle_circle_intersection(self, cx1: float, cy1: float, r1: float, cx2: float, cy2: float, r2: float) -> tuple | None:
        """
        Intersection de deux cercles
        
        Returns:
            None : pas d'intersection
            ((px, py),) : tangence (1 point)
            ((p1x, p1y), (p2x, p2y)) : 2 points d'intersection
        """
        dx = cx2 - cx1
        dy = cy2 - cy1
        d_sq = dx**2 + dy**2
        d = math.sqrt(d_sq)
        
        # Pas d'intersection
        if d > r1 + r2 or d < abs(r1 - r2) or d == 0:
            return None
        
        # Tangence
        if abs(d - (r1 + r2)) < 1e-10 or abs(d - abs(r1 - r2)) < 1e-10:
            ratio = r1 / d
            return ((cx1 + ratio * dx, cy1 + ratio * dy),)
        
        # Deux points
        a = (r1**2 - r2**2 + d_sq) / (2 * d)
        h = math.sqrt(r1**2 - a**2)
        
        mx = cx1 + a * dx / d
        my = cy1 + a * dy / d
        
        return (
            (mx + h * dy / d, my - h * dx / d),
            (mx - h * dy / d, my + h * dx / d),
        )

    # ======================================== CERCLE - LIGNE ========================================
    def circle_line_collide(self, cx: float, cy: float, r: float,ox: float, oy: float, vx: float, vy: float) -> bool:
        """
        Collision cercle / droite
        Droite définie par origine (ox, oy) et vecteur directeur (vx, vy)
        """
        dist = self.line_point_distance(ox, oy, vx, vy, cx, cy)
        return dist <= r

    def circle_line_intersection(self, cx: float, cy: float, r: float, ox: float, oy: float, vx: float, vy: float) -> tuple | None:
        """
        Intersection cercle / droite
        
        Returns:
            None : pas d'intersection
            ((px, py),) : tangence
            ((p1x, p1y), (p2x, p2y)) : 2 points
        """
        v_dot_v = vx**2 + vy**2
        if v_dot_v == 0:
            return None
        
        # Projection du centre sur la droite
        ocx, ocy = cx - ox, cy - oy
        t_proj = (ocx * vx + ocy * vy) / v_dot_v
        
        # Point le plus proche sur la droite
        hx = ox + t_proj * vx
        hy = oy + t_proj * vy
        
        # Distance centre -> droite
        d_sq = (cx - hx)**2 + (cy - hy)**2
        
        if d_sq > r**2:
            return None
        
        # Tangence
        if abs(d_sq - r**2) < 1e-10:
            return ((hx, hy),)
        
        # Deux points
        delta = math.sqrt(r**2 - d_sq)
        v_norm = math.sqrt(v_dot_v)
        ux, uy = vx / v_norm, vy / v_norm
        
        return (
            (hx + delta * ux, hy + delta * uy),
            (hx - delta * ux, hy - delta * uy),
        )

    # ======================================== CERCLE - SEGMENT ========================================
    def circle_segment_collide(self, cx: float, cy: float, r: float, x1: float, y1: float, x2: float, y2: float) -> bool:
        """Collision cercle / segment"""
        dist = self.segment_point_distance(x1, y1, x2, y2, cx, cy)
        return dist <= r

    def circle_segment_intersection(self, cx: float, cy: float, r: float, x1: float, y1: float, x2: float, y2: float) -> tuple | None:
        """
        Intersection cercle / segment
        
        Returns:
            None : pas d'intersection
            tuple de points sur le segment
        """
        vx, vy = x2 - x1, y2 - y1
        line_pts = self.circle_line_intersection(cx, cy, r, x1, y1, vx, vy)
        
        if line_pts is None:
            return None
        
        # Filtrer les points qui sont sur le segment
        seg_len_sq = vx**2 + vy**2
        if seg_len_sq == 0:
            return None
        
        valid = []
        for px, py in line_pts:
            # Paramètre t du point sur la droite
            t = ((px - x1) * vx + (py - y1) * vy) / seg_len_sq
            if 0 <= t <= 1:
                valid.append((px, py))
        
        return tuple(valid) if valid else None

    # ======================================== CERCLE - RECT ========================================
    def circle_rect_collide(self, cx: float, cy: float, r: float, left: float, top: float, right: float, bottom: float, border_radius: float = 0) -> bool:
        """Collision cercle / rect"""
        clx, cly = self.rect_closest_point(cx, cy, left, top, right, bottom, border_radius)
        return self.point_distance_sq(cx, cy, clx, cly) <= r**2

    def circle_rect_intersection(self, cx: float, cy: float, r: float, left: float, top: float, right: float, bottom: float, border_radius: float = 0) -> tuple | None:
        """
        Intersection cercle / rect (prend en compte border_radius)
        
        Returns:
            None ou tuple de points d'intersection
        """
        br = max(border_radius, 0)
        points = []
        
        # Segments droits du rect
        if br <= 0:
            segments = [
                (left, top, right, top),
                (right, top, right, bottom),
                (right, bottom, left, bottom),
                (left, bottom, left, top),
            ]
        else:
            segments = [
                (left + br, top, right - br, top),          # top
                (right, top + br, right, bottom - br),      # right
                (right - br, bottom, left + br, bottom),    # bottom
                (left, bottom - br, left, top + br),        # left
            ]
        
        for x1, y1, x2, y2 in segments:
            pts = self.circle_segment_intersection(cx, cy, r, x1, y1, x2, y2)
            if pts:
                points.extend(pts)
        
        # Coins arrondis
        if br > 0:
            for corner_cx, corner_cy in self._rect_corner_centers(left, top, right, bottom, br):
                pts = self.circle_circle_intersection(cx, cy, r, corner_cx, corner_cy, br)
                if pts:
                    # Filtrer selon le quadrant du coin
                    for px, py in pts:
                        if self._point_in_corner_quadrant(px, py, corner_cx, corner_cy, left, top, right, bottom, br):
                            points.append((px, py))
        
        if not points:
            return None
        
        # Dédupe
        unique = list(dict.fromkeys((round(x, 6), round(y, 6)) for x, y in points))
        return tuple(unique) if unique else None

    # ======================================== LIGNE - LIGNE ========================================
    def line_line_collide(self, ox1: float, oy1: float, vx1: float, vy1: float, ox2: float, oy2: float, vx2: float, vy2: float) -> bool:
        """Collision deux droites (True si sécantes ou confondues)"""
        det = vx1 * vy2 - vy1 * vx2
        if abs(det) > 1e-10:
            return True  # Sécantes
        dx, dy = ox2 - ox1, oy2 - oy1
        cross = dx * vy1 - dy * vx1
        return abs(cross) < 1e-10

    def line_line_intersection(self, ox1: float, oy1: float, vx1: float, vy1: float, ox2: float, oy2: float, vx2: float, vy2: float) -> tuple | None:
        """
        Intersection deux droites
        
        Returns:
            None : parallèles (non confondues)
            (px, py) : point d'intersection
        """
        det = vx1 * (-vy2) - vy1 * (-vx2)
        if abs(det) < 1e-10:
            return None
        
        dx, dy = ox2 - ox1, oy2 - oy1
        t = (dx * (-vy2) - dy * (-vx2)) / det
        
        return (ox1 + vx1 * t, oy1 + vy1 * t)

    # ======================================== LIGNE - SEGMENT ========================================
    def line_segment_collide(self, ox: float, oy: float, vx: float, vy: float, x1: float, y1: float, x2: float, y2: float) -> bool:
        """Collision droite / segment"""
        pts = self.line_segment_intersection(ox, oy, vx, vy, x1, y1, x2, y2)
        return pts is not None

    def line_segment_intersection(self, ox: float, oy: float, vx: float, vy: float, x1: float, y1: float, x2: float, y2: float) -> tuple | None:
        """
        Intersection droite / segment
        
        Returns:
            None ou (px, py)
        """
        svx, svy = x2 - x1, y2 - y1
        det = vx * (-svy) - vy * (-svx)
        
        if abs(det) < 1e-10:
            return None
        
        dx, dy = x1 - ox, y1 - oy
        t = (dx * (-svy) - dy * (-svx)) / det
        s = (dx * vy - dy * vx) / det
        
        if 0 <= s <= 1:
            return (ox + vx * t, oy + vy * t)
        return None

    # ======================================== LIGNE - RECT ========================================
    def line_rect_collide(self, ox: float, oy: float, vx: float, vy: float, left: float, top: float, right: float, bottom: float, border_radius: float = 0) -> bool:
        """Collision droite / rect"""
        pts = self.line_rect_intersection(ox, oy, vx, vy, left, top, right, bottom, border_radius)
        return pts is not None and len(pts) > 0

    def line_rect_intersection(self, ox: float, oy: float, vx: float, vy: float, left: float, top: float, right: float, bottom: float, border_radius: float = 0) -> tuple | None:
        """
        Intersection droite / rect (prend en compte border_radius)
        
        Returns:
            None ou tuple de points triés par paramètre t
        """
        br = max(border_radius, 0)
        points = []
        
        # Côtés droits
        if vy != 0:  # top
            t = (top - oy) / vy
            x = ox + t * vx
            if left + br <= x <= right - br:
                points.append((x, top, t))
        
        if vx != 0:  # right
            t = (right - ox) / vx
            y = oy + t * vy
            if top + br <= y <= bottom - br:
                points.append((right, y, t))
        
        if vy != 0:  # bottom
            t = (bottom - oy) / vy
            x = ox + t * vx
            if left + br <= x <= right - br:
                points.append((x, bottom, t))
        
        if vx != 0:  # left
            t = (left - ox) / vx
            y = oy + t * vy
            if top + br <= y <= bottom - br:
                points.append((left, y, t))
        
        # Coins arrondis
        if br > 0:
            A = vx**2 + vy**2
            if A != 0:
                for corner_cx, corner_cy in self._rect_corner_centers(left, top, right, bottom, br):
                    B = 2 * (vx * (ox - corner_cx) + vy * (oy - corner_cy))
                    C = (ox - corner_cx)**2 + (oy - corner_cy)**2 - br**2
                    
                    discriminant = B**2 - 4 * A * C
                    if discriminant < 0:
                        continue
                    
                    sqrt_d = math.sqrt(discriminant)
                    for t in ((-B - sqrt_d) / (2 * A), (-B + sqrt_d) / (2 * A)):
                        px = ox + t * vx
                        py = oy + t * vy
                        if self._point_in_corner_quadrant(px, py, corner_cx, corner_cy, left, top, right, bottom, br):
                            points.append((px, py, t))
        
        if not points:
            return None
        
        # Dédupe + tri par t
        seen = set()
        unique = []
        for px, py, t in sorted(points, key=lambda p: p[2]):
            key = (round(px, 6), round(py, 6))
            if key not in seen:
                unique.append((px, py))
                seen.add(key)
        
        return tuple(unique) if unique else None

    # ======================================== SEGMENT - SEGMENT ========================================
    def segment_segment_collide(self, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float, x4: float, y4: float) -> bool:
        """Collision deux segments"""
        return self.segment_segment_intersection(x1, y1, x2, y2, x3, y3, x4, y4) is not None

    def segment_segment_intersection(self, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float, x4: float, y4: float) -> tuple | None:
        """
        Intersection deux segments
        
        Returns:
            None ou (px, py)
        """
        vx1, vy1 = x2 - x1, y2 - y1
        vx2, vy2 = x4 - x3, y4 - y3
        
        det = vx1 * (-vy2) - vy1 * (-vx2)
        if abs(det) < 1e-10:
            return None
        
        dx, dy = x3 - x1, y3 - y1
        t = (dx * (-vy2) - dy * (-vx2)) / det
        s = (dx * vy1 - dy * vx1) / det
        
        if 0 <= t <= 1 and 0 <= s <= 1:
            return (x1 + vx1 * t, y1 + vy1 * t)
        return None

    # ======================================== SEGMENT - RECT ========================================
    def segment_rect_collide(self, x1: float, y1: float, x2: float, y2: float, left: float, top: float, right: float, bottom: float, border_radius: float = 0) -> bool:
        """Collision segment / rect"""
        # Une extrémité dans le rect
        if self.rect_contains_point(x1, y1, left, top, right, bottom, border_radius):
            return True
        if self.rect_contains_point(x2, y2, left, top, right, bottom, border_radius):
            return True
        # Sinon intersection avec un bord
        vx, vy = x2 - x1, y2 - y1
        pts = self.line_rect_intersection(x1, y1, vx, vy, left, top, right, bottom, border_radius)
        if pts is None:
            return False
        # Filtrer par t sur le segment
        seg_len_sq = vx**2 + vy**2
        if seg_len_sq == 0:
            return False
        for px, py in pts:
            t = ((px - x1) * vx + (py - y1) * vy) / seg_len_sq
            if 0 <= t <= 1:
                return True
        return False

    def segment_rect_intersection(self, x1: float, y1: float, x2: float, y2: float, left: float, top: float, right: float, bottom: float, border_radius: float = 0) -> tuple | None:
        """
        Intersection segment / rect
        
        Returns:
            None ou tuple de points
        """
        vx, vy = x2 - x1, y2 - y1
        line_pts = self.line_rect_intersection(x1, y1, vx, vy, left, top, right, bottom, border_radius)
        
        if line_pts is None:
            return None
        
        seg_len_sq = vx**2 + vy**2
        if seg_len_sq == 0:
            return None
        
        valid = []
        for px, py in line_pts:
            t = ((px - x1) * vx + (py - y1) * vy) / seg_len_sq
            if 0 <= t <= 1:
                valid.append((px, py))
        
        return tuple(valid) if valid else None

    # ======================================== RECT - RECT ========================================
    def rect_rect_collide(self, l1: float, t1: float, r1: float, b1: float, br1: float, l2: float, t2: float, r2: float, b2: float, br2: float) -> bool:
        """Collision deux rects (avec border_radius)"""
        # AABB rapide
        if r1 < l2 or r2 < l1 or b1 < t2 or b2 < t1:
            return False
        
        if br1 <= 0 and br2 <= 0:
            return True
        
        # Zones centrales
        if not (r1 - br1 < l2 or l1 + br1 > r2 or t1 > b2 or b1 < t2):
            return True
        if not (l1 > r2 or r1 < l2 or b1 - br1 < t2 or t1 + br1 > b2):
            return True
        
        corners1 = self._rect_corner_centers(l1, t1, r1, b1, br1) if br1 > 0 else []
        corners2 = self._rect_corner_centers(l2, t2, r2, b2, br2) if br2 > 0 else []
        
        # Coin vs coin
        if br1 > 0 and br2 > 0:
            for cx1, cy1 in corners1:
                for cx2, cy2 in corners2:
                    if self.point_distance_sq(cx1, cy1, cx2, cy2) <= (br1 + br2)**2:
                        return True
        
        # Coin vs rect
        if br1 > 0:
            for cx, cy in corners1:
                if self.circle_rect_collide(cx, cy, br1, l2, t2, r2, b2):
                    return True
        if br2 > 0:
            for cx, cy in corners2:
                if self.circle_rect_collide(cx, cy, br2, l1, t1, r1, b1):
                    return True
        
        return False

    # ======================================== RECT - UTILITIES ========================================
    def rect_contains_point(self, px: float, py: float, left: float, top: float, right: float, bottom: float, border_radius: float = 0) -> bool:
        """Vérifie si un point est dans un rect (avec border_radius)"""
        if not (left <= px <= right and top <= py <= bottom):
            return False
        
        br = max(border_radius, 0)
        if br <= 0:
            return True
        
        # Zones centrales — pas de coin à vérifier
        if left + br <= px <= right - br:
            return True
        if top + br <= py <= bottom - br:
            return True
        
        # Coins
        for cx, cy in self._rect_corner_centers(left, top, right, bottom, br):
            # Vérifier si dans le quadrant de ce coin
            in_quadrant = (
                (px <= cx if cx < (left + right) / 2 else px >= cx) and
                (py <= cy if cy < (top + bottom) / 2 else py >= cy)
            )
            if in_quadrant:
                return self.point_distance_sq(px, py, cx, cy) <= br**2
        
        return False

    def rect_closest_point(px: float, py: float, left: float, top: float, right: float, bottom: float, border_radius: float = 0) -> tuple[float, float]:
        """Point du rect le plus proche d'un point donné"""
        br = max(border_radius, 0)
        
        if br <= 0:
            return (max(left, min(px, right)), max(top, min(py, bottom)))
        
        # Zones centrales
        if left + br <= px <= right - br:
            return (px, max(top, min(py, bottom)))
        if top + br <= py <= bottom - br:
            return (max(left, min(px, right)), py)
        
        # Coins
        for cx, cy, sx, sy in (
            (left + br, top + br, -1, -1),
            (right - br, top + br, 1, -1),
            (left + br, bottom - br, -1, 1),
            (right - br, bottom - br, 1, 1),
        ):
            if sx * (px - cx) >= 0 and sy * (py - cy) >= 0:
                dx, dy = px - cx, py - cy
                dist = math.sqrt(dx**2 + dy**2)
                if dist == 0:
                    return (cx + sx * br, cy)
                if dist <= br:
                    return (px, py)
                ratio = br / dist
                return (cx + dx * ratio, cy + dy * ratio)
        
        # Fallback
        return (max(left, min(px, right)), max(top, min(py, bottom)))

    def rect_collision_normal(self, px: float, py: float, left: float, top: float, right: float, bottom: float, border_radius: float = 0, circle_cx: float = 0, circle_cy: float = 0) -> tuple[float, float]:
        """
        Vecteur normal au point de collision sur un rect (normalisé)
        circle_cx/cy = centre du cercle qui collide (utilisé comme fallback)
        """
        br = max(border_radius, 0)
        epsilon = 1e-6
        
        if br <= 0:
            if abs(py - top) < epsilon:       return (0.0, -1.0)
            if abs(py - bottom) < epsilon:    return (0.0, 1.0)
            if abs(px - left) < epsilon:      return (-1.0, 0.0)
            if abs(px - right) < epsilon:     return (1.0, 0.0)
        else:
            # Côtés droits
            if left + br <= px <= right - br:
                if abs(py - top) < epsilon:       return (0.0, -1.0)
                if abs(py - bottom) < epsilon:    return (0.0, 1.0)
            if top + br <= py <= bottom - br:
                if abs(px - left) < epsilon:      return (-1.0, 0.0)
                if abs(px - right) < epsilon:     return (1.0, 0.0)
            
            # Coins arrondis
            for cx, cy in self._rect_corner_centers(left, top, right, bottom, br):
                if self.point_distance_sq(px, py, cx, cy) < (br + epsilon)**2:
                    dx, dy = px - cx, py - cy
                    dist = math.sqrt(dx**2 + dy**2)
                    if dist > 0:
                        return (dx / dist, dy / dist)
        
        # Fallback : normale depuis le centre du cercle
        dx, dy = px - circle_cx, py - circle_cy
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 0:
            return (dx / dist, dy / dist)
        return (0.0, -1.0)

    # ======================================== LIGNE - POINT ========================================
    def line_point_distance(self, ox: float, oy: float, vx: float, vy: float, px: float, py: float) -> float:
        """Distance d'un point à une droite"""
        v_len_sq = vx**2 + vy**2
        if v_len_sq == 0:
            return self.point_distance(ox, oy, px, py)
        t = ((px - ox) * vx + (py - oy) * vy) / v_len_sq
        proj_x = ox + t * vx
        proj_y = oy + t * vy
        return self.point_distance(px, py, proj_x, proj_y)

    def line_point_projection(self, ox: float, oy: float, vx: float, vy: float, px: float, py: float) -> tuple[float, float]:
        """Projection d'un point sur une droite"""
        v_len_sq = vx**2 + vy**2
        if v_len_sq == 0:
            return (ox, oy)
        t = ((px - ox) * vx + (py - oy) * vy) / v_len_sq
        return (ox + t * vx, oy + t * vy)

    # ======================================== SEGMENT - POINT ========================================
    def segment_point_distance(self, x1: float, y1: float, x2: float, y2: float, px: float, py: float) -> float:
        """Distance d'un point à un segment"""
        proj_x, proj_y = self.segment_point_projection(x1, y1, x2, y2, px, py)
        return self.point_distance(px, py, proj_x, proj_y)

    def segment_point_projection(self, x1: float, y1: float, x2: float, y2: float,px: float, py: float) -> tuple[float, float]:
        """Projection d'un point sur un segment (clampée entre les extrémités)"""
        vx, vy = x2 - x1, y2 - y1
        v_len_sq = vx**2 + vy**2
        if v_len_sq == 0:
            return (x1, y1)
        t = max(0, min(1, ((px - x1) * vx + (py - y1) * vy) / v_len_sq))
        return (x1 + t * vx, y1 + t * vy)

    # ======================================== HELPERS INTERNES ========================================
    def _rect_corner_centers(self, left: float, top: float, right: float, bottom: float, br: float) -> list[tuple[float, float]]:
        """Centres des 4 coins arrondis d'un rect"""
        return [
            (left + br, top + br),
            (right - br, top + br),
            (left + br, bottom - br),
            (right - br, bottom - br),
        ]

    def _point_in_corner_quadrant(self, px: float, py: float, cx: float, cy: float, left: float, top: float, right: float, bottom: float) -> bool:
        """Vérifie si un point est dans le quadrant d'un coin arrondi"""
        mid_x = (left + right) / 2
        mid_y = (top + bottom) / 2
        
        if cx < mid_x:  # gauche
            if px > cx: return False
        else:           # droite
            if px < cx: return False
        
        if cy < mid_y:  # haut
            if py > cy: return False
        else:           # bas
            if py < cy: return False
        
        return True


# ======================================== INSTANCE ========================================
geometry_manager = GeometryManager()