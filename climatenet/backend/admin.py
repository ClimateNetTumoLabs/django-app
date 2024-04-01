from django.contrib import admin
from backend.models import Device, About, DeviceDetail, Footer, ContactUs


# Customize the admin site title and header
admin.site.site_title = "ClimateNet Admin"
admin.site.site_header = "ClimateNet Admin"


admin.site.register(Device)
admin.site.register(About)
admin.site.register(DeviceDetail)
admin.site.register(Footer)
admin.site.register(ContactUs)
