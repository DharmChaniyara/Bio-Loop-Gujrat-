"""
Geographical calculations, Haversine formula, and transport time estimation.
"""
import math
from typing import Dict, Any, List

# Estimated average rural road transit speed for commercial tractors/trucks in Gujarat
DEFAULT_RURAL_TRANSIT_SPEED_KMH = 32.0


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees).
    Returns distance in kilometers (rounded to 1 decimal place).
    """
    R = 6371.0  # Earth radius in kilometers

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return round(R * c, 1)


def estimate_trip_time_minutes(distance_km: float, speed_kmh: float = DEFAULT_RURAL_TRANSIT_SPEED_KMH) -> int:
    """
    Estimate one-way tractor-trolley or rural truck transit time in minutes.
    Incorporates an indicative 25% road winding/circuity factor over straight-line distance.
    """
    circuity_factor = 1.25
    effective_road_km = distance_km * circuity_factor
    hours = effective_road_km / speed_kmh
    return max(5, int(round(hours * 60)))
