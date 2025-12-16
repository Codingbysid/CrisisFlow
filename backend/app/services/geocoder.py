from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from typing import Tuple, Optional
import time


def get_coordinates(address: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Geocode an address string to latitude and longitude using OpenStreetMap Nominatim.
    
    Args:
        address: Address string (e.g., "5th and Main Street, San Francisco")
        
    Returns:
        Tuple of (latitude, longitude) or (None, None) if geocoding fails
    """
    if not address or address == "Location not specified":
        return None, None
    
    try:
        geolocator = Nominatim(user_agent="crisisflow_app")
        # Add a small delay to respect rate limits (1 request per second)
        time.sleep(1)
        location = geolocator.geocode(address, timeout=10)
        
        if location:
            return location.latitude, location.longitude
        return None, None
        
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"Geocoding error for '{address}': {e}")
        return None, None
    except Exception as e:
        print(f"Unexpected geocoding error for '{address}': {e}")
        return None, None

