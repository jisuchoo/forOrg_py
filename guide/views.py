from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from .models import Employee, Disease, Insurance


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
            return redirect("search")
        except Employee.DoesNotExist:
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

    # 보험사 목록 추가
    insurances = Insurance.objects.all().order_by("type", "company")

    context = {
        "results": results,
        "query": query,
        "user_name": request.session.get("user_name"),
        "insurances": insurances,   # ✅ 보험사 정보 추가
    }
    return render(request, "guide/search.html", context)
