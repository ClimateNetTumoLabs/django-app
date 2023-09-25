from rest_framework import serializers
from .models import Device, About, DeviceDetail, Footer, ContactUs

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'

class DeviceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceDetail
        fields = '__all__'
class AboutPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = About
        fields = '__all__'

class FooterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Footer
        fields = '__all__'

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = '__all__'
