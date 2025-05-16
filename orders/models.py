from django.db import models

from store.models import ChargersItems


class Order(models.Model):
	ORDER_STATUS = [
		('ordered', 'Нове замовлення'), ('shipped', 'Доставлено'), ('refusal', 'Відмова')
	]
	SHIPPING_TYPE = [
		('nova_poshta', 'Нова Пошта'), ('self', 'Самовивіз'),
	]
	PAYMENT_TYPE = [
		('cash', 'Готівка'), ('bank_card', 'Сплата на карту'), ('cashless_payments', 'Безготівковий розрахунок')
	]
	CONTACT_METHOD = [
		('viber', 'Viber'), ('whatsapp', 'Whatsapp'), ('telegram', 'Telegram')
	]

	order_number = models.IntegerField(blank=True, null=True)
	user = models.CharField(max_length=50)
	name = models.CharField(max_length=70, null=True)
	phone_number = models.CharField(max_length=15)
	email = models.EmailField(blank=True, null=True)
	payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE, default='bank_card')
	shipping_type = models.CharField(max_length=15, choices=SHIPPING_TYPE)
	shipping_address = models.CharField(max_length=200, null=True, blank=True)
	contact_method = models.CharField(max_length=15, choices=CONTACT_METHOD, null=True, blank=True)
	comment = models.CharField(max_length=255, null=True, blank=True)
	total_cost = models.IntegerField(default=0)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	status = models.CharField(max_length=20, choices=ORDER_STATUS, default='ordered')

	class Meta:
		ordering = ('-created',)
		verbose_name = 'Замовлення'
		verbose_name_plural = 'Замовлення'

	def __str__(self):
		return str(self.created)


class QuickOrder(models.Model):
	ORDER_STATUS = [
		('ordered', 'Нове замовлення'), ('shipped', 'Доставлено'), ('refusal', 'Відмова')
	]

	order_number = models.IntegerField(blank=True, null=True)
	name = models.CharField(max_length=50, null=True, blank=True)
	phone_number = models.CharField(max_length=15)
	total_cost = models.IntegerField(default=0)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	type = models.CharField(max_length=25, blank=True, null=True)
	status = models.CharField(max_length=20, choices=ORDER_STATUS, default='ordered')

	class Meta:
		ordering = ('-created',)
		verbose_name = 'Швидке замовлення і зворотній дзвінок'
		verbose_name_plural = 'Швидкі замовлення і зворотні дзвінки'

	def __str__(self):
		return str(self.type)

class OrderItem(models.Model):
	order = models.ForeignKey(Order, related_name='items', null=True, blank=True, on_delete=models.CASCADE)
	quick_order = models.ForeignKey(QuickOrder, related_name='items', null=True, blank=True, on_delete=models.CASCADE)
	product = models.ForeignKey(ChargersItems, related_name='order_items', on_delete=models.CASCADE)
	price = models.IntegerField()
	quantity = models.IntegerField(default=1)