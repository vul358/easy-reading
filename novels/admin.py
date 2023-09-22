from django.contrib import admin

# Register your models here.
from .models import TestNovel, NovelsInfo, ChosenNovels


admin.site.register(TestNovel)
admin.site.register(NovelsInfo)
admin.register(ChosenNovels)