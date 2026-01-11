from django.urls import path
from . import views

urlpatterns = [
    # 로그인 및 홈
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("home/", views.home_view, name="home"),

    # 아인병원 산모관리 관련
    path("maternal/", views.maternal_menu, name="maternal_menu"),
    path("maternal/register/", views.maternal_register, name="maternal_register"),
    path("maternal/search/", views.maternal_search, name="maternal_search"),
    path("maternal/manage/", views.customer_management, name="customer_management"),

    # 기존 인수 가이드 및 API
    path("search/", views.search_view, name="search"),
    path("limits/products/", views.get_products, name="get_products"),
    path("limits/plans/", views.get_plans, name="get_plans"),
    path("limits/ages/", views.get_ages, name="get_ages"),
    path("limits/results/", views.get_results, name="get_results"),
]
