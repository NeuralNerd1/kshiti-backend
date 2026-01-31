from django.urls import path
from .views import LoginView, LogoutView, SessionView, ResetPasswordView, CompanyBootstrapListView

urlpatterns = [
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("session/", SessionView.as_view(), name="auth-session"),
    path("reset-password/", ResetPasswordView.as_view(), name="auth-reset-password"),
    path("companies/", CompanyBootstrapListView.as_view(), name="company-list"),
]
