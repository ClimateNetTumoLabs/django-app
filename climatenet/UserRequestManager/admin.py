from django.contrib import admin
from .models import UserForm, ApprovedUser
from .helper import send_mail
from django import forms
import os
import requests
import json
from django.conf import settings

class UserFormAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'coordinates', 'status', 'submitted_at','device_id')
    actions = ['approve_forms', 'reject_forms', 'delete_user']



    def approve_forms(self, request, queryset):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        things_dir = os.path.join(BASE_DIR, "UserRequestManager/things")
        
        # Ensure the `things` directory exists
        os.makedirs(things_dir, exist_ok=True)

        approved_users = []
        for form in queryset:
            print(f"Form {form.name} has already been approved.")
            print(form.status)
            if form.status == 'approved':
                continue

            try:
                # Make the API call
                response = requests.get("https://ze0hor39xk.execute-api.us-east-1.amazonaws.com/default/certificate_automation")
                response.raise_for_status()
                certificate_id = response.headers.get("Id")
                if not certificate_id:
                    self.message_user(request, f"Certificate ID not found for {form.name}.", level="error")
                    continue

                # Save the response content as a zip file in the `things` directory
                file_path = os.path.join(things_dir, f"{certificate_id}_certificate.zip")
                with open(file_path, "wb") as file:
                    file.write(response.content)
            
            except requests.RequestException as e:
                self.message_user(request, f"API call failed for {form.name}: {e}", level="error")
                continue

            # Create ApprovedUser object
            approved_user = ApprovedUser(
                name=form.name,
                email=form.email,
                phone=None,  # Add phone number handling if necessary
                coordinates=form.coordinates,
                device_id=certificate_id,
            )
            approved_users.append(approved_user)

            # Update form status to 'approved'
            form.status = 'approved'
            form.device_id = certificate_id
            form.save()

            # Send approval email
            send_mail(
                recipient=form.email,
                subject="Approval Notification",
                attachment=file_path,  
                html_file_path="approval.html",
                name=form.name
            )

        # Bulk create approved users in the database
        ApprovedUser.objects.bulk_create(approved_users)
        self.message_user(request, "Selected forms have been approved and moved to Approved Users.")

    def reject_forms(self, request, queryset):
        # queryset.update(status='rejected')
        for form in queryset:
            print(f"Form {form.name} has already been approved.")
            print(form.status)
            if form.status == 'approved':
                self.message_user(request, "Selected User has already been approved.",level="error")
                continue
            send_mail(
                recipient=form.email,
                subject="Rejection Notification",
                attachment=None,
                html_file_path="decline.html"
            )
            form.status = 'rejected'
            form.save()
            self.message_user(form.email, "Selected forms have been rejected.")
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

class ApprovedUserForm(forms.ModelForm):
    class Meta:
        model = ApprovedUser
        fields = ['name', 'email', 'phone', 'coordinates', 'device_id']


from django.utils.html import format_html
from django.urls import reverse
import os

class ApprovedUserAdmin(admin.ModelAdmin):
    form = ApprovedUserForm
    list_display = ('name', 'email', 'phone', 'coordinates', 'device_id', 'created_at', 'download_certificate')
    search_fields = ('name', 'email', 'device_id')
    list_filter = ('created_at',)
    actions = ['delete_approved_users']

    def download_certificate(self, obj):
        """
        Provides a link to download the certificate file for the user.
        """
        # Path to the certificate file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, "UserRequestManager/things", f"{obj.device_id}_certificate.zip")

        # Check if the file exists
        if os.path.exists(file_path):
            download_url = reverse('download_certificate', args=[obj.device_id])
            return format_html('<a href="{}" target="_blank">Download</a>', download_url)
        return "No file"

    download_certificate.short_description = "Certificate"

    def delete_aws_thing_and_certificate(self, device_id, request):
        """
        Handles the deletion of an AWS IoT thing and its associated certificate.
        """
        try:
            # API payload to delete the AWS thing
            payload = {
                "thingName": device_id,
                "delete": True
            }

            # API call to delete AWS IoT thing
            response = requests.post(
                "https://ze0hor39xk.execute-api.us-east-1.amazonaws.com/default/certificate_automation",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )
            response.raise_for_status()

            if response.status_code == 200:
                # Path to the certificate file
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                file_path = os.path.join(base_dir, "UserRequestManager/things", f"{device_id}_certificate.zip")

                # Delete the certificate file
                if os.path.exists(file_path):
                    os.remove(file_path)
                else:
                    self.message_user(request, f"Certificate file for {device_id} not found.", level="warning")
            else:
                self.message_user(request, f"Failed to delete thing '{device_id}'. API Response: {response.text}", level="error")

        except requests.RequestException as e:
            self.message_user(request, f"API call failed for {device_id}: {e}", level="error")
        except Exception as e:
            self.message_user(request, f"Error deleting certificate file for {device_id}: {e}", level="error")

    def delete_model(self, request, obj):
        """
        Overriding delete_model to handle AWS thing and certificate deletion before user deletion.
        """
        self.delete_aws_thing_and_certificate(obj.device_id, request)

        # Notify user about deletion
        send_mail(
            recipient=obj.email,
            subject="Account Deletion Notification",
            attachment=None,
            html_file_path="account_deletion.html"
        )
        super().delete_model(request, obj)
        self.message_user(request, f"Approved User '{obj.name}' was successfully deleted.")

    def delete_approved_users(self, request, queryset):
        """
        Custom action to delete multiple approved users along with their AWS things and certificates.
        """
        for user in queryset:
            self.delete_aws_thing_and_certificate(user.device_id, request)
            try:
                user_form = UserForm.objects.get(email=user.email , device_id=user.device_id)
                user_form.status = 'terminated'
                user_form.device_id = None
                user_form.save()
            except UserForm.DoesNotExist:
                self.message_user("User not found",level="error")
                pass
            # Notify user about deletion
            send_mail(
                recipient=user.email,
                subject="Account Deletion Notification",
                attachment=None,
                html_file_path="account_deletion.html"
            )

        queryset.delete()
        self.message_user(request, "Selected Approved Users have been deleted.")

    delete_approved_users.short_description = "Terminate selected Approved Users"

admin.site.register(UserForm, UserFormAdmin)
admin.site.register(ApprovedUser,ApprovedUserAdmin)