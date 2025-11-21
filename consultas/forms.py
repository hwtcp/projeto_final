from django import forms
from .models import Consulta, HorarioTrabalho
from core.models import Medico, Paciente

class HorarioTrabalhoForm(forms.ModelForm):
    class Meta:
        model = HorarioTrabalho
        fields = ["dia_semana", "hora_inicio", "hora_fim", "medico"]

        # O campo 'medico' será escondido na view do médico,
        # mas mantido para ser preenchido programaticamente.
        widgets = {
            "medico": forms.HiddenInput(),
            # Usar Select para o dia da semana é o padrão, mas customizar a Hora
            "dia_semana": forms.Select(attrs={"class": "form-control"}),
            # Utiliza TextInput com type='time' do HTML5 para um seletor de tempo amigável
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

        # Validação: Garante que a hora de início não seja depois da hora de fim
        if hora_inicio and hora_fim and hora_inicio >= hora_fim:
            raise forms.ValidationError("A hora de início deve ser anterior à hora de fim do turno.")

        return cleaned_data


class ConsultaForm(forms.ModelForm):
    # Campo extra para selecionar o médico (será preenchido antes da data/hora)
    medico_selecionado = forms.ModelChoiceField(
        queryset=Medico.objects.all(),
        label="Médico",
        required=True,
        # Você pode adicionar um atributo para ser um select2 ou outro widget
        widget=forms.Select(attrs={"class": "form-control"}),
        empty_label="--- Selecione o Médico ---",
    )

    # Campos de data/hora serão hidden ou preenchidos via JavaScript,
    # pois o usuário selecionará um slot pré-calculado
    data_hora_selecionada = forms.DateTimeField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Consulta
        # Incluímos apenas os campos necessários para a CRIAÇÃO do agendamento
        fields = ["paciente", "medico", "data_hora_inicio", "data_hora_fim", "retorno", "sintomas", "status"]

        widgets = {
            "medico": forms.HiddenInput(),
            "paciente": forms.Select(attrs={"class": "form-control"}),  # Se o agendamento for pelo Atendente
            # Estes campos de data/hora serão preenchidos pela lógica de slot e devem ser hidden
            "data_hora_inicio": forms.HiddenInput(),
            "data_hora_fim": forms.HiddenInput(),
            "sintomas": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "status": forms.HiddenInput(attrs={"value": "agendada"}),
        }

        labels = {
            "paciente": "Paciente",
            "retorno": "É consulta de retorno?",
            "sintomas": "Motivo ou Sintomas da Consulta",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajusta a queryset de pacientes (pode ser necessário se tiver filtros de acesso)
        self.fields["paciente"].queryset = Paciente.objects.all().order_by("usuario__nome_completo")

        # Move o campo medico_selecionado para o topo para ser processado primeiro
        self.order_fields(["medico_selecionado", "paciente", "retorno", "sintomas"])

    def clean(self):
        cleaned_data = super().clean()

        # Lógica de validação se necessário

        return cleaned_data
