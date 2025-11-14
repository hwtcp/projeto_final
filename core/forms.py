from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario, Medico, Paciente, Atendente, Especialidade
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class UsuarioForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = [
            'nome_completo', 'username', 'email', 'cpf',
            'data_nascimento', 'endereco', 'telefone', 'tipo',
            'password1', 'password2'
        ]
        labels = {
            'nome_completo': 'Nome completo',
            'username': 'Nome de usuário',
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
        fields = [
            'nome_completo', 'username', 'email', 'cpf',
            'data_nascimento', 'endereco', 'telefone',
            'password1', 'password2'
        ]
        labels = {
            'nome_completo': 'Nome completo',
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


class MedicoForm(forms.Form):
    # Campos do usuário
    nome_completo = forms.CharField(label='Nome completo')
    email = forms.EmailField(label='E-mail')
    cpf = forms.CharField(label='CPF')
    telefone = forms.CharField(label='Telefone', required=False)
    data_nascimento = forms.DateField(
        label='Data de Nascimento',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    endereco = forms.CharField(label='Endereço', required=False)

    # Campos do médico
    crm = forms.CharField(label='CRM')
    especialidade = forms.ModelChoiceField(
        queryset=Especialidade.objects.all(),
        label='Especialidade'
    )

    def save(self):
        # Criar usuário
        usuario = Usuario.objects.create_user(
            username=self.cleaned_data['cpf'],
            nome_completo=self.cleaned_data['nome_completo'],
            email=self.cleaned_data['email'],
            cpf=self.cleaned_data['cpf'],
            telefone=self.cleaned_data.get('telefone', ''),
            data_nascimento=self.cleaned_data.get('data_nascimento'),
            endereco=self.cleaned_data.get('endereco', ''),
            tipo='medico',
            password='123456'
        )

        # Criar médico
        medico = Medico.objects.create(
            usuario=usuario,
            crm=self.cleaned_data['crm'],
            especialidade=self.cleaned_data['especialidade']
        )

        return medico


class AtendenteForm(forms.Form):
    # Dados do usuário
    nome_completo = forms.CharField(label='Nome completo')
    email = forms.EmailField(label='E-mail')
    cpf = forms.CharField(label='CPF')
    telefone = forms.CharField(label='Telefone', required=False)
    data_nascimento = forms.DateField(
        label='Data de Nascimento',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    endereco = forms.CharField(label='Endereço', required=False)

    def save(self):
        # Criar usuário
        usuario = Usuario.objects.create_user(
            username=self.cleaned_data['cpf'],
            nome_completo=self.cleaned_data['nome_completo'],
            email=self.cleaned_data['email'],
            cpf=self.cleaned_data['cpf'],
            telefone=self.cleaned_data.get('telefone', ''),
            data_nascimento=self.cleaned_data.get('data_nascimento'),
            endereco=self.cleaned_data.get('endereco', ''),
            tipo='atendente',
            password='123456'
        )

        # Criar atendente
        atendente = Atendente.objects.create(
            usuario=usuario
        )

        return atendente

class PacienteForm(forms.Form):
    # Dados do usuário
    nome_completo = forms.CharField(label='Nome completo')
    email = forms.EmailField(label='E-mail')
    cpf = forms.CharField(label='CPF')
    telefone = forms.CharField(label='Telefone', required=False)
    data_nascimento = forms.DateField(
        label='Data de Nascimento',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    endereco = forms.CharField(label='Endereço', required=False)

    # Dados específicos do paciente
    peso = forms.DecimalField(
        label='Peso (kg)',
        required=False,
        decimal_places=2,
        max_digits=5
    )
    altura = forms.DecimalField(
        label='Altura (m)',
        required=False,
        decimal_places=2,
        max_digits=4
    )

    def save(self):
        # Criar usuário
        usuario = Usuario.objects.create_user(
            username=self.cleaned_data['cpf'],
            nome_completo=self.cleaned_data['nome_completo'],
            email=self.cleaned_data['email'],
            cpf=self.cleaned_data['cpf'],
            telefone=self.cleaned_data.get('telefone', ''),
            data_nascimento=self.cleaned_data.get('data_nascimento'),
            endereco=self.cleaned_data.get('endereco', ''),
            tipo='paciente',
            password='123456'
        )

        # Criar paciente
        paciente = Paciente.objects.create(
            usuario=usuario,
            peso=self.cleaned_data.get('peso'),
            altura=self.cleaned_data.get('altura')
        )

        return paciente


