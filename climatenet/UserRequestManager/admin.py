from django.contrib import admin
from .models import UserForm, ApprovedUser
from .helper import send_mail

class UserFormAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'coordinates', 'status', 'submitted_at')
    actions = ['approve_forms', 'reject_forms', 'delete_user']

    def approve_forms(self, request, queryset):
        approved_users = []
        for form in queryset:
            
            if form.status == 'approved':
                continue
            
            
            approved_user = ApprovedUser(
                name=form.name,
                email=form.email,
                phone=None,  
                coordinates=form.coordinates,
                device_id=form.device_id,
            )
            approved_users.append(approved_user)
            
            
            form.status = 'approved'
            form.save()

            
            send_mail(
                recipient=form.email,
                subject="Approval Notification",
                attachment="approval.html",
                html_file_path="approval.html",
                name=form.name
            )
        
        ApprovedUser.objects.bulk_create(approved_users)

        self.message_user(request, "Selected forms have been approved and moved to Approved Users.")

    def reject_forms(self, request, queryset):
        queryset.update(status='rejected')
        for form in queryset:
            send_mail(
                recipient=form.email,
                subject="Rejection Notification",
                attachment=None,
                html_file_path="decline.html"
            )
        self.message_user(request, "Selected forms have been rejected.")

    def delete_user(self, request, queryset):
        for form in queryset:
            send_mail(
                recipient=form.email,
                subject="Account Termination",
                attachment=None,
                html_file_path="termination.html"
            )
        queryset.delete()
        self.message_user(request, "Selected forms have been deleted.")

admin.site.register(UserForm, UserFormAdmin)
admin.site.register(ApprovedUser)
