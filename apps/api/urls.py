from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from .views import *

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='api_token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='api_token_blacklist'),

    # Usuários
    path('cadastro/', cadastro, name='api_cadastro'),
    path('eu/', eu, name='api_eu'),
]