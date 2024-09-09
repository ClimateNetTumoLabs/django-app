from rest_framework import serializers
from django.conf import settings
from .models import Participant, Device

class ParticipantSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Participant
        fields = '__all__'

    def get_image_url(self, obj):
        if obj.image:
            return f"{settings.MEDIA_URL}{obj.image}"
        return None


class DeviceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'
