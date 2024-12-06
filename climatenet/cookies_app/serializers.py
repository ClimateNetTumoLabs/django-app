from rest_framework import serializers
from .models import UserDataCookie

class UserDataCookieSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDataCookie
        fields = ['name', 'surname', 'email', 'phone', 'longitude', 'latitude']