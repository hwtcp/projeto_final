from django.db import models

class Atendente(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField()
    endereco = models.CharField(max_length=200)

    def __str__(self):
        return self.nome

class Medico(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    crm = models.CharField(max_length=20, unique=True)
    data_nascimento = models.DateField()
    endereco = models.CharField(max_length=200)
    especialidade = models.CharField(max_length=100) 

    def __str__(self):
        return f"Dr(a). {self.nome} - {self.crm}"

class Paciente(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    endereco = models.CharField(max_length=200)
    data_nascimento = models.DateField()
    telefone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nome

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


