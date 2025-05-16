from django.contrib import admin
from .models import Order, OrderItem, QuickOrder

class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 0

class OrderAdmin(admin.ModelAdmin):
	model = Order
	inlines = [
		OrderItemInline
	]
	search_fields = ['order_number']

admin.site.register(Order, OrderAdmin)

class QuickOrderInline(admin.TabularInline):
	model = OrderItem
	extra = 0

class QuickOrderAdmin(admin.ModelAdmin):
	model = QuickOrder
	inlines = [
		QuickOrderInline
	]
admin.site.register(QuickOrder, QuickOrderAdmin)