from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from .models import Consulta
from .forms import ConsultaForm


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.tipo == "admin"

    def handle_no_permission(self):
        messages.error(self.request, "Acesso negado. Apenas administradores podem acessar esta área.")
        return redirect("dashboard")


class ConsultaListView(AdminRequiredMixin, ListView):
    model = Consulta
    template_name = "consultas/listar_consultas.html"
    context_object_name = "consultas"
    ordering = ["-data"]


class ConsultaCreateView(AdminRequiredMixin, CreateView):
    model = Consulta
    form_class = ConsultaForm
    template_name = "consultas/form_consulta.html"
    success_url = reverse_lazy("listar_consultas")

    def form_valid(self, form):
        messages.success(self.request, "Consulta criada com sucesso!")
        return super().form_valid(form)


class ConsultaUpdateView(AdminRequiredMixin, UpdateView):
    model = Consulta
    form_class = ConsultaForm
    template_name = "consultas/form_consulta.html"
    success_url = reverse_lazy("listar_consultas")

    def form_valid(self, form):
        messages.success(self.request, "Consulta atualizada com sucesso!")
        return super().form_valid(form)


class ConsultaDeleteView(AdminRequiredMixin, DeleteView):
    model = Consulta
    template_name = "consultas/confirmar_exclusao.html"
    success_url = reverse_lazy("listar_consultas")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Consulta excluída com sucesso!")
        return super().delete(request, *args, **kwargs)
