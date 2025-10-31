import requests
from django.db import models
from django.utils.timezone import now

class Visitor(models.Model):
    ip_address = models.GenericIPAddressField(blank=True, null=True)  # Public IP (optional)
    private_ip = models.CharField(max_length=50, blank=True, null=True)  # Private IP (optional)
    user_agent = models.TextField()  # User-Agent string (used to identify visitors)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    last_visit = models.DateTimeField(default=now)  # Last visit time
    visit_count = models.PositiveIntegerField(default=0)  # Visit count

    def update_location(self):
        """
        Fetch city and country based on the visitor's IP address using ip-api.
        """
        if not self.ip_address:
            return
        
        url = f"http://ip-api.com/json/{self.ip_address}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'fail':
                    self.city = "Unknown"
                    self.country = "Unknown"
                else:
                    self.city = data.get("city", "Unknown")
                    self.country = data.get("country", "Unknown")
        except requests.RequestException:
            # If the API request fails, default to "Unknown"
            self.city = "Unknown"
            self.country = "Unknown"

    def __str__(self):
        return f"{self.user_agent} - {self.visit_count} visits"
