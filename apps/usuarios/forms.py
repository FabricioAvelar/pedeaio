from django import forms
from django.forms import ModelForm
from .models import Usuario, Endereco


class UsuarioForm(ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'


class UsuarioEditarForm(ModelForm):

    nascimento = forms.DateField(
        required=False,
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date'
            }
        )
    )

    class Meta:
        model = Usuario

        fields = [
            'first_name',
            'last_name',
            'email',
            'nascimento',
        ]

        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail',
            'nascimento': 'Data de nascimento',
        }

        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'placeholder': 'Digite seu nome'
                }
            ),

            'last_name': forms.TextInput(
                attrs={
                    'placeholder': 'Digite seu sobrenome'
                }
            ),

            'email': forms.EmailInput(
                attrs={
                    'placeholder': 'Digite seu e-mail'
                }
            ),

            'nascimento': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date'
                }
            ),
        }


class EnderecoForm(ModelForm):
    class Meta:
        model = Endereco

        fields = [
            'rua',
            'numero',
            'cidade',
            'estado',
        ]