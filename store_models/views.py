from django.shortcuts import render, get_object_or_404
from django.views import View
from django_user_agents.utils import get_user_agent
from store.models import ChargerItemModel, ChargersItems, Category, Currency, FavoriteProducts, FavoriteAccessories
from django.views.generic import DetailView, ListView, TemplateView
from django.contrib.postgres.search import SearchQuery, SearchVector
from django.db.models import Q, BooleanField
from store.utils import get_all_images, get_first_image_favorite_products, get_first_image
from django.db.models import Case, When, IntegerField, Min

# сторінка де перелічені моделі товарів
class ModelView(TemplateView):
	model = ChargerItemModel
	template_name = 'store_models/models_page.html'

	def get(self, request, *args, **kwargs):
		category = self.kwargs.get('category')
		brand = self.request.GET.getlist('brand', '')
		brand_list = None
		if len(brand) < 2:
			brand = self.request.GET.get('brand', '')
		else:
			brand_list = brand = self.request.GET.getlist('brand', '')
		# Отримуємо бренди
		brands = ChargerItemModel.objects.filter(category__slug=category).values_list('brand', flat=True).distinct()
		context = {
			'brands': brands,
			'category': category,
			'brand': brand,
			'brand_list': brand_list,
		}

		return render(request, self.template_name, context)


class ModelsCategoryMenu(TemplateView):
	model = ChargerItemModel
	template_name = 'store_models/store_models_categories_menu.html'


# сторінка котра підвантажує список моделей товарів за допомогою htmx
class ItemsModel(ListView):
	model = ChargerItemModel
	template_name = 'store_models/models_list.html'
	context_object_name = 'category_model'
	paginate_by = 4

	def get_queryset(self):
		# Отримання категорії з URL параметрів
		category = self.kwargs.get('category')

		brand = self.request.GET.get('brand')
		if brand:
			if len(brand) < 2:
				return ChargerItemModel.objects.filter(category__slug=category, brand=brand)
			else:
				brand = self.request.GET.getlist('brand')
				return ChargerItemModel.objects.filter(category__slug=category, brand__in=brand)
		else:
			return ChargerItemModel.objects.filter(category__slug=category)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		# Отримуємо категорію з URL
		category = self.kwargs.get('category')

		if category:
			context['category'] = category
		all_items = ChargerItemModel.objects.filter(category__slug=category)
		print(all_items, 'ALL')
		for items in all_items:
			print(items.slug)
		currency = Currency.objects.first()
		# нижче є помилка, якщо товарів немає то ціна = None і при множенні currency сторінка ламається
		context['all_items'] = [{
			'product': item,
			# 'min_price': int(
			# 	ChargersItems.objects.filter(
			# 		category__slug=item.category.slug,
			# 		model__slug=item.slug
			# 	).aggregate(Min('price'))['price__min'] * currency.current
			# )
		}
			for item in all_items]
		return context

class ModelItemsInfo(ListView):
	model = ChargersItems
	template_name = 'store_models/partials/models_info.html'

	def get_context_data(self, *, object_list=None, **kwargs):
		context = super().get_context_data(**kwargs)

		items_model = self.kwargs.get('model')
		items_category = self.kwargs.get('category')

		query = ChargersItems.objects.filter(model__slug=items_model, category__slug=items_category)

		min_price = query.aggregate(Min('price'))
		item_sale_price = query.filter(sale_price__isnull=False)
		print(item_sale_price, 'SP')


		currency = Currency.objects.all().first()
		context['currency_price'] = int(min_price['price__min'] * currency.current)
		context['currency_token'] = currency.token
		if item_sale_price:
			context['sale_price'] = int(item_sale_price[0].sale_price * currency.current)

		return context

