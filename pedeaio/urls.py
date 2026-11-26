"""
URL configuration for pedeaio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from decouple import config

urlpatterns = [
    path(config('ADMIN_URL', default='admin/'), admin.site.urls),

    path('', include('apps.core.urls')),
    path('produtos/', include('apps.produtos.urls')),
    path('usuarios/', include('apps.usuarios.urls')),
    path('pedidos/', include('apps.pedidos.urls')),
    path('sig/', include('apps.sig.urls')),
    path('sad/', include('apps.sad.urls')),
    path('painel/', include('apps.painel.urls')),
    path('entregas/', include('apps.entregas.urls')),
    path('api/v1/', include('apps.api.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('favoritos/', include('apps.favoritos.urls')),
    path('cupons/', include('apps.cupons.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)