from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Disease


# ✅ 로그인 화면
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("search")
    else:
        form = AuthenticationForm()
    return render(request, "guide/login.html", {"form": form})


# ✅ 로그아웃
def logout_view(request):
    logout(request)
    return redirect("login")


# ✅ 검색 화면 (로그인 필요)
@login_required
def search_view(request):
    query = request.GET.get("q", "").strip()
    results = []

    if query:
        # 부분 일치 + 대소문자 무시 검색
        results = Disease.objects.filter(name__icontains=query)

    return render(request, "guide/search.html", {
        "query": query,
        "results": results
    })
