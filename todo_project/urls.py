"""URL configuration for the to-do project."""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from tasks.forms import EmailAuthenticationForm


urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "login/",
        auth_views.LoginView.as_view(
            authentication_form=EmailAuthenticationForm,
            template_name="registration/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", include("tasks.urls")),
]
