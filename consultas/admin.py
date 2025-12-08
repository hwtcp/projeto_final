from django.contrib import admin
from .models import Consulta
from core.models import Especialidade
# Importação da timezone para garantir que as datas sejam formatadas corretamente
from django.utils import timezone 


class EspecialidadeFilter(admin.SimpleListFilter):
    title = "Especialidade"
    parameter_name = "especialidade"

    def lookups(self, request, model_admin):
        especialidades = Especialidade.objects.all()
        return [(e.id, e.nome) for e in especialidades]

    def queryset(self, request, queryset):
        if self.value():
            # Filtra consultas onde o médico tem a especialidade selecionada
            return queryset.filter(medico__especialidade__id=self.value())
        return queryset


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    # Correção: O campo 'data_formatada' será o display da data, e 'status' estava faltando
    list_display = ("paciente", "medico", "especialidade", "data_formatada", "status", "retorno")
    
    # list_filter corrigido
    # Ordem sugerida: Status, Retorno, Filtro Customizado, Filtro de Data
    list_filter = ("status", "retorno", EspecialidadeFilter, "data_hora_inicio") 
    
    search_fields = ("paciente__usuario__nome_completo", "medico__usuario__nome_completo", "sintomas", "diagnostico")
    
    # O ordering já estava correto com 'data_hora_inicio'
    ordering = ("-data_hora_inicio",)

    @admin.display(description="Especialidade")
    def especialidade(self, obj):
        """Retorna o nome da especialidade do médico da consulta."""
        return obj.medico.especialidade if obj.medico and obj.medico.especialidade else "-"

    @admin.display(description="Data e Hora") # Mudança no título para refletir o conteúdo
    def data_formatada(self, obj):
        """
        CORREÇÃO: Usa 'obj.data_hora_inicio' e não 'obj.data'. 
        Garante que o campo correto do modelo seja acessado.
        """
        if obj.data_hora_inicio:
            # Garante que a data seja exibida no fuso horário correto
            data_local = timezone.localtime(obj.data_hora_inicio)
            return data_local.strftime("%d/%m/%Y %H:%M")
        return "-"
    
    # Adicionando um campo para facilitar a navegação por data
    date_hierarchy = 'data_hora_inicio'
