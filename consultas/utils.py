# utils.py
from datetime import datetime, timedelta, time as _time, date as _date
from typing import Dict, List
from django.utils import timezone
from django.db.models import Q

from .models import HorarioTrabalho, ExcecaoHorario, Consulta
from core.models import Medico

# Ajuste se quiser outro intervalo de slot
SLOT_MINUTOS = 30
DURACAO_CONSULTA = timedelta(minutes=SLOT_MINUTOS)


def _make_aware(dt: datetime) -> datetime:
    """Retorna datetime aware no timezone corrente. Se já for aware, normaliza para timezone local."""
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, timezone.get_current_timezone())
    return timezone.localtime(dt, timezone.get_current_timezone())


def _day_to_model_day(d: _date) -> int:
    """
    Converte Python weekday() para o que o model HorarioTrabalho usa:
    - Python weekday(): Monday=0 ... Sunday=6
    - Model: 0=Domingo, 1=Segunda, ..., 6=Sábado
    Regra: (weekday + 1) % 7
    """
    return (d.weekday() + 1) % 7


def calcular_slots_disponiveis(medico_id: int, dias_a_frente: int = 7) -> Dict[str, List[str]]:
    """
    Retorna um dicionário { 'YYYY-MM-DD': ['ISO_SLOT1', 'ISO_SLOT2', ...'], ... }
    para os próximos `dias_a_frente` dias (a partir de hoje).
    """
    try:
        medico = Medico.objects.get(pk=medico_id)
    except Medico.DoesNotExist:
        return {}

    tz = timezone.get_current_timezone()
    hoje_date = timezone.localtime(timezone.now(), tz).date()
    data_fim_busca = hoje_date + timedelta(days=dias_a_frente)

    # Periodo total para buscar consultas/exceções (da meia-noite de hoje até fim do último dia)
    period_start = _make_aware(datetime.combine(hoje_date, _time.min))
    period_end = _make_aware(datetime.combine(data_fim_busca, _time.max))

    # Horários recorrentes do médico
    horarios_recorrentes = HorarioTrabalho.objects.filter(medico=medico)

    # Exceções que intersectam o período de interesse
    excecoes = ExcecaoHorario.objects.filter(
        medico=medico,
        data_fim__gte=period_start,
        data_inicio__lte=period_end
    )

    # Consultas existentes no período (apenas status que ocupam)
    consultas_agendadas = Consulta.objects.filter(
        medico=medico,
        status__in=['agendada', 'confirmada'],
        data_hora_inicio__lte=period_end,
        data_hora_fim__gte=period_start
    )

    # Construir lista de intervalos ocupados (aware)
    intervalos_ocupados = []

    for exc in excecoes.filter(esta_bloqueado=True):
        inicio_ex = _make_aware(exc.data_inicio)
        fim_ex = _make_aware(exc.data_fim)
        intervalos_ocupados.append((inicio_ex, fim_ex))

    for cons in consultas_agendadas:
        inicio_cons = _make_aware(cons.data_hora_inicio)
        if cons.data_hora_fim:
            fim_cons = _make_aware(cons.data_hora_fim)
        else:
            fim_cons = inicio_cons + DURACAO_CONSULTA
        intervalos_ocupados.append((inicio_cons, fim_cons))

    slots_disponiveis = {}

    for i in range(dias_a_frente):
        data_atual = hoje_date + timedelta(days=i)
        model_day = _day_to_model_day(data_atual)

        # horários recorrentes desse dia (ex.: segunda, terça...)
        horarios_dia = horarios_recorrentes.filter(dia_semana=model_day)

        # exceções do tipo disponibilidade extra (esta_bloqueado=False) que ocorram no dia
        extras_dia = excecoes.filter(
            esta_bloqueado=False,
            data_inicio__date__lte=data_atual,
            data_fim__date__gte=data_atual
        )

        # construir períodos de trabalho (lista de tuplas aware)
        periodos_trabalho = []
        for h in horarios_dia:
            inicio_naive = datetime.combine(data_atual, h.hora_inicio)
            fim_naive = datetime.combine(data_atual, h.hora_fim)
            inicio = _make_aware(inicio_naive)
            fim = _make_aware(fim_naive)
            # pular se fim <= inicio por configuração inválida
            if fim <= inicio:
                continue
            periodos_trabalho.append((inicio, fim))

        for e in extras_dia:
            # exceções já são datetimes (possivelmente com tz)
            inicio_e = _make_aware(e.data_inicio)
            fim_e = _make_aware(e.data_fim)
            if fim_e <= inicio_e:
                continue
            periodos_trabalho.append((inicio_e, fim_e))

        if not periodos_trabalho:
            continue

        # ordenar e (opcional) mesclar periodos para evitar sobreposição duplicada
        periodos_trabalho.sort(key=lambda x: x[0])

        slots_dia = []
        now = timezone.localtime(timezone.now(), tz)

        for inicio_periodo, fim_periodo in periodos_trabalho:
            # se o período começa antes do 'now' no dia atual, iniciamos do próximo slot válido
            slot_inicio = inicio_periodo
            if data_atual == hoje_date and slot_inicio < now:
                # avançar para o próximo slot de 30min a partir de now
                mins = (now.minute // SLOT_MINUTOS) * SLOT_MINUTOS
                proximo = now.replace(minute=mins, second=0, microsecond=0)
                if proximo < now:
                    proximo = proximo + timedelta(minutes=SLOT_MINUTOS)
                slot_inicio = max(slot_inicio, proximo)

            # gerar slots
            while slot_inicio + DURACAO_CONSULTA <= fim_periodo:
                slot_fim = slot_inicio + DURACAO_CONSULTA

                # verificar conflito com intervalos ocupados
                livre = True
                for ocupado_inicio, ocupado_fim in intervalos_ocupados:
                    # se intersecta -> não livre
                    if max(slot_inicio, ocupado_inicio) < min(slot_fim, ocupado_fim):
                        livre = False
                        break

                if livre:
                    # armazenar ISO (aware) — bom para JSON/frontend
                    slots_dia.append(slot_inicio.isoformat())

                slot_inicio = slot_inicio + DURACAO_CONSULTA

        if slots_dia:
            slots_disponiveis[data_atual.isoformat()] = slots_dia

    return slots_disponiveis


def checar_conflito_consulta(medico_id: int, inicio: datetime, fim: datetime, consulta_id: int = None) -> bool:
    """
    Retorna True se houver conflito (consulta / bloqueio / início no passado), False se livre.
    `inicio` e `fim` podem ser naive ou aware — serão normalizados.
    """
    inicio = _make_aware(inicio)
    fim = _make_aware(fim)

    # conflito com outras consultas
    qs = Consulta.objects.filter(
        medico_id=medico_id,
        status__in=['agendada', 'confirmada'],
        data_hora_inicio__lt=fim,
        data_hora_fim__gt=inicio
    )
    if consulta_id:
        qs = qs.exclude(pk=consulta_id)
    if qs.exists():
        return True

    # conflito com bloqueios/exceções
    bloqueios = ExcecaoHorario.objects.filter(
        medico_id=medico_id,
        esta_bloqueado=True,
        data_inicio__lt=fim,
        data_fim__gt=inicio
    )
    if bloqueios.exists():
        return True

    # início no passado
    if inicio < timezone.now():
        return True

    return False
