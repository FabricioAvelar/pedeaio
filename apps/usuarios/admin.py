from django.contrib import admin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'is_staff', 'is_entregador')
    list_filter = ('is_staff', 'is_entregador')
    search_fields = ('email', 'first_name')
    list_editable = ('is_entregador',)