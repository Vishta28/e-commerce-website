from django import forms

from store.models import ChargersItems


class ChargersItemsFilterForm(forms.Form):
	power_choices = [(1, '1'), (2, '2'), (3, '3')]
	type_choices = [('type1', 'Type 1'), ('type2', 'Type 2')]
	cable_length_choices = [(3, '3 метри'), (5, '5 метрів')]

	power = forms.ChoiceField(label='Потужність, кВт', choices=power_choices)
	type = forms.ChoiceField(label='Тип роз\'єму', choices=type_choices, required=False)
	cable_length = forms.ChoiceField(label='Довжина кабелю', choices=cable_length_choices)