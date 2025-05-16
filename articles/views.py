from django.shortcuts import render
from django.views.generic import DetailView, ListView
from .models import ArticleModel
from django.db.models import Q


# Create your views here.
class ArticleView(ListView):
	model = ArticleModel
	context_object_name = 'articles'
	template_name = 'article/articles_list.html'

	def get_context_data(self, *, object_list=None, **kwargs):
		context = super().get_context_data(**kwargs)
		articles_tags = ArticleModel.objects.filter(article_type='user_article').values_list('tags', flat=True).distinct()
		context['article'] = ArticleModel.objects.filter(article_type='user_article')
		uniq_tags = set()
		for tags in articles_tags:
			individual_tags = tags.split(',')
			for tag in individual_tags:
				uniq_tags.add(tag.strip())

		tag = self.request.GET.get('tag', '')
		if tag:
			context['tag'] = tag

		context['uniq_tags'] = uniq_tags
		return context

	def get_queryset(self):
		tag = self.request.GET.get('tag', '')
		query = Q()
		if tag:
			query |= Q(tags__icontains=tag)
			return ArticleModel.objects.filter(query).distinct()
		return ArticleModel.objects.filter(article_type='user_article')

class ArticleDetailView(DetailView):
	model = ArticleModel
	context_object_name = 'article'
	template_name = 'article/article_detail.html'