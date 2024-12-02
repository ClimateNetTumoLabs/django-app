from django.contrib import admin
from .models import PrivacyPolicy

# Register your models here.
@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(admin.ModelAdmin):
    list_display = ('title',)