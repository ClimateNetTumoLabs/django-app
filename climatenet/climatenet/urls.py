from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.generic import RedirectView
from django.shortcuts import HttpResponseRedirect

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html')),
    re_path(r'^admin$', lambda x: HttpResponseRedirect('/admin/')),
    path('admin/', admin.site.urls),
    path('', include('backend.urls')),  # Include your app's URLs here
    path('device_cl/<str:device_id>', TemplateView.as_view(template_name='index.html')),
    re_path("about", TemplateView.as_view(template_name='index.html'))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
