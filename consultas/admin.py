from django.contrib import admin
from .models import Consulta
from core.models import Especialidade


class EspecialidadeFilter(admin.SimpleListFilter):
    title = "Especialidade"
    parameter_name = "especialidade"

    def lookups(self, request, model_admin):
        especialidades = Especialidade.objects.all()
        return [(e.id, e.nome) for e in especialidades]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(medico__especialidade__id=self.value())
        return queryset


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ("paciente", "medico", "especialidade", "data_formatada", "retorno")
    list_filter = ("retorno", EspecialidadeFilter, "data")
    search_fields = ("paciente__usuario__nome_completo", "medico__usuario__nome_completo", "sintomas", "diagnostico")
    ordering = ("-data",)

    @admin.display(description="Especialidade")
    def especialidade(self, obj):
        return obj.medico.especialidade if obj.medico and obj.medico.especialidade else "-"

    @admin.display(description="Data")
    def data_formatada(self, obj):
        return obj.data.strftime("%d/%m/%Y %H:%M")
