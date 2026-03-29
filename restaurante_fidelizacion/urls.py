from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path
from django.views.static import serve

from clientes.forms import LoginUsuarioForm
from clientes.views import registro_usuario

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("carta.urls")),
    path("pedidos/", include("pedidos.urls")),
    path("clientes/", include("clientes.urls")),
    path('registro/', registro_usuario, name='registro_publico'),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="login.html",
            authentication_form=LoginUsuarioForm,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]

if str(settings.MEDIA_URL).startswith('/'):
    media_prefix = settings.MEDIA_URL.lstrip('/')
    urlpatterns += [
        re_path(rf'^{media_prefix}(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})
    ]


    
