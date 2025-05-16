from django.contrib import admin
from .models import ArticleModel

# Register your models here.

class ArticleAdmin(admin.ModelAdmin):
	model = ArticleModel


admin.site.register(ArticleModel, ArticleAdmin)
