from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Disease
from .models import Employee


# ✅ 로그인 화면
def login_view(request):
    if request.method == "POST":
        empno = request.POST.get("empno")
        password = request.POST.get("password")

        try:
            user = Employee.objects.get(empno=empno, password=password)
            request.session["user_id"] = user.id
            request.session["empno"] = user.empno
            return redirect("search")
        except Employee.DoesNotExist:
            messages.error(request, "코드 또는 비밀번호가 잘못되었습니다.")

    return render(request, "guide/login.html")


# ✅ 로그아웃
def logout_view(request):
    logout(request)
    return redirect("login")


# ✅ 검색 화면 (로그인 필요)
@login_required
def search_view(request):
    query = request.POST.get("query")
    results = []
    if query:
        results = Disease.objects.filter(name__icontains=query)
    return render(request, "guide/search.html", {"results": results})
