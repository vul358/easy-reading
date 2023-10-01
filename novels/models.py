from django.db import models
from django.contrib.auth.models import User


class ChosenNovels(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    outline = models.TextField()
    url = models.TextField() 
    category = models.CharField(max_length=200)


class Bookshelf(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    novel = models.ForeignKey(ChosenNovels, on_delete=models.CASCADE)
    bookshelf = models.CharField(max_length=200)
    folder = models.CharField(max_length=200)


# class TestNovel(models.Model):
#     title = models.CharField(max_length=200)
#     author = models.CharField(max_length=200)
#     outline = models.TextField()


# class NovelsInfo(models.Model):
#     title = models.CharField(max_length=200)
#     author = models.CharField(max_length=200)
#     outline = models.TextField()    
#     category = models.CharField(max_length=200)
#     tags = models.CharField(max_length=200)
#     year = models.IntegerField()
#     url = models.TextField()  
#     website = models.CharField(max_length=200)
#     comment = models.IntegerField()
#     size = models.IntegerField()
#     date = models.DateField() 
                
     
