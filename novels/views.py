from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import redirect
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib import auth
from .forms import RegisterForm
from .models import ChosenNovels, Bookshelf
from .documents import NovelsDocument
from elasticsearch_dsl import Q
from collections import defaultdict
from datetime import date, timedelta
import json
import base64
import re


def home(request):
    if request.user.is_authenticated:
        return redirect(reverse("index"))
    return render(request, "home.html")


@login_required
def index(request):
    user_id = request.user.id  
    username = request.user.username  
    return render(request, "index.html", {"user_id": user_id, "username": username})


def exclude_novels(user_id):
    user_books = Bookshelf.objects.filter(user_id=user_id)
    exclude_titles = []
    for book in user_books:
        novel = book.novel_id
        chosen_novel = ChosenNovels.objects.get(id=novel) 
        chosen_title = chosen_novel.title 
        exclude_titles.append(chosen_title)
    return exclude_titles


def transfer_size(size):
    if size == "2h":
        range_query = Q("range", size={"lt": "240"})
    elif size == "5h":
        range_query = Q("range", size={"gte":"240", "lt": "600"})
    elif size == "10h":
        range_query = Q("range", size={"gte":"600", "lt": "1200"})
    elif size == "20h":
        range_query = Q("range", size={"gte":"1200", "lt": "2400"})
    elif size == "max":
        range_query = Q("range", size={"gte":"2400"})
    else:
        range_query = Q()
    return range_query


def novel_to_dict(novel_query_results, limit=None):
    if limit is not None:
        novel_query_results = novel_query_results[:limit]
    results = []
    for hit in novel_query_results:
        result = {
            "title": hit.title,
            "author": hit.author,
            "outline": hit.outline,
            "url": hit.url,
            "category": hit.category,
            "year": hit.year,
            "size": hit.size,
            "date": hit.date,
        }
        if hit.tags != "":
            result["tags"] = hit.tags
        results.append(result)
    return results


def results_to_json(results, message):
    if len(results) == 0:
        not_found = [{ "message": message}]
        results = JsonResponse(not_found, status = 200, safe=False, json_dumps_params={"ensure_ascii": False})
    else:
        results = JsonResponse(results, status = 200, safe=False, json_dumps_params={"ensure_ascii": False})
    return results


def search_novel(request):
    if request.method == "GET":
        term = request.GET["term"]
        user = request.GET.get("user_id","")
        year = request.GET.get("year", "")
        size = request.GET.get("size", "")
        exclude_titles = exclude_novels(user)
        term_query = Q("match", outline = term)
        year_query = Q() if not year else Q("match", year=year)
        title_query = [Q("match", title_kw = title) for title in exclude_titles]
        range_query = transfer_size(size)
        s = NovelsDocument.search().query("bool", must=[term_query, year_query], must_not = title_query)
        s = s.query(range_query)
        results = novel_to_dict(s, limit=3)
        message = "抱歉書庫中尚未有符合條件的作品，目前只接受繁體中文關鍵字，建議檢視您的輸入字詞，年份與閱讀時間設定，移除部分限制再嘗試一次。小提醒：已加入書櫃/黑名單的書籍不會出現在搜尋結果唷。"
        return results_to_json(results, message)


def search_author(request):
    if request.method == "GET":
        author = request.GET["author"]
        title = request.GET["title"]
        user = request.GET.get("user_id","")
        author_query = Q("match", author = author)
        exclude_titles = exclude_novels(user) if user else []
        if author:
            title_query = [Q("match", title_kw=title) for title in exclude_titles]
            s = NovelsDocument.search().query("bool",  must=[author_query], must_not=title_query)
            results = novel_to_dict(s)
            message = f"抱歉書庫中尚未有{author}其他作品。小提醒：作者名稱為繁體中文完全比對，請確認輸入完整字數嘗試。建議檢視您的輸入字詞，年份與閱讀時間設定，移除部分限制再嘗試一次。小提醒：已加入書櫃/黑名單的書籍不會出現在搜尋結果唷。" 
            return results_to_json(results, message)
        else:
            results = []
            message = "請輸入想尋找的作者：） 小提醒：作者名稱為繁體中文完全比對"
            return results_to_json(results, message)


