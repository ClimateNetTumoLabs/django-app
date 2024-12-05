from rest_framework import serializers
from .models import UserForm
from django.conf import settings


class SubmitFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserForm
        fields = ['name', 'email', 'message', 'coordinates']

    def create(self, validated_data):
        return UserForm.objects.create(**validated_data)