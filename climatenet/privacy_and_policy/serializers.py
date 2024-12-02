# serializers.py
from rest_framework import serializers
from .models import PrivacyPolicy

class PrivacyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = ['title_en', 'title_hy', 'content_en', 'content_hy']
