import os
import requests
from geopy.geocoders import Nominatim
from dotenv import load_dotenv

load_dotenv()

def get_lat_long(location_name):
    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.geocode(location_name)
    return (location.latitude, location.longitude) if location else (None, None)

def get_solar_data(location_name):
    lat, long = get_lat_long(location_name)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": long,
        "hourly": "direct_normal_irradiance,shortwave_radiation",
        "current": "temperature_2m,cloud_cover",
        "timezone": "auto"
    }

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None

  # Example usage
