from django import forms
from .models import Consulta, AvisoAusencia
from core.models import Medico, Paciente

class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = [
            'paciente',
            'medico',
            'data',
            'retorno',
            'sintomas',
            'diagnostico',
            'receita_virtual',
        ]
        labels = {
            'paciente': 'Paciente',
            'medico': 'Médico',
            'data': 'Data e hora da consulta',
            'retorno': 'É retorno?',
            'sintomas': 'Sintomas relatados',
            'diagnostico': 'Diagnóstico',
            'receita_virtual': 'Receita (opcional)',
        }
        widgets = {
            'data': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'sintomas': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descreva os sintomas...'}),
            'diagnostico': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descreva o diagnóstico...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['paciente'].queryset = Paciente.objects.select_related('usuario').order_by('usuario__nome_completo')
        self.fields['medico'].queryset = Medico.objects.select_related('usuario').order_by('usuario__nome_completo')

class AvisoAusenciaForm(forms.ModelForm):
    class Meta:
        model = AvisoAusencia
        fields = ['medico', 'data_inicio', 'data_fim', 'motivo']
        labels = {
            'medico': 'Médico',
            'data_inicio': 'Data e hora de início',
            'data_fim': 'Data e hora de término',
            'motivo': 'Motivo da ausência',
        }
        widgets = {
            'data_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'data_fim': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'motivo': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descreva o motivo da ausência...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['medico'].queryset = Medico.objects.select_related('usuario').order_by('usuario__nome_completo')












