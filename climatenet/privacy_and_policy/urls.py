from django.urls import path
from .views import PrivacyPolicyView

urlpatterns = [
    path('api/privacy-policy/', PrivacyPolicyView.as_view(), name='privacy-policy'),
]