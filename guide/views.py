from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import JsonResponse
from .models import Employee, Disease, Insurance, Fetal, Limit, Maternal
from .utils import log_activity

def login_view(request):
    if request.method == "POST":
        empno = request.POST.get("empno")
        password = request.POST.get("password")
        try:
            user = Employee.objects.get(empno=empno, password=password)
            request.session["user_id"] = user.id
            request.session["user_name"] = user.name
            log_activity(request, "LOGIN", "성공")
            return redirect("home")
        except Employee.DoesNotExist:
            return render(request, "guide/login.html", {"error": "사번 또는 비밀번호 오류"})
    return render(request, "guide/login.html")

def logout_view(request):
    request.session.flush()
    return redirect("login")

def home_view(request):
    if not request.session.get("user_id"): return redirect("login")
    return render(request, "guide/home.html")

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

def customer_management(request):
    user_id = request.session.get("user_id")
    if not user_id: return redirect("login")
    maternals = Maternal.objects.filter(registered_by_id=user_id)
    q = request.GET.get("q", "")
    if q:
        maternals = maternals.filter(
            Q(name__icontains=q) | Q(birthdate__icontains=q) | Q(contact__endswith=q)
        )
    return render(request, "guide/customer_management.html", {"maternals": maternals.order_by("-created_at")})

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
