from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.pedidos.models import Carrinho, ItemCarrinho
from .forms import CupomForm
from .models import Cupom
from .services import SESSION_KEY, CupomInvalido, validar_cupom


def _subtotal_do_carrinho(usuario):
    carrinho, _ = Carrinho.objects.get_or_create(usuario=usuario)
    itens = ItemCarrinho.objects.filter(carrinho=carrinho).select_related('produto')
    return sum(item.subtotal for item in itens)


# ------------------------------------------------------------ CLIENTE

@login_required
def meus_cupons(request):
    """Cupons que a pessoa pode usar agora."""
    agora = timezone.now()

    candidatos = Cupom.objects.filter(ativo=True).filter(
        Q(valido_ate__isnull=True) | Q(valido_ate__gte=agora)
    )

    disponiveis = []
    for cupom in candidatos:
        if cupom.limite_uso is not None and cupom.usos >= cupom.limite_uso:
            continue
        if cupom.uso_unico_por_cliente and cupom.pedidos.filter(
            usuario=request.user
        ).exclude(status='Cancelado').exists():
            continue
        disponiveis.append(cupom)

    return render(request, 'privado/meus_cupons.html', {
        'cupons': disponiveis,
        'aplicado': request.session.get(SESSION_KEY),
    })


@login_required
@require_POST
def aplicar_cupom(request):
    codigo = request.POST.get('codigo', '').strip().upper()
    subtotal = _subtotal_do_carrinho(request.user)

    if subtotal <= 0:
        messages.error(request, 'Adicione produtos ao carrinho antes de usar um cupom.')
        return redirect('carrinhocompras')

    try:
        cupom, desconto = validar_cupom(codigo, request.user, subtotal)
    except CupomInvalido as erro:
        messages.error(request, str(erro))
    else:
        request.session[SESSION_KEY] = cupom.codigo
        messages.success(request, f'Cupom {cupom.codigo} aplicado: -R$ {desconto}.')

    return redirect('carrinhocompras')


@login_required
@require_POST
def remover_cupom(request):
    request.session.pop(SESSION_KEY, None)
    messages.info(request, 'Cupom removido.')
    return redirect('carrinhocompras')


# ------------------------------------------------------ ADMINISTRADOR

@staff_member_required(login_url='login')
def cupom_gerenciar(request):
    if request.method == 'POST':
        form = CupomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cupom cadastrado.')
            return redirect('cupom_gerenciar')
    else:
        form = CupomForm()

    return render(request, 'privado/cupom_gerenciar.html', {
        'form': form,
        'cupons': Cupom.objects.all(),
    })


@staff_member_required(login_url='login')
def cupom_editar(request, id):
    cupom = get_object_or_404(Cupom, id=id)

    if request.method == 'POST':
        form = CupomForm(request.POST, instance=cupom)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cupom atualizado.')
            return redirect('cupom_gerenciar')
    else:
        form = CupomForm(instance=cupom)

    return render(request, 'privado/cupom_gerenciar.html', {
        'form': form,
        'cupom': cupom,
        'cupons': Cupom.objects.all(),
    })


@staff_member_required(login_url='login')
@require_POST
def cupom_alternar(request, id):
    cupom = get_object_or_404(Cupom, id=id)
    cupom.ativo = not cupom.ativo
    cupom.save(update_fields=['ativo'])
    return redirect('cupom_gerenciar')


@staff_member_required(login_url='login')
@require_POST
def cupom_remover(request, id):
    cupom = get_object_or_404(Cupom, id=id)

    try:
        cupom.delete()
        messages.success(request, 'Cupom excluído.')
    except ProtectedError:
        messages.error(
            request,
            'Este cupom já foi usado em pedidos e não pode ser excluído. '
            'Desative-o em vez disso.'
        )

    return redirect('cupom_gerenciar')