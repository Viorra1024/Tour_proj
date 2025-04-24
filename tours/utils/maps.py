import requests
import logging
import json
from django.conf import settings

logger = logging.getLogger(__name__)

def get_coordinates_from_address(address):
    """
    Get coordinates (latitude, longitude) from an address using Google Maps Geocoding API
    """
    api_key = settings.GOOGLE_MAPS_API_KEY
    
    if not api_key:
        logger.warning("Google Maps API key is not configured")
        return None, None
    
    try:
        # Format the address for URL encoding
        formatted_address = address.replace(' ', '+')
        
        # Prepare the geocoding API request
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={formatted_address}&key={api_key}"
        
        # Make the request
        response = requests.get(url)
        data = response.json()
        
        # Check the API response
        if data['status'] == 'OK':
            # Extract coordinates from the first result
            location = data['results'][0]['geometry']['location']
            latitude = location['lat']
            longitude = location['lng']
            
            logger.info(f"Successfully geocoded address: {address}")
            return latitude, longitude
        else:
            logger.error(f"Error geocoding address {address}: {data['status']}")
            return None, None
    
    except Exception as e:
        logger.error(f"Exception during geocoding: {str(e)}")
        return None, None

def get_nearby_attractions(latitude, longitude, radius=5000, attraction_type=None):
    """
    Get nearby attractions using Google Maps Places API
    
    Args:
        latitude: float - the latitude coordinate
        longitude: float - the longitude coordinate
        radius: int - search radius in meters (default: 5000)
        attraction_type: str - type of place (e.g., 'museum', 'park', etc.)
    
    Returns:
        list of places near the coordinates
    """
    api_key = settings.GOOGLE_MAPS_API_KEY
    
    if not api_key:
        logger.warning("Google Maps API key is not configured")
        return []
    
    try:
        # Build the base URL
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius={radius}&key={api_key}"
        
        # Add attraction type if specified
        if attraction_type:
            url += f"&type={attraction_type}"
        
        # Make the request
        response = requests.get(url)
        data = response.json()
        
        # Check the API response
        if data['status'] == 'OK':
            # Extract place information
            places = data['results']
            
            # Format the results
            formatted_places = []
            for place in places:
                formatted_place = {
                    'name': place['name'],
                    'location': place['geometry']['location'],
                    'rating': place.get('rating', None),
                    'types': place.get('types', []),
                    'vicinity': place.get('vicinity', ''),
                    'place_id': place['place_id']
                }
                formatted_places.append(formatted_place)
            
            logger.info(f"Found {len(formatted_places)} places near coordinates ({latitude}, {longitude})")
            return formatted_places
        else:
            logger.error(f"Error finding nearby places: {data['status']}")
            return []
    
    except Exception as e:
        logger.error(f"Exception during nearby search: {str(e)}")
        return []

def get_directions(origin_lat, origin_lng, dest_lat, dest_lng, mode="driving"):
    """
    Get directions between two points using Google Maps Directions API
    
    Args:
        origin_lat: float - origin latitude
        origin_lng: float - origin longitude
        dest_lat: float - destination latitude
        dest_lng: float - destination longitude
        mode: str - transportation mode ('driving', 'walking', 'bicycling', 'transit')
    
    Returns:
        dictionary with route information
    """
    api_key = settings.GOOGLE_MAPS_API_KEY
    
    if not api_key:
        logger.warning("Google Maps API key is not configured")
        return None
    
    try:
        # Build the URL
        url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin_lat},{origin_lng}&destination={dest_lat},{dest_lng}&mode={mode}&key={api_key}"
        
        # Make the request
        response = requests.get(url)
        data = response.json()
        
        # Check the API response
        if data['status'] == 'OK':
            # Extract route information
            route = data['routes'][0]
            leg = route['legs'][0]
            
            # Format the results
            directions = {
                'distance': leg['distance']['text'],
                'duration': leg['duration']['text'],
                'start_address': leg['start_address'],
                'end_address': leg['end_address'],
                'steps': []
            }
            
            # Extract steps
            for step in leg['steps']:
                directions['steps'].append({
                    'instruction': step['html_instructions'],
                    'distance': step['distance']['text'],
                    'duration': step['duration']['text']
                })
            
            logger.info(f"Successfully retrieved directions from ({origin_lat}, {origin_lng}) to ({dest_lat}, {dest_lng})")
            return directions
        else:
            logger.error(f"Error getting directions: {data['status']}")
            return None
    
    except Exception as e:
        logger.error(f"Exception during directions request: {str(e)}")
        return None 