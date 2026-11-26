from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from apps.produtos.models import Produto
from .models import Favorito


@login_required
def meus_favoritos(request):
    favoritos = (
        Favorito.objects
        .filter(usuario=request.user)
        .select_related('produto', 'produto__categoria')
    )
    return render(request, 'privado/meus_favoritos.html', {'favoritos': favoritos})


@login_required
@require_POST
def alternar_favorito(request, produto_id):
    """Favorita se ainda não é favorito; desfavorita se já é."""
    produto = get_object_or_404(Produto, id=produto_id)

    favorito, criado = Favorito.objects.get_or_create(
        usuario=request.user, produto=produto
    )

    if criado:
        messages.success(request, f'"{produto.nome}" foi para os seus favoritos.')
    else:
        favorito.delete()
        messages.info(request, f'"{produto.nome}" saiu dos seus favoritos.')

    # volta para a página de onde a pessoa veio (só se for do próprio site)
    destino = request.POST.get('next', '')
    if not url_has_allowed_host_and_scheme(destino, allowed_hosts={request.get_host()}):
        destino = 'produtos'
    return redirect(destino)