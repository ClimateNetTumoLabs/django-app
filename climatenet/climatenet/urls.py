from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='main-page'),
    path('about/', TemplateView.as_view(template_name='index.html'), name='about-page'),
    path('device/<str:device_id>/', TemplateView.as_view(template_name='index.html'), name='device-detail-page'),
    path('admin/', admin.site.urls),
    path('device_inner/', include('backend.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
