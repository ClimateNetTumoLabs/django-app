from django.urls import path
from .views import CollectUserDataView

urlpatterns = [
    path('save-cookies/', CollectUserDataView.as_view(), name='save_cookies'),
]