from django.db import models
from django.contrib.auth.models import User
import uuid

class Device(models.Model):
    generated_id = models.CharField(max_length=200, unique=True, default="")
    name = models.CharField(max_length=200, default="")
    parent_name = models.CharField(max_length=200, default="")
    latitude = models.DecimalField(max_digits=18, decimal_places=15, default=0.0)
    longitude = models.DecimalField(max_digits=18, decimal_places=15, default=0.0)

    def __str__(self):
        return f"{self.generated_id}"


class TeamMember(models.Model):
    generated_id = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    github_link = models.CharField(max_length=200, null=True, blank=True)
    linkedin_link = models.CharField(max_length=200, null=True, blank=True)
    image = models.ImageField(upload_to="team", null=True, blank=True)

    def __str__(self):
        return f"{self.generated_id}"

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

    def __str__(self):
        return f"{self.name} - {self.status}"