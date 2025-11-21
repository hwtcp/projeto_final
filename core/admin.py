from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Medico, Paciente, Atendente, Especialidade


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ("nome_completo", "email", "cpf", "tipo", "is_active", "is_staff")
    list_filter = ("tipo", "is_active", "is_staff")
    search_fields = ("nome_completo", "cpf", "email")
    ordering = ("nome_completo",)

    fieldsets = (
        ("Informações de Login", {"fields": ("username", "password")}),
        (
            "Informações Pessoais",
            {"fields": ("nome_completo", "email", "cpf", "data_nascimento", "endereco", "telefone")},
        ),
        ("Função", {"fields": ("tipo",)}),
        ("Permissões", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
        ("Datas Importantes", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "nome_completo",
                    "email",
                    "cpf",
                    "data_nascimento",
                    "endereco",
                    "telefone",
                    "tipo",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )


@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ("get_nome", "get_cpf", "crm", "get_especialidade")
    search_fields = ("usuario__nome_completo", "usuario__cpf", "crm", "especialidade__nome")
    list_filter = ["especialidade__nome"]

    def get_especialidade(self, obj):
        return obj.especialidade.nome if obj.especialidade else "-"

    get_especialidade.short_description = "Especialidade"

    def get_nome(self, obj):
        return obj.usuario.nome_completo

    get_nome.short_description = "Nome"

    def get_cpf(self, obj):
        return obj.usuario.cpf

    get_cpf.short_description = "CPF"


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ("get_nome", "get_cpf", "peso", "altura", "get_telefone", "get_email")
    search_fields = ("usuario__nome_completo", "usuario__cpf", "usuario__telefone", "usuario__email")

    fieldsets = (("Informações Pessoais", {"fields": ("usuario", "peso", "altura", "historico_medico")}),)

    def get_nome(self, obj):
        return obj.usuario.nome_completo

    get_nome.short_description = "Nome"

    def get_cpf(self, obj):
        return obj.usuario.cpf

    get_cpf.short_description = "CPF"

    def get_telefone(self, obj):
        return obj.usuario.telefone

    get_telefone.short_description = "Telefone"

    def get_email(self, obj):
        return obj.usuario.email

    get_email.short_description = "Email"


@admin.register(Atendente)
class AtendenteAdmin(admin.ModelAdmin):
    list_display = ("get_nome", "get_cpf", "get_data_nascimento", "get_endereco")
    search_fields = ("usuario__nome_completo", "usuario__cpf")

    def get_nome(self, obj):
        return obj.usuario.nome_completo

    get_nome.short_description = "Nome"

    def get_cpf(self, obj):
        return obj.usuario.cpf

    get_cpf.short_description = "CPF"

    def get_data_nascimento(self, obj):
        return obj.usuario.data_nascimento

    get_data_nascimento.short_description = "Data de Nascimento"

    def get_endereco(self, obj):
        return obj.usuario.endereco

    get_endereco.short_description = "Endereço"


@admin.register(Especialidade)
class EspecialidadeAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome",)
