from django import forms
from .models import Cupom


class CupomForm(forms.ModelForm):
    class Meta:
        model = Cupom
        fields = [
            'codigo', 'descricao', 'tipo', 'valor', 'valor_minimo',
            'valido_ate', 'limite_uso', 'uso_unico_por_cliente', 'ativo',
        ]
        widgets = {
            'valido_ate': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'
            ),
            'valor': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'valor_minimo': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['valido_ate'].input_formats = ['%Y-%m-%dT%H:%M']

    def clean_codigo(self):
        codigo = self.cleaned_data['codigo'].strip().upper()
        if ' ' in codigo:
            raise forms.ValidationError('O código não pode ter espaços.')
        return codigo