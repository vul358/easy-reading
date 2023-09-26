from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("test_api/", views.test_api, name="test_api"),
    path("clear_table/", views.clear_table, name="clear_table"),
    path("search_novel/", views.search_novel, name="search_novel"),
    path("search_author/", views.search_author, name="search_author"),
    path("search_category/", views.search_category, name="search_category"),
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
]
