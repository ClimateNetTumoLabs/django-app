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
from django.http import FileResponse, Http404
from django.conf import settings
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