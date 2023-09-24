from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.http import JsonResponse #剛剛的JsonResponse套件
from .models import ChosenNovels
from .documents import NovelsDocument
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from .forms import RegisterForm
from django.contrib import auth


def index(request):
    return render(request, 'index.html')


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
            return redirect('/login/')
        elif user and user.is_staff is True:
            auth.login(request, user)
            return redirect('/quiz/')
        else:
            return redirect('/login/')
    else:
        return render(request, 'login.html', locals())


def logout(request):
    logout(request)
    return redirect('/login') #重新導向到登入畫面


def search_novel(request):
    if request.method == 'GET':
        term = request.GET['term']
        s = NovelsDocument.search().query("match", outline = term)
        results =[]
        for hit in s[0:3]:
            result = {
                "title": hit.title,
                "author": hit.author,
                "outline": hit.outline,
                "url": hit.url
            }
            results.append(result)    
        results = JsonResponse(results, status = 200, safe=False, json_dumps_params={'ensure_ascii': False})
        return results
    

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