from django.urls import path
from .views import (
    index, home, login_usuario, logout_usuario,
    cadastro_medico, cadastro_atendente,
    cadastro_paciente, auto_cadastro_paciente, perfil_atendente, perfil_medico, perfil_paciente,
    MedicoListView, MedicoCreateView, MedicoUpdateView, MedicoDeleteView,
    AtendenteListView, AtendenteCreateView, AtendenteUpdateView, AtendenteDeleteView,
    PacienteListView, PacienteCreateView, PacienteUpdateView, PacienteDeleteView, AlterarSenhaView
)

urlpatterns = [
    # Páginas principais
    path('', index, name='index'),
    path('home/', home, name='home'),

    # Autenticação
    path('login/', login_usuario, name='login'),
    path('logout/', logout_usuario, name='logout'),

    path('cadastro_interno/paciente/', cadastro_paciente, name='cadastro_paciente'),
    path('cadastro/', auto_cadastro_paciente, name='auto_cadastro_paciente'),

    # CRUD de Médicos
    path('medicos/', MedicoListView.as_view(), name='listar_medicos'),
    path('medicos/novo/', cadastro_medico, name='criar_medico'),
    path('medicos/<int:pk>/editar/', MedicoUpdateView.as_view(), name='editar_medico'),
    path('medicos/<int:pk>/deletar/', MedicoDeleteView.as_view(), name='deletar_medico'),

    # CRUD de Atendentes
    path('atendentes/', AtendenteListView.as_view(), name='listar_atendentes'),
    path('atendentes/novo/', cadastro_atendente, name='criar_atendente'),
    path('atendentes/<int:pk>/editar/', AtendenteUpdateView.as_view(), name='editar_atendente'),
    path('atendentes/<int:pk>/deletar/', AtendenteDeleteView.as_view(), name='deletar_atendente'),

    # CRUD de Pacientes
    path('pacientes/', PacienteListView.as_view(), name='listar_pacientes'),
    path('pacientes/novo/', cadastro_paciente, name='criar_paciente'),
    path('pacientes/<int:pk>/editar/', PacienteUpdateView.as_view(), name='editar_paciente'),
    path('pacientes/<int:pk>/deletar/', PacienteDeleteView.as_view(), name='deletar_paciente'),

    # Perfis
    path('perfil/medico/<int:pk>/', perfil_medico, name='perfil_medico'),
    path('perfil/atendente/<int:pk>/', perfil_atendente, name='perfil_atendente'),
    path('perfil/paciente/<int:pk>/', perfil_paciente, name='perfil_paciente'),

    path('alterar-senha/', AlterarSenhaView.as_view(), name='alterar_senha'),


]

