from django.contrib import admin
from .models import UserDataCookie

@admin.register(UserDataCookie)
class UserDataCookieAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'email', 'phone', 'longitude', 'latitude', 'created_at')
