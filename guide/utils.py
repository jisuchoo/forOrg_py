from .models import ActivityLog

def log_activity(request, action, detail=""):
    ActivityLog.objects.create(
        user=request.session.get("user_name"),
        action=action,
        detail=detail,
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")
    )

def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")
