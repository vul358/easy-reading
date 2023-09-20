from django.db import models


class Test(models.Model):
    question_text = models.CharField(max_length=200)
    question_num = models.IntegerField()


class TestNovel(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    outline = models.TextField()


class NovelsInfo(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    outline = models.TextField()    
    category = models.CharField(max_length=200)
    tags = models.CharField(max_length=200)
    words = models.IntegerField()
    year = models.IntegerField()
    collectedCount = models.IntegerField()
    url = models.TextField()  
    website = models.CharField(max_length=200)
                
     
