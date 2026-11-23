from decimal import Decimal

from django.db.models import ProtectedError, Q
from django.shortcuts import render, get_object_or_404
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView


from apps.pedidos.models import Carrinho, ItemCarrinho, Pedido, ItemPedido, HistoricoStatus
from apps.entregas.models import Entrega
from apps.usuarios.models import Usuario, Endereco
from apps.produtos.models import Categoria, Produto
from .permissions import IsStaffOrReadOnly
from .throttles import LoginRateThrottle, CadastroRateThrottle
from .serializers import (
    UsuarioSerializer, UsuarioCadastroSerializer, EnderecoSerializer,
    CategoriaSerializer, ProdutoSerializer, ItemCarrinhoSerializer, 
    PedidoSerializer, EntregaSerializer,
)


# Usuários
class LoginView(TokenObtainPairView):
    # Limita tentativas de login por IP (429 ao exceder)
    throttle_classes = [LoginRateThrottle]


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([CadastroRateThrottle])
def cadastro(request):
    serializer = UsuarioCadastroSerializer(data=request.data)
    if serializer.is_valid():
        usuario = serializer.save()
        refresh = RefreshToken.for_user(usuario)
        return Response({
            'usuario': UsuarioSerializer(usuario).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def eu(request):
    if request.method == 'GET':
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)

    serializer = UsuarioSerializer(
        request.user,
        data=request.data,
        partial=(request.method == 'PATCH')
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Endereços
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def enderecos(request):
    if request.method == 'GET':
        serializer = EnderecoSerializer(request.user.enderecos.all(), many=True)
        return Response(serializer.data)

    serializer = EnderecoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(usuario=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def endereco_atualizar(request, id):
    # Filtra pelo dono: o endereço de outro usuário responde 404
    endereco = get_object_or_404(Endereco, id=id, usuario=request.user)
    serializer = EnderecoSerializer(
        endereco,
        data=request.data,
        partial=(request.method == 'PATCH')
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def endereco_deletar(request, id):
    endereco = get_object_or_404(Endereco, id=id, usuario=request.user)
    try:
        endereco.delete()
    except ProtectedError:
        return Response(
            {'detail': 'Este endereço não pode ser excluído porque está vinculado a um ou mais pedidos.'},
            status=status.HTTP_409_CONFLICT
        )
    return Response(status=status.HTTP_204_NO_CONTENT)


# Categorias (leitura pública; escrita só is_staff)
@api_view(['GET', 'POST'])
@permission_classes([IsStaffOrReadOnly])
def categorias(request):
    if request.method == 'GET':
        serializer = CategoriaSerializer(Categoria.objects.order_by('nome'), many=True)
        return Response(serializer.data)

    serializer = CategoriaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsStaffOrReadOnly])
def categoria_atualizar(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    serializer = CategoriaSerializer(
        categoria,
        data=request.data,
        partial=(request.method == 'PATCH')
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsStaffOrReadOnly])
def categoria_deletar(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    try:
        categoria.delete()
    except ProtectedError:
        return Response(
            {'detail': 'Não é possível excluir esta categoria porque existem produtos vinculados a ela.'},
            status=status.HTTP_409_CONFLICT
        )
    return Response(status=status.HTTP_204_NO_CONTENT)


# Produtos (leitura pública; escrita só is_staff)
@api_view(['GET', 'POST'])
@permission_classes([IsStaffOrReadOnly])
def produtos(request):
    if request.method == 'GET':
        lista = Produto.objects.select_related('categoria').order_by('nome')

        # Mesmos filtros do site: ?buscar=texto&categoria=id
        busca = request.query_params.get('buscar', '').strip()
        categoria_id = request.query_params.get('categoria', '').strip()

        if busca:
            lista = lista.filter(Q(nome__icontains=busca) | Q(descricao__icontains=busca))
        if categoria_id.isdigit():
            lista = lista.filter(categoria_id=categoria_id)

        serializer = ProdutoSerializer(lista, many=True, context={'request': request})
        return Response(serializer.data)

    # Cadastro com imagem: enviar como multipart/form-data
    serializer = ProdutoSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsStaffOrReadOnly])
def produto_detalhes(request, id):
    produto = get_object_or_404(Produto, id=id)
    serializer = ProdutoSerializer(produto, context={'request': request})
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsStaffOrReadOnly])
def produto_atualizar(request, id):
    produto = get_object_or_404(Produto, id=id)
    # PUT exige todos os campos (inclusive a imagem); use PATCH para mudar só alguns
    serializer = ProdutoSerializer(
        produto,
        data=request.data,
        partial=(request.method == 'PATCH'),
        context={'request': request}
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsStaffOrReadOnly])
def produto_deletar(request, id):
    produto = get_object_or_404(Produto, id=id)
    try:
        produto.delete()
    except ProtectedError:
        return Response(
            {'detail': 'Este produto não pode ser excluído porque faz parte de um ou mais pedidos.'},
            status=status.HTTP_409_CONFLICT
        )
    return Response(status=status.HTTP_204_NO_CONTENT)


