from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Medico, Paciente, Atendente, Consulta, AvisoAusencia

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ['username', 'email', 'first_name', 'last_name', 'tipo', 'is_staff', 'is_active']
    list_filter = ['tipo', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Informações adicionais', {
            'fields': ('cpf', 'data_nascimento', 'endereco', 'telefone', 'tipo'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações adicionais', {
            'fields': ('cpf', 'data_nascimento', 'endereco', 'telefone', 'tipo'),
        }),
    )
    search_fields = ['username', 'email', 'cpf']
    ordering = ['username']

@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ['get_nome', 'get_cpf', 'crm', 'especialidade']
    search_fields = ['usuario__nome', 'usuario__cpf', 'crm', 'especialidade']
    list_filter = ['especialidade']

    def get_nome(self, obj):
        return obj.usuario.nome
    get_nome.short_description = 'Nome'

    def get_cpf(self, obj):
        return obj.usuario.cpf
    get_cpf.short_description = 'CPF'

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['get_nome', 'get_cpf', 'get_telefone', 'get_email']
    search_fields = ['usuario__nome', 'usuario__cpf', 'usuario__telefone', 'usuario__email']

    def get_nome(self, obj):
        return obj.usuario.nome
    get_nome.short_description = 'Nome'

    def get_cpf(self, obj):
        return obj.usuario.cpf
    get_cpf.short_description = 'CPF'

    def get_telefone(self, obj):
        return obj.usuario.telefone
    get_telefone.short_description = 'Telefone'

    def get_email(self, obj):
        return obj.usuario.email
    get_email.short_description = 'Email'

@admin.register(Atendente)
class AtendenteAdmin(admin.ModelAdmin):
    list_display = ['get_nome', 'get_cpf', 'get_data_nascimento', 'get_endereco']
    search_fields = ['usuario__nome', 'usuario__cpf']

    def get_nome(self, obj):
        return obj.usuario.nome
    get_nome.short_description = 'Nome'

    def get_cpf(self, obj):
        return obj.usuario.cpf
    get_cpf.short_description = 'CPF'

    def get_data_nascimento(self, obj):
        return obj.usuario.data_nascimento
    get_data_nascimento.short_description = 'Data de Nascimento'

    def get_endereco(self, obj):
        return obj.usuario.endereco
    get_endereco.short_description = 'Endereço'

@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'medico', 'data', 'retorno']
    search_fields = ['paciente__usuario__nome', 'medico__usuario__nome']
    list_filter = ['data', 'retorno']

@admin.register(AvisoAusencia)
class AvisoAusenciaAdmin(admin.ModelAdmin):
    list_display = ['medico', 'data_inicio', 'data_fim', 'motivo']
    search_fields = ['medico__usuario__nome', 'motivo']
    list_filter = ['data_inicio', 'data_fim']
