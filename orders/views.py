from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, DetailView, FormView
from store.models import ChargersItems, Currency, ChargerItemModel
from .cart import Cart
from django_user_agents.utils import get_user_agent
from .forms import OrderForm
from .models import Order, OrderItem, QuickOrder
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from store.views import get_first_image, get_all_images
import random

# Create your views here.
class CartView(ListView):
	template_name = 'orders/cart.html'
	model = ChargersItems
	context_object_name = 'items'


def add_to_cart(request, slug, id):
	cart = Cart(request)
	cart.add(slug)

	context = {
		'id': id,
		'slug': slug,
	}

	return render(request, 'orders/partials/header_menu_cart_button.html', context)

def update_cart(request, slug, action):
	cart = Cart(request)
	cart.add(slug)

	if action == 'increment':
		cart.add(slug, 1, True)
	elif action == 'decrement':
		cart.add(slug, -1, True)
	elif action == 'remove':
		cart.remove(slug)
	else:
		pass

	product = ChargersItems.objects.get(slug=slug)
	currency = Currency.objects.all().first()
	quantity = cart.get_item(slug)
	chargersitems_images = get_all_images(product)

	if quantity:
		quantity = quantity['quantity']
		if product.sale_price:
			item = {
				'product': {
					'slug': product.slug,
					'title': product.title,
					'price': product.price,
					'model': product.model,
					'category': product.category.slug,
					'in_stock': product.in_stock,
				},
				'total_price': int((quantity * currency.current * product.sale_price)),
				'quantity': quantity,
				'image': chargersitems_images,
			}
		elif not product.sale_price:
			item = {
				'product': {
					'slug': product.slug,
					'title': product.title,
					'price': product.price,
					'model': product.model,
					'category': product.category.slug,
					'in_stock': product.in_stock,
				},
				'total_price': int((quantity * currency.current * product.price)),
				'quantity': quantity,
				'image': chargersitems_images,
			}
	else:
		item = None

	#правки правки правки
	user_agent = get_user_agent(request)
	if user_agent.is_mobile or user_agent.is_tablet:
		response = render(request, 'orders/partials/cart_item_mob.html', {'item': item})
	else:
		response = render(request, 'orders/partials/cart_item.html', {'item': item})

	response['HX-Trigger'] = 'update_cart'

	return response


def header_menu_cart(request):
	return render(request, 'orders/partials/header_menu_cart_button.html')


def cart_total(request):
	return render(request, 'orders/partials/cart_total.html')


def cart_items_total(request):
	return render(request, 'orders/partials/cart_items_total.html')

def check_shipping_type(request):
	if request.method == 'GET':
		shipping_type = request.GET.get('shipping_type')
		context = {
			'shipping_type': shipping_type
		}
		return render(request, 'orders/partials/check_shipping_type.html', context)

def check_comment(request):
	if request.method == 'GET':
		checkbox_comment = request.GET.get('checkbox_comment')
		print(checkbox_comment, 'COMMENT')
		context = {
			'checkbox_comment': checkbox_comment
		}
		return render(request, 'orders/partials/check_comment.html', context)

def loader(request):
	return render(request, 'orders/partials/loader.html')


class CartAccessoriesView(ListView):
	template_name = 'orders/cart_accessories.html'
	model = ChargersItems
	context_object_name = 'items'

	def get_queryset(self):
		model = self.kwargs['model']
		slug = self.kwargs['slug']
		item = ChargersItems.objects.get(slug=slug)
		qs = ChargersItems.objects.filter(Q(category__slug='accessories') & Q(model__title=model)).exclude(
			accessories_type='plugs').exclude(accessories_type='Trimach_conectora')
		qs2 = ChargersItems.objects.filter(
			Q(category__slug='accessories') & Q(model__title=model) & Q(accessories_type='plugs') & Q(phases=item.phases))
		qs3 = ChargersItems.objects.filter(
			Q(category__slug='accessories') & Q(model__title=model) & Q(accessories_type='Trimach_conectora') & Q(
				type=item.type))
		final_qs = qs | qs2 | qs3
		return final_qs

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		currency = Currency.objects.all().first()
		model = self.kwargs['model']

		qs = ChargersItems.objects.filter(Q(category__slug='accessories') & Q(model__title=model))
		context['chargersitems_images'] = get_first_image(qs)
		for items in qs:
			product = ChargersItems.objects.get(slug=items.slug)
			# context['sale_price'] = int(product.sale_price * currency.current)
			context['currency'] = currency.current
			context['currency_token'] = currency.token
			# else:
			# 	context['currency_price'] = int(product.price * currency.current)
			# 	context['currency_token'] = currency.token
		context['session_cart'] = self.request.session.get('cart')

		return context


