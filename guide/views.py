from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from .models import Employee, Disease, Insurance
from .utils import log_activity


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
            return render(request, "guide/login.html", {"error": "코드 또는 비밀번호가 올바르지 않습니다."})

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

    if request.method == "POST":
        query = request.POST.get("query", "").strip()
        if query:
            results = Disease.objects.filter(name__icontains=query)
            log_activity(request, "SEARCH", f"검색어: {query}, 결과 {len(results)}건")

    # 한화손해보험 (highlight=True)
    hanwha = Insurance.objects.filter(highlight=True).first()

    # 나머지 보험사들 (type 순서 강제)
    insurances = Insurance.objects.filter(highlight=False).order_by(
        # type 순서를 "손해보험 → 생명보험 → 공제" 로 고정
        models.Case(
            models.When(type="손해보험", then=0),
            models.When(type="생명보험", then=1),
            models.When(type="공제", then=2),
            default=3,
            output_field=models.IntegerField(),
        ),
        "company"
    )

    context = {
        "results": results,
        "query": query,
        "user_name": request.session.get("user_name"),
        "hanwha": hanwha,         # 한화손보 따로
        "insurances": insurances, # 나머지
    }
    return render(request, "guide/search.html", context)
