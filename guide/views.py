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
    guide_type = request.POST.get("guide", "chronic")  # 기본값: 유병자 가이드

    if request.method == "POST":
        query = request.POST.get("query", "").strip()
        if query:
            if guide_type == "fetal":
                # 태아 인수가이드 JSON 로드
                json_path = os.path.join(settings.BASE_DIR, "templates", "fetal_ins.json")
                if os.path.exists(json_path):
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        results = [row for row in data if query in row["disease"]]
                log_activity(request, "SEARCH", f"[태아] 검색어: {query}, 결과 {len(results)}건")

            else:
                # 유병자 가이드 (DB Disease 검색)
                results = Disease.objects.filter(name__icontains=query)
                log_activity(request, "SEARCH", f"[유병자] 검색어: {query}, 결과 {len(results)}건")

    # 한화손해보험 (highlight=True)
    hanwha = Insurance.objects.filter(highlight=True).first()

    # 나머지 보험사들 (type 순서 강제)
    insurances = Insurance.objects.filter(highlight=False).order_by(
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
        "guide_type": guide_type,   # ✅ 어떤 가이드인지 템플릿에서 구분
        "user_name": request.session.get("user_name"),
        "hanwha": hanwha,
        "insurances": insurances,
    }
    return render(request, "guide/search.html", context)