class ConfirmOrderStep1View(FormView):
	template_name = 'orders/order.html'
	context_object_name = 'items'
	form_class = OrderForm

	def form_valid(self, form):
		# Зберігаємо дані форми у сесії
		self.request.session['order_form_data'] = form.cleaned_data
		return redirect('order_step2')


class ConfirmOrderStep2View(TemplateView):
	template_name = 'orders/order_step2.html'

	def get(self, request):
		order_form_data = self.request.session.get('order_form_data')

		payment_type_display = dict(Order.PAYMENT_TYPE).get(order_form_data['payment_type'])
		shipping_type_display = dict(Order.SHIPPING_TYPE).get(order_form_data['shipping_type'])

		# Отримання інформації про валюту
		currency = Currency.objects.first()

		# Отримання інформації про кошик
		cart = Cart(request)
		total_cost = cart.total_cost()

		# Отримання інформації про замовлені товари
		product_list = []
		for item in cart:
			product = item['product']
			quantity = item['quantity']

			if product.sale_price:
				price = int((product.sale_price * currency.current) * quantity)
				product_list.append({
					'product': product,
					'quantity': quantity,
					'price': price,
				})

			if not product.sale_price:
				price = int((product.price * currency.current) * quantity)

				product_list.append({
					'product': product,
					'quantity': quantity,
					'price': price,
				})

		# Передача контексту у шаблон
		context = {
			'form': OrderForm(order_form_data),  # Ініціалізація порожньої форми
			'order_form_data': order_form_data,
			'payment_type_display': payment_type_display,
			'shipping_type_display': shipping_type_display,
			'product_list': product_list,
			'currency_token': currency.token,
			'total_cost': total_cost,
		}

		return render(request, self.template_name, context)


class ConfirmOrderFinalView(TemplateView):
	template_name = 'orders/order_confirm.html'

	def post(self, request):
		# Отримуємо дані з сесії
		order_form_data = self.request.session.get('order_form_data')

		# очищення даних для форми
		payment_type_display = dict(Order.PAYMENT_TYPE).get(order_form_data['payment_type'])

		shipping_type_display = dict(Order.SHIPPING_TYPE).get(order_form_data['shipping_type'])

		order_number = random.randint(10000, 99998)

		# Отримання інформації про валюту
		currency = Currency.objects.first()

		# Отримання інформації про кошик
		cart = Cart(request)
		total_cost = cart.total_cost()

		session_key = request.session.session_key
		user = session_key

		context = {
			'order_number': order_number,
		}

		order_number_exists = Order.objects.filter(order_number=order_number).exists()
		if order_number_exists:
			order_number = order_number + 1
		order = Order.objects.create(order_number=order_number, user=user, name=order_form_data['name'], phone_number=order_form_data['phone_number'],
									 total_cost=total_cost, shipping_type=order_form_data['shipping_type'], payment_type=order_form_data['payment_type'],
									 shipping_address=order_form_data['shipping_address'], comment=order_form_data['comment'],)
		product_list = []
		for item in cart:
			product = item['product']
			quantity = item['quantity']
			price = 0
			if product.sale_price:
				price = int((product.sale_price * currency.current) * quantity)
			elif not product.sale_price:
				price = int((product.price * currency.current) * quantity)
			OrderItem.objects.create(order=order, product=product, price=price, quantity=quantity)

			product_list.append({
				'product': product,
				'quantity': quantity,
				'price': price,
			})
		context2 = {
			'product_list': product_list,
			'order_number': order_number,
			'type': 'Нове замовлення',
			'name': order_form_data['name'],
			'phone_number': order_form_data['phone_number'],
			'email': order_form_data['email'],
			'payment_type': payment_type_display,
			'shipping_type': shipping_type_display,
			'total_cost': total_cost,
			'currency_token': currency.token,
			'shipping_address': order_form_data['shipping_address'],
			'comment': order_form_data['comment'],
		}
		html_message = render_to_string('orders/partials/order_email.html', context2)
		plain_message = strip_tags(html_message)
		message = EmailMultiAlternatives(
			subject='Замовлення',
			body=plain_message,
			from_email='mailtrap@demomailtrap.com',
			to=['vishta28@gmail.com']
		)
		message.attach_alternative(html_message, 'text/html')
		message.send()

		cart = request.session.get('cart')
		if cart:
			del request.session['cart']
			request.session.modified = True

		return render(request, self.template_name, context)


