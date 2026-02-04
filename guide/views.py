import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from django.db.models import Q, Case, When, IntegerField  # ← 오류 해결을 위해 Case, When, IntegerField 추가
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
from .models import Employee, Disease, Insurance, Fetal, Limit, Maternal
from .utils import log_activity
from django.http import HttpResponse
import openpyxl
from openpyxl.utils import get_column_letter

# --- 로그인 / 로그아웃 및 홈 ---
def login_view(request):
    if request.method == "POST":
        empno, password = request.POST.get("empno"), request.POST.get("password")
        try:
            user = Employee.objects.get(empno=empno, password=password)
            request.session["user_id"], request.session["user_name"] = user.id, user.name or user.empno
            return redirect("home")
        except Employee.DoesNotExist:
            return render(request, "guide/login.html", {"error": "사번 또는 비밀번호가 올바르지 않습니다."})
    return render(request, "guide/login.html")

# 비밀번호 변경 기능 추가
def password_change_view(request):
    if request.method == "POST":
        empno = request.POST.get("empno")
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        
        try:
            employee = Employee.objects.get(empno=empno, password=old_password) #
            employee.password = new_password
            employee.save()
            log_activity(request, "PWD_CHANGE", f"비밀번호 변경 성공: {empno}")
            return render(request, "guide/login.html", {"message": "비밀번호가 성공적으로 변경되었습니다. 다시 로그인하세요."})
        except Employee.DoesNotExist:
            return render(request, "guide/password_change.html", {"error": "사번 또는 기존 비밀번호가 일치하지 않습니다."})
            
    return render(request, "guide/password_change.html")

def logout_view(request):
    request.session.flush()
    return redirect("login")

def home_view(request):
    if not request.session.get("user_id"): return redirect("login")
    return render(request, "guide/home.html")

# 보험사 별 청구하기 뷰 추가
def insurance_claim_view(request):
    if not request.session.get("user_id"): return redirect("login")
    
    hanwha = Insurance.objects.filter(highlight=True).first()
    insurances = Insurance.objects.filter(highlight=False).order_by(
        Case(
            When(type="손해보험", then=0),
            When(type="생명보험", then=1),
            When(type="공제", then=2),
            default=3,
            output_field=IntegerField(),
        ),
        "company",
    )
    return render(request, "guide/insurance_claims.html", {
        "hanwha": hanwha,
        "insurances": insurances
    })

# --- 아인병원 산모관리 ---
def maternal_menu(request):
    if not request.session.get("user_id"): return redirect("login")
    return render(request, "guide/maternal_menu.html")

def maternal_register(request):
    if not request.session.get("user_id"): return redirect("login")
    if request.method == "POST":
        Maternal.objects.create(
            name=request.POST.get("name"),
            birthdate=request.POST.get("birthdate"),
            contact=request.POST.get("contact"),
            registered_by_id=request.session["user_id"]
        )
        return redirect("maternal_menu")
    return render(request, "guide/maternal_register.html")

def maternal_search(request):
    if not request.session.get("user_id"): return redirect("login")
    results = []
    if request.method == "POST":
        name = request.POST.get("name")
        val = request.POST.get("val")
        results = Maternal.objects.filter(
            Q(name=name, contact__endswith=val) | Q(name=name, birthdate=val)
        ).select_related('registered_by')
    return render(request, "guide/maternal_search.html", {"results": results})

# 나의 고객관리 (이번 달 기본 노출 및 월별 필터)
def customer_management(request):
    user_id = request.session.get("user_id")
    if not user_id: return redirect("login")
    
    now = timezone.now()
    # 선택된 월 가져오기 (기본값: 현재 년-월)
    selected_month = request.GET.get('month', now.strftime('%Y-%m'))
    
    # 본인이 등록한 산모 필터링
    maternals = Maternal.objects.filter(registered_by_id=user_id)
    
    # 월별 필터 적용
    try:
        year, month = map(int, selected_month.split('-'))
        maternals = maternals.filter(created_at__year=year, created_at__month=month)
    except:
        pass

    # 이름/생일/번호 검색 필터
    q = request.GET.get("q", "")
    if q:
        maternals = maternals.filter(
            Q(name__icontains=q) | Q(birthdate__icontains=q) | Q(contact__endswith=q)
        )

    # 최근 12개월 리스트 생성 (셀렉트 박스용)
    month_list = []
    for i in range(12):
        m = (now.month - i - 1) % 12 + 1
        y = now.year + (now.month - i - 1) // 12
        month_list.append(f"{y}-{m:02d}")

    return render(request, "guide/customer_management.html", {
        "maternals": maternals.order_by("-created_at"),
        "month_list": month_list,
        "selected_month": selected_month,
        "q": q
    })

