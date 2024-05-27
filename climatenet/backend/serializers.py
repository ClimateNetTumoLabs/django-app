from rest_framework import serializers
from .models import Device


class DeviceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'
