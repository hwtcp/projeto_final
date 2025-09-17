from django.contrib import admin
from .models import Atendente, Medico, Paciente, Consulta, AvisoAusencia

@admin.register(Atendente)
class AtendenteAdmin(admin.ModelAdmin):
    list_display = ("nome", "cpf", "data_nascimento", "endereco")
    search_fields = ("nome", "cpf")
    list_filter = ("data_nascimento",)

@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ("nome", "cpf", "crm", "especialidade")
    search_fields = ("nome", "cpf", "crm", "especialidade")
    list_filter = ("especialidade",)


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ("nome", "cpf", "telefone", "email")
    search_fields = ("nome", "cpf", "telefone", "email")
    list_filter = ("data_nascimento",)


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ("paciente", "medico", "data", "retorno")
    search_fields = ("paciente__nome", "medico__nome")
    list_filter = ("data", "retorno")


@admin.register(AvisoAusencia)
class AvisoAusenciaAdmin(admin.ModelAdmin):
    list_display = ("medico", "data_inicio", "data_fim", "motivo")
    search_fields = ("medico__nome", "motivo")
    list_filter = ("data_inicio", "data_fim")
