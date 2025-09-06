from django.urls import path
from . import views

app_name = "guide"

urlpatterns = [
    path("", views.login_view, name="login"),
    path("search/", views.search_view, name="search"),
    path("logout/", views.logout_view, name="logout"),
]
