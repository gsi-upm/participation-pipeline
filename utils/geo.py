import os
import json
from geopy.geocoders import GoogleV3


def geolocate(location, api_key=None):
    geolocator = GoogleV3(api_key=api_key or os.environ['GOOGLE_API_KEY'])

    try:
        geolocation = geolocator.geocode(location)
    except:
        geolocation = None

    if geolocation:
        result = list(geolocation.raw["geometry"]["location"].values())
        
        try:
            country = next(filter(lambda x: "country" in x["types"], geolocation.raw["address_components"]))["long_name"]
        except StopIteration:
            try:
                country = next(filter(lambda x: "continent" in x["types"], geolocation.raw["address_components"]))["long_name"]
            except:
                country = None
        
        return result, country
    else:
        return None, None