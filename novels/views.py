from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse #剛剛的JsonResponse套件
from .models import Test
from .documents import NovelsDocument
from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


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