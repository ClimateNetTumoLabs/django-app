from django.db import models

class UserDataCookie(models.Model):
    name = models.CharField(max_length=100)  # Name
    surname = models.CharField(max_length=100)  # Surname
    email = models.EmailField(unique=True)  # Email (unique)
    phone = models.CharField(max_length=15)  # Phone number
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)  # Longitude
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)  # Latitude
    created_at = models.DateTimeField(auto_now_add=True)  # Date of creation

    def __str__(self):
        return f"{self.name} {self.surname} ({self.email})"