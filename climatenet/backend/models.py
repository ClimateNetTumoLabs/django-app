from django.db import models
import uuid


class Device(models.Model):
    generated_id = models.CharField(max_length=200, unique=True, default=uuid.uuid4)
    name = models.CharField(max_length=200, default="Unnamed Device")
    parent_name = models.CharField(max_length=200, default="None")
    latitude = models.DecimalField(max_digits=18, decimal_places=15, default=0.000000000000000)
    longitude = models.DecimalField(max_digits=18, decimal_places=15, default=0.000000000000000)

    def __str__(self):
        return f"{self.generated_id}"
