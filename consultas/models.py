from django.db import models
from core.models import Medico, Paciente


class HorarioTrabalho(models.Model):
    DIAS_SEMANA = [
        (0, "Domingo"),
        (1, "Segunda-feira"),
        (2, "Terça-feira"),
        (3, "Quarta-feira"),
        (4, "Quinta-feira"),
        (5, "Sexta-feira"),
        (6, "Sábado"),
    ]

    medico = models.ForeignKey(
        Medico,
        on_delete=models.CASCADE,
        related_name="horarios_trabalho",
        verbose_name="Médico",
    )
    dia_semana = models.IntegerField(choices=DIAS_SEMANA, verbose_name="Dia da Semana")
    hora_inicio = models.TimeField(verbose_name="Hora de Início")
    hora_fim = models.TimeField(verbose_name="Hora de Fim")

    class Meta:
        unique_together = ("medico", "dia_semana", "hora_inicio", "hora_fim")
        verbose_name = "Horário de Trabalho Recorrente"
        verbose_name_plural = "Horários de Trabalho Recorrentes"
        ordering = ["medico", "dia_semana", "hora_inicio"]

    def __str__(self):
        dia = self.get_dia_semana_display()
        inicio = self.hora_inicio.strftime("%H:%M")
        fim = self.hora_fim.strftime("%H:%M")
        nome = self.medico.usuario.nome_completo
        return f"{nome} - {dia}: {inicio} - {fim}"


class Consulta(models.Model):
    medico = models.ForeignKey(
        Medico,
        on_delete=models.PROTECT,
        related_name="consultas_medico",
    )
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name="consultas_paciente",
    )
    data_hora_inicio = models.DateTimeField(verbose_name="Início da Consulta")
    data_hora_fim = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fim da Consulta",
    )
    retorno = models.BooleanField(default=False)
    sintomas = models.TextField(blank=True, null=True)
    diagnostico = models.TextField(blank=True, null=True)
    receita_virtual = models.FileField(upload_to="receitas/", blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("agendada", "Agendada"),
            ("confirmada", "Confirmada"),
            ("concluida", "Concluída"),
            ("cancelada", "Cancelada"),
        ],
        default="agendada",
    )

    lembrete_enviado = models.BooleanField(default=False)

    class Meta:
        unique_together = ("medico", "data_hora_inicio")
        ordering = ["data_hora_inicio"]
        verbose_name = "Consulta"
        verbose_name_plural = "Consultas"

    def __str__(self):
        data = self.data_hora_inicio.strftime("%d/%m/%Y %H:%M")
        nome_medico = self.medico.usuario.nome_completo
        nome_paciente = self.paciente.usuario.nome_completo
        return f"{nome_paciente} - {nome_medico} em {data}"


class ExcecaoHorario(models.Model):
    medico = models.ForeignKey(
        Medico,
        on_delete=models.CASCADE,
        related_name="excecoes_horario",
        verbose_name="Médico",
    )
    data_inicio = models.DateTimeField(verbose_name="Início da Exceção")
    data_fim = models.DateTimeField(verbose_name="Fim da Exceção")
    esta_bloqueado = models.BooleanField(
        default=True,
        verbose_name="Bloquear Agenda?",
    )
    motivo = models.TextField(verbose_name="Motivo")

    class Meta:
        verbose_name = "Exceção de Horário/Ausência"
        verbose_name_plural = "Exceções de Horário/Ausências"
        ordering = ["data_inicio"]

    def __str__(self):
        status = "BLOQUEIO" if self.esta_bloqueado else "DISPONIBILIDADE EXTRA"
        inicio = self.data_inicio.strftime("%d/%m %H:%M")
        fim = self.data_fim.strftime("%d/%m %H:%M")
        nome = self.medico.usuario.nome_completo
        return f"{nome} - {status}: {inicio} a {fim}"
