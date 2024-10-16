from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('device_inner/', include('backend.urls')),
    path('api/', include('backend.urls'))
]

# Prefix URL patterns with the language code
urlpatterns += i18n_patterns(
    path('', TemplateView.as_view(template_name='index.html'), name='main-page'),
    path('about/', TemplateView.as_view(template_name='index.html'), name='about-page'),
    path('diy/', TemplateView.as_view(template_name='index.html'), name='diy-page'),
    path('device/<str:device_id>/', TemplateView.as_view(template_name='index.html'), name='device-detail-page'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
