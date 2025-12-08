from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, AccessMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.contrib import messages
from datetime import datetime, timedelta, time
from django.shortcuts import redirect, render, get_object_or_404
from django import forms
from django.views.generic import TemplateView
from django.http import JsonResponse
from .utils import calcular_slots_disponiveis
from .models import Consulta, HorarioTrabalho, ExcecaoHorario
from .forms import ConsultaForm, HorarioTrabalhoForm, ExcecaoHorarioForm, ConsultaEdicaoForm
from core.models import Medico, Usuario, Paciente
from django.views import View
from django.shortcuts import get_object_or_404
from .utils import SLOT_MINUTOS
from django.db.models import Q
from django.utils.dateparse import parse_datetime 
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.tipo == "admin" or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "Acesso negado. Apenas administradores podem acessar esta área.")
        return redirect("home")

class AdminOrMedicoRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        user = request.user
        is_admin = user.tipo == "admin" or user.is_superuser
        is_medico = user.tipo == "medico"
        if not (is_admin or is_medico):
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

class AdminOrAtendenteRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return (
            self.request.user.is_superuser or self.request.user.tipo == "admin" or self.request.user.tipo == "atendente"
        )

class MedicoAgendaJsonView(View):
    def get(self, request, *args, **kwargs):
        medico_id = kwargs.get('medico_id')
        
        if not medico_id:
            return JsonResponse({"erro": "ID do médico não fornecido."}, status=400)
        
        try:
            slots_disponiveis = calcular_slots_disponiveis(medico_id)
            return JsonResponse(slots_disponiveis)
        
        except Exception as e:
            return JsonResponse({"erro": f"Ocorreu um erro no cálculo da agenda: {e}"}, status=500)

