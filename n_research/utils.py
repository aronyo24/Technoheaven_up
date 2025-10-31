import geoip2.database
from django.conf import settings

def get_client_ip(request):
    """
    Retrieve the client's IP address from the request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_location(ip):
    """
    Retrieve city and country based on the IP address using GeoLite2.
    """
    try:
        reader = geoip2.database.Reader(settings.GEOIP_PATH)
        response = reader.city(ip)
        return {
            'city': response.city.name,
            'country': response.country.name,
        }
    except Exception as e:
        return {'city': None, 'country': None}
