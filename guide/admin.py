# admin.py
from django.contrib import admin
from .models import Employee, Disease, ActivityLog

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("empno", "name")

@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ("name", "acceptance", "surgery", "recurrence")

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("user",
        "action",
        "detail",        # 👉 조회/검색 내용
        "ip_address",
        "user_agent",    # 👉 접속 브라우저/OS 정보
        "created_at"
    )
    list_filter = ("action", "created_at")
    search_fields = ("user__username", "detail", "ip_address", "user_agent")
