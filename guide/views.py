import os
import json
from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from django.conf import settings
from .models import Employee, Disease, Insurance, Fetal, Limit
from .utils import log_activity

def get_products(request):
    products = Limit.objects.values_list("product", flat=True).distinct()
    return JsonResponse(list(products), safe=False)

def get_plans(request):
    product = request.GET.get("product")
    plans = Limit.objects.filter(product=product).values_list("plan", flat=True).distinct()
    return JsonResponse(list(plans), safe=False)

def get_ages(request):
    product = request.GET.get("product")
    plan = request.GET.get("plan")
    ages = Limit.objects.filter(product=product, plan=plan).values("minAge", "maxAge")
    return JsonResponse(list(ages), safe=False)

def get_results(request):
    product = request.GET.get("product")
    plan = request.GET.get("plan")
    age = int(request.GET.get("age", 0))

    qs = Limit.objects.filter(product=product, plan=plan, minAge__lte=age, maxAge__gte=age)
    data = [
        {
            "coverage": l.coverage,
            "amount": l.amount,
            "note": l.note or ""
        } for l in qs
    ]
    return JsonResponse(data, safe=False)

# 로그인 뷰
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


# 로그아웃 뷰
def logout_view(request):
    auth_logout(request)  # Django 기본 세션 로그아웃
    request.session.flush()
    return redirect("login")


# 검색 뷰
def search_view(request):
    if not request.session.get("user_id"):
        return redirect("login")

    results = []
    query = ""
    guide_type = None  # 처음엔 선택되지 않음

    if request.method == "POST":
        guide_type = request.POST.get("guide")
        query = request.POST.get("query", "").strip()

        if guide_type and query:
            if guide_type == "fetal":
                # 태아 인수가이드 검색
                results = Fetal.objects.filter(disease__icontains=query)
                log_activity(
                    request,
                    "SEARCH",
                    f"[태아] 검색어: {query}, 결과 {len(results)}건",
                )
            elif guide_type == "disease":
                # 유병자 가이드 검색
                results = Disease.objects.filter(name__icontains=query)
                log_activity(
                    request,
                    "SEARCH",
                    f"[유병자] 검색어: {query}, 결과 {len(results)}건",
                )
            elif guide_type == "limit":
                # 인수한도 검색
                limit_results = Limit.objects.filter(
                    models.Q(product__icontains=query) |
                    models.Q(plan__icontains=query) |
                    models.Q(coverage__icontains=query)
                ).order_by("product", "plan", "minAge")
                if limit_results.exists():
                    max_amount = limit_results.aggregate(models.Max("amount"))["amount__max"]
                log_activity(
                    request,
                    "SEARCH",
                    f"[인수한도] 검색어: {query}, 결과 {len(limit_results)}건",
                )

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
        "guide_type": guide_type,  # 처음에는 None → 버튼만 보임
        "user_name": request.session.get("user_name"),
        "hanwha": hanwha,
        "insurances": insurances,
    }
    return render(request, "guide/search.html", context)
