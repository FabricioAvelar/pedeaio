from django import forms
from django.forms import ModelForm
from .models import Produto, Categoria

class ProdutoForm(ModelForm):
    class Meta:
        model = Produto
        fields = '__all__'

class CategoriaForm(ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']