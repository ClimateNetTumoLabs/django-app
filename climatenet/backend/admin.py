from django.contrib import admin
from backend.models import DeviceDetail


# Customize the admin site title and header
admin.site.site_title = "ClimateNet Admin"
admin.site.site_header = "ClimateNet Admin"

admin.site.register(DeviceDetail)