from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import SignUpForm, TaskForm
from .models import Task


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("tasks:list")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "Account created. Welcome to TaskFlow.")
        return response


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "all")
        priority = self.request.GET.get("priority", "all")

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        if status == "active":
            queryset = queryset.filter(completed=False)
        elif status == "completed":
            queryset = queryset.filter(completed=True)
        if priority in dict(Task.Priority.choices):
            queryset = queryset.filter(priority=priority)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_tasks = Task.objects.all()
        context.update(
            {
                "total_count": all_tasks.count(),
                "active_count": all_tasks.filter(completed=False).count(),
                "completed_count": all_tasks.filter(completed=True).count(),
                "current_query": self.request.GET.get("q", ""),
                "current_status": self.request.GET.get("status", "all"),
                "current_priority": self.request.GET.get("priority", "all"),
                "priority_choices": Task.Priority.choices,
            }
        )
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Task created.")
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Task updated.")
        return super().form_valid(form)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = "tasks/task_confirm_delete.html"
    success_url = reverse_lazy("tasks:list")

    def form_valid(self, form):
        messages.success(self.request, "Task deleted.")
        return super().form_valid(form)


@require_POST
@login_required
def toggle_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.completed = not task.completed
    task.save(update_fields=["completed", "updated_at"])
    messages.success(request, "Task marked complete." if task.completed else "Task reopened.")
    return redirect("tasks:list")
