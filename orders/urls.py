from django.urls import path
from . import views
from orders.views import add_to_cart, header_menu_cart, update_cart, \
	cart_total, cart_items_total, CartAccessoriesView, ConfirmOrderQuickView, loader, check_quick_order, \
	ConfirmOrderStep2View, ConfirmOrderFinalView, check_shipping_type, check_comment, check_order_phone_number

urlpatterns = [
	path('cart', views.CartView.as_view(), name='cart'),
	path('add_to_cart/<slug:slug>/<str:id>/', add_to_cart, name='add_to_cart'),
	path('header_menu_cart', header_menu_cart, name='header_menu_cart'),
	path('update_cart/<slug:slug>/<str:action>/', update_cart, name='update_cart'),
	path('cart_total/', cart_total, name='cart_total'),
	path('cart_items_total/', cart_items_total, name='cart_items_total'),
	path('orders/order_step2/', ConfirmOrderStep2View.as_view(), name='order_step2'),
	path('orders/order_quick/<slug:slug>/', views.OrderQuickView.as_view(), name='order_quick'),
	path('orders/order_model_quick/<str:category>/<slug:slug>/', views.OrderModelQuickView.as_view(), name='order_model_quick'),
	path('orders/order_step1/', views.ConfirmOrderStep1View.as_view(), name='order_step1'),
	path('orders/order_confirm/', ConfirmOrderFinalView.as_view(), name='order_confirm'),
	path('orders/order_quick_confirm/', views.ConfirmOrderQuickView.as_view(), name='order_quick_confirm'),
	path('orders/partials/check_order_phone_number/', check_order_phone_number, name='check_order_phone_number'),
	path('orders/loader', loader, name='loader'),
	path('orders/check_quick_order/', check_quick_order, name='check_quick_order'),
	path('orders/partials/check_shipping_type/', check_shipping_type, name='check_shipping_type'),
	path('orders/partials/comment/', check_comment, name='check_comment'),
	path('orders/cart_accessories/<str:model>/<slug:slug>/', views.CartAccessoriesView.as_view(), name='cart_accessories'),
]