def search_title(request):
    if request.method == "GET":
        title = request.GET["title"]
        user = request.GET.get("user_id","")
        if title:
            title_query = Q("match", title=title)
            exclude_titles = exclude_novels(user) if user else []
            title_exclude_query = [Q("match", title_kw=title) for title in exclude_titles]
            s = NovelsDocument.search().query("bool",  must=[title_query], must_not=title_exclude_query)
            results = novel_to_dict(s, limit=3)
            message = f"抱歉書庫中尚未有您在尋找的作品。小提醒：作品名稱為繁體中文比對，且建議輸入完整書名。小提醒：已加入書櫃/黑名單的書籍不會出現在搜尋結果唷。"  
            return results_to_json(results, message)
        else:
            results = []
            message = "請輸入想尋找的作品名稱：）"
            return results_to_json(results, message)


def search_category(request):
    if request.method == "GET":
        category = request.GET["category"]
        tag = request.GET["tag"]
        title = request.GET["title"]
        user = request.GET.get("user_id","")
        year = request.GET.get("year", "")
        size = request.GET.get("size", "")
        exclude_titles = exclude_novels(user) if user else []
        year_query = Q() if not year else Q("match", year=year)
        tag_query = Q() if not tag else Q("match", tags=tag)
        range_query = transfer_size(size)
        if len(exclude_titles) > 0:
            if title:
                exclude_titles.append(title)
            bool_query = Q("bool", must=[Q("match", category=category), year_query, tag_query], must_not=[Q("match", title_kw=title) for title in exclude_titles])
        else:
            bool_query = Q("bool", must=[Q("match", category=category), year_query, tag_query])
        s = NovelsDocument.search().query(bool_query)
        s = s.query(range_query)
        s = s.sort({"comment": {"order":"desc"}})
        results = novel_to_dict(s, limit=3)
        message = "抱歉書庫中尚未有符合條件的作品，建議檢視您的標籤，年份與閱讀時間設定，移除部分限制再嘗試一次。"
        return results_to_json(results, message)


@csrf_exempt
def mark(request):
    try:
        body = request.body
        novel = json.loads(body.decode("utf-8"))
        title = novel["title"]
        author = novel["author"]
        existing_book = ChosenNovels.objects.filter(title=title, author=author).first()
        if existing_book:
            novel_id = existing_book.id
        else:
            book = ChosenNovels()
            book.title = title
            book.author = author
            book.outline = novel["outline"]
            book.url = novel["url"]
            book.category = novel["category"]
            book.save()
            novel_id = book.id
        user = novel["user_id"]
        check = Bookshelf.objects.filter(user_id=user, novel_id=novel_id).first()
        bookshelf_status = novel["bookshelf"]
        folder = novel.get("folder")
        if not check:
            bookshelf_object = Bookshelf()
            bookshelf_object.bookshelf = bookshelf_status
            bookshelf_object.folder = folder
            bookshelf_object.novel_id = novel_id
            bookshelf_object.user_id = user
            bookshelf_object.save()
        else:
            if bookshelf_status == "deleted":
                check.delete()
            else:
                if check.bookshelf != bookshelf_status or check.folder != folder:
                    check.bookshelf = bookshelf_status
                    check.folder = folder
                    check.save()
        if bookshelf_status == "done":      
            title_query = Q("match", title=title)
            author_query = Q("match", author = author)
            s = NovelsDocument.search().query("bool",  must=[author_query, title_query])
            if folder =="good":
                for hit in s:
                    hit.comment += 10
                    hit.save()
            elif folder == "normal":
                for hit in s:
                    hit.comment += 5
                    hit.save()
        return JsonResponse({"status": "success"})
    except json.JSONDecodeError as e:
        return JsonResponse({"status": "failed", "msg": str(e)}, status=400)


