from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import (
    LoginForm,
    PacienteAutoCadastroForm,
    MedicoForm,
    AtendenteForm,
    PacienteForm,
    PerfilForm,
    MedicoExtraForm,
    PacienteExtraForm,
    UsuarioFilterForm,
)
from .models import Medico, Paciente, Atendente, Usuario
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.views import View
from django.db.models import Q


def index(request):
    if request.user.is_authenticated:
        return redirect("home")
    return render(request, "index.html")


def login_usuario(request):
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            return redirect(request.GET.get("next") or "home")
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    return render(request, "index.html", {"form": form})


def logout_usuario(request):
    logout(request)
    return redirect("login")


@login_required
@user_passes_test(lambda u: u.is_staff)
def cadastro_medico(request):
    if request.method == "POST":
        form = MedicoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Médico cadastrado com sucesso.")
            return redirect("listar_medicos")
        else:
            print(form.errors)
    else:
        form = MedicoForm()

    return render(request, "templates_usuarios/form_medico.html", {"form": form})


@login_required
@user_passes_test(lambda u: u.is_staff)
def cadastro_atendente(request):
    if request.method == "POST":
        form = AtendenteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Atendente cadastrado com sucesso.")
            return redirect("listar_atendentes")
        else:
            print(form.errors)
    else:
        form = AtendenteForm()

    return render(request, "templates_usuarios/form_atendente.html", {"form": form})


@login_required
@user_passes_test(lambda u: u.is_staff)
def cadastro_paciente(request):
    if request.method == "POST":
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Paciente cadastrado com sucesso.")
            return redirect("listar_pacientes")
        else:
            print(form.errors)
    else:
        form = PacienteForm()

    return render(request, "templates_usuarios/form_paciente.html", {"form": form})


def auto_cadastro_paciente(request):
    if request.user.is_authenticated:
        return redirect("perfil")

    if request.method == "POST":
        form = PacienteAutoCadastroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Conta criada com sucesso! Faça login para continuar.")
            return redirect("login")
    else:
        form = PacienteAutoCadastroForm()

    return render(request, "cadastro.html", {"form": form})


@login_required
def home(request):
    return redirect("perfil")


class AlterarSenhaView(PasswordChangeView):
    template_name = "templates_usuarios/alterar_senha.html"
    success_url = reverse_lazy("perfil")


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.tipo == "admin"

    def handle_no_permission(self):
        messages.error(self.request, "Acesso negado. Apenas administradores podem acessar esta área.")
        return redirect("home")


class AdminOrAtendenteRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return (
            self.request.user.is_superuser or self.request.user.tipo == "admin" or self.request.user.tipo == "atendente"
        )


class DetalhesUsuarioView(AdminOrAtendenteRequiredMixin, View):

    def get(self, request, pk):
        usuario_base = get_object_or_404(Usuario, pk=pk)
        objeto_extra = None
        if usuario_base.tipo == "medico":
            # Usa .filter().first() para ser seguro caso o objeto extra não tenha sido criado
            objeto_extra = Medico.objects.filter(usuario=usuario_base).first()

        elif usuario_base.tipo == "paciente":
            objeto_extra = Paciente.objects.filter(usuario=usuario_base).first()

        # 4. Prepara o Contexto
        context = {
            "usuario": usuario_base,
            "objeto_extra": objeto_extra,
            "tipo_usuario": usuario_base.tipo,
            # Garanta que este template base é o que tem a estrutura do seu dashboard
            "base_template": "base_dashboard.html",
        }

        # Renderiza o template de detalhes que criamos anteriormente
        return render(request, "templates_usuarios/detalhes_usuario.html", context)


class EditarUsuarioView(AdminOrAtendenteRequiredMixin, View):

    def get_forms(self, user, data=None):

        perfil_form = PerfilForm(data=data, instance=user)
        medico_form = None
        paciente_form = None

        if user.tipo == "medico":
            medico_instance, created = Medico.objects.get_or_create(usuario=user)
            medico_form = MedicoExtraForm(data=data, instance=medico_instance)
        elif user.tipo == "paciente":
            paciente_instance, created = Paciente.objects.get_or_create(usuario=user)
            paciente_form = PacienteExtraForm(data=data, instance=paciente_instance)

        return perfil_form, medico_form, paciente_form

    def get(self, request, pk):
        usuario_base = get_object_or_404(Usuario, pk=pk)

        perfil_form, medico_form, paciente_form = self.get_forms(usuario_base)

        context = {
            "usuario_base": usuario_base,
            "perfil_form": perfil_form,
            "medico_form": medico_form,
            "paciente_form": paciente_form,
            "base_template": "base_dashboard.html",
        }

        return render(request, "templates_usuarios/editar_usuario.html", context)

    def post(self, request, pk):
        usuario_base = get_object_or_404(Usuario, pk=pk)
        action = request.POST.get("action")

        perfil_form, medico_form, paciente_form = self.get_forms(usuario_base, data=request.POST)

        if action == "update_status":
            status_form = PerfilForm(request.POST, instance=usuario_base)

            if status_form.is_valid():
                usuario_base.is_active = status_form.cleaned_data.get("is_active")
                usuario_base.save(update_fields=["is_active"])
                messages.success(request, f"Status de {usuario_base.tipo} atualizado com sucesso!")
            else:
                messages.error(request, "Erro ao atualizar status. O campo 'Conta Ativa?' não é válido.")

        elif action == "update_profile":
            valid = perfil_form.is_valid()

            if medico_form:
                valid = valid and medico_form.is_valid()
            if paciente_form:
                valid = valid and paciente_form.is_valid()

            if valid:
                perfil_form.save()
                if medico_form:
                    medico_form.save()
                if paciente_form:
                    paciente_form.save()

                messages.success(request, f"Perfil do {usuario_base.tipo} atualizado com sucesso!")
                return redirect("editar_usuario", pk=usuario_base.pk)
            else:
                messages.error(request, "Erro ao salvar dados. Verifique os campos com erros.")

        context = {
            "usuario_base": usuario_base,
            "perfil_form": perfil_form,
            "medico_form": medico_form,
            "paciente_form": paciente_form,
            "base_template": "base_dashboard.html",
        }
        return render(request, "templates_usuarios/editar_usuario.html", context)


