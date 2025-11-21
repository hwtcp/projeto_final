from django.urls import path
from .views import (
    ConsultaListView,
    ConsultaCreateView,
    ConsultaUpdateView,
    ConsultaDeleteView,
    AvisoListView,
    AvisoCreateView,
    AvisoUpdateView,
    AvisoDeleteView,
)

urlpatterns = [
    path("consultas/", ConsultaListView.as_view(), name="listar_consultas"),
    path("consultas/novo/", ConsultaCreateView.as_view(), name="criar_consulta"),
    path("consultas/<int:pk>/editar/", ConsultaUpdateView.as_view(), name="editar_consulta"),
    path("consultas/<int:pk>/deletar/", ConsultaDeleteView.as_view(), name="deletar_consulta"),
    path("avisos/", AvisoListView.as_view(), name="listar_avisos"),
    path("avisos/novo/", AvisoCreateView.as_view(), name="criar_aviso"),
    path("avisos/<int:pk>/editar/", AvisoUpdateView.as_view(), name="editar_aviso"),
    path("avisos/<int:pk>/deletar/", AvisoDeleteView.as_view(), name="deletar_aviso"),
]
