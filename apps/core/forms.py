from django import forms
from apps.usuarios.models import Usuario
from django.contrib.auth.forms import UserCreationForm

class CadastroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = [
            'first_name',
            'last_name',
            'email',
            'cpf',
            'nascimento'
        ]