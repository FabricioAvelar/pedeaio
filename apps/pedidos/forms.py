from django import forms
from .models import Pedido


class PagamentoForm(forms.ModelForm):
    forma_pagamento = forms.ChoiceField(
        choices=Pedido.FORMA_PAGAMENTO_CHOICES,
        widget=forms.RadioSelect,
        label='Forma de pagamento',
    )

    class Meta:
        model = Pedido
        fields = ['forma_pagamento', 'troco_para']
        labels = {'troco_para': 'Troco para quanto?'}
        widgets = {
            'troco_para': forms.NumberInput(attrs={
                'step': '0.01', 'min': '0', 'placeholder': 'Ex.: 50.00',
            }),
        }