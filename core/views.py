from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import UsuarioForm, LoginForm, PacienteAutoCadastroForm 
from .models import Medico, Paciente, Atendente, Usuario

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
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.tipo = 'medico'
            usuario.is_staff = False
            usuario.save()
            Medico.objects.create(usuario=usuario)
            messages.success(request, 'Médico cadastrado com sucesso.')
            return redirect('home')
    else:
        form = UsuarioForm(initial={'tipo': 'medico'})
    return render(request, 'cadastro.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def cadastro_atendente(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.tipo = 'atendente'
            usuario.is_staff = False
            usuario.save()
            Atendente.objects.create(usuario=usuario)
            messages.success(request, 'Atendente cadastrado com sucesso.')
            return redirect('home')
    else:
        form = UsuarioForm(initial={'tipo': 'atendente'})
    return render(request, 'cadastro.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def cadastro_paciente(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.tipo = 'paciente'
            usuario.is_staff = False
            usuario.save()
            Paciente.objects.create(usuario=usuario)
            messages.success(request, 'Paciente cadastrado com sucesso.')
            return redirect('home')
    else:
        form = UsuarioForm(initial={'tipo': 'paciente'})
    
    return render(request, 'cadastro.html', {'form': form})

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
    contexto = {}

    # Admin
    if usuario.is_staff:
        contexto['menu'] = 'admin'
        contexto['mensagem'] = 'Bem-vindo, Administrador! Você pode cadastrar médicos, atendentes e pacientes.'

    # Atendente
    elif usuario.tipo == 'atendente':
        contexto['menu'] = 'atendente'
        contexto['mensagem'] = 'Bem-vindo, Atendente! Você pode cadastrar pacientes.'

    # Médico
    elif usuario.tipo == 'medico':
        contexto['menu'] = 'medico'
        contexto['mensagem'] = 'Bem-vindo, Doutor! Aqui você pode ver suas consultas e avisos de ausência.'

    # Paciente
    elif usuario.tipo == 'paciente':
        contexto['menu'] = 'paciente'
        contexto['mensagem'] = 'Bem-vindo! Aqui você pode ver suas consultas e agendar novas.'

    return render(request, 'home.html', contexto)

