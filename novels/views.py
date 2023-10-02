from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.http import JsonResponse 
from .models import ChosenNovels, Bookshelf
from .documents import NovelsDocument
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from .forms import RegisterForm
from django.contrib import auth
from elasticsearch_dsl import Q
import json
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'home.html')

@login_required
def index(request):
    user_id = request.user.id  # 获取当前登录用户的ID
    username = request.user.username  # 获取当前登录用户的用户名
    return render(request, 'index.html', {'user_id': user_id, 'username': username})


def register(request):
    if request.method == 'POST': #當使用者提交資料
        form = RegisterForm(request.POST) #內建的form，model為User。
        if form.is_valid():
            form.save()
            return redirect('/novels')
        else:
            return render(request, 'register.html', {'form':form})
    else:
        form = RegisterForm()
        context = {'form':form}
        return render(request, 'register.html', context)


def login(request):
    if request.method == 'POST':
        password = request.POST['password']
        email = request.POST['email']
        user = auth.authenticate(password=password, email=email)
        if user and user.is_staff is False:
            auth.login(request, user)
            return redirect('/novels/')
        elif user and user.is_staff is True:
            auth.login(request, user)
            return redirect('/novels/')
        else:
            return redirect('/novels/login/')
    else:
        return render(request, 'login.html', locals())


def logout(request):
    return redirect('/novels/home') #重新導向到登入畫面


def search_novel(request):
    if request.method == 'GET':
        term = request.GET['term']
        s = NovelsDocument.search().query("match", outline = term)
        results =[]
        for hit in s[:3]:
            if hit.tags == "":
                result = {
                    "title": hit.title,
                    "author": hit.author,
                    "outline": hit.outline,
                    "url": hit.url,
                    "category": hit.category
                }
            else:
                result = {
                    "title": hit.title,
                    "author": hit.author,
                    "tags": hit.tags,
                    "outline": hit.outline,
                    "url": hit.url,
                    "category": hit.category
                }
            results.append(result) 
        results = JsonResponse(results, status = 200, safe=False, json_dumps_params={'ensure_ascii': False})
        return results


def search_author(request):
    if request.method == 'GET':
        author = request.GET['author']
        title = request.GET['title']
        author_query = Q('match', author = author)
        title_query = Q('match', title= title )
        s = NovelsDocument.search().query('bool',  must=[author_query], must_not=[title_query])
        results = []
        for hit in s:
            if hit.tags == "":
                result = {
                    "title": hit.title,
                    "author": hit.author,
                    "outline": hit.outline,
                    "url": hit.url,
                    "category": hit.category
                }
            else:
                result = {
                    "title": hit.title,
                    "author": hit.author,
                    "tags": hit.tags,
                    "outline": hit.outline,
                    "url": hit.url,
                    "category": hit.category
                }
            results.append(result)
        if len(results) == 0:
                not_found = [{ 
                    "title": f"抱歉書庫中尚未有{author}的其他作品",
                    "author": "小提醒：作者名稱為繁體中文完全比對，請確認輸入完整字數嘗試" }]
                results = JsonResponse(not_found, status = 200, safe=False, json_dumps_params={'ensure_ascii': False})
                return results
        else:
            results = JsonResponse(results, status = 200, safe=False, json_dumps_params={'ensure_ascii': False})
            return results


def search_category(request):
    if request.method == 'GET':
        category = request.GET['category']
        tag = request.GET['tag']
        title = request.GET['title']
        # s = NovelsDocument.search().query("bool", must=[
        #     {"match":{"category":category}},
        #     {"match":{"tags":tag}}
        #     ])
        if title:
            bool_query = Q('bool', must=[Q('match', category=category)], must_not=[Q('match', title=title)])
        else:
            bool_query = Q('bool', must=[Q('match', category=category)])
        if tag:
            bool_query.should.append(Q('match', tags=tag))
        s = NovelsDocument.search().query(bool_query)
        s = s.sort({"comment": {"order":"desc"}})
        results =[]
        for hit in s[0:3]:
            if hit.tags == "":
                result = {
                    "title": hit.title,
                    "author": hit.author,
                    "outline": hit.outline,
                    "url": hit.url,
                    "category": hit.category
                    }
            else:
                result = {
                    "title": hit.title,
                    "author": hit.author,
                    "tags": hit.tags,
                    "outline": hit.outline,
                    "url": hit.url,
                    "category": hit.category
                    }
            results.append(result)  
        results = JsonResponse(results, status = 200, safe=False, json_dumps_params={'ensure_ascii': False})
        return results


@csrf_exempt
def mark(request):
    try:
        body = request.body
        # 轉換成JSON
        novel = json.loads(body.decode('utf-8'))
        title = novel['title']
        author = novel['author']
        existing_book = ChosenNovels.objects.filter(title=title, author=author).first()
        if existing_book:
            novel_id = existing_book.id
        else:
            book = ChosenNovels()
            book.title = title
            book.author = author
            book.outline = novel['outline']
            book.url = novel['url']
            book.category = novel['category']
            book.save()
            novel_id = book.id
        user = novel['user_id']
        check = Bookshelf.objects.filter(user_id=user, novel_id=novel_id).first()
        bookshelf_status = novel['bookshelf']
        folder = novel.get('folder')
        if not check:
            bookshelf_object = Bookshelf()
            bookshelf_object.bookshelf = bookshelf_status
            bookshelf_object.folder = folder
            bookshelf_object.novel_id = novel_id
            bookshelf_object.user_id = user
            bookshelf_object.save()
        else:
            if check.bookshelf != bookshelf_status or check.folder != folder:
                check.bookshelf = bookshelf_status
                check.folder = folder
                check.save()
        return JsonResponse({"status": "success"})
    except json.JSONDecodeError as e:
        return JsonResponse({"status": "failed", "msg": str(e)}, status=400)
        # return HttpResponse(f"Error decoding JSON: {str(e)}", status=400)


def bookshelfs(request):
    if request.method == 'GET':
        bookshelf = request.GET['bookshelf']
        user = request.GET['user_id']  
        books = Bookshelf.objects.filter(user_id=user, bookshelf=bookshelf)
        folders = defaultdict(list)
        for book in books:
            folder_name = book.folder or 'no_folder'
            novel = ChosenNovels.objects.filter(id=book.novel_id).first()
            result = {
                "id": novel.id,
                "title": novel.title,
                "author": novel.author,
                "outline": novel.outline,
                "category": novel.category,
                "url": novel.url
            }
            folders[folder_name].append(result)

        return JsonResponse(folders, status=200, json_dumps_params={'ensure_ascii': False})


def my_bookshelf(request, user_id):
    return render(request, 'bookshelf_c.html', {'user_id': user_id})


def test_api(request):
    new_obj = Test()
    new_obj.question_num = 5
    new_obj.save()
    return JsonResponse(data={'msg': 'add object success.'}, status=200)


def clear_table(request):
    #將table所有data撈出來
    all_obj = Test.objects.all()
    #砍掉
    all_obj.delete()
    #回傳200，這裡使用JsonResponse，data記得回傳格式為dict
    return JsonResponse(data={'msg':'clear table success.'}, status=200)