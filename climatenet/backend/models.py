from django.db import models


class DeviceDetail(models.Model):
    generated_id = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200)
    parent_name = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=18, decimal_places=15)
    longitude = models.DecimalField(max_digits=18, decimal_places=15)

    def __str__(self):
        return f"{self.generated_id}"
