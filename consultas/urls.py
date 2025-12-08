# urls.py do app consultas
from django.urls import path
from .views import (
    ConsultaListView,
    ConsultaDeleteView,
    GerenciarAgendaView,
    HorarioTrabalhoUpdateView,
    HorarioTrabalhoDeleteView,
    ExcecaoHorarioCreateView,
    ExcecaoHorarioUpdateView,
    ExcecaoHorarioDeleteView,
    MedicoAgendaJsonView,
    ConsultaCreateByMedicoView,
    HorariosDisponiveisAjaxView, 
    MedicoSlotsView,
    ConsultaEditarView,
    minhas_consultas_paciente,
    detalhes_consulta,
    marcar_concluida,
)

urlpatterns = [
    path(
        'agendar/medico/<int:medico_id>/',
        ConsultaCreateByMedicoView.as_view(),
        name='agendar_consulta_por_medico'
    ),

    # endpoint AJAX para retornar slots disponíveis (GET ?medico=<id>&data=YYYY-MM-DD)
    path('ajax/horarios/', HorariosDisponiveisAjaxView.as_view(), name='ajax_horarios_disponiveis'),
    path('medico/<int:medico_id>/slots/', MedicoSlotsView.as_view(), name='slots_medico'),

    path("consultas/", ConsultaListView.as_view(), name="listar_consultas"),
    path("consultas/<int:pk>/deletar/", ConsultaDeleteView.as_view(), name="deletar_consulta"),
    path('consulta/<int:pk>/concluir/', marcar_concluida, name='marcar_concluida'), 
    path("consultas/<int:pk>/editar/", ConsultaEditarView.as_view(), name="editar_consulta"),
    path("consulta/<int:pk>/", detalhes_consulta, name="detalhes_consulta"),

    path('minhas-consultas/paciente/', minhas_consultas_paciente, name='minhas_consultas_paciente'),

    path('agenda/gerenciar/', GerenciarAgendaView.as_view(), name='gerenciar_agenda'),

    path('agenda/horario/editar/<int:pk>/', HorarioTrabalhoUpdateView.as_view(), name='editar_horario'),
    path('agenda/horario/deletar/<int:pk>/', HorarioTrabalhoDeleteView.as_view(), name='deletar_horario'),

    path('agenda/excecao/adicionar/', ExcecaoHorarioCreateView.as_view(), name='adicionar_excecao'),
    path('agenda/excecao/editar/<int:pk>/', ExcecaoHorarioUpdateView.as_view(), name='editar_excecao'),
    path('agenda/excecao/deletar/<int:pk>/', ExcecaoHorarioDeleteView.as_view(), name='deletar_excecao'),

    # API/JSON com agenda (você já tinha)
    path('api/agenda/<int:medico_id>/', MedicoAgendaJsonView.as_view(), name='api_agenda_medico'),
]
