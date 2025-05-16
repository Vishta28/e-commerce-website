from store.models import ChargerItemModel, ChargersItems, Category, Currency
from django.views.generic import DetailView, ListView, TemplateView, CreateView, View
from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404
from store.utils import get_first_image

class FavoritesView(ListView):
	template_name = 'favorites/favorites.html'
	model = ChargersItems
	context_object_name = 'items'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['chargersitems_images'] = get_first_image(context)

		currency = Currency.objects.all().first()
		context['currency'] = currency.current
		context['currency_token'] = currency.token

		return context

class AddToFavoritesView(View):
	def post(self, request):
		slug = request.POST.get('slug')

		# Отримуємо характеристики товару за допомогою slug
		charger_item = get_object_or_404(ChargersItems, slug=slug)

		# Якщо 'favorites' немає, то створюємо його як пустий список
		if request.session.get('favorites') is None:
			request.session['favorites'] = []
		else:
			request.session['favorites'] = list(request.session['favorites'])

		# Перевірка чи наявний товар у списку
		item_exist = next((item for item in request.session['favorites'] if item['slug'] == slug), None)

		# Якщо товар не в списку, то додаємо його slug та характеристики до списку favorites
		if not item_exist and len(request.session['favorites']) < 10:
			request.session['favorites'].append({
				'slug': slug,
			})
			request.session.modified = True

		return redirect('favorites')

class DeleteFromFavoritesView(View):
	def post(self, request):
		slug = request.POST.get('slug')

		for item in request.session['favorites']:
			if item['slug'] == slug:
				item.clear()
				request.session.modified = True

		while {} in request.session['favorites']:
			request.session['favorites'].remove({})

		if not request.session['favorites']:
			del request.session['favorites']
			request.session.modified = True

		return redirect('favorites')



