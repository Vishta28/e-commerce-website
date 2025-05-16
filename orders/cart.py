from store.models import ChargersItems, Currency
from store.views import get_all_images

class Cart(object):
	def __init__(self, request):
		self.session = request.session
		cart = self.session.get('cart')

		if not cart:
			self.session['cart'] = {}

		self.cart = cart

	def __iter__(self):
		for slug in self.cart.keys():

			product = ChargersItems.objects.get(slug=slug)
			currency = Currency.objects.all().first()
			chargersitems_images = get_all_images(product)

			self.cart[slug]['product'] = product
			self.cart[slug]['image'] = chargersitems_images

		for item in self.cart.values():
			if item['product'].sale_price:
				item['total_price'] = int((item['product'].sale_price * currency.current * item['quantity']))
			else:
				item['total_price'] = int((item['product'].price * currency.current * item['quantity']))

			yield item

	def total_cost(self):
		for slug in self.cart.keys():
			self.cart[slug]['product'] = ChargersItems.objects.get(slug=slug)
			currency = Currency.objects.all().first()
		sum_price = 0
		sum_sale_price = 0
		for item in self.cart.values():
			if item['product'].sale_price:
				sum_sale_price += int(item['product'].sale_price * currency.current * item['quantity'])
			if not item['product'].sale_price:
				sum_price += int(item['product'].price * currency.current * item['quantity'])

		return int(sum_price + sum_sale_price)


	def __len__(self):
		return sum(item['quantity'] for item in self.cart.values())


	def save(self):
		self.session['cart'] = self.cart
		self.session.modified = True

	def add(self, slug, quantity=1, update_quantity=False):

		if slug not in self.cart:
			self.cart[slug] = {'quantity': 1, 'slug': slug}

		if update_quantity:
			self.cart[slug]['quantity'] += int(quantity)

			if self.cart[slug]['quantity'] == 0:
				self.remove(slug)

		self.save()

	def remove(self, slug):
		if slug in self.cart:
			del self.cart[slug]
			self.save()

		if not self.cart:
			del self.session['cart']
			self.session.modified = True

	def remove_all(self):
		del self.session['cart']
		self.session.modified = True

	def get_item(self, slug):
		if slug in self.cart:
			return self.cart[slug]
		else:
			return None
