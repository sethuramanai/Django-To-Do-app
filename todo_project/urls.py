"""URL configuration for the to-do project."""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import include, path

from tasks.forms import EmailAuthenticationForm


def root_redirect(request):
    return redirect("login")


urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "login/",
        auth_views.LoginView.as_view(
            authentication_form=EmailAuthenticationForm,
            template_name="registration/login.html",
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", root_redirect),
    path("tasks/", include("tasks.urls")),
]
