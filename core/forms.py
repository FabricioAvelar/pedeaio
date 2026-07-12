from django.forms import ModelForm
from .models import (Usuario, Endereco, Favorito, Cupom, Produto)
from django.contrib.auth.forms import UserCreationForm

class UsuarioForm(ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'

class EnderecoForm(ModelForm):
    class Meta:
        model = Endereco
        fields = '__all__'

class FavoritoForm(ModelForm):
    class Meta:
        model = Favorito
        fields = '__all__'

class CupomForm(ModelForm):
    class Meta:
        model = Cupom
        fields = '__all__'

class ProdutoForm(ModelForm):
    class Meta:
        model = Produto
        fields = '__all__'

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