from django.shortcuts import render
from django.shortcuts import get_object_or_404
from articles.models import ArticleModel

def policy(request):
    article = get_object_or_404(ArticleModel, tags='policy')
    context = {
        'article': article,
    }
    return render(request, 'footer/policy.html', context)

