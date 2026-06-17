from django.urls import path

from . import views


app_name = "tasks"

urlpatterns = [
    path("", views.TaskListView.as_view(), name="list"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("new/", views.TaskCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", views.TaskUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.TaskDeleteView.as_view(), name="delete"),
    path("<int:pk>/toggle/", views.toggle_task, name="toggle"),
]