class GerenciarAgendaView(LoginRequiredMixin, AdminOrMedicoRequiredMixin, View):
    template_name = 'templates_consulta/gerenciar_agenda.html'
    DURACAO_CONSULTA = 30

    def get_medico(self):
        if self.request.user.tipo == "medico":
            try:
                return Medico.objects.get(usuario=self.request.user)
            except Medico.DoesNotExist:
                return None
        return None

    def get(self, request, *args, **kwargs):
        medico_instance = self.get_medico()
        if not medico_instance and request.user.tipo == Usuario.TipoUsuario.MEDICO:
            messages.error(request, "Seu perfil de médico não foi encontrado.")
            return redirect(reverse_lazy('home'))
        if not medico_instance and request.user.tipo == Usuario.TipoUsuario.ADMINISTRADOR:
            messages.info(request, "Administradores precisam selecionar um médico para gerenciar a agenda.")
            return redirect(reverse_lazy('home'))
        horarios = HorarioTrabalho.objects.filter(medico=medico_instance).order_by('dia_semana', 'hora_inicio')
        excecoes = ExcecaoHorario.objects.filter(medico=medico_instance).order_by('data_inicio')
        form_horario = HorarioTrabalhoForm(initial={'medico': medico_instance.pk})
        context = {
            'medico': medico_instance,
            'horarios': horarios,
            'excecoes': excecoes,
            'form_horario': form_horario,
            'duracao_consulta': self.DURACAO_CONSULTA
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        medico_instance = self.get_medico()
        if not medico_instance:
            return redirect(reverse_lazy('home'))
        mutable_post = request.POST.copy()
        mutable_post['medico'] = medico_instance.pk
        form_horario = HorarioTrabalhoForm(mutable_post)
        if form_horario.is_valid():
            form_horario.save()
            messages.success(request, "Horário recorrente adicionado com sucesso!")
            return redirect(reverse_lazy('gerenciar_agenda'))
        messages.error(request, "Erro ao adicionar horário. Verifique os dados.")
        horarios = HorarioTrabalho.objects.filter(medico=medico_instance).order_by('dia_semana', 'hora_inicio')
        excecoes = ExcecaoHorario.objects.filter(medico=medico_instance).order_by('data_inicio')
        context = {
            'medico': medico_instance,
            'horarios': horarios,
            'excecoes': excecoes,
            'form_horario': form_horario,
            'duracao_consulta': self.DURACAO_CONSULTA
        }
        return render(request, self.template_name, context)

class HorarioTrabalhoUpdateView(LoginRequiredMixin, AdminOrMedicoRequiredMixin, UpdateView):
    model = HorarioTrabalho
    form_class = HorarioTrabalhoForm
    success_url = reverse_lazy('gerenciar_agenda')
    template_name = 'templates_consulta/horario_trabalho_form.html'

    def get_queryset(self):
        return self.model.objects.filter(medico__usuario=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar Horário Recorrente'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Horário recorrente atualizado com sucesso.")
        return super().form_valid(form)

class HorarioTrabalhoDeleteView(LoginRequiredMixin, AdminOrMedicoRequiredMixin, DeleteView):
    model = HorarioTrabalho
    success_url = reverse_lazy('gerenciar_agenda')
    template_name = 'templates_consulta/confirmar_exclusao.html'

    def get_queryset(self):
        return self.model.objects.filter(medico__usuario=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Horário recorrente excluído com sucesso.")
        return super().delete(request, *args, **kwargs)

class ExcecaoHorarioCreateView(LoginRequiredMixin, AdminOrMedicoRequiredMixin, CreateView):
    model = ExcecaoHorario
    form_class = ExcecaoHorarioForm
    success_url = reverse_lazy('gerenciar_agenda')
    template_name = 'templates_consulta/excecao_horario_form.html'

    def form_valid(self, form):
        try:
            medico_instance = Medico.objects.get(usuario=self.request.user)
        except Medico.DoesNotExist:
            return redirect(reverse_lazy('home'))
        form.instance.medico = medico_instance
        messages.success(self.request, "Exceção de horário adicionada com sucesso.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Adicionar Ausência ou Horário Extra'
        return context

class ExcecaoHorarioUpdateView(LoginRequiredMixin, AdminOrMedicoRequiredMixin, UpdateView):
    model = ExcecaoHorario
    form_class = ExcecaoHorarioForm
    success_url = reverse_lazy('gerenciar_agenda')
    template_name = 'templates_consulta/excecao_horario_form.html'

    def get_queryset(self):
        return self.model.objects.filter(medico__usuario=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar Ausência ou Horário Extra'
        return context

    def form_valid(self, form):
        messages.success(self.request, "Exceção de horário atualizada com sucesso.")
        return super().form_valid(form)

class ExcecaoHorarioDeleteView(LoginRequiredMixin, AdminOrMedicoRequiredMixin, DeleteView):
    model = ExcecaoHorario
    success_url = reverse_lazy('gerenciar_agenda')
    template_name = 'templates_consulta/confirmar_exclusao.html'

    def get_queryset(self):
        return self.model.objects.filter(medico__usuario=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Exceção de horário excluída com sucesso.")
        return super().delete(request, *args, **kwargs)

class ConsultaListView(LoginRequiredMixin, AdminOrAtendenteRequiredMixin, ListView):
    model = Consulta
    template_name = "templates_consulta/listar_consultas.html"
    context_object_name = "consultas"
    paginate_by = 10  # itens por página

    def get_template_names(self):
        # mantém a lógica que usa template diferente para médicos
        if getattr(self.request.user, "tipo", None) == "medico":
            return ["templates_consulta/minhas_consultas.html"]
        return ["templates_consulta/listar_consultas.html"]

    def get_queryset(self):
        user = self.request.user
        user_tipo = getattr(user, "tipo", None)

        # base queryset com select_related para otimizar queries
        base_qs = Consulta.objects.select_related("paciente__usuario", "medico__usuario")

        # Admin / superuser vê todas as consultas
        if user.is_superuser or user_tipo == "admin":
            qs = base_qs.order_by("-data_hora_inicio")

        # Médico vê apenas suas consultas
        elif user_tipo == "medico":
            try:
                medico = Medico.objects.get(usuario=user)
            except Medico.DoesNotExist:
                return Consulta.objects.none()
            qs = base_qs.filter(medico=medico).order_by("-data_hora_inicio")

        else:
            return Consulta.objects.none()

        # FILTRO OPCIONAL por médico via GET (ex.: ?medico=3)
        medico_id = self.request.GET.get("medico")
        if medico_id:
            try:
                # filtra por pk do médico (seguro contra valores inválidos)
                qs = qs.filter(medico__pk=int(medico_id))
            except (ValueError, TypeError):
                pass

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        user_tipo = getattr(user, "tipo", None)

        # ----- TITULO DINÂMICO -----
        if user.is_superuser or user_tipo == "admin":
            context['titulo'] = "Todas as Consultas do Sistema"
        elif user_tipo == "medico":
            context['titulo'] = "Minhas Próximas Consultas"
        else:
            context['titulo'] = "Consultas"

        # ----- LISTA DE MÉDICOS PARA O FILTRO -----
        if user.is_superuser or user_tipo == "admin":
            medicos_qs = Medico.objects.select_related("usuario").all()
        elif user_tipo == "medico":
            medicos_qs = Medico.objects.select_related("usuario").filter(usuario=user)
        else:
            medicos_qs = Medico.objects.none()

        context["medicos"] = medicos_qs
        context["filtro_medico"] = self.request.GET.get("medico", "")

        return context
        

def gerar_horarios_disponiveis(medico, data):

    dia_semana = data.weekday()

    # 1. Buscar horário base do médico neste dia da semana
    horarios_base = HorarioTrabalho.objects.filter(
        medico=medico,
        dia_semana=dia_semana
    )

    if not horarios_base.exists():
        return []  # médico não trabalha neste dia

    # Lista final de horários
    horarios = []

    for h in horarios_base:
        inicio = datetime.combine(data, h.hora_inicio)
        fim = datetime.combine(data, h.hora_fim)

        atual = inicio
        while atual < fim:
            horarios.append(atual)
            atual += timedelta(minutes=30)  # slot de 30 minutos

    # 2. Remover horários já ocupados
    consultas = Consulta.objects.filter(
        medico=medico,
        data_hora_inicio__date=data
    ).values_list("data_hora_inicio", flat=True)

    horarios = [h for h in horarios if h not in consultas]

    # 3. Remover horários bloqueados por exceções
    excecoes = ExcecaoHorario.objects.filter(
        medico=medico,
        esta_bloqueado=True,
        data_inicio__date=data,
    )

    for ex in excecoes:
        horarios = [
            h for h in horarios
            if not (ex.data_inicio <= h <= ex.data_fim)
        ]

    return horarios

class ConsultaDeleteView(AdminRequiredMixin, DeleteView):
    model = Consulta
    template_name = "templates_consulta/confirmar_exclusao.html"
    success_url = reverse_lazy("listar_consultas")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Consulta excluída com sucesso!")
        return super().delete(request, *args, **kwargs)

class ConsultaCreateByMedicoView(AdminOrAtendenteRequiredMixin, CreateView):
    model = Consulta
    form_class = ConsultaForm
    template_name = "templates_consulta/form_consulta.html"
    success_url = reverse_lazy("listar_consultas")

    def get_initial(self):
        # Este método está OK para preencher o form.instance inicialmente.
        # Ele só lida com dados do GET.
        initial = super().get_initial()
        medico_id = self.kwargs.get('medico_id') or self.request.GET.get('medico')
        if medico_id:
            medico = get_object_or_404(Medico, pk=medico_id)
            initial['medico'] = medico
        # slot na querystring (ex: ?slot=2025-12-10T10:00:00-03:00)
        slot = self.request.GET.get('slot')
        if slot:
            initial['data_hora_inicio'] = slot
            try:
                from django.utils.dateparse import parse_datetime
                dt = parse_datetime(slot)
                if dt:
                    fim = dt + timedelta(minutes=SLOT_MINUTOS)
                    initial['data_hora_fim'] = fim.isoformat()
            except Exception:
                pass
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Variáveis para o Card de Confirmação Visual
        context['medico_nome'] = None
        context['horario_selecionado'] = None
        context['paciente_nome_inicial'] = "" # Variável para preencher o campo de busca de texto

        # Tenta obter o ID do médico: 1. URL kwargs, 2. GET (acesso inicial), 3. POST (erro de form)
        medico_id = self.kwargs.get('medico_id') or self.request.GET.get('medico') or self.request.POST.get('medico')
        
        if medico_id:
            try:
                medico = get_object_or_404(Medico, pk=int(medico_id))
                context['medico_atual'] = medico
                # Preenche o nome do médico
                context['medico_nome'] = medico.usuario.nome_completo
                context['slots_disponiveis'] = calcular_slots_disponiveis(medico.pk, dias_a_frente=14)
            except Medico.DoesNotExist:
                context['slots_disponiveis'] = {}
                context['medico_atual'] = None
        else:
            context['slots_disponiveis'] = {}
            context['medico_atual'] = None

        # Tenta obter o horário selecionado: 1. GET, 2. POST (se falhou a validação)
        slot_str = self.request.GET.get('slot') or self.request.POST.get('data_hora_inicio')
        if slot_str:
            try:
                # parse_datetime lida com o formato ISO
                context['horario_selecionado'] = parse_datetime(slot_str)
            except Exception:
                pass

        # 🎯 CORREÇÃO 3: Obter nome do Paciente para preencher o campo de busca de texto
        
        # 1. Tenta obter o ID do paciente do formulário (que pode estar no POST ou na instância se for edição)
        paciente_id = self.request.POST.get('paciente')
        
        # 2. Se for a primeira carga ou se não houver POST, verifica se o form já foi instanciado com um paciente (edição)
        if not paciente_id and self.object and self.object.paciente:
             paciente_id = self.object.paciente.pk
        
        # 3. Se o formulário tiver erros, ele pode ter o paciente no self.request.POST
        if self.request.POST.get('paciente') and not paciente_id:
            paciente_id = self.request.POST.get('paciente')
            
        if paciente_id:
            try:
                # Busca o paciente pelo ID
                paciente = Paciente.objects.get(pk=paciente_id)
                # Preenche a variável que será usada no atributo `value` do template
                context['paciente_nome_inicial'] = paciente.usuario.nome_completo if hasattr(paciente, 'usuario') else paciente.nome_completo
            except Paciente.DoesNotExist:
                pass


        context['medicos_list'] = Medico.objects.all().order_by('usuario__nome_completo')
        
        return context

class HorariosDisponiveisAjaxView(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        medico_id = request.GET.get('medico')
        data_str = request.GET.get('data')  # espera YYYY-MM-DD
        if not medico_id or not data_str:
            return JsonResponse({'error': 'medico e data são obrigatórios'}, status=400)
        try:
            medico = Medico.objects.get(pk=medico_id)
            data = datetime.strptime(data_str, "%Y-%m-%d").date()
            slots = gerar_horarios_disponiveis(medico, data)
            # serializar para strings ISO local
            slots_str = [s.strftime("%Y-%m-%d %H:%M:%S") for s in slots]
            display = [s.strftime("%H:%M") for s in slots]
            return JsonResponse({'slots': slots_str, 'display': display})
        except Medico.DoesNotExist:
            return JsonResponse({'error': 'Médico não encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class MedicoSlotsView(AdminRequiredMixin, TemplateView):
    template_name = "templates_consulta/slots_only.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        medico_id = kwargs.get('medico_id') or self.request.GET.get('medico')
        if not medico_id:
            context['error'] = "Médico não informado."
            context['slots_disponiveis'] = {}
            context['medico'] = None
            return context

        medico = get_object_or_404(Medico, pk=int(medico_id))
        context['medico'] = medico
        context['slots_disponiveis'] = calcular_slots_disponiveis(medico.pk, dias_a_frente=14)
        return context

@require_POST
def marcar_concluida(request, pk):
    """Muda o status para 'concluida', verificando se o usuário logado é o médico da consulta."""
    consulta = get_object_or_404(Consulta, pk=pk)
    
    if request.user != consulta.medico.usuario:
        # Se não for o médico responsável, levanta uma exceção de permissão
        raise PermissionDenied("Você não tem permissão para concluir esta consulta.")
    
    # --- Lógica da Ação ---
    if consulta.status == 'agendada':
        consulta.status = 'concluida'
        consulta.save()
        messages.success(request, f"Consulta de {consulta.paciente.usuario.nome_completo} concluída.")
    else:
         messages.warning(request, f"A consulta não pode ser concluída (status: {consulta.get_status_display()}).")
         
    return redirect('lista_consultas')

class ConsultaUpdateView(AdminRequiredMixin, UpdateView):
    model = Consulta
    form_class = ConsultaForm
    template_name = "templates_consulta/form_consulta.html"
    success_url = reverse_lazy("listar_consultas")

    def form_valid(self, form):
        messages.success(self.request, "Consulta atualizada com sucesso!")
        return super().form_valid(form)

class ConsultaEditarView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Consulta
    form_class = ConsultaEdicaoForm
    template_name = "templates_consulta/editar_consulta.html"
    context_object_name = "consulta"
    success_url = reverse_lazy("listar_consultas")

    def get_queryset(self):
        """Restringe quem pode editar a consulta."""
        qs = Consulta.objects.select_related(
            "medico__usuario", "paciente__usuario"
        )

        user = self.request.user
        tipo = getattr(user, "tipo", None)

        # Admin pode editar tudo
        if user.is_superuser or tipo == "admin":
            return qs

        # Médico só pode editar suas consultas
        if tipo == "medico":
            try:
                medico = Medico.objects.get(usuario=user)
            except Medico.DoesNotExist:
                return Consulta.objects.none()
            return qs.filter(medico=medico)

        # Outros não podem editar
        return Consulta.objects.none()

    def test_func(self):
        """UserPassesTestMixin — verifica permissão."""
        consulta = self.get_object()
        return consulta in self.get_queryset()

    def form_valid(self, form):
        messages.success(self.request, "Consulta atualizada com sucesso!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Erro ao atualizar a consulta. Verifique os dados.")
        return super().form_invalid(form)

@login_required
def minhas_consultas_paciente(request):
    """
    Lista todas as consultas do paciente logado.
    """
    user = request.user
    
    # 1. Verificação de Tipo (Boas Práticas)
    # Garante que só pacientes vejam esta página
    if not hasattr(user, 'tipo') or user.tipo != "paciente":
        # Se não for paciente, retorna uma lista vazia ou redireciona
        consultas = Consulta.objects.none()
        # Opcional: Adicione um redirecionamento aqui, se preferir
        # return redirect('alguma_outra_pagina_do_dashboard')
    else:
        # 2. Filtro (Correto, usando a relação paciente__usuario)
        consultas = Consulta.objects.filter(
            paciente__usuario=user 
        ).select_related(
            "medico", 
            "paciente",
            "medico__usuario", 
            "medico__especialidade"
        ).order_by("data_hora_inicio") # Ordena corretamente pelo campo do seu modelo

    # 3. Renderização
    context = {
        'consultas': consultas
    }
    return render(request, 'templates_consulta/minhas_consultas_paciente.html', context)

@login_required
def detalhes_consulta(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk)

    user = request.user

    # 🔒 Permissões:
    # Paciente só pode ver a consulta dele
    if user.tipo == "paciente" and consulta.paciente.usuario != user:
        return render(request, "403.html", status=403)

    # Médico só pode ver as consultas dele
    if user.tipo == "medico" and consulta.medico.usuario != user:
        return render(request, "403.html", status=403)

    # Admin e Atendente podem ver tudo
    return render(request, "templates_consulta/detalhes_consulta.html", {"consulta": consulta})