class OrderQuickView(DetailView):
	template_name = 'orders/order_quick.html'
	slug_url_kwarg = 'slug'
	context_object_name = 'item'
	model = ChargersItems

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		slug = self.kwargs.get(self.slug_url_kwarg)
		item = ChargersItems.objects.get(slug=slug)

		currency = Currency.objects.all().first()
		if item.sale_price:
			context['currency_sale_price'] = int(context['item'].sale_price * currency.current)
			context['currency_price'] = int(context['item'].price * currency.current)
		else:
			context['currency_price'] = int(context['item'].price * currency.current)
		context['currency_token'] = currency.token
		context['chargersitems_images'] = get_all_images(item)

		return context

class OrderModelQuickView(DetailView):
	template_name = 'orders/order_model_quick.html'
	slug_url_kwarg = 'slug'
	context_object_name = 'item'
	model = ChargerItemModel

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		slug = self.kwargs.get('slug')
		category = self.kwargs.get('category')
		item = ChargerItemModel.objects.get(slug=slug)
		print(slug, category, 'INFO')

		context['item'] = item
		context['category'] = category

		return context

def check_quick_order(request):
	if request.method == 'GET':
		phone_number = request.GET.get('phone_number', '')
		if len(phone_number) == 9 and phone_number.isdigit():
			context = {'valid': 'valid'}
			print(context)
			return render(request, 'orders/partials/quick_order_confirm_button.html', context)
		else:
			context = {'false_valid': 'false_valid'}
			print(context)
			return render(request, 'orders/partials/quick_order_confirm_button.html', context)

def check_order_phone_number(request):
	if request.method == 'GET':
		phone_number = request.GET.get('phone_number', '')
		if len(phone_number) == 9 and phone_number.isdigit():
			context = {'valid': 'valid',
					'phone_number': phone_number}
			print(context)
			return render(request, 'orders/partials/check_order_phone_number.html', context)
		else:
			context = {'false_valid': 'false_valid',
					   'phone_number': phone_number}
			print(context)
			return render(request, 'orders/partials/check_order_phone_number.html', context)

class ConfirmOrderQuickView(TemplateView):
	template_name = 'orders/partials/quick_order_confirm.html'

	def post(self, request):
		order_type = request.POST.get('order_type')
		order_number = random.randint(10000, 99998)

		context_order_type = {
			'order_type': order_type,
			'order_number': order_number,
		}

		if order_type == 'quick_order':
			phone_number = request.POST.get('phone_number')

			price = int(request.POST.get('price'))
			currency_token = request.POST.get('currency_token')
			slug = request.POST.get('slug')
			product = ChargersItems.objects.get(slug=slug)

			order = QuickOrder.objects.create(order_number=order_number,
										 phone_number=phone_number, total_cost=price, type='Швидке замовлення')
			OrderItem.objects.create(quick_order=order, product=product, price=price, quantity=1)

			product_list = []

			product_list.append({
				'product': product,
				'quantity': 1,
				'price': price,
			})

			context = {
				'phone_number': phone_number,
				'product_list': product_list,
				'order_number': order_number,
				'type': 'Швидке замовлення',
				'currency_token': currency_token,
			}

			html_message = render_to_string('orders/partials/order_email.html', context)
			plain_message = strip_tags(html_message)
			message = EmailMultiAlternatives(
				subject='Замовлення',
				body=plain_message,
				from_email='mailtrap@demomailtrap.com',
				to=['vishta28@gmail.com']
			)
			message.attach_alternative(html_message, 'text/html')
			message.send()

		elif order_type == 'callback':
			name = request.POST.get('name')
			phone_number = request.POST.get('phone_number')
			order_model = request.POST.get('order_model')
			if order_model:
				context = {
					'phone_number': phone_number,
					'name': name,
					'type': 'Зворотній дзвінок',
					'order_model': order_model
				}
			else:
				context = {
					'phone_number': phone_number,
					'name': name,
					'type': 'Зворотній дзвінок',
				}

			QuickOrder.objects.create(phone_number=phone_number, name=name, type='Зворотній дзвінок')

			html_message = render_to_string('orders/partials/order_email.html', context)
			plain_message = strip_tags(html_message)
			message = EmailMultiAlternatives(
				subject='Замовлення',
				body=plain_message,
				from_email='mailtrap@demomailtrap.com',
				to=['vishta28@gmail.com']
			)
			message.attach_alternative(html_message, 'text/html')
			message.send()

		return render(request, 'orders/partials/quick_order_confirm.html', {'context_order_type': context_order_type})
