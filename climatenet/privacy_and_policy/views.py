from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import PrivacyPolicy
from .serializers import PrivacyPolicySerializer

class PrivacyPolicyView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        policy = PrivacyPolicy.objects.last()  # Fetch the latest privacy policy
        if policy:
            serializer = PrivacyPolicySerializer(policy)
            return Response(serializer.data)
        return Response({"detail": "Can`t find Privacy and Policy "}, status=404)
