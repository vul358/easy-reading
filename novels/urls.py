from django.urls import path
from . import views
from django.views.generic.base import RedirectView

urlpatterns = [
    path("", views.index, name="index"),
    path("home/", views.home, name="home"),
    path("search_bookshelf/", views.search_bookshelf, name="search_bookshelf"),
    path("search_novel/", views.search_novel, name="search_novel"),
    path("search_author/", views.search_author, name="search_author"),
    path("search_category/", views.search_category, name="search_category"),
    path("mark/", views.mark, name="mark"),
    path("bookshelfs/", views.bookshelfs, name="bookshelfs"),
    path("my_bookshelf/<int:user_id>/", views.my_bookshelf, name="my_bookshelf"),
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("daily/", views.daily, name="daily"),
    path("daily_novel/", views.daily_novel, name="daily_novel"),
    path("ranking/", views.ranking, name="ranking"),
    path("ranking_novel/", views.ranking_novel, name="ranking_novel"),
    path("update_url/", views.update_url, name="update_url"),
    path('favicon.ico', RedirectView.as_view(url=r'static/favicon.ico')),
]
