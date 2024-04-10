from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.shortcuts import redirect

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('admin/', admin.site.urls),
    path('device/<str:device_id>/', TemplateView.as_view(template_name='index.html'), name='device_detail'),
    path('about/', TemplateView.as_view(template_name='index.html'), name='about'),
    path('device_data/', include('backend.urls')),  # Include your app's URLs here
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Redirect /admin to /admin/
# urlpatterns.append(re_path(r'^admin$', lambda x: redirect('/admin/')))
