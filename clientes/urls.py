from django.urls import path

from .views import mi_perfil

urlpatterns = [
    path("mi-perfil/", mi_perfil, name="mi_perfil"),
]

