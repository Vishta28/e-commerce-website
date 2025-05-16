from django.shortcuts import get_object_or_404
from django_user_agents.utils import get_user_agent

from articles.models import ArticleModel
from .models import ChargersItems, Currency, FavoriteProducts
from django.views.generic import DetailView, ListView
from django.db.models import Q
from django.template.defaulttags import register
from .utils import get_first_image, get_all_images
from user_agents import parse


class StoreFilter:
	def get_parameters(self):
		types = ChargersItems.objects.filter(Q(category__slug='charging_stations') |
												Q(category__slug='charging_cables')).values_list('type', flat=True).distinct()
		powers_amps = ChargersItems.objects.filter(Q(category__slug='charging_stations') |
													Q(category__slug='charging_cables')).values_list('power_amps', flat=True).distinct()
		powers_amps_plugs = ChargersItems.objects.filter(Q(category__slug='accessories')).values_list('power_amps',
																								  flat=True).distinct()
		power = ChargersItems.objects.filter(Q(category__slug='charging_stations') |
												   Q(category__slug='charging_cables')).values_list('power', flat=True).distinct()
		brands = ChargersItems.objects.filter(Q(category__slug='charging_stations') |
												Q(category__slug='charging_cables')).values_list('brand', flat=True).distinct()
		phases = ChargersItems.objects.filter(Q(category__slug='charging_stations') |
												Q(category__slug='charging_cables')).values_list('phases', flat=True).distinct()
		categories = ChargersItems.objects.filter(Q(category__slug='charging_stations') |
													Q(category__slug='charging_cables')).values_list('category', flat=True).distinct()
		# accessories_type = ChargersItems.objects.filter(category__slug='accessories').values_list('accessories_type', flat=True).distinct()
		accessories_type = ChargersItems.get_accessories_type_dict()

		return {'types': types, 'powers_amps': powers_amps, 'power': power, 'brands': brands, 'phases': phases, 'categories': categories, 'accessories_type': accessories_type, 'power_amps_plugs': powers_amps_plugs}

# сторінка магазину з фільтрами


