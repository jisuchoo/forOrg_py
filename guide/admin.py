from django.urls import path
from django.shortcuts import redirect
from django.contrib import admin
from .models import Employee, Disease, Insurance, Fetal, ActivityLog, Maternal, Limit

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("empno", "name")
    search_fields = ("empno", "name")

# --- 산모 DB 관리: 월별 조회 및 필터 기능 추가 ---
@admin.register(Maternal)
class MaternalAdmin(admin.ModelAdmin):
    # 목록에 표시할 항목
    list_display = ("name", "birthdate", "contact", "registered_by", "created_at")
    # 검색 기능: 이름, 연락처, 등록 직원 이름으로 검색 가능
    search_fields = ("name", "contact", "registered_by__name")
    
    # 1. 우측 사이드바 필터: 등록 직원 및 등록 날짜별 필터
    list_filter = ("registered_by", "created_at")
    
    # 2. 상단 월별/연도별 네비게이션 (핵심 기능)
    # 이 설정을 통해 관리자 페이지 상단에 '모든 날짜 / 2026 / 1월' 형태의 메뉴가 생깁니다.
    date_hierarchy = 'created_at'    
    ordering = ("-created_at",)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            # ID 패턴보다 위에 있어야 먼저 인식됩니다.
            path('export-excel-all/', self.admin_site.admin_view(self.export_excel_view), name='maternal_export_excel'),
        ]
        return custom_urls + urls

    def export_excel_view(self, request):
        # 실제 엑셀을 만드는 로직은 views.py의 함수를 호출하도록 연결
        from .views import export_maternal_excel
        return export_maternal_excel(request)

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

# --- 활동 로그 관리 (에러 수정 및 현대적 방식 적용) ---
@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("display_who", "action", "display_detail", "ip_address", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("user__username", "actor", "detail", "ip_address")

    @admin.display(description="User")
    def display_who(self, obj):
        return obj.user.username if obj.user else (obj.actor or "-")

    @admin.display(description="Detail")
    def display_detail(self, obj):
        return (obj.detail[:30] + "...") if obj.detail and len(obj.detail) > 30 else obj.detail
