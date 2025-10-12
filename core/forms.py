from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario, Medico, Paciente, Atendente

class UsuarioForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'cpf', 'data_nascimento',
            'endereco', 'telefone', 'tipo', 'password1', 'password2'
        ]
        labels = {
            'username': 'Nome completo',
            'email': 'E-mail',
            'cpf': 'CPF',
            'data_nascimento': 'Data de Nascimento',
            'endereco': 'Endereço',
            'telefone': 'Telefone',
            'tipo': 'Tipo de Usuário',
            'password1': 'Senha',
            'password2': 'Confirmação de Senha',
        }
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }

class PacienteAutoCadastroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['nome_completo', 'username', 'email', 'cpf', 'data_nascimento', 'endereco', 'telefone', 'password1', 'password2']
        labels = {
            'nome_completo' : 'Nome completo', 
            'username': 'Nome de usuário',
            'email': 'E-mail',
            'cpf': 'CPF',
            'data_nascimento': 'Data de Nascimento',
            'endereco': 'Endereço',
            'telefone': 'Telefone',
            'password1': 'Senha',
            'password2': 'Confirmação de Senha',
        }
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'tipo' in self.fields:
            self.fields.pop('tipo')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tipo = 'paciente'  
        user.is_staff = False
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Usuário ou CPF")
    password = forms.CharField(widget=forms.PasswordInput)

class MedicoForm(forms.ModelForm):
    class Meta:
        model = Medico
        fields = ['crm', 'especialidade']

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = []

class AtendenteForm(forms.ModelForm):
    class Meta:
        model = Atendente
        fields = []
