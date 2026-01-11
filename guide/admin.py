from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.utils.html import format_html
from django.template.response import TemplateResponse
import openpyxl  # 엑셀 생성을 위한 라이브러리
from .models import Employee, Disease, Insurance, Fetal, ActivityLog, Maternal, Limit

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("empno", "name")
    search_fields = ("empno", "name")

# --- 산모 DB 관리 및 필터링된 전체 엑셀 다운로드 기능 ---
@admin.register(Maternal)
class MaternalAdmin(admin.ModelAdmin):
    list_display = ("name", "birthdate", "contact", "registered_by", "created_at")
    search_fields = ("name", "contact", "registered_by__name")
    list_filter = ("registered_by", "created_at")
    
    # 1. 상단에 연도/월별 이동 메뉴 추가
    date_hierarchy = 'created_at'
    ordering = ("-created_at",)

    # 2. 엑셀 다운로드 URL 등록
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-excel/', self.admin_site.admin_view(self.export_all_to_excel), name='maternal_export_excel'),
        ]
        return custom_urls + urls

    # 3. 필터링된 전체 데이터를 엑셀로 생성하는 함수
    def export_all_to_excel(self, request):
        # 현재 적용된 모든 필터(월별, 검색어 등)를 유지한 쿼리셋 가져오기
        from django.contrib.admin.views.main import ChangeList
        cl = self.get_changelist_instance(request)
        queryset = cl.get_queryset(request)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=maternal_list_all.xlsx'
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "필터링된 산모 리스트"
        
        headers = ['산모이름', '생년월일', '연락처', '등록직원', '등록일시']
        ws.append(headers)
        
        for obj in queryset:
            reg_employee = obj.registered_by.name if obj.registered_by else "-"
            created_at_str = obj.created_at.strftime('%Y-%m-%d %H:%M') if obj.created_at else ""
            ws.append([obj.name, obj.birthdate, obj.contact, reg_employee, created_at_str])
        
        wb.save(response)
        return response

    # 4. 관리자 페이지 목록 우측 상단에 버튼 추가를 위한 템플릿 전달
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_export_button'] = True
        return super().changelist_view(request, extra_context=extra_context)

# --- 기타 기존 관리자 설정 ---
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
    list_display = ("who", "action", "short_detail", "ip_address", "created_at")
    list_filter = ("action", "created_at")
    
    def who(self, obj):
        return obj.user.username if obj.user else (obj.actor or "-")
