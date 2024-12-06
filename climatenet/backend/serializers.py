from rest_framework import serializers
from .models import Device, TeamMember
from django.conf import settings


class DeviceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'


class TeamMemberSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = TeamMember
        fields = '__all__'

    def get_image_url(self, obj):
        if obj.image:
            return f"{settings.MEDIA_URL}{obj.image}"
        return None

# class SubmitFormSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserForm
#         fields = ['name', 'email', 'message', 'coordinates']

#     def create(self, validated_data):
#         return UserForm.objects.create(**validated_data)