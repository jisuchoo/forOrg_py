from django.contrib import admin
from .models import Employee, Disease, Insurance, Fetal, ActivityLog, Maternal, Limit

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("empno", "name")
    search_fields = ("empno", "name")

# --- 산모 DB 관리 기능 추가 ---
@admin.register(Maternal)
class MaternalAdmin(admin.ModelAdmin):
    # 관리자 목록에 보여줄 항목들
    list_display = ("name", "birthdate", "contact", "registered_by", "created_at")
    # 이름, 연락처, 등록한 직원의 이름으로 검색 가능
    search_fields = ("name", "contact", "registered_by__name")
    # 등록 일시 및 사번별로 필터링해서 보기
    list_filter = ("created_at", "registered_by")
    # 등록 일시 기준 최신순 정렬
    ordering = ("-created_at",)

@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ("name", "health", "general", "simple")
    search_fields = ("name", "health", "general", "simple")

@admin.register(Insurance)
class InsuranceAdmin(admin.ModelAdmin):
    list_display = ("company", "type", "highlight")
    search_fields = ("company", "type")
    list_filter = ("type", "highlight")

@admin.register(Fetal)
class FetalAdmin(admin.ModelAdmin):
    list_display = ("disease", "current", "history", "documents")
    search_fields = ("disease", "current", "history", "documents")

@admin.register(Limit)
class LimitAdmin(admin.ModelAdmin):
    list_display = ("product", "plan", "coverage", "minAge", "maxAge", "amount")
    list_filter = ("product", "plan")
    search_fields = ("product", "plan", "coverage")

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
