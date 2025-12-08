from django import forms
from .models import Consulta, HorarioTrabalho, ExcecaoHorario
from core.models import Medico, Paciente
from .utils import checar_conflito_consulta
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from datetime import datetime, timedelta
from .utils import checar_conflito_consulta, SLOT_MINUTOS
from django.utils import timezone

class HorarioTrabalhoForm(forms.ModelForm):
    class Meta:
        model = HorarioTrabalho
        fields = ["dia_semana", "hora_inicio", "hora_fim", "medico"]
        widgets = {
            "medico": forms.HiddenInput(),
            "dia_semana": forms.Select(attrs={"class": "form-control"}),
            "hora_inicio": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "hora_fim": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
        }

        labels = {
            "dia_semana": "Dia da Semana",
            "hora_inicio": "Hora de Início",
            "hora_fim": "Hora de Fim",
        }

    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get("hora_inicio")
        hora_fim = cleaned_data.get("hora_fim")

        if hora_inicio and hora_fim and hora_inicio >= hora_fim:
            raise forms.ValidationError("A hora de início deve ser anterior à hora de fim do turno.")

        return cleaned_data


class ExcecaoHorarioForm(forms.ModelForm):
    TIPO_EXCECAO_CHOICES = [
        (True, 'Bloqueio de Agenda (Folga/Ausência)'),
        (False, 'Disponibilidade Extra (Plantão)'),
    ]

    esta_bloqueado = forms.TypedChoiceField(
        choices=TIPO_EXCECAO_CHOICES,
        coerce=lambda x: x == 'True',
        label="Tipo de Exceção",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = ExcecaoHorario
        fields = ['data_inicio', 'data_fim', 'esta_bloqueado', 'motivo']

        widgets = {
            'motivo': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Motivo da ausência ou plantão extra.'}),
            'data_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}, format='%Y-%m-%dT%H:%M'),
            'data_fim': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}, format='%Y-%m-%dT%H:%M'),
        }

        labels = {
            'data_inicio': 'Início do Período',
            'data_fim': 'Fim do Período',
            'motivo': 'Motivo',
        }

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')

        # Normalizar para timezone-aware se necessário
        if isinstance(data_inicio, str):
            data_inicio = parse_datetime(data_inicio)
            if data_inicio:
                data_inicio = timezone.make_aware(data_inicio) if timezone.is_naive(data_inicio) else timezone.localtime(data_inicio)
            cleaned_data['data_inicio'] = data_inicio

        if isinstance(data_fim, str):
            data_fim = parse_datetime(data_fim)
            if data_fim:
                data_fim = timezone.make_aware(data_fim) if timezone.is_naive(data_fim) else timezone.localtime(data_fim)
            cleaned_data['data_fim'] = data_fim

        if data_inicio and data_fim and data_inicio >= data_fim:
            self.add_error('data_fim', "A data de fim deve ser posterior à data de início.")

        # usar timezone.now() (aware)
        if data_fim and data_fim < timezone.now():
            raise forms.ValidationError("Não é possível cadastrar exceções para um período que já terminou.")

        return cleaned_data

class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = [
            "paciente",
            "medico",
            "data_hora_inicio",
            "data_hora_fim",
            "retorno",
            "sintomas",
            "status"
        ]

        widgets = {
            "medico": forms.HiddenInput(),
            "paciente": forms.Select(attrs={"class": "form-control"}),
            "data_hora_inicio": forms.HiddenInput(),
            "data_hora_fim": forms.HiddenInput(),
            "sintomas": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["paciente"].queryset = Paciente.objects.all().order_by("usuario__nome_completo")
        if not self.instance.pk:
            self.initial.setdefault('status', 'agendada')
            self.fields['status'].widget = forms.HiddenInput(attrs={"value": "agendada"})
        else:
            self.fields['status'].widget = forms.Select(attrs={"class": "form-control"})

    def _parse_dt(self, value):
        """Aceita datetime ou string ISO e retorna aware datetime (ou None)."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return timezone.make_aware(value) if timezone.is_naive(value) else timezone.localtime(value)
        if isinstance(value, str):
            # tenta parse flexível
            dt = parse_datetime(value)
            if not dt:
                # tenta substituir espaço por T (caso venha "YYYY-MM-DD HH:MM:SS")
                try:
                    dt = parse_datetime(value.replace(' ', 'T'))
                except Exception:
                    dt = None
            if dt:
                return timezone.make_aware(dt) if timezone.is_naive(dt) else timezone.localtime(dt)
        return None

    def clean(self):
        cleaned = super().clean()
        medico = cleaned.get("medico")
        raw_inicio = cleaned.get("data_hora_inicio")
        raw_fim = cleaned.get("data_hora_fim")

        inicio = self._parse_dt(raw_inicio)
        fim = self._parse_dt(raw_fim)

        # se veio só inicio (caso do botão de slot), preenche fim automático
        if inicio and not fim:
            fim = inicio + timedelta(minutes=SLOT_MINUTOS)
            cleaned['data_hora_fim'] = fim

        cleaned['data_hora_inicio'] = inicio
        cleaned['data_hora_fim'] = fim

        # validação básica
        if inicio and fim and inicio >= fim:
            self.add_error("data_hora_fim", "A hora de fim deve ser posterior à hora de início.")
            return cleaned

        if medico:
            if inicio and inicio < timezone.now():
                raise forms.ValidationError("Não é possível agendar consultas no passado.")

            consulta_id = getattr(self.instance, 'pk', None)
            if inicio and fim and checar_conflito_consulta(medico_id=medico.pk, inicio=inicio, fim=fim, consulta_id=consulta_id):
                raise forms.ValidationError("O horário selecionado está indisponível ou em conflito com outro agendamento/bloqueio.")
        else:
            raise forms.ValidationError("Médico não foi selecionado. Reinicie o agendamento a partir da lista de médicos.")

        return cleaned

class ConsultaEdicaoForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = [
            "sintomas",
            "diagnostico",
            "receita_virtual",
            "status",
        ]

        widgets = {
            "sintomas": forms.Textarea(attrs={"rows": 3, "placeholder": "Descreva os sintomas..."}),
            "diagnostico": forms.Textarea(attrs={"rows": 3, "placeholder": "Descreva o diagnóstico..."}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def clean(self):
        cleaned = super().clean()
        status = cleaned.get("status")
        diagnostico = cleaned.get("diagnostico")

        # Exemplo de regra: não permitir concluir sem diagnóstico
        if status == "concluida" and not diagnostico:
            self.add_error("diagnostico", "Para concluir a consulta, escreva o diagnóstico.")
        
        return cleaned