class MedicoListView(AdminRequiredMixin, ListView):
    model = Medico
    template_name = "templates_usuarios/listar_medicos.html"
    context_object_name = "medicos"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related("usuario", "especialidade").order_by("usuario__nome_completo")
        self.form = UsuarioFilterForm(self.request.GET)
        if self.form.is_valid():
            nome_query = self.form.cleaned_data.get("nome")
            if nome_query:
                queryset = queryset.filter(Q(usuario__nome_completo__icontains=nome_query))
            especialidade_obj = self.form.cleaned_data.get("especialidade")
            if especialidade_obj:
                queryset = queryset.filter(especialidade=especialidade_obj)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form
        return context


class MedicoDeleteView(AdminRequiredMixin, DeleteView):
    model = Medico
    template_name = "confirmar_exclusao.html"
    success_url = reverse_lazy("listar_medicos")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Médico excluído com sucesso!")
        return super().delete(request, *args, **kwargs)


class AtendenteListView(AdminRequiredMixin, ListView):
    model = Atendente
    template_name = "templates_usuarios/listar_atendentes.html"
    context_object_name = "atendentes"
    aginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related("usuario").order_by("usuario__nome_completo")
        self.form = UsuarioFilterForm(self.request.GET)
        if self.form.is_valid():
            nome_query = self.form.cleaned_data.get("nome")
            if nome_query:
                queryset = queryset.filter(Q(usuario__nome_completo__icontains=nome_query))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form
        return context


class AtendenteDeleteView(AdminRequiredMixin, DeleteView):
    model = Atendente
    template_name = "confirmar_exclusao.html"
    success_url = reverse_lazy("listar_atendentes")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Atendente excluído com sucesso!")
        return super().delete(request, *args, **kwargs)


class PacienteListView(AdminOrAtendenteRequiredMixin, ListView):
    model = Paciente
    template_name = "templates_usuarios/listar_pacientes.html"
    context_object_name = "pacientes"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related("usuario").order_by("usuario__nome_completo")
        self.form = UsuarioFilterForm(self.request.GET)
        if self.form.is_valid():
            nome_query = self.form.cleaned_data.get("nome")
            if nome_query:
                queryset = queryset.filter(Q(usuario__nome_completo__icontains=nome_query))
            cpf_query = self.form.cleaned_data.get("cpf")
            if cpf_query:
                cpf_limpo = "".join(filter(str.isdigit, cpf_query))
                queryset = queryset.filter(usuario__cpf__icontains=cpf_limpo)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form
        return context


class PacienteDeleteView(AdminRequiredMixin, DeleteView):
    model = Paciente
    template_name = "confirmar_exclusao.html"
    success_url = reverse_lazy("listar_pacientes")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Paciente excluído com sucesso!")
        return super().delete(request, *args, **kwargs)


@login_required
def perfil(request):
    user = request.user
    perfil_form = PerfilForm(request.POST or None, request.FILES or None, instance=request.user)
    senha_form = PasswordChangeForm(user=request.user, data=request.POST or None)

    medico_form = paciente_form = None
    if user.tipo == "medico":
        medico_form = MedicoExtraForm(request.POST or None, instance=getattr(user, "medico", None))
    elif user.tipo == "paciente":
        paciente_form = PacienteExtraForm(request.POST or None, instance=getattr(user, "paciente", None))

    if request.method == "POST":
        valid = perfil_form.is_valid()
        if medico_form:
            valid = valid and medico_form.is_valid()
        if paciente_form:
            valid = valid and paciente_form.is_valid()

        if valid:
            perfil_form.save()
            if medico_form:
                medico_form.save()
            if paciente_form:
                paciente_form.save()
            messages.success(request, "Dados atualizados com sucesso!")
            return redirect("perfil")

    return render(
        request,
        "templates_usuarios/perfil.html",
        {
            "perfil_form": perfil_form,
            "senha_form": senha_form,
            "medico_form": medico_form,
            "paciente_form": paciente_form,
            "user": user,
        },
    )


@login_required
def remover_foto(request):
    user = request.user
    if user.foto:
        user.foto.delete()
        user.foto = None
        user.save()
    messages.success(request, "Foto removida com sucesso!")
    return redirect("perfil")
