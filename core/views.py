from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import UsuarioForm, LoginForm, PacienteAutoCadastroForm, MedicoForm, AtendenteForm, PacienteForm
from .models import Medico, Paciente, Atendente, Usuario
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView

def index(request):
    return render(request, 'index.html')

def login_usuario(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            return redirect('home')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_usuario(request):
    logout(request)
    return redirect('login')

@login_required
@user_passes_test(lambda u: u.is_staff)
def cadastro_medico(request):
    if request.method == 'POST':
        form = MedicoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Médico cadastrado com sucesso.')
            return redirect('listar_medicos')
        else:
            print(form.errors) 
    else:
        form = MedicoForm()

    return render(request, 'templates_usuarios/form_medico.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.is_staff)
def cadastro_atendente(request):
    if request.method == 'POST':
        form = AtendenteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Atendente cadastrado com sucesso.')
            return redirect('listar_atendentes')
        else:
            print(form.errors)
    else:
        form = AtendenteForm()

    return render(request, 'templates_usuarios/form_atendente.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def cadastro_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente cadastrado com sucesso.')
            return redirect('listar_pacientes')
        else:
            print(form.errors)
    else:
        form = PacienteForm()

    return render(request, 'templates_usuarios/form_paciente.html', {'form': form})


def auto_cadastro_paciente(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = PacienteAutoCadastroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conta criada com sucesso! Faça login para continuar.')
            return redirect('login')
    else:
        form = PacienteAutoCadastroForm()

    return render(request, 'cadastro.html', {'form': form})

@login_required
def home(request):
    usuario = request.user

    if usuario.is_superuser or usuario.tipo == 'admin':
        return render(request, 'templates_usuarios/perfil_admin.html', {'usuario': usuario})

    elif usuario.tipo == 'medico':
        medico = Medico.objects.get(usuario=usuario)
        return render(request, 'templates_usuarios/perfil_medico.html', {'medico': medico})

    elif usuario.tipo == 'atendente':
        atendente = Atendente.objects.get(usuario=usuario)
        return render(request, 'templates_usuarios/perfil_atendente.html', {'atendente': atendente})

    elif usuario.tipo == 'paciente':
        paciente = Paciente.objects.get(usuario=usuario)
        return render(request, 'templates_usuarios/perfil_paciente.html', {'paciente': paciente})

    else:
        messages.error(request, "Tipo de usuário não reconhecido.")
        return redirect('logout')

@login_required
def perfil_medico(request, pk):
    medico = Medico.objects.get(pk=pk)
    return render(request, 'usuarios/perfil_medico.html', {'medico': medico})


@login_required
def perfil_atendente(request, pk):
    atendente = Atendente.objects.get(pk=pk)
    return render(request, 'usuarios/perfil_atendente.html', {'atendente': atendente})


@login_required
def perfil_paciente(request, pk):
    paciente = Paciente.objects.get(pk=pk)
    return render(request, 'usuarios/perfil_paciente.html', {'paciente': paciente})

class AlterarSenhaView(PasswordChangeView):
    template_name = 'templates_usuarios/alterar_senha.html'
    success_url = reverse_lazy('home')
# Usando Class-Based Views para RUD (Read, Update, Delet) com mixins de permissão

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.tipo == 'admin'

    def handle_no_permission(self):
        messages.error(self.request, "Acesso negado. Apenas administradores podem acessar esta área.")
        return redirect('home')

class AdminOrAtendenteRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return (
            self.request.user.is_superuser
            or self.request.user.tipo == 'admin'
            or self.request.user.tipo == 'atendente'
        )


class MedicoListView(AdminRequiredMixin, ListView):
    model = Medico
    template_name = 'templates_usuarios/listar_medicos.html'
    context_object_name = 'medicos'

class MedicoCreateView(AdminRequiredMixin, CreateView):
    model = Medico
    form_class = MedicoForm
    template_name = 'templates_usuarios/form_medico.html'
    success_url = reverse_lazy('listar_medicos')

    def form_valid(self, form):
        messages.success(self.request, 'Médico cadastrado com sucesso!')
        return super().form_valid(form)

class MedicoUpdateView(AdminRequiredMixin, UpdateView):
    model = Medico
    form_class = MedicoForm
    template_name = 'templates_usuarios/form_medico.html'
    success_url = reverse_lazy('listar_medicos')

    def form_valid(self, form):
        messages.success(self.request, 'Médico atualizado com sucesso!')
        return super().form_valid(form)

class MedicoDeleteView(AdminRequiredMixin, DeleteView):
    model = Medico
    template_name = 'confirmar_exclusao.html'
    success_url = reverse_lazy('listar_medicos')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Médico excluído com sucesso!')
        return super().delete(request, *args, **kwargs)
    

class AtendenteListView(AdminRequiredMixin, ListView):
    model = Atendente
    template_name = 'templates_usuarios/listar_atendentes.html'
    context_object_name = 'atendentes'

class AtendenteCreateView(AdminRequiredMixin, CreateView):
    model = Atendente
    form_class = AtendenteForm
    template_name = 'templates_usuarios/form_atendente.html'
    success_url = reverse_lazy('listar_atendentes')

    def form_valid(self, form):
        messages.success(self.request, 'Atendente cadastrado com sucesso!')
        return super().form_valid(form)

class AtendenteUpdateView(AdminRequiredMixin, UpdateView):
    model = Atendente
    form_class = AtendenteForm
    template_name = 'templates_usuarios/form_atendente.html'
    success_url = reverse_lazy('listar_atendentes')

    def form_valid(self, form):
        messages.success(self.request, 'Atendente atualizado com sucesso!')
        return super().form_valid(form)

class AtendenteDeleteView(AdminRequiredMixin, DeleteView):
    model = Atendente
    template_name = 'confirmar_exclusao.html'
    success_url = reverse_lazy('listar_atendentes')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Atendente excluído com sucesso!')
        return super().delete(request, *args, **kwargs)
    

class PacienteListView(AdminOrAtendenteRequiredMixin, ListView):
    model = Paciente
    template_name = 'templates_usuarios/listar_pacientes.html'
    context_object_name = 'pacientes'


class PacienteCreateView(AdminRequiredMixin, CreateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'templates_usuarios/form_paciente.html'
    success_url = reverse_lazy('listar_pacientes')

    def form_valid(self, form):
        messages.success(self.request, 'Paciente cadastrado com sucesso!')
        return super().form_valid(form)

class PacienteUpdateView(AdminRequiredMixin, UpdateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'templates_usuarios/form_paciente.html'
    success_url = reverse_lazy('listar_pacientes')

    def form_valid(self, form):
        messages.success(self.request, 'Paciente atualizado com sucesso!')
        return super().form_valid(form)

class PacienteDeleteView(AdminRequiredMixin, DeleteView):
    model = Paciente
    template_name = 'confirmar_exclusao.html'
    success_url = reverse_lazy('listar_pacientes')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Paciente excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