# сторінка товарів котрі відносяться до моделі виробу та фільтр конструктора
class ItemListPage(ListView):
	model = ChargersItems
	template_name = 'store_models/constructor_page.html'
	context_object_name = 'model_items'

	def get_queryset(self):
		type_get = self.request.GET.get('type')
		phases_get = self.request.GET.get('phases')
		power_amps_get = self.request.GET.get('power_amps')
		cable_length_get = self.request.GET.get('cable_length')
		item_result = self.request.GET.get('item_result')


		item_model = self.kwargs.get('model')
		item_category = self.kwargs.get('category')
		# сюди потрібно буде до фільтру додати контекст категорію
		query = ChargersItems.objects.filter(Q(model__slug=item_model) & Q(category__slug=item_category)).order_by('price')

		type = ChargersItems.objects.filter(Q(model__slug=item_model) & Q(category__slug=item_category)).order_by('price').values('type').distinct()
		phases = ChargersItems.objects.filter(Q(model__slug=item_model) & Q(category__slug=item_category)).order_by('price').values('phases').distinct()
		power_amps = ChargersItems.objects.filter(Q(model__slug=item_model) & Q(category__slug=item_category)).order_by('price').values('power_amps').distinct()
		cable_length = ChargersItems.objects.filter(Q(model__slug=item_model) & Q(category__slug=item_category)).order_by('price').values('cable_length').distinct()

		context = {
			'type': type,
			'phases': phases,
			'power_amps': power_amps,
			'cable_length': cable_length,
			'item_model': item_model,
			'item_category': item_category,
			'query': query,
			'type_get': type_get,
			'phases_get': phases_get,
			'power_amps_get': power_amps_get,
			'cable_length_get': cable_length_get,
			'item_result': item_result,
		}

		return context

class ModelsConstructorView(ListView):
	model = ChargersItems
	template_name = 'store_models/constructor_results.html'
	context_object_name = 'item'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		queryset = self.get_queryset()
		if queryset:
			first_item = queryset.first()
		else:
			first_item = queryset
		type = self.request.GET.get('type')
		phases = self.request.GET.get('phases')
		power_amps = self.request.GET.get('power_amps')
		cable_length = self.request.GET.get('cable_length')

		item_model = self.kwargs.get('model')
		item_category = self.kwargs.get('category')
		context['item_model'] = item_model
		context['item_category'] = item_category


		custom_order_type = Case(
			When(type=type, then=True),
			default=False,
			output_field=BooleanField(),
		)
		custom_order_phases = Case(
			When(phases=phases, then=True),
			default=False,
			output_field=BooleanField(),
		)
		custom_order_power_amps = Case(
			When(power_amps=power_amps, then=True),
			default=False,
			output_field=BooleanField(),
		)
		custom_order_cable_length = Case(
			When(cable_length=cable_length, then=True),
			default=False,
			output_field=BooleanField(),
		)

		# сюди потрібно буде до фільтру додати контекст категорію
		query = ChargersItems.objects.filter(model__slug=item_model)
		context['type'] = ChargersItems.objects.filter(
			Q(model__slug=item_model) & Q(category__slug=item_category)).annotate(
			is_desired_type=custom_order_type).order_by('-is_desired_type', 'type').values('type').distinct()
		context['phases'] = ChargersItems.objects.filter(
			Q(model__slug=item_model) & Q(category__slug=item_category)).annotate(
			is_desired_phases=custom_order_phases).order_by('-is_desired_phases', 'phases').values(
			'phases').distinct()
		context['power_amps'] = ChargersItems.objects.filter(
			Q(model__slug=item_model) & Q(category__slug=item_category)).annotate(
			is_desired_power_amps=custom_order_power_amps).order_by('-is_desired_power_amps', 'power_amps').values(
			'power_amps').distinct()
		context['cable_length'] = ChargersItems.objects.filter(
			Q(model__slug=item_model) & Q(category__slug=item_category)).annotate(
			is_desired_cable_length=custom_order_cable_length).order_by('-is_desired_cable_length',
																		'cable_length').values(
			'cable_length').distinct()

		if context['item']:
			session_comparison = self.request.session.get('comparison')
			if session_comparison:
				item_exist_comparison = next(
					(item for item in session_comparison if item['slug'] == context['item'][0].slug), None)
				context['item_exist_comparison'] = item_exist_comparison

			session_favorites = self.request.session.get('favorites')
			if session_favorites:
				item_exist_favorites = next(
					(item for item in session_favorites if item['slug'] == context['item'][0].slug), None)
				context['item_exist_favorites'] = item_exist_favorites

		context['chargersitems_images'] = get_all_images(first_item)
		context['first_item'] = first_item

		if first_item:
			currency = Currency.objects.all().first()
			if context['first_item'].sale_price:
				context['sale_price'] = int(context['first_item'].sale_price * currency.current)
				context['currency_price'] = int(context['first_item'].price * currency.current)
				context['currency_token'] = currency.token
			else:
				context['currency_price'] = int(context['first_item'].price * currency.current)
				context['currency_token'] = currency.token

		return context

	def get_queryset(self, *args, **kwargs):
		category = self.kwargs.get('category')
		model = self.kwargs.get('model')

		if category and model:
			qs = ChargersItems.objects.filter(category__slug=category, model__slug=model)
		else:
			qs = super().get_queryset(*args, **kwargs)

		filters = Q()

		type_filters = Q()
		type = self.request.GET.get('type')
		if type:
			type_filters |= Q(type=type)

		power_amps_filters = Q()
		power_amps = self.request.GET.get('power_amps')
		if power_amps:
			power_amps_filters |= Q(power_amps=power_amps)

		phases_filters = Q()
		phases = self.request.GET.get('phases')
		if phases:
			phases_filters |= Q(phases=phases)

		cable_length_filters = Q()
		cable_length = self.request.GET.get('cable_length')
		if cable_length:
			cable_length_filters |= Q(cable_length=cable_length)

		filters &= type_filters
		filters &= power_amps_filters
		filters &= phases_filters
		filters &= cable_length_filters

		filtered_chargers = qs.filter(filters)
		# charger = get_object_or_404(ChargersItems, filters)

		if filtered_chargers:
			return filtered_chargers
		else:
			pass


