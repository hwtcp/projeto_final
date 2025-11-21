from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from .views import (
    index,
    home,
    login_usuario,
    logout_usuario,
    cadastro_medico,
    cadastro_atendente,
    cadastro_paciente,
    auto_cadastro_paciente,
    perfil,
    remover_foto,
    MedicoListView,
    MedicoDeleteView,
    AtendenteListView,
    AtendenteDeleteView,
    PacienteListView,
    PacienteDeleteView,
    DetalhesUsuarioView,
    EditarUsuarioView,
)

urlpatterns = [
    # Páginas principais
    path("", index, name="index"),
    path("home/", home, name="home"),
    # Autenticação
    path("login/", login_usuario, name="login"),
    path("logout/", logout_usuario, name="logout"),
    path("cadastro_interno/paciente/", cadastro_paciente, name="cadastro_paciente"),
    path("cadastro/", auto_cadastro_paciente, name="auto_cadastro_paciente"),
    # CRUD de Médicos
    path("medicos/", MedicoListView.as_view(), name="listar_medicos"),
    path("medicos/novo/", cadastro_medico, name="criar_medico"),
    path("medicos/<int:pk>/deletar/", MedicoDeleteView.as_view(), name="deletar_medico"),
    # CRUD de Atendentes
    path("atendentes/", AtendenteListView.as_view(), name="listar_atendentes"),
    path("atendentes/novo/", cadastro_atendente, name="criar_atendente"),
    path("atendentes/<int:pk>/deletar/", AtendenteDeleteView.as_view(), name="deletar_atendente"),
    # CRUD de Pacientes
    path("pacientes/", PacienteListView.as_view(), name="listar_pacientes"),
    path("pacientes/novo/", cadastro_paciente, name="criar_paciente"),
    path("pacientes/<int:pk>/deletar/", PacienteDeleteView.as_view(), name="deletar_paciente"),
    path("perfil/", perfil, name="perfil"),
    path("perfil/remover-foto/", remover_foto, name="remover_foto"),
    path(
        "alterar-senha/",
        PasswordChangeView.as_view(
            template_name="templates_usuarios/alterar_senha.html", success_url=reverse_lazy("perfil")
        ),
        name="alterar_senha",
    ),
    path("usuarios/<int:pk>/", DetalhesUsuarioView.as_view(), name="detalhes_usuario"),
    path("usuarios/editar/<int:pk>/", EditarUsuarioView.as_view(), name="editar_usuario"),
]
