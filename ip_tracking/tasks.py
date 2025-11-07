from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from ip_tracking.models import RequestLog, SuspiciousIP

@shared_task
def detect_suspicious_ips():
    """Detect IPs with abnormal request patterns or sensitive access."""
    now = timezone.now()
    one_hour_ago = now - timedelta(hours=1)

    # Get requests in the past hour
    recent_requests = RequestLog.objects.filter(timestamp__gte=one_hour_ago)

    # Group by IP and count
    ip_counts = {}
    for req in recent_requests:
        ip_counts[req.ip_address] = ip_counts.get(req.ip_address, 0) + 1

    # Threshold-based detection
    for ip, count in ip_counts.items():
        if count > 100:
            SuspiciousIP.objects.update_or_create(
                ip_address=ip,
                defaults={'reason': f'High request volume: {count} requests in the last hour'}
            )

    # Sensitive path detection
    sensitive_paths = ['/admin', '/login', '/ip_tracking/login-anonymous', '/ip_tracking/login-authenticated']
    sensitive_hits = recent_requests.filter(path__in=sensitive_paths).values_list('ip_address', flat=True).distinct()

    for ip in sensitive_hits:
        SuspiciousIP.objects.update_or_create(
            ip_address=ip,
            defaults={'reason': 'Accessed sensitive paths'}
        )

    return f"Anomaly detection completed at {now}."
