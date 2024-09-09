from .models import Device, Participant
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

# Customize the admin site title and header
admin.site.site_title = "ClimateNet Admin"
admin.site.site_header = "ClimateNet Admin"


class ParticipantAdmin(TranslationAdmin):
    pass


admin.site.register(Device)
admin.site.register(Participant, ParticipantAdmin)