class StorePageView(ListView, StoreFilter):
	model = ChargersItems
	context_object_name = 'items'
	paginate_by = 4

	def get_paginate_by(self, queryset):
		user_agent = get_user_agent(self.request)
		if user_agent.is_mobile:
			return 2
		elif user_agent.is_tablet:
			return 3
		elif user_agent.is_pc:
			return 3
		return super().get_paginate_by(queryset)

	# підвантажуємо сторінку в залежності від типу притсрою
	def get_template_names(self, *args, **kwargs):
		user_agent = get_user_agent(self.request)
		if user_agent.is_mobile:
			return ['store/store_mob.html']
		elif user_agent.is_tablet:
			return ['store/store.html']
		elif user_agent.is_pc:
			return ['store/store.html']
		return super().get_template_names(*args, **kwargs)


	# Параметри для пагінації та фільтрації

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		categories = context['categories'] = self.request.GET.get('categories', '')
		type = context['type'] = self.request.GET.get('type', '')
		power_amps = context['power_amps'] = self.request.GET.get('power_amps', '')
		power_amps_plugs = context['power_amps_plugs'] = self.request.GET.get('powers_amps_plugs', '')
		power = context['power'] = self.request.GET.get('power', '')
		phases = context['phases'] = self.request.GET.get('phases', '')
		brand = context['brand'] = self.request.GET.get('brand', '')
		accessories_type = context['accessories_type'] = self.request.GET.get('accessories_type', '')
		print(power_amps_plugs, 'POWER AMPS')

		context['chargersitems_images'] = get_first_image(context)
		context['q'] = self.request.GET.get('q')
		# accessories_store
		context['ac'] = self.request.GET.get('ac')
		# plugs_store
		context['plg'] = self.request.GET.get('plg')
		print(context['plg'], 'HOPHEY')
		# Створити список з отриманих значень
		parameters_list = [categories, type, power_amps, power, phases, brand, accessories_type, power_amps_plugs]

		context['parameters_list'] = ''
		for el in parameters_list:
			if el:
				context['parameters_list'] = parameters_list
				context['q'] = ''

		# отримуємо копію url видаляючи ключ page з url

		queries_without_page = self.request.GET.copy()
		if queries_without_page.get('page'):
			del queries_without_page['page']

		context['queries'] = queries_without_page.urlencode()
		context['article'] = get_object_or_404(ArticleModel, id=3)

		# отримуємо курс валюти та розраховуємо ціну
		currency = Currency.objects.all().first()
		context['currency'] = currency.current
		context['currency_token'] = currency.token

		return context

	# Фільтрація товарів на сторінці магазину

	def get_queryset(self, *args, **kwargs):
		ac = self.request.GET.get('ac')
		plg = self.request.GET.get('plg')
		if plg:
			qs = ChargersItems.objects.filter(
				 Q(accessories_type='plugs') | Q(accessories_type='auto_adapt') | Q(accessories_type='electric_adapt'))
		elif ac:
			qs = ChargersItems.objects.filter(
				Q(category__slug='accessories'))
		else:
			qs = ChargersItems.objects.filter(Q(category__slug='charging_stations') | Q(category__slug='charging_cables'))

		# сортування товару (order_by)

		sorting_options = {
			'price_up': 'price',
			'price_down': '-price',
			'date_new': '-time',
			'in_stock': '-in_stock',
		}

		sort = self.request.GET.get('sort')
		if sort in sorting_options:
			sort_by = sorting_options[sort]
			if plg:
				sorted_queryset = ChargersItems.objects.filter(
					Q(accessories_type='plugs') | Q(accessories_type='auto_adapt') | Q(
						accessories_type='electric_adapt')).order_by(sort_by)
			elif ac:
				sorted_queryset = ChargersItems.objects.filter(category__slug='accessories').order_by(sort_by)
			else:
				sorted_queryset = ChargersItems.objects.filter(Q(category__slug='charging_stations') |
														   Q(category__slug='charging_cables')).order_by(sort_by)
			return sorted_queryset

		# Пошук товарів в стрчці пошуку в шапці сайту

		q = self.request.GET.get('q')

		if q:
			# split_q = q.split(' ')
			search_query = Q(title__icontains=q) | Q(category__title__icontains=q)
			# Фільтруємо об'єкти ChargersItems за цим об'єктом Q
			object_list = ChargersItems.objects.filter(search_query)
			if object_list:
				return object_list
			else:
				return qs.filter(Q(title__icontains=q) | Q(category__title__icontains=q))

		# логіка фільтру на сторінці магазину

		filters = Q()

		accessories_type = Q()
		values = self.request.GET.getlist('accessories_type')
		for value in values:
			if value:
				accessories_type |= Q(accessories_type=value)

		categories_filters = Q()
		values = self.request.GET.getlist('categories')
		for value in values:
			if value:
				categories_filters |= Q(category=value)

		type_filters = Q()
		values = self.request.GET.getlist('type')
		for value in values:
			if value:
				type_filters |= Q(type=value)

		power_amps_filters = Q()
		values = self.request.GET.getlist('power_amps')
		for value in values:
			if value:
				power_amps_filters |= Q(power_amps=value)

		power_filters = Q()
		values = self.request.GET.getlist('power')
		for value in values:
			if value:
				power_filters |= Q(power=value)

		phases_filters = Q()
		phases_values = self.request.GET.getlist('phases')
		for value in phases_values:
			if value:
				phases_filters |= Q(phases=value)

		brand_filter = Q()
		value = self.request.GET.getlist('brand')
		for value in value:
			if value:
				brand_filter |= Q(brand=value)

		filters &= categories_filters
		filters &= type_filters
		filters &= power_amps_filters
		filters &= phases_filters
		filters &= brand_filter
		filters &= power_filters
		filters &= accessories_type

		filtered_chargers = qs.filter(filters)

		return filtered_chargers

