from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import JsonResponse
from .models import Employee, Disease, Insurance, Fetal, Limit, Maternal
from .utils import log_activity

# --- 로그인 / 로그아웃 및 홈 ---
def login_view(request):
    if request.method == "POST":
        empno, password = request.POST.get("empno"), request.POST.get("password")
        try:
            user = Employee.objects.get(empno=empno, password=password)
            request.session["user_id"], request.session["user_name"] = user.id, user.name or user.empno
            return redirect("home")
        except Employee.DoesNotExist:
            return render(request, "guide/login.html", {"error": "사번 또는 비밀번호가 올바르지 않습니다."})
    return render(request, "guide/login.html")

def logout_view(request):
    request.session.flush()
    return redirect("login")

def home_view(request):
    if not request.session.get("user_id"): return redirect("login")
    return render(request, "guide/home.html")

# 보험사 별 청구하기 뷰 추가
def insurance_claim_view(request):
    if not request.session.get("user_id"): return redirect("login")
    
    hanwha = Insurance.objects.filter(highlight=True).first()
    insurances = Insurance.objects.filter(highlight=False).order_by(
        Case(
            When(type="손해보험", then=0),
            When(type="생명보험", then=1),
            When(type="공제", then=2),
            default=3,
            output_field=IntegerField(),
        ),
        "company",
    )
    return render(request, "guide/insurance_claims.html", {
        "hanwha": hanwha,
        "insurances": insurances
    })

# --- 아인병원 산모관리 ---
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

# 고객 관리 (월별 필터 포함)
def customer_management(request):
    user_id = request.session.get("user_id")
    if not user_id: return redirect("login")
    
    now = timezone.now()
    selected_month = request.GET.get('month', now.strftime('%Y-%m'))
    year, month = map(int, selected_month.split('-'))
    
    maternals = Maternal.objects.filter(
        registered_by_id=user_id,
        created_at__year=year,
        created_at__month=month
    )
    
    q = request.GET.get("q", "")
    if q:
        maternals = maternals.filter(Q(name__icontains=q) | Q(birthdate__icontains=q) | Q(contact__endswith=q))
        
    month_list = [f"{(now.year + (now.month - i - 1) // 12)}-{(now.month - i - 1) % 12 + 1:02d}" for i in range(12)]
    
    return render(request, "guide/customer_management.html", {
        "maternals": maternals.order_by("-created_at"),
        "month_list": month_list,
        "selected_month": selected_month,
        "q": q
    })

def maternal_edit(request, pk):
    """산모 정보 수정: 본인이 등록한 데이터만 가능"""
    user_id = request.session.get("user_id")
    if not user_id: return redirect("login")
    
    # 수정 대상 불러오기 (본인 고객이 아니면 404 에러)
    maternal = get_object_or_404(Maternal, pk=pk, registered_by_id=user_id)
    
    if request.method == "POST":
        maternal.name = request.POST.get("name")
        maternal.birthdate = request.POST.get("birthdate")
        maternal.contact = request.POST.get("contact")
        maternal.save()
        log_activity(request, "EDIT", f"산모 정보 수정: {maternal.name}")
        return redirect("customer_management")
        
    return render(request, "guide/maternal_edit.html", {"maternal": maternal})

# --- 인수 가이드 검색 ---
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

# --- 상품별 인수한도 API ---
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
