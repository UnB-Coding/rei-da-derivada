"""
URL configuration for api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Rei e Rainha da Derivada - API",
        default_version='v1',
        description="""API para o projeto Aplicação Mobile para apoio ao Rei e Rainha da Derivada

        Grupos de usuários e permissões:
            - Event_Admin: Permissão para Alterar, Deletar e Visualizar Eventos e todas as permissões de Sumula, Player_Score e player.
            - Staff_Manager: Permissão para Visualizar Eventos e todas as permissões de Sumula, Player_Score e player, exceto deletar player.
            - Staff_Member: Permissão para Visualizar Eventos, Alterar e Visualizar Sumulas, Alterar e Visualizar Player_Score e player.
            - Player: Permissão para Visualizar Eventos, Visualizar Player_Score e player.
        """,
        contact=openapi.Contact(email="reidaderivada2024@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Views
    path('users/', include('users.urls')),
    path('api/', include('api.urls')),
    # swagger
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),
]
