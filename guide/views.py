from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from .forms import LoginForm, SearchForm
from .models import Employee, Disease

# 관리자 계정 상수
ADMIN = {"empno": "8091768", "password": "dcw8091"}

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            empno = form.cleaned_data["empno"]
            password = form.cleaned_data["password"]

            # 관리자 계정 확인
            if empno == ADMIN["empno"] and password == ADMIN["password"]:
                request.session["user"] = empno
                request.session["is_admin"] = True
                return redirect("guide:search")

            # DB 직원 확인
            try:
                emp = Employee.objects.get(empno=empno, password=password)
                request.session["user"] = emp.empno
                request.session["is_admin"] = False
                return redirect("guide:search")
            except Employee.DoesNotExist:
                messages.error(request, "코드 또는 비밀번호 오류")
    else:
        form = LoginForm()

    return render(request, "guide/login.html", {"form": form})

def logout_view(request):
    auth_logout(request)  # Django 기본 세션 클리어
    request.session.flush()
    return redirect("guide:login")

def search_view(request):
    if "user" not in request.session:
        return redirect("guide:login")

    form = SearchForm(request.POST or None)
    results = []
    msg = ""

    if request.method == "POST" and form.is_valid():
        q = form.cleaned_data["query"].strip().lower()
        if q:
            results = Disease.objects.filter(name__icontains=q)
            if not results:
                msg = "검색 결과가 없습니다."

    return render(request, "guide/search.html", {
        "user": request.session.get("user"),
        "is_admin": request.session.get("is_admin", False),
        "form": form,
        "results": results,
        "msg": msg,
        "count": Disease.objects.count()
    })
