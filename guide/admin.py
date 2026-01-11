from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.utils.html import format_html
from django.template.response import TemplateResponse
import openpyxl  # 엑셀 생성을 위해 필수 (requirements.txt에 추가 필요)
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
    
    # 상단에 연도/월별로 편리하게 이동할 수 있는 메뉴 추가
    date_hierarchy = 'created_at'
    ordering = ("-created_at",)

    # 엑셀 다운로드를 위한 전용 URL 등록
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-excel-all/', self.admin_site.admin_view(self.export_all_to_excel), name='maternal_export_excel_all'),
        ]
        return custom_urls + urls

    # 필터링된(월별 조회 등) 전체 데이터를 엑셀로 생성하는 함수
    def export_all_to_excel(self, request):
        # 현재 화면에 적용된 모든 필터(월별, 검색어 등)가 반영된 전체 쿼리셋 가져오기
        from django.contrib.admin.views.main import ChangeList
        list_display = self.get_list_display(request)
        list_display_links = self.get_list_display_links(request, list_display)
        
        cl = ChangeList(
            request, self.model, list_display,
            list_display_links, self.get_list_filter(request),
            self.date_hierarchy, self.search_fields,
            self.get_list_select_related(request),
            self.list_per_page, self.list_max_show_all,
            self.list_editable, self, self.sortable_by,
            self.search_help_text
        )
        queryset = cl.get_queryset(request)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=maternal_filtered_full_list.xlsx'
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "산모 리스트"
        
        # 헤더 작성
        headers = ['산모이름', '생년월일', '연락처', '등록직원', '등록일시']
        ws.append(headers)
        
        # 데이터 작성 (페이징 무관하게 필터링된 전체)
        for obj in queryset:
            reg_name = obj.registered_by.name if obj.registered_by else "-"
            created_str = obj.created_at.strftime('%Y-%m-%d %H:%M') if obj.created_at else ""
            ws.append([obj.name, obj.birthdate, obj.contact, reg_name, created_str])
        
        wb.save(response)
        return response

# --- 활동 로그 관리 (에러 수정 완료) ---
@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("display_who", "action", "display_detail", "ip_address", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("user__username", "actor", "detail", "ip_address")

    @admin.display(description="사용자")
    def display_who(self, obj):
        return obj.user.username if obj.user else (obj.actor or "-")

    @admin.display(description="상세내용")
    def display_detail(self, obj):
        if obj.detail and len(obj.detail) > 30:
            return obj.detail[:30] + "..."
        return obj.detail

# --- 기타 기존 모델 등록 ---
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
