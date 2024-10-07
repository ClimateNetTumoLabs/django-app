from django.contrib import admin
from .models import Device, TeamMember
from modeltranslation.admin import TranslationAdmin

# Customize the admin site title and header
admin.site.site_title = "ClimateNet Admin"
admin.site.site_header = "ClimateNet Admin"


class TeamMemberAdmin(TranslationAdmin):
    pass


class DeviceAdmin(TranslationAdmin):
    pass


admin.site.register(Device, DeviceAdmin)
admin.site.register(TeamMember, TeamMemberAdmin)