# Carrinho (sempre do usuário logado)
def montar_carrinho(request):
    """Monta a resposta padrão do carrinho: itens, total e quantidade de itens."""
    carrinho, criado = Carrinho.objects.get_or_create(usuario=request.user)
    itens = list(
        ItemCarrinho.objects
        .filter(carrinho=carrinho)
        .select_related('produto__categoria')
        .order_by('id')
    )
    total = sum((item.subtotal for item in itens), Decimal('0.00'))

    return {
        'itens': ItemCarrinhoSerializer(itens, many=True, context={'request': request}).data,
        'total': f'{total:.2f}',
        'quantidade_itens': len(itens),
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def carrinho(request):
    return Response(montar_carrinho(request))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def carrinho_adicionar(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)

    if not produto.disponivel:
        return Response(
            {'detail': 'Este produto está indisponível no momento.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    carrinho, criado = Carrinho.objects.get_or_create(usuario=request.user)
    item, criado = ItemCarrinho.objects.get_or_create(carrinho=carrinho, produto=produto)

    # Igual ao site: se o produto já está no carrinho, soma 1
    if not criado:
        item.quantidade += 1
        item.save()

    return Response(
        montar_carrinho(request),
        status=status.HTTP_201_CREATED if criado else status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def carrinho_aumentar(request, item_id):
    item = get_object_or_404(ItemCarrinho, id=item_id, carrinho__usuario=request.user)

    if not item.produto.disponivel:
        return Response(
            {'detail': 'Este produto está indisponível no momento.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    item.quantidade += 1
    item.save()
    return Response(montar_carrinho(request))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def carrinho_diminuir(request, item_id):
    item = get_object_or_404(ItemCarrinho, id=item_id, carrinho__usuario=request.user)

    # Igual ao site: com quantidade 1, diminuir remove o item
    if item.quantidade > 1:
        item.quantidade -= 1
        item.save()
    else:
        item.delete()

    return Response(montar_carrinho(request))


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def carrinho_remover(request, item_id):
    item = get_object_or_404(ItemCarrinho, id=item_id, carrinho__usuario=request.user)
    item.delete()
    return Response(montar_carrinho(request))


# Pedidos
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def pedidos(request):

    # Listar pedidos do usuário autenticado
    if request.method == 'GET':
        lista = Pedido.objects.filter(
            usuario=request.user
        ).select_related(
            'endereco', 'entregador'
        ).prefetch_related(
            'itens__produto',
            'historico__alterado_por'
        ).order_by('-criado_em')

        serializer = PedidoSerializer(
            lista,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    # Criar pedido a partir do carrinho
    carrinho, criado = Carrinho.objects.get_or_create(
        usuario=request.user
    )

    itens = list(
        ItemCarrinho.objects.filter(
            carrinho=carrinho
        ).select_related('produto')
    )

    if not itens:
        return Response(
            {'detail': 'Seu carrinho está vazio.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    indisponiveis = [
        item.produto.nome
        for item in itens
        if not item.produto.disponivel
    ]

    if indisponiveis:
        return Response(
            {
                'detail': 'Remova do carrinho os produtos indisponíveis.',
                'produtos': indisponiveis
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    endereco_id = request.data.get('endereco')

    if not endereco_id:
        return Response(
            {'detail': 'Informe o endereço de entrega.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    endereco = get_object_or_404(
        Endereco,
        id=endereco_id,
        usuario=request.user
    )

    taxas_entrega = {
        'Canguaretama': Decimal('5.00'),
        'Barra do Cunhaú': Decimal('7.00'),
        'Goianinha': Decimal('8.00'),
        'Natal': Decimal('15.00'),
    }

    taxa_entrega = taxas_entrega.get(endereco.cidade)

    if taxa_entrega is None:
        return Response(
            {'detail': 'Não realizamos entregas para esta cidade.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    subtotal = sum(
        (item.subtotal for item in itens),
        Decimal('0.00')
    )

    total = subtotal + taxa_entrega

    with transaction.atomic():
        pedido = Pedido.objects.create(
            usuario=request.user,
            endereco=endereco,
            taxa_entrega=taxa_entrega,
            valor_total=total,
        )

        Entrega.objects.create(pedido=pedido)

        for item in itens:
            ItemPedido.objects.create(
                pedido=pedido,
                produto=item.produto,
                quantidade=item.quantidade,
                preco_unitario=item.produto.preco,
            )

        HistoricoStatus.objects.create(
            pedido=pedido,
            status='Pendente',
            alterado_por=request.user
        )

        ItemCarrinho.objects.filter(
            carrinho=carrinho
        ).delete()

    serializer = PedidoSerializer(
        pedido,
        context={'request': request}
    )

    return Response(
        serializer.data,
        status=status.HTTP_201_CREATED
    )


# Entregas

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def entregas(request):
    if not request.user.is_entregador:
        return Response(
            {'detail': 'Apenas entregadores podem acessar esta área.'},
            status=status.HTTP_403_FORBIDDEN
        )

    disponiveis = Entrega.objects.filter(
        pedido__status='Pronto para entrega',
        pedido__entregador__isnull=True
    ).select_related(
        'pedido', 'pedido__usuario', 'pedido__endereco'
    ).prefetch_related(
        'pedido__itens__produto',
        'pedido__historico'
    )

    minhas = Entrega.objects.filter(
        pedido__entregador=request.user
    ).select_related(
        'pedido', 'pedido__usuario', 'pedido__endereco'
    ).prefetch_related(
        'pedido__itens__produto',
        'pedido__historico'
    )

    serializer = EntregaSerializer(
        list(disponiveis) + list(minhas),
        many=True,
        context={'request': request}
    )

    return Response(serializer.data)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def aceitar_entrega(request, pedido_id):
    if not request.user.is_entregador:
        return Response(
            {'detail': 'Apenas entregadores podem aceitar entregas.'},
            status=status.HTTP_403_FORBIDDEN
        )

    with transaction.atomic():
        atualizados = Pedido.objects.filter(
            id=pedido_id,
            status='Pronto para entrega',
            entregador__isnull=True
        ).update(
            entregador=request.user,
            status='Saiu para entrega'
        )

        if not atualizados:
            pedido = Pedido.objects.filter(id=pedido_id).first()

            if not pedido:
                return Response(
                    {'detail': 'Pedido não encontrado.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            if (
                pedido.status == 'Saiu para entrega'
                and pedido.entregador_id == request.user.pk
            ):
                entrega, _ = Entrega.objects.get_or_create(
                    pedido=pedido
                )

                if not entrega.data_saida:
                    entrega.iniciar_entrega()

                serializer = EntregaSerializer(
                    entrega,
                    context={'request': request}
                )
                return Response(serializer.data)

            if pedido.entregador_id is not None:
                return Response(
                    {'detail': 'Este pedido já foi aceito por outro entregador.'},
                    status=status.HTTP_409_CONFLICT
                )

            return Response(
                {'detail': f'Pedido indisponível. Status atual: {pedido.status}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        pedido = Pedido.objects.get(id=pedido_id)

        HistoricoStatus.objects.create(
            pedido=pedido,
            status='Saiu para entrega',
            alterado_por=request.user
        )

        entrega, _ = Entrega.objects.get_or_create(
            pedido=pedido
        )

        if not entrega.data_saida:
            entrega.iniciar_entrega()

    serializer = EntregaSerializer(
        entrega,
        context={'request': request}
    )

    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def concluir_entrega(request, pedido_id):
    if not request.user.is_entregador:
        return Response(
            {'detail': 'Apenas entregadores podem concluir entregas.'},
            status=status.HTTP_403_FORBIDDEN
        )

    with transaction.atomic():
        pedido = Pedido.objects.filter(id=pedido_id).first()

        if not pedido:
            return Response(
                {'detail': 'Pedido não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if pedido.entregador_id != request.user.pk:
            return Response(
                {'detail': 'Este pedido não está atribuído a você.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if pedido.status == 'Entregue':
            entrega = Entrega.objects.filter(pedido=pedido).first()

            if entrega:
                serializer = EntregaSerializer(
                    entrega,
                    context={'request': request}
                )
                return Response(serializer.data)

            return Response(
                {'detail': 'Pedido entregue, mas o registro da entrega não foi encontrado.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if pedido.status != 'Saiu para entrega':
            return Response(
                {'detail': f'Não é possível concluir. Status atual: {pedido.status}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        pedido.mudar_status('Entregue', request.user)

        if not pedido.pago:
            pedido.marcar_como_pago()

        entrega, _ = Entrega.objects.get_or_create(
            pedido=pedido
        )

        if not entrega.data_conclusao:
            entrega.concluir_entrega()

    serializer = EntregaSerializer(
        entrega,
        context={'request': request}
    )

    return Response(serializer.data, status=status.HTTP_200_OK)
