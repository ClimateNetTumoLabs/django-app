from django.contrib import admin
from backend.models import Device


# Customize the admin site title and header
admin.site.site_title = "ClimateNet Admin"
admin.site.site_header = "CliamteNet Admin"


admin.site.register(Device)
