from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class Usuario(AbstractUser):
    nome_completo = models.CharField(max_length=150)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField(null=True, blank=True)
    endereco = models.CharField(max_length=200, blank=True)
    telefone = models.CharField(max_length=15, blank=True, null=True)

    TIPO_USUARIO = [
        ('medico', 'Médico'),
        ('atendente', 'Atendente'),
        ('paciente', 'Paciente'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_USUARIO)

    def __str__(self):
        return f"{self.username} ({self.get_tipo_display()})"
    
class Medico(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    crm = models.CharField(max_length=20, unique=True)
    especialidade = models.CharField(max_length=100)

    def __str__(self):
        return f"Dr(a). {self.usuario.first_name} - {self.crm}"

class Atendente(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.usuario.first_name

class Paciente(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.usuario.first_name


class Consulta(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    data = models.DateTimeField()
    retorno = models.BooleanField(default=False)
    sintomas = models.TextField(blank=True, null=True)
    diagnostico = models.TextField(blank=True, null=True)
    receita_virtual = models.FileField(upload_to="receitas/", blank=True, null=True)

    def __str__(self):
        return f"{self.paciente} - {self.medico} em {self.data.strftime('%d/%m/%Y %H:%M')}"

class AvisoAusencia(models.Model):
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    motivo = models.TextField()

    def __str__(self):
        return f"{self.medico} ausente de {self.data_inicio.strftime('%d/%m/%Y')} até {self.data_fim.strftime('%d/%m/%Y')}"


