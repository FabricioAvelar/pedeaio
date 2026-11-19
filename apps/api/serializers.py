from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.usuarios.models import Usuario

# Usuários
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['cpf', 'email', 'first_name', 'last_name', 'nascimento', 'is_entregador', 'is_staff']
        read_only_fields = ['cpf', 'email', 'is_entregador', 'is_staff']


class UsuarioCadastroSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=Usuario.objects.all(),
            message='Já existe um usuário com este e-mail.'
        )]
    )
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ['cpf', 'first_name', 'last_name', 'email', 'nascimento', 'password', 'password2']
        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
        }

    def validate_cpf(self, valor):
        if not valor.isdigit() or len(valor) != 11:
            raise serializers.ValidationError('Informe o CPF com 11 números, sem pontos e traço.')
        return valor

    def validate(self, dados):
        if dados['password'] != dados['password2']:
            raise serializers.ValidationError({'password2': 'As senhas não conferem.'})
        validate_password(dados['password'])
        return dados

    def create(self, dados):
        dados.pop('password2')
        return Usuario.objects.create_user(username=dados['email'], **dados)