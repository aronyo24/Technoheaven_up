from django.db import models
from django.utils.timezone import localtime, now
import pytz

class Visitor(models.Model):
    ip_address = models.GenericIPAddressField()  # Public IP
    private_ip = models.CharField(max_length=50, blank=True, null=True)  # Private IP
    user_agent = models.TextField()  # User-Agent string
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    visit_date = models.DateTimeField(auto_now_add=True)  # Auto timestamp
    
    def get_local_time(self, timezone_str):
        try:
            tz = pytz.timezone(timezone_str)
            local_time = localtime(self.visit_date, tz)
            return local_time.strftime('%Y-%m-%d %H:%M:%S')  # 24-hour format
        except pytz.UnknownTimeZoneError:
            return "Invalid Timezone"

    def __str__(self):
        return f"{self.ip_address} - {self.visit_date}"

    @staticmethod
    def get_monthly_visitors():
        current_month = now().month
        current_year = now().year
        return Visitor.objects.filter(visit_date__year=current_year, visit_date__month=current_month).count()

    @staticmethod
    def get_total_visitors():
        return Visitor.objects.count()
