from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class Usuario(AbstractUser):
    nome_completo = models.CharField(max_length=150)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField(null=True, blank=True)
    endereco = models.CharField(max_length=200, blank=True)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    foto = models.ImageField(upload_to='usuarios/', blank=True, null=True)

    TIPO_USUARIO = [
        ('medico', 'Médico'),
        ('atendente', 'Atendente'),
        ('paciente', 'Paciente'),
        ('admin', 'Admin'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_USUARIO)

    def __str__(self):
        return f"{self.nome_completo} ({self.get_tipo_display()})"


class Especialidade(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome


class Medico(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    crm = models.CharField(max_length=20, unique=True, blank=True, null=True)
    especialidade = models.ForeignKey(Especialidade, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Dr(a). {self.usuario.nome_completo} ({self.especialidade})"


class Atendente(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.usuario.nome_completo

    class Meta:
        verbose_name = "Atendente"
        verbose_name_plural = "Atendentes"


class Paciente(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    altura = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    historico_medico = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.usuario.nome_completo





