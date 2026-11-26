from .models import Favorito


def ids_favoritos(usuario):
    """Ids dos produtos favoritados (vazio se a pessoa não estiver logada)."""
    if not usuario.is_authenticated:
        return set()
    return set(
        Favorito.objects.filter(usuario=usuario).values_list('produto_id', flat=True)
    )