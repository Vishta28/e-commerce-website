from django import forms
from store.models import ChargersItems
from django.db.models import Q

# class ConstructorOptionsForm(forms.Form):
#
# 	topping_choices = forms.ModelMultipleChoiceField(
# 		widget=forms.Select(attrs={'class': 'your-css-class'}),
# 		# queryset=ChargersItems.objects.filter(Q(model__slug=item_model) & Q(category__slug=item_category)).values('type').distinct(),
# 		required=False
# 	)
