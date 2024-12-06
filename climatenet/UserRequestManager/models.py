from django.db import models
from django.contrib.auth.models import User
import uuid

class UserForm(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) 
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'), 
        ('approved', 'Approved'), 
        ('rejected', 'Rejected')
    ], default='pending')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    coordinates = models.CharField(max_length=50, 
                                    help_text="Latitude, Longitude (e.g., 40.7128, -74.0060)", 
                                    default="0.0, 0.0")
    submitted_at = models.DateTimeField(auto_now_add=True)
    device_id = models.CharField(max_length=255, null=True, blank=True, default=None)
   

    def __str__(self):
        return f"{self.name} - {self.status}"
    
class ApprovedUser(models.Model): 
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.IntegerField(unique=True, blank=True, null=True, default=None)
    coordinates = models.CharField(
        max_length=50, 
        help_text="Latitude, Longitude (e.g., 40.7128, -74.0060)", 
        default="0.0, 0.0"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    device_id = models.CharField(max_length=255, null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.name} - {self.email} - {self.device_id}"
