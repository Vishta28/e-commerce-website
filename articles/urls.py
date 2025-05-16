from django.urls import path
from .views import ArticleView, ArticleDetailView

urlpatterns = [
	path('articles/', ArticleView.as_view(), name='articles'),
	path('article/<slug:slug>', ArticleDetailView.as_view(), name='article_detail')
]