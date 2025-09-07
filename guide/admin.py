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
    list_display = ("who", "action", "short_detail", "ip_address", "short_user_agent", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("user__username", "actor", "detail", "ip_address", "user_agent")

    def who(self, obj):
        return obj.user.username if obj.user else (obj.actor or "-")
    who.short_description = "User"

    def short_detail(self, obj):
        return (obj.detail[:30] + "...") if obj.detail and len(obj.detail) > 30 else obj.detail
    short_detail.short_description = "Detail"

    def short_user_agent(self, obj):
        return (obj.user_agent[:40] + "...") if obj.user_agent and len(obj.user_agent) > 40 else obj.user_agent
    short_user_agent.short_description = "User Agent"
