from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),          # 로그인 페이지
    path("search/", views.search_view, name="search"), # 검색 페이지
    path("logout/", views.logout_view, name="logout"), # 로그아웃
]
