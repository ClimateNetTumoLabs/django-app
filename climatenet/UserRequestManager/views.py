from django.shortcuts import render
from django.contrib import admin
from .models import UserForm
from datetime import datetime, timedelta
from django.db import connections
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import SubmitFormSerializer
from django.utils.translation import activate
from django.http import FileResponse, Http404,HttpResponse
from django.conf import settings
from django.urls import path
import os


# Create your views here.
class SubmitFormView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SubmitFormSerializer(data=request.data)
        if serializer.is_valid():
            # Save the form data without requiring a user
            user_form = serializer.save(user=None)  # or simply save the serializer
            return Response({"message": "Form submitted successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def download_certificate(request, device_id):
    """
    Serve the certificate file for download.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "UserRequestManager/things", f"{device_id}_certificate.zip")

    if os.path.exists(file_path):
        with open(file_path, "rb") as file:
            response = HttpResponse(file.read(), content_type="application/zip")
            response['Content-Disposition'] = f'attachment; filename="{device_id}_certificate.zip"'
            return response
    return HttpResponse("File not found.", status=404)