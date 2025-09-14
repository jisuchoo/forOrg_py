import os
from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from django.http import JsonResponse
from .models import Employee, Disease, Insurance, Fetal, Limit
from .utils import log_activity


# ----------------------
# 로그인 / 로그아웃
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
            return redirect("search")
        except Employee.DoesNotExist:
            log_activity(request, "LOGIN_FAIL", "로그인 실패")
            return render(
                request,
                "guide/login.html",
                {"error": "코드 또는 비밀번호가 올바르지 않습니다."},
            )

    return render(request, "guide/login.html")


def logout_view(request):
    auth_logout(request)
    request.session.flush()
    return redirect("login")


# ----------------------
# 메인 검색 화면 (질병/태아 가이드)
# ----------------------
def search_view(request):
    if not request.session.get("user_id"):
        return redirect("login")

    results = []
    query = ""
    guide_type = None

    if request.method == "POST":
        guide_type = request.POST.get("guide")
        query = request.POST.get("query", "").strip()

        if guide_type and query:
            if guide_type == "fetal":
                results = Fetal.objects.filter(disease__icontains=query)
                log_activity(request, "SEARCH", f"[태아] {query} → {len(results)}건")
            elif guide_type == "chronic":
                results = Disease.objects.filter(name__icontains=query)
                log_activity(request, "SEARCH", f"[유병자] {query} → {len(results)}건")

    # 보험사 정보
    hanwha = Insurance.objects.filter(highlight=True).first()
    insurances = Insurance.objects.filter(highlight=False).order_by(
        models.Case(
            models.When(type="손해보험", then=0),
            models.When(type="생명보험", then=1),
            models.When(type="공제", then=2),
            default=3,
            output_field=models.IntegerField(),
        ),
        "company",
    )

    context = {
        "results": results,
        "query": query,
        "guide_type": guide_type,
        "user_name": request.session.get("user_name"),
        "hanwha": hanwha,
        "insurances": insurances,
    }
    return render(request, "guide/search.html", context)


# ----------------------
# 인수한도 API (상품별/플랜별/연령별)
# ----------------------
def get_products(request):
    """상품 목록"""
    products = (
        Limit.objects.values_list("product", flat=True)
        .distinct()
        .order_by("product")
    )
    return JsonResponse(list(products), safe=False)


def get_plans(request):
    """특정 상품의 플랜 목록"""
    product = request.GET.get("product")
    plans = (
        Limit.objects.filter(product=product)
        .values_list("plan", flat=True)
        .distinct()
        .order_by("plan")
    )
    return JsonResponse(list(plans), safe=False)


def get_ages(request):
    """특정 상품+플랜의 연령 구간"""
    product = request.GET.get("product")
    plan = request.GET.get("plan")

    ages = (
        Limit.objects.filter(product=product, plan=plan)
        .values("minAge", "maxAge")
        .distinct()
        .order_by("minAge", "maxAge")
    )
    return JsonResponse(list(ages), safe=False)


def get_results(request):
    """상품+플랜+연령으로 인수한도 결과"""
    product = request.GET.get("product")
    plan = request.GET.get("plan")
    age = request.GET.get("age")

    qs = Limit.objects.filter(product=product, plan=plan)
    if age:
        age = int(age)
        qs = qs.filter(minAge__lte=age, maxAge__gte=age)

    results = qs.values("coverage", "amount", "note").order_by("coverage")
    return JsonResponse(list(results), safe=False)
