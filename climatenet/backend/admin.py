from django.contrib import admin
from .models import Device, TeamMember,UserForm
from modeltranslation.admin import TranslationAdmin
from .mailSender import send_approval_email

# Customize the admin site title and header
admin.site.site_title = "ClimateNet Admin"
admin.site.site_header = "ClimateNet Admin"


class TeamMemberAdmin(TranslationAdmin):
    pass


class DeviceAdmin(TranslationAdmin):
    pass

class UserFormAdmin(admin.ModelAdmin):
    list_display = ('name','email','coordinates', 'status', 'submitted_at')
    actions = ['approve_forms', 'reject_forms','delete_user']

    def approve_forms(self, request, queryset):
        queryset.update(status='approved')
        # Send approval email logic
        for form in queryset:
            send_approval_email(form.user)
        self.message_user(request, "Selected forms have been approved")

    def reject_forms(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, "Selected forms have been rejected")
    def delete_user(self, request, queryset):
        # queryset.update(status='rejected')
        self.message_user(request, "Selected forms have been deleted")

admin.site.register(Device, DeviceAdmin)
admin.site.register(TeamMember, TeamMemberAdmin)
admin.site.register(UserForm,UserFormAdmin)