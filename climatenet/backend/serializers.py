from rest_framework import serializers
from .models import DeviceDetail


class DeviceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceDetail
        fields = '__all__'