class QuickModelView(DetailView):
	model = ChargerItemModel
	template_name = 'store_models/partials/quick_model_view.html'
	context_object_name = 'item'
	slug_url_kwarg = 'model'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		items_model = self.kwargs.get('model')
		items_category = self.kwargs.get('category')

		query = ChargersItems.objects.filter(model__slug=items_model, category__slug=items_category)
		context['available_types'] = query.values('type').distinct()
		context['protection'] = query.values('protection').distinct()
		context['phases'] = query.values('phases').distinct()
		context['country'] = query.values('country').distinct()
		context['brand'] = query.values('brand').distinct()
		context['min_price'] = query.aggregate(Min('price'))

		return context

class FavoriteProductsView(ListView):
	model = FavoriteProducts
	template_name = 'store/partials/favorite_products.html'

	def get_context_data(self, *, object_list=None, **kwargs):
		context = super().get_context_data(**kwargs)
		fav_query = FavoriteProducts.objects.all()
		context['favorite_products'] = []

		context['favorite_accessories'] = FavoriteAccessories.objects.all()
		context['chargersitems_images'] = get_first_image_favorite_products(context['favorite_accessories'])

		# отримуємо курс валюти та розраховуємо ціну
		currency = Currency.objects.all().first()
		context['currency'] = currency.current
		context['currency_token'] = currency.token

		for items in fav_query:

			query = ChargersItems.objects.filter(model__slug=items.products.slug, category__slug=items.products.category.slug)
			min_price = query.aggregate(Min('price'))
			currency_price = int(min_price['price__min'] * currency.current)
			print(currency_price, 'CUR_PRICE')
			context['favorite_products'].append({
				'items': items,
				'min_price': currency_price,
			})

		return context

class ConstructorOptionsView(TemplateView):
	model = ChargersItems
	template_name = 'store_models/constructor_options.html'

	def get_context_data(self, **kwargs):
		context_type = self.request.GET.get('type', '')
		context_phases = self.request.GET.get('phases', '')
		type_list = self.kwargs.get('type_list')
		print(type_list)



		return {'context_type': context_type, 'type_list': type_list, 'context_phases': context_phases}