def maternal_edit(request, pk):
    """산모 정보 수정: 본인이 등록한 데이터만 가능"""
    user_id = request.session.get("user_id")
    if not user_id: return redirect("login")
    
    # 수정 대상 불러오기 (본인 고객이 아니면 404 에러)
    maternal = get_object_or_404(Maternal, pk=pk, registered_by_id=user_id)
    
    if request.method == "POST":
        maternal.name = request.POST.get("name")
        maternal.birthdate = request.POST.get("birthdate")
        maternal.contact = request.POST.get("contact")
        maternal.save()
        log_activity(request, "EDIT", f"산모 정보 수정: {maternal.name}")
        return redirect("customer_management")
        
    return render(request, "guide/maternal_edit.html", {"maternal": maternal})

# --- 인수 가이드 검색 ---
def search_view(request):
    if not request.session.get("user_id"): return redirect("login")
    results = []
    query = ""
    guide_type = request.GET.get("guide", "chronic")
    if request.method == "POST":
        guide_type = request.POST.get("guide")
        query = request.POST.get("query", "").strip()
        if guide_type == "fetal":
            results = Fetal.objects.filter(disease__icontains=query)
        else:
            results = Disease.objects.filter(name__icontains=query)
    hanwha = Insurance.objects.filter(highlight=True).first()
    insurances = Insurance.objects.filter(highlight=False).order_by("company")
    return render(request, "guide/search.html", {
        "results": results, "query": query, "guide_type": guide_type, "hanwha": hanwha, "insurances": insurances
    })

# --- 상품별 인수한도 API ---
def get_products(request):
    products = Limit.objects.values_list("product", flat=True).distinct().order_by("product")
    return JsonResponse(list(products), safe=False)

def get_plans(request):
    product = request.GET.get("product")
    plans = Limit.objects.filter(product=product).values_list("plan", flat=True).distinct().order_by("plan")
    return JsonResponse(list(plans), safe=False)

def get_ages(request):
    product = request.GET.get("product")
    plan = request.GET.get("plan")
    ages = Limit.objects.filter(product=product, plan=plan).values("minAge", "maxAge").distinct().order_by("minAge")
    return JsonResponse(list(ages), safe=False)

def get_results(request):
    product = request.GET.get("product")
    plan = request.GET.get("plan")
    age = request.GET.get("age")
    qs = Limit.objects.filter(product=product, plan=plan)
    if age:
        qs = qs.filter(minAge__lte=int(age), maxAge__gte=int(age))
    results = qs.values("coverage", "amount", "note").order_by("coverage")
    return JsonResponse(list(results), safe=False)

def export_maternal_excel(request):
    # 1. 엑셀 파일 생성
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "산모관리_리스트"
    headers = ['성함', '생년월일', '연락처', '등록자', '등록일시']
    ws.append(headers)

    # 2. 현재 적용된 필터 조건 그대로 데이터 가져오기
    queryset = Maternal.objects.all().select_related('registered_by')
    
    # URL의 필터값(?created_at__month=1&...)을 쿼리에 적용
    filters = {}
    for key, value in request.GET.items():
        if value: # 값이 있는 경우만 필터 적용
            filters[key] = value
    
    try:
        queryset = queryset.filter(**filters)
    except:
        pass # 잘못된 필터 형식일 경우 전체 출력

    # 3. 데이터 쓰기
    for obj in queryset.order_by("-created_at"):
        ws.append([
            obj.name,
            obj.birthdate,
            obj.contact,
            obj.registered_by.name if obj.registered_by else '-',
            obj.created_at.strftime('%Y-%m-%d %H:%M')
        ])

    # 4. 파일 다운로드 응답
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="maternal_list.xlsx"'
    wb.save(response)
    return response
