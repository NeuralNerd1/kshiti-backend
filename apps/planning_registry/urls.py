from django.urls import path
from .views import ActionRegistryView

urlpatterns = [
    path("actions/", ActionRegistryView.as_view()),
]
