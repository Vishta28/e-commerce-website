from django import forms
from django.urls import reverse_lazy

from .models import Order


class OrderForm(forms.ModelForm):
	class Meta:
		model = Order

		fields = ('name', 'phone_number', 'email', 'payment_type', 'shipping_type', 'shipping_address', 'comment')

		labels = {
			'name': "Ім'я/Прізвище",
			'phone_number': "Номер телефону",
			'email': "Email (*не обов'язково)",
			'payment_type': "Спосіб оплати",
			'shipping_type': "Спосіб доставки",
			'shipping_address': "",
			'comment': "",
		}

		widgets = {
			'name': forms.TextInput(attrs={'class': 'form-control rounded-0 fw-light', 'placeholder': "Ім'я/Призвіще"}),
			'phone_number': forms.TextInput(attrs={'id': 'phone_number', 'class': 'form-control form-floating rounded-0 fw-light', 'placeholder': "+380",
												'hx-get': reverse_lazy('check_order_phone_number'),
												'hx-trigger': 'keyup changed delay:0.5s',
												'hx-target': '#bottom_line',
												'hx-swap': 'innerHTML transition:true'
		}),
			'email': forms.EmailInput(attrs={'class': 'form-control rounded-0 fw-light', 'placeholder': "Email (*не обов'язково)"}),
			'payment_type': forms.Select(attrs={'class': 'order-form form-select rounded-0 fw-light'}),
			'shipping_type': forms.Select(attrs={'class': 'order-form form-select rounded-0 fw-light',
													'hx-get': reverse_lazy('check_shipping_type'),
													'hx-trigger': 'change',
													'hx-target': '#message_shipping',
													'hx-swap': 'innerHTML transition:true'}),
			'shipping_address': forms.Select(attrs={'class': 'd-none order-form form-select rounded-0 fw-light'}),
			'comment': forms.Textarea(attrs={'class': 'd-none form-control rounded-0 fw-light', 'rows': 5, 'placeholder': "Напишіть додаткове питання або коментар"})
		}


# widgets = {
# 			'name': forms.TextInput(attrs={'class': 'form-control rounded-0', 'placeholder': "Ім'я/Призвіще",
# 										'hx-get': reverse_lazy('check_order_name'),
# 										'hx-trigger': 'keyup changed',
# 										'hx-target': '#message',
# 										'hx-swap': 'innerHTML'}),

