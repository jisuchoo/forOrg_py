from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("home/", views.home_view, name="home"),
    path("search/", views.search_view, name="search"),
    
    # 아인병원 산모관리
    path("maternal/", views.maternal_menu, name="maternal_menu"),
    path("maternal/register/", views.maternal_register, name="maternal_register"),
    path("maternal/search/", views.maternal_search, name="maternal_search"),
    path("maternal/manage/", views.customer_management, name="customer_management"),
    
    # 상품별 인수한도 API
    path("limits/products/", views.get_products, name="get_products"),
    path("limits/plans/", views.get_plans, name="get_plans"),
    path("limits/ages/", views.get_ages, name="get_ages"),
    path("limits/results/", views.get_results, name="get_results"),
]
