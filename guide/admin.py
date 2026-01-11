from django.contrib import admin
from django.http import HttpResponse
from .models import Employee, Disease, Insurance, Fetal, ActivityLog, Maternal, Limit

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("empno", "name")
    search_fields = ("empno", "name")

# --- 산모 DB 관리 기능 (월별 조회 및 엑셀 다운로드 추가) ---
@admin.register(Maternal)
class MaternalAdmin(admin.ModelAdmin):
    list_display = ("name", "birthdate", "contact", "registered_by", "created_at")
    search_fields = ("name", "contact", "registered_by__name")
    list_filter = ("registered_by", "created_at")
    
    # 1. 등록 월 별 조회를 위한 날짜 계층 메뉴 추가
    # 관리자 페이지 상단에 연도/월별로 이동할 수 있는 메뉴가 생성됩니다.
    date_hierarchy = 'created_at'
    
    ordering = ("-created_at",)

    # 2. 엑셀 다운로드 기능 정의
    actions = ["export_as_excel"]

    def export_as_excel(self, request, queryset):
        import openpyxl # 엑셀 생성을 위한 라이브러리
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=maternal_list.xlsx'
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "산모 리스트"
        
        # 엑셀 상단 헤더 작성
        headers = ['산모이름', '생년월일', '연락처', '등록직원', '등록일시']
        ws.append(headers)
        
        # 필터링되거나 선택된 데이터 작성
        for obj in queryset:
            reg_employee = obj.registered_by.name if obj.registered_by else "정보없음"
            created_at_str = obj.created_at.strftime('%Y-%m-%d %H:%M') if obj.created_at else ""
            ws.append([obj.name, obj.birthdate, obj.contact, reg_employee, created_at_str])
        
        wb.save(response)
        return response
    
    export_as_excel.short_description = "선택된 산모 데이터 엑셀 다운로드"

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
