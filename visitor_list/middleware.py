import requests
from visitors.models import Visitor
from django.utils.timezone import now

class VisitorTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Get the IP address
            ip_address = self.get_ip_address(request)

            # Fetch location data
            geo_data = self.get_location(ip_address)

            # Get the user agent
            user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')

            # Save visitor data
            Visitor.objects.create(
                ip_address=ip_address,
                user_agent=user_agent,
                city=geo_data.get('city', 'Unknown'),
                country=geo_data.get('country', 'Unknown'),
            )
        except Exception as e:
            print(f"VisitorTrackingMiddleware error: {e}")

        return self.get_response(request)

    def get_ip_address(self, request):
        """
        Retrieves the client's IP address from request headers or META.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        return ip_address

    def get_location(self, ip_address):
        """
        Fetches city and country based on the IP address using ip-api.com.
        """
        try:
            # Exclude private and loopback addresses
            private_prefixes = ('127.', '192.168.', '10.', '172.16.', '172.31.')
            if ip_address.startswith(private_prefixes):
                return {"city": "Local", "country": "Local Network"}

            # Use a geolocation service
            response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    "city": data.get("city", "Unknown"),
                    "country": data.get("country", "Unknown"),
                }
        except requests.exceptions.RequestException as e:
            print(f"Error fetching location data: {e}")
        return {"city": "Unknown", "country": "Unknown"}
