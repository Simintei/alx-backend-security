from django.http import HttpResponseForbidden
from django.core.cache import cache
from ipgeolocation import IPGeolocationAPI
from .models import BlockedIP, RequestLog

class IPBlockMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.geo_api = IPGeolocationAPI()

    def __call__(self, request):
        ip = self.get_client_ip(request)

        # Block IP if in blacklist
        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden("Access denied: Your IP has been blocked.")

        # Log request with geolocation
        self.log_request(ip, request.path)

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

    def log_request(self, ip, path):
        """Fetch geolocation data (cached for 24 hours) and save request log."""
        cache_key = f"geo_{ip}"
        geo_data = cache.get(cache_key)

        if not geo_data:
            try:
                response = self.geo_api.get_geolocation(ip_address=ip)
                geo_data = {
                    'country': response.get('country_name', ''),
                    'city': response.get('city', '')
                }
                cache.set(cache_key, geo_data, 60 * 60 * 24)  # Cache for 24 hours
            except Exception:
                geo_data = {'country': '', 'city': ''}

        RequestLog.objects.create(
            ip_address=ip,
            path=path,
            country=geo_data['country'],
            city=geo_data['city']
        )
