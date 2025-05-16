from django.shortcuts import redirect
from django.views.generic import DetailView, ListView

from store.models import ChargersItems, Currency
from store.utils import get_first_image


class ComparisonView(ListView):
	template_name = 'comparison/comparison_page.html'
	model = ChargersItems
	context_object_name = 'items'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['chargersitems_images'] = get_first_image(context)

		currency = Currency.objects.all().first()
		context['currency'] = currency.current
		context['currency_token'] = currency.token

		return context

class AddToComparisonView(DetailView):
	def post(self, request):
		slug = request.POST.get('slug')
		user_agent = request.POST.get('user_agent')

		# Отримуємо характеристики товару за допомогою slug

		# Якщо 'favorites' немає, то створюємо його як пустий список
		if request.session.get('comparison') is None:
			request.session['comparison'] = []
		else:
			request.session['comparison'] = list(request.session['comparison'])

		item_exist = next((item for item in request.session['comparison'] if item['slug'] == slug), None)

		if user_agent == 'True':
			if len(request.session['comparison']) >= 2:
				request.session['comparison'] = []
				if not item_exist:
					request.session['comparison'].append({
						'slug': slug,
					})
					request.session.modified = True
			else:
				if not item_exist:
					request.session['comparison'].append({
						'slug': slug,
					})
					request.session.modified = True
		else:
			if len(request.session['comparison']) >= 3:
				request.session['comparison'] = []
				if not item_exist:
					request.session['comparison'].append({
						'slug': slug,
					})
					request.session.modified = True
			else:
				if not item_exist:
					request.session['comparison'].append({
						'slug': slug,
					})
					request.session.modified = True

		return redirect('comparison')

class DeleteFromComparisonView(DetailView):
	def post(self, request):
		slug = request.POST.get('slug')

		for item in request.session['comparison']:
			if item['slug'] == slug:
				item.clear()
				request.session.modified = True

		while {} in request.session['comparison']:
			request.session['comparison'].remove({})

		if not request.session['comparison']:
			del request.session['comparison']
			request.session.modified = True

		return redirect('comparison')

