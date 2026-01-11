import os
from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from django.db.models import Q
from django.http import JsonResponse
from .models import Employee, Disease, Insurance, Fetal, Limit, Maternal
from .utils import log_activity

# ----------------------
# 1. 로그인 / 로그아웃 및 홈 화면
# ----------------------
@csrf_exempt
def login_view(request):
    if request.method == "POST":
        empno = request.POST.get("empno")
        password = request.POST.get("password")
        try:
            user = Employee.objects.get(empno=empno, password=password)
            request.session["user_id"] = user.id
            request.session["user_name"] = user.name or user.empno
            log_activity(request, "LOGIN", "로그인 성공")
            return redirect("home") # 로그인 후 홈 화면으로 이동
        except Employee.DoesNotExist:
            log_activity(request, "LOGIN_FAIL", "로그인 실패")
            return render(request, "guide/login.html", {"error": "사번 또는 비밀번호가 올바르지 않습니다."})
    return render(request, "guide/login.html")

def logout_view(request):
    auth_logout(request)
    request.session.flush()
    return redirect("login")

def home_view(request):
    """첫 화면: 기존 3개 메뉴 + 아인병원 산모관리 메뉴 구성"""
    if not request.session.get("user_id"):
        return redirect("login")
    return render(request, "guide/home.html")

# ----------------------
# 2. 아인병원 산모관리 (서브 메뉴 및 기능)
# ----------------------
def maternal_menu(request):
    """산모관리 클릭 시: 산모 등록, 검색, 고객관리 메뉴 구성"""
    if not request.session.get("user_id"):
        return redirect("login")
    return render(request, "guide/maternal_menu.html")

def maternal_register(request):
    """산모 등록: 이름, 생년월일, 연락처 저장"""
    if not request.session.get("user_id"):
        return redirect("login")
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
    """산모 검색: 이름+연락처(뒤4자리) 또는 이름+생년월일"""
    if not request.session.get("user_id"):
        return redirect("login")
    results = []
    if request.method == "POST":
        name = request.POST.get("name")
        val = request.POST.get("val") # 뒤 4자리 혹은 생년월일
        results = Maternal.objects.filter(
            Q(name=name, contact__endswith=val) | Q(name=name, birthdate=val)
        ).select_related('registered_by')
    return render(request, "guide/maternal_search.html", {"results": results})

def customer_management(request):
    """고객 관리: 로그인한 직원이 등록한 리스트만 한정 검색"""
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")
    
    # 본인이 등록한 산모 리스트만 가져옴
    maternals = Maternal.objects.filter(registered_by_id=user_id)
    
    # 이름/생년월일/연락처 뒤 4자리 중 한 가지 조건으로 검색
    q = request.GET.get("q", "")
    if q:
        maternals = maternals.filter(
            Q(name__icontains=q) | Q(birthdate__icontains=q) | Q(contact__endswith=q)
        )
    return render(request, "guide/customer_management.html", {
        "maternals": maternals.order_by("-created_at")
    })

# ----------------------
# 3. 기존 메인 검색 화면 (질병/태아 가이드 유지)
# ----------------------
def search_view(request):
    if not request.session.get("user_id"):
        return redirect("login")
    results = []
    query = ""
    guide_type = request.GET.get("guide") # URL 파라미터로 구분

    if request.method == "POST":
        guide_type = request.POST.get("guide")
        query = request.POST.get("query", "").strip()
        if guide_type and query:
            if guide_type == "fetal":
                results = Fetal.objects.filter(disease__icontains=query)
            elif guide_type == "chronic":
                results = Disease.objects.filter(name__icontains=query)

    hanwha = Insurance.objects.filter(highlight=True).first()
    insurances = Insurance.objects.filter(highlight=False).order_by("company")
    context = {
        "results": results, "query": query, "guide_type": guide_type,
        "user_name": request.session.get("user_name"),
        "hanwha": hanwha, "insurances": insurances,
    }
    return render(request, "guide/search.html", context)

# ----------------------
# 4. 인수한도 API (기존 유지)
# ----------------------
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