def bookshelfs(request):
    if request.method == "GET":
        bookshelf = request.GET["bookshelf"]
        user = request.GET["user_id"]  
        books = Bookshelf.objects.filter(user_id=user, bookshelf=bookshelf)
        folders = defaultdict(list)
        for book in books:
            folder_name = book.folder or "no_folder"
            novel = ChosenNovels.objects.filter(id=book.novel_id).first()
            result = {
                "id": novel.id,
                "title": novel.title,
                "author": novel.author,
                "outline": novel.outline,
                "category": novel.category,
                "url": novel.url,
                "url_page": book.url_page,
            }
            folders[folder_name].append(result)
        return JsonResponse(folders, status=200, json_dumps_params={"ensure_ascii": False})


@login_required
def my_bookshelf(request):
    user_id = request.user.id 
    username = request.user.username
    return render(request, "bookshelf_c.html", {"user_id": user_id, "user_name": username})


def daily(request):
    user_id = request.user.id 
    today = date.today()
    return render(request, "daily.html", {"user_id": user_id, "today": today})


def ranking(request):
    user_id = request.user.id 
    return render(request, "ranking.html", {"user_id": user_id})


def search_bookshelf(request):
    if request.method == "GET":
        user = request.GET["user_id"]
        title = request.GET["title"]
        titles = exclude_novels(user)
        if title in titles:
            book_id = ChosenNovels.objects.filter(title=title).first().id
            result = {"book_id": book_id}
            result = JsonResponse(result, status = 200, safe=False, json_dumps_params={"ensure_ascii": False})
            return result
        else:
            not_found = {"message": "書櫃中沒有這本書喔！"}
            result = JsonResponse(not_found, status = 200, safe=False, json_dumps_params={"ensure_ascii": False})
            return result


def daily_novel(request):
    if request.method == "GET":
        today = date.today()
        yesterday = today - timedelta(days=1)
        date_query = Q("match", date = yesterday)
        s = NovelsDocument.search().query("bool", must=[date_query])
        results = novel_to_dict(s)
        if len(results) == 0:
            s = NovelsDocument.search().sort({"date": {"order":"desc"}})
            results = novel_to_dict(s, limit=10)
        results = JsonResponse(results, status = 200, safe=False, json_dumps_params={"ensure_ascii": False})
        return results


def ranking_novel(request):
    if request.method == "GET":
        category = request.GET.get("category","")
        category_query = Q() if not category else Q("match", category=category)
        s = NovelsDocument.search().query("bool", must=[category_query])
        s = s.sort({"comment": {"order":"desc"}})
        results = novel_to_dict(s, limit=10)
        results = JsonResponse(results, status = 200, safe=False, json_dumps_params={"ensure_ascii": False})
        return results


def update_url(request):
    if request.method == "GET":
        user = request.GET["user_id"]
        bookID = request.GET["book_id"]
        page = request.GET["page"]
        if page:
            book = Bookshelf.objects.get(user_id=user, novel_id=bookID)
            book.url_page = page
            book.save()
            novel_url = ChosenNovels.objects.get(id=bookID).url
            pattern = r"https://www.sto.cx/(book-\d+-)"
            pattern1 = r"https://www.sto.cx/(serial/sbook.aspx\?bid=\d+&page=)"
            match = re.match(pattern, novel_url)
            match1 = re.match(pattern1, novel_url)
            if match:
                url = "https://www.sto.cx/"+match.group(1) + page + ".html"
            elif match1:
                url = "https://www.sto.cx/"+match1.group(1) + page
            else:
                url = novel_url
            result = {"url": url}
            return JsonResponse(result, status = 200, safe=False, json_dumps_params={"ensure_ascii": False})


def health_check(request):
    return HttpResponse(status=200)


def bookshelf_share(request, encoded_data):
    decoded_data = base64.urlsafe_b64decode(encoded_data.encode("utf-8")).decode("utf-8")
    user_id, user_name = decoded_data.split(":")
    return render(request, "bookshelf_s.html", {"user_id": user_id, "user_name": user_name})


def bookshelf_url(request):
    if request.method == "GET":
        user_id = request.GET["user_id"]
        user_name = request.GET["user_name"]
        encoded_data = f"{user_id}:{user_name}".encode("utf-8")
        encoded_data = base64.urlsafe_b64encode(encoded_data).decode("utf-8")
        result = {"bookshelf_url": f"https://novel.likedream.life/novels/bookshelf_share/{encoded_data}"}
        return JsonResponse(result, status = 200, safe=False)