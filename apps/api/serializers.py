from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.pedidos.models import ItemCarrinho, Pedido, ItemPedido, HistoricoStatus
from apps.entregas.models import Entrega
from apps.produtos.models import Categoria, Produto
from apps.usuarios.models import Usuario, Endereco


# Usuários
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['cpf', 'email', 'first_name', 'last_name', 'nascimento', 'is_entregador', 'is_staff']
        # O e-mail é o username (como no site), então não pode ser trocado por aqui
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
        # Igual ao cadastro do site: o e-mail é o username
        return Usuario.objects.create_user(username=dados['email'], **dados)


# Endereços
class EnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = ['id', 'rua', 'numero', 'cidade', 'estado']

    def validate_estado(self, valor):
        valor = valor.strip().upper()
        if len(valor) != 2 or not valor.isalpha():
            raise serializers.ValidationError('Informe a sigla do estado com 2 letras (ex.: RN).')
        return valor


# Produtos
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome']


class ProdutoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    # default=True explícito: em multipart, um booleano ausente seria lido como False
    disponivel = serializers.BooleanField(default=True)

    class Meta:
        model = Produto
        fields = [
            'id', 'nome', 'descricao', 'preco', 'categoria', 'categoria_nome',
            'imagem', 'disponivel',
        ]

    def validate_preco(self, valor):
        if valor <= 0:
            raise serializers.ValidationError('O preço deve ser maior que zero.')
        return valor


# Carrinho
class ItemCarrinhoSerializer(serializers.ModelSerializer):
    produto = ProdutoSerializer(read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = ItemCarrinho
        fields = ['id', 'produto', 'quantidade', 'subtotal']


# Pedidos

class ItemPedidoSerializer(serializers.ModelSerializer):
    produto = ProdutoSerializer(read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = ItemPedido
        fields = [
            'id',
            'produto',
            'quantidade',
            'preco_unitario',
            'subtotal',
        ]


class HistoricoStatusSerializer(serializers.ModelSerializer):
    alterado_por = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = HistoricoStatus
        fields = [
            'id',
            'status',
            'alterado_por',
            'criado_em',
        ]


class PedidoSerializer(serializers.ModelSerializer):
    endereco = EnderecoSerializer(read_only=True)
    itens = ItemPedidoSerializer(many=True, read_only=True)
    historico = HistoricoStatusSerializer(many=True, read_only=True)
    entregador = serializers.StringRelatedField(read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Pedido
        fields = [
            'id',
            'endereco',
            'itens',
            'historico',
            'entregador',
            'subtotal',
            'taxa_entrega',
            'valor_total',
            'status',
            'forma_pagamento',
            'pago',
            'pago_em',
            'troco_para',
            'criado_em',
        ]


class EntregaSerializer(serializers.ModelSerializer):
    pedido = PedidoSerializer(read_only=True)

    class Meta:
        model = Entrega
        fields = [
            'id',
            'pedido',
            'data_saida',
            'data_conclusao',
            'observacoes',
            'criado_em',
        ]
        read_only_fields = [
            'id',
            'pedido',
            'data_saida',
            'data_conclusao',
            'criado_em',
        ]
