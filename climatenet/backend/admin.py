from django.contrib import admin
from .models import Device


# Customize the admin site title and header
admin.site.site_title = "ClimateNet Admin"
admin.site.site_header = "ClimateNet Admin"

admin.site.register(Device)