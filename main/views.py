from django.db.models import Min
from django.views.generic import View, TemplateView
from django.shortcuts import redirect, render
from django_user_agents.utils import get_user_agent
from store.models import FavoriteProducts, ChargerItemModel, Currency, ChargersItems
from django.core import serializers
from django.http import HttpResponse


# стартова сторінка
def welcome_page(request):
	favorite_products = FavoriteProducts.objects.all()
	context = {
		'favorite_products': favorite_products,
	}
	user_agent = get_user_agent(request)
	if user_agent.is_mobile:
		return render(request, 'main/welcome_mob.html', context)
	else:
		return render(request, 'main/welcome.html', context)


def contact_info(request):
	return render(request, 'main/contact_info.html')

class RobotstxtView(TemplateView):
	template_name = 'main/robots.txt'
	content_type = 'text/plain'

class ActiveButtonsView(View):
	template_name = 'main/active_buttons.html'

	def get(self, request):
		context = self.request.GET.get('q')
		print(context)
		return render(request, self.template_name, {'context': context})

def product_feed(request):

	all_items = ChargerItemModel.objects.filter(category__slug='charging_stations')
	currency = Currency.objects.first()
	all_items = [{
		'product': item,
		'min_price': int(
			ChargersItems.objects.filter(
				category__slug=item.category.slug,
				model__slug=item.slug
			).aggregate(Min('price'))['price__min'] * currency.current if (Min('price')) else 0
		)
	}
		for item in all_items]

	context = {'query': all_items}
	response = render(request, 'main/example.xml', context)
	response['Content-Type'] = 'application/xml'
	return response