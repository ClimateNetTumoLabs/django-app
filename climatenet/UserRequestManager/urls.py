from django.urls import path
from .views import SubmitFormView, download_certificate


urlpatterns = [

    path('submit-form/', SubmitFormView.as_view(), name='submit-form'),
    path('download_certificate/<str:device_id>/', download_certificate, name='download_certificate'),
]

