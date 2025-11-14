from django.db import models
from core.models import Usuario, Medico, Paciente

class Consulta(models.Model):
    medico = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='consultas_medico',
        limit_choices_to={'tipo': 'medico'}
    )
    paciente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='consultas_paciente',
        limit_choices_to={'tipo': 'paciente'}
    )
    data = models.DateTimeField()
    retorno = models.BooleanField(default=False)
    sintomas = models.TextField(blank=True, null=True)
    diagnostico = models.TextField(blank=True, null=True)
    receita_virtual = models.FileField(upload_to='receitas/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('agendada', 'Agendada'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ], default='agendada')

    def __str__(self):
        return f'{self.paciente.username} - {self.medico.username} em {self.data.strftime("%d/%m/%Y %H:%M")}'


class AvisoAusencia(models.Model):
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    motivo = models.TextField()

    def __str__(self):
        return f"{self.medico} ausente de {self.data_inicio.strftime('%d/%m/%Y')} até {self.data_fim.strftime('%d/%m/%Y')}"

