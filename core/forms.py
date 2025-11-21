from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import Medico, Paciente, Atendente, Especialidade

Usuario = get_user_model()


class UsuarioForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = [
            "nome_completo",
            "username",
            "email",
            "cpf",
            "data_nascimento",
            "endereco",
            "telefone",
            "tipo",
            "password1",
            "password2",
        ]
        labels = {
            "nome_completo": "Nome completo",
            "username": "Nome de usuário",
            "email": "E-mail",
            "cpf": "CPF",
            "data_nascimento": "Data de Nascimento",
            "endereco": "Endereço",
            "telefone": "Telefone",
            "tipo": "Tipo de Usuário",
            "password1": "Senha",
            "password2": "Confirmação de Senha",
        }
        widgets = {
            "data_nascimento": forms.DateInput(attrs={"type": "date"}),
        }


class PacienteAutoCadastroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = [
            "nome_completo",
            "username",
            "email",
            "cpf",
            "data_nascimento",
            "endereco",
            "telefone",
            "password1",
            "password2",
        ]
        labels = {
            "nome_completo": "Nome completo",
            "username": "Nome de usuário",
            "email": "E-mail",
            "cpf": "CPF",
            "data_nascimento": "Data de Nascimento",
            "endereco": "Endereço",
            "telefone": "Telefone",
            "password1": "Senha",
            "password2": "Confirmação de Senha",
        }
        widgets = {
            "data_nascimento": forms.DateInput(attrs={"type": "date"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tipo = "paciente"
        user.is_staff = False
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Usuário ou CPF")
    password = forms.CharField(widget=forms.PasswordInput)


class MedicoForm(forms.Form):
    nome_completo = forms.CharField(label="Nome completo")
    email = forms.EmailField(label="E-mail")
    cpf = forms.CharField(label="CPF")
    telefone = forms.CharField(label="Telefone", required=False)
    data_nascimento = forms.DateField(
        label="Data de Nascimento",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    endereco = forms.CharField(label="Endereço", required=False)

    crm = forms.CharField(label="CRM")
    especialidade = forms.ModelChoiceField(
        queryset=Especialidade.objects.all(),
        label="Especialidade",
    )

    def save(self):
        usuario = Usuario.objects.create_user(
            username=self.cleaned_data["cpf"],
            nome_completo=self.cleaned_data["nome_completo"],
            email=self.cleaned_data["email"],
            cpf=self.cleaned_data["cpf"],
            telefone=self.cleaned_data.get("telefone", ""),
            data_nascimento=self.cleaned_data.get("data_nascimento"),
            endereco=self.cleaned_data.get("endereco", ""),
            tipo="medico",
            password="123456",
        )

        return Medico.objects.create(
            usuario=usuario,
            crm=self.cleaned_data["crm"],
            especialidade=self.cleaned_data["especialidade"],
        )


class AtendenteForm(forms.Form):
    nome_completo = forms.CharField(label="Nome completo")
    email = forms.EmailField(label="E-mail")
    cpf = forms.CharField(label="CPF")
    telefone = forms.CharField(label="Telefone", required=False)
    data_nascimento = forms.DateField(
        label="Data de Nascimento",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    endereco = forms.CharField(label="Endereço", required=False)

    def save(self):
        usuario = Usuario.objects.create_user(
            username=self.cleaned_data["cpf"],
            nome_completo=self.cleaned_data["nome_completo"],
            email=self.cleaned_data["email"],
            cpf=self.cleaned_data["cpf"],
            telefone=self.cleaned_data.get("telefone", ""),
            data_nascimento=self.cleaned_data.get("data_nascimento"),
            endereco=self.cleaned_data.get("endereco", ""),
            tipo="atendente",
            password="123456",
        )

        return Atendente.objects.create(usuario=usuario)


class PacienteForm(forms.Form):
    nome_completo = forms.CharField(label="Nome completo")
    email = forms.EmailField(label="E-mail")
    cpf = forms.CharField(label="CPF")
    telefone = forms.CharField(label="Telefone", required=False)
    data_nascimento = forms.DateField(
        label="Data de Nascimento",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    endereco = forms.CharField(label="Endereço", required=False)

    peso = forms.DecimalField(
        label="Peso (kg)",
        required=False,
        decimal_places=2,
        max_digits=5,
    )
    altura = forms.DecimalField(
        label="Altura (m)",
        required=False,
        decimal_places=2,
        max_digits=4,
    )

    def save(self):
        usuario = Usuario.objects.create_user(
            username=self.cleaned_data["cpf"],
            nome_completo=self.cleaned_data["nome_completo"],
            email=self.cleaned_data["email"],
            cpf=self.cleaned_data["cpf"],
            telefone=self.cleaned_data.get("telefone", ""),
            data_nascimento=self.cleaned_data.get("data_nascimento"),
            endereco=self.cleaned_data.get("endereco", ""),
            tipo="paciente",
            password="123456",
        )

        return Paciente.objects.create(
            usuario=usuario,
            peso=self.cleaned_data.get("peso"),
            altura=self.cleaned_data.get("altura"),
        )


def validar_cpf(cpf):
    cpf = "".join(filter(str.isdigit, str(cpf)))

    if len(cpf) != 11:
        return False
    if cpf == cpf[0] * 11:
        return False

    def dv_calc(cpf_slice):
        total = sum(int(cpf_slice[i]) * (len(cpf_slice) + 1 - i) for i in range(len(cpf_slice)))
        result = (total * 10) % 11
        return 0 if result == 10 else result

    return dv_calc(cpf[:9]) == int(cpf[9]) and dv_calc(cpf[:10]) == int(cpf[10])


class PerfilForm(forms.ModelForm):
    def clean_foto(self):
        foto = self.cleaned_data.get("foto")

        if foto:
            if foto.size > 5 * 1024 * 1024:
                raise forms.ValidationError("A imagem não pode ultrapassar 5MB.")

            valid_types = ["image/jpeg", "image/png"]
            if foto.content_type not in valid_types:
                raise forms.ValidationError("Envie apenas imagens JPEG ou PNG.")

        return foto

    class Meta:
        model = Usuario
        fields = ["nome_completo", "email", "telefone", "endereco", "foto"]
        widgets = {
            "nome_completo": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefone": forms.TextInput(attrs={"class": "form-control telefone-mask"}),
            "endereco": forms.TextInput(attrs={"class": "form-control"}),
        }


class MedicoExtraForm(forms.ModelForm):
    class Meta:
        model = Medico
        fields = ["crm", "especialidade"]


class PacienteExtraForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ["peso", "altura"]


class UsuarioFilterForm(forms.Form):
    nome = forms.CharField(
        required=False,
        label="Buscar por Nome",
        widget=forms.TextInput(attrs={"placeholder": "Nome completo..."}),
    )
    especialidade = forms.ModelChoiceField(
        queryset=Especialidade.objects.all().order_by("nome"),
        required=False,
        empty_label="Todas as Especialidades",
        label="Filtrar por Especialidade",
    )
    cpf = forms.CharField(
        required=False,
        label="Buscar por CPF",
        widget=forms.TextInput(attrs={"placeholder": "000.000.000-00"}),
    )
