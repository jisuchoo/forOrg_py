from .models import ActivityLog

def log_activity(request, action, detail=""):
    actor_name = request.session.get("user_name") \
                 or (request.user.username if request.user.is_authenticated else None)
    try:
        ActivityLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            actor=actor_name,
            action=action,
            detail=detail,
            ip_address=get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")
        )
    except Exception:
        # 로깅 실패로 본 기능이 깨지지 않도록
        import logging
        logging.exception("Failed to log activity")

def get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    return xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR")