# детальна сторінка товару
class ItemDetail(DetailView):
	model = ChargersItems
	template_name = 'store/item_detail.html'
	slug_url_kwarg = 'charger_slug'
	context_object_name = 'item'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		session_comparison = self.request.session.get('comparison')
		if session_comparison:
			item_exist_comparison = next((item for item in session_comparison if item['slug'] == context['item'].slug), None)
			context['item_exist_comparison'] = item_exist_comparison

		session_favorites = self.request.session.get('favorites')
		if session_favorites:
			item_exist_favorites = next((item for item in session_favorites if item['slug'] == context['item'].slug), None)
			context['item_exist_favorites'] = item_exist_favorites

		session_cart = self.request.session.get('cart')
		if session_cart:
			if context['item'].slug in session_cart:
				context['item_exist_cart'] = 'true'

		currency = Currency.objects.all().first()
		if context['item'].sale_price:
			context['sale_price'] = int(context['item'].sale_price * currency.current)
			context['currency_price'] = int(context['item'].price * currency.current)
			context['currency_token'] = currency.token
		else:
			context['currency_price'] = int(context['item'].price * currency.current)
			context['currency_token'] = currency.token

		features = context['item'].features.split(',')
		context['features'] = features

		context['chargersitems_images'] = get_all_images(context)

		return context

class ItemDetailAccessoriesView(ListView):
	template_name = 'store/partials/item_detail_accessories.html'
	model = ChargersItems
	context_object_name = 'items'

	def get_queryset(self):
		model = self.kwargs['model']
		slug = self.kwargs['slug']
		item = ChargersItems.objects.get(slug=slug)
		print('HAHAHAHAHA', model, slug, item)

		qs = ChargersItems.objects.filter(Q(category__slug='accessories') & Q(model__title=model)).exclude(accessories_type='plugs').exclude(accessories_type='Trimach_conectora')
		qs2 = ChargersItems.objects.filter(Q(category__slug='accessories') & Q(accessories_type='plugs') & Q(phases=item.phases))
		qs3 = ChargersItems.objects.filter(
			Q(category__slug='accessories') & Q(model__title=model) & Q(accessories_type='Trimach_conectora') & Q(type=item.type))
		final_qs = qs | qs2 | qs3
		return final_qs

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['chargersitems_images'] = get_first_image(context)

		currency = Currency.objects.all().first()
		context['currency'] = currency.current
		context['currency_token'] = currency.token

		context['session_cart'] = self.request.session.get('cart')

		return context


class SearchResults(ListView):
	model = ChargersItems
	template_name = 'store/search_results.html'
	context_object_name = 'items'

	def get_queryset(self, *args, **kwargs):
		qs = super().get_queryset(*args, **kwargs)

		q = self.request.GET.get('q')
		print(len(q))

		if len(q) > 0:
			print(q)
			search_query = Q(title__icontains=q) | Q(category__title__icontains=q)
			# Фільтруємо об'єкти ChargersItems за цим об'єктом Q
			object_list = ChargersItems.objects.filter(search_query)
			if object_list:
				return object_list
			else:
				return qs.filter(Q(title__icontains=q) | Q(category__title__icontains=q))

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		# коли довжина зпиту 0 символів виникає помилка
		try:
			context['chargersitems_images'] = get_first_image(context)
		except:
			pass

		currency = Currency.objects.all().first()
		context['currency_price'] = currency.current
		context['currency_token'] = currency.token

		return context

class QuickView(DetailView):
	model = ChargersItems
	template_name = 'store/quick_view.html'
	context_object_name = 'item'
	slug_url_kwarg = 'charger_slug'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		session_comparison = self.request.session.get('comparison')
		if session_comparison:
			item_exist_comparison = next((item for item in session_comparison if item['slug'] == context['item'].slug),
										 None)
			context['item_exist_comparison'] = item_exist_comparison

		session_favorites = self.request.session.get('favorites')
		if session_favorites:
			item_exist_favorites = next((item for item in session_favorites if item['slug'] == context['item'].slug),
										None)
			context['item_exist_favorites'] = item_exist_favorites

		session_cart = self.request.session.get('cart')
		if session_cart:
			if context['item'].slug in session_cart:
				context['item_exist_cart'] = 'true'

		context['chargersitems_images'] = get_all_images(context)

		return context

@register.filter
def get_item(dictionary, key):
	return dictionary.get(key)

@register.filter
def multiply(value, arg):
	return int(value * arg)
