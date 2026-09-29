import math
from typing import Optional


def haversine_km(lat1: Optional[float], lon1: Optional[float], lat2: Optional[float], lon2: Optional[float]) -> Optional[float]:
    """Great-circle distance in kilometres between two lat/lon points.
    Returns None if either point is missing coordinates (caller should fall
    back to city-name matching in that case)."""
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return None

    R = 6371.0  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)


def proximity_score(distance_km: Optional[float], same_city: bool) -> int:
    """Maps a distance (or city match) to a 0-20 hyperlocal proximity score."""
    if distance_km is not None:
        if distance_km <= 5:
            return 20
        if distance_km <= 15:
            return 15
        if distance_km <= 50:
            return 8
        return 2
    # No coordinates available - fall back to city-name comparison.
    return 15 if same_city else 